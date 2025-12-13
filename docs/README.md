frontend（CamelCase）
-------------------------
backend（SnakeCase）
-------------------------
shemasではCamelModel（キャメル⇔スネーク変換）を必ず継承する

# 備考
- 以降では`id:str`になっているが`id:int`に統一する。
- 基本的なバックエンドフォルダ構成：
  - api/ : エンドポイント
  - services/ : ビジネスロジック。APIから呼ばれる主処理
  - crud/ : DB操作
  - models/ : DBテーブル定義
  - schemas/ : Pydanticバリデーション。リクエスト・レスポンス型
  - deps/ : 依存関数
  - core/ : 共通ユーティリティ（設定、JWT、ハッシュ、例外など）
  - seeds/ : 初期データ投入スクリプト

## テーブル


## 共通
- エラーフォーマット
>```ts
>type ErrorResponse = {
>   code: string;  //フロント判別用の一意なコード
>   detail: string;  //ユーザー向けメッセージ
>   fieldErrors?: {
>       [fiels: string]: string[];  //バリデーションエラーなどに使う（任意）
>   };
>};
>```


## `/auth` リソース  
### 2. 何ができるか
- 社員コード＋パスワードでログインする
- 許可されたIPアドレス以外からのログインを制限する（ただし施設長と役員または管理者はMFAあればログイン可）
- MFA必須ユーザーは、ログイン時にTOTPコードで二段階認証を完了する 
- 一時パスワード（`temporaryPassword`）でログインしているユーザーに`/auth/change-password`を促す 
- 現在のログインユーザー情報を取得する（`/auth/me`）
- ログアウトする（トークンを消去）
- アカウントページでMFAをセットアップする（施設長・役員・管理者）
- アカウントページでログイン済みユーザーがパスワードを変更する

### 3. どのように行うか
- ユースケース１：通常ログイン
    - フロントで「社員コード」「パスワード」を入力して送信
    - サーバー側で：
        - 社員コード・パスワードチェック
        - ログインしているIPアドレスを取得
        - `LoginIpPolicy`(テーブル)を参照して、このユーザーに対してIPを許可するか判定
    - 許可されれば：
        - アクセストークン（JWT）＋（リフレッシュトークン？）を生成
        - httpOnly Cookieにセット
        - レスポンスでユーザー情報を返す
    - ログイン完了後`mustChangePasswordAtNextLogin`が：
        - trueなら`/account`ページに遷移し、パスワードの変更を促す。
        - falseなら`/dashboard`に遷移
- ユースケース２：MFA必須ログイン
    - フロントで「社員コード」「パスワード」を送信
    - サーバー側で：
        - 資格情報OK
        - IPは許可外だが「MFA有効かつ施設長・役員・管理者」を満たす場合
        - ワンタイムな`temporary_token`を発行
    - フロントはTOTP入力画面に：
        - `temporary_token`+`totp_code`で`/auth/mfa/verify-login`にPOST
    - サーバーでTOTPが正しければ：
        - 本番アクセストークン（JWT）＋Cookieを発行 
        - ユーザー情報を返す
    - ログイン完了後`mustChangePasswordAtNextLogin`が：
        - trueなら`/account`ページに遷移し、パスワードの変更を促す。
        - falseなら`/dashboard`に遷移
- ユースケース３：MFAセットアップ
    - ログイン済みユーザーが「MFA設定画面」を開く
    - フロントが`/auth/mfa/setup-init`を叩く
    - サーバー側は：
        - TOTPシークレット生成
        - otpauth URL or QRコード用文字列を返す（フロントは表示）
    - ユーザー側で：
        - Google AuthenticatorなどでQRを読み取る
        - TOTPコードを入力して`/auth/mfa/setup-verify`に送る
    - 成功したら：
        - ユーザーの`mfa_enabled=true`を保存
        - 今後のログインフローでMFAが要求されるようになる
- ユースケース４：ログアウト
    - ログイン済みユーザーがログアウトボタンを押す
    - `/auth/logout`を叩いてログアウト
- ユースケース５：パスワード変更
    - ログイン済みユーザーがアカウントページで「現在のパスワード」「新しいパスワード」を入力
    - サーバーが現在のパスワードを検証し、新パスワードの強度・ポリシーをチェック
    - 問題がなければパスワードを変更する

### 4&5. 入力と出力
- 認証系
    - `Post /api/v1/auth/login`
        - 権限：全従業員
        - ログイン時の分岐
            1. 社員コード・パスワードをチェック
            2. 成功なら、リクエスト元IPアドレスが許可されているか？
                - はい-->ログイン完了
                - いいえ-->権限チェック
            3. 施設長・役員・管理者であるか？
                - いいえ-->エラー
                - はい-->MFA有効か
            4. MFA有効か？
                - いいえ-->エラー
                - はい-->TOTPコードを入力
            5. TOTP検証
                - 失敗-->エラー
                - 成功-->ログイン完了
        - 入力
        >```json
        >{
        >    "employeeCode":"str",
        >    "password":"str"
        >}
        >```
        - 出力（2-はい）
        >```json
        >{
        >   "employeeId":"int",
        >   "grade":"str",
        >   "isAdmin":"boolean",
        >   "requiresMfa":false, //必ずfalse
        >   "mustChangePasswordAtNextLogin":"boolean"
        >}
        >```
        - 出力（4-はい）
        >```json
        >{
        >   "requiresMfa":true, //必ずtrue
        >   "temporaryToken":"str",
        >}
        >```
        - 出力（1で失敗）
        >```json
        >{
        >   // 401 Unauthorized
        >   "code":"invalid_credentials",
        >   "detail":"社員コードまたはパスワードが正しくありません。"
        >}
        >```
        - 出力（3-いいえ）
        >```json
        >{
        >   //403 Forbidden
        >   "code":"ip_not_allowed",
        >   "detail":"このネットワークからはログインできません。"
        >}
        - 出力（4-いいえ）
        >```json
        >{
        >   //403 Forbidden
        >   "code":"mfa_required_but_not_enabled",
        >   "detail":"外部からログインするには二段階認証の設定が必要です。許可されているネットワークからログインし、二段階認証の設定を完了してください。"
        >}
    - `POST /api/v1/auth/mfa/verify-login`
        - 権限：MFA有効化している役員・施設長または管理者
        - 入力
        >```json
        >{
        >    "temporaryToken":"str",
        >    "totpCode":"str"
        >}
        >```
        - 出力（成功時）
        >```json
        >{
        >   "employeeId":"int",
        >   "grade":"str",
        >   "isAdmin":"boolean",
        >   "mustChangePasswordAtNextLogin":"boolean"
        >}
        >```
        - 出力（5で失敗）
        >```json
        >{
        >   //400 Bad Request
        >   "code":"invalid_totp_code",
        >   "detail":"ワンタイムパスワードが正しくありません。"
        >}
        >```
        - 出力（5で失敗）
        >```json
        >{
        >   //400
        >   //temporaryTokenが期限切れ
        >   "code":"login_challenge_expired",
        >   "detail":"二段階認証の有効期限が切れました。最初からログインし直してください。"
        >}

    - `POST /api/v1/auth/logout`
        - 権限：全従業員
        - 入力：なし
        - 出力
        >```json
        >{
        >   "detail":"Logged out"
        >}
        >```
    - `GET /api/v1/auth/me`
        - 権限：全従業員
        - 入力：Cookieの`access_token`（JWT）
        - 出力
        >```json
        >{
        >   "user":{
        >     "employeeId": "int",
        >     "employeeCode": "str",
        >     "firstName": "str",
        >     "lastName": "str",
        >     "gradeName": "str",
        >     "isAdmin": "boolean",
        >     "mfaEnabled": "boolean"
        >     },
        >   "mustChangePasswordAtNextLogin":"boolean"
        >}
        >```
        or `401 Unauthhorized`
    - `POST /api/v1/auth/change-password`
        - 権限：全従業員
        - 入力
        >```json
        >{
        >   "currentPassword":"str",
        >   "newPassword":"str"
        >}
        >```
        - 出力（成功時）
        >```json
        >{
        >   // 204 No Content
        >   // フロントで「パスワードを変更しました」と表示
        >}
        >```
        - 出力（未ログイン/トークン不正）
        >```json
        >{
        >   // 401 Unauthenticated
        >   "code":"not_authenticated",
        >   "detail":"この操作にはログインが必要です。"
        >}
        >```
        - 出力（現在のパスワードが間違っている）
        >```json
        >{
        >   // 400 Bad Request
        >   "code":"current_password_mismatch",
        >   "detail":"現在のパスワードが正しくありません。"
        >}
        >```
        - 出力（新パスワードが弱い）
        >```json
        >{
        >   // 400 Bad Request
        >   "code":"weak_password",
        >   "detail":"新しいパスワードがぱしわーどポリシーを満たしていません。",
        >   "fieldErrors":{
        >       "newPassword":[
        >           "8文字以上にしてください。",
        >           "英字・数字・記号をそれぞれ1文字以上含めてください。"
        >]
        >}
        >}
        >```
        - 出力（新パスワードが現在のパスワードと同じ）
        >```json
        >{
        >   //400
        >   "code":"password_unchanged",
        >   "detail":"現在のパスワードと異なるものを設定してください。"
        >}
        >```
        - 出力（想定外のサーバー内部エラー）
        >```json
        >{
        >   // 500 Internal Server Error
        >   "code":"internal_server_error",
        >   "detail":"サーバー内部でエラーが発生しました。時間をおいて再度お試しください。"
        >}
- MFAセットアップ系
    - `POST /api/v1/auth/mfa/setup-init`
        - 権限：全従業員
        - 入力：なし
        - 出力（成功時）
        >```json
        >{
        >   "otpauthUrl":"str", //QRコード表示用
        >   "secret":"str" //手入力用
        >}
        >```
        - 出力（未ログイン/トークン不正）
        >```json
        >{
        >   // 401
        >   "code":"not_authenticated",
        >   "detail":"この操作にはログインが必要です。"
        >}
        >```
        - 出力（すでにMFAが有効）
        >```json
        >{
        >   // 400
        >   "code":"mfa_already_enabled",
        >   "detail":"すでに二段階認証が有効になっています。"
        >}
        >```
        - 出力（内部エラー）
        >```json
        >{
        >   // 500
        >   "code":"Internal_server_error",
        >   "detail":"二段階認証の設定中にエラーが発生しました。時間をおいて再度お試しください。"
        >}
        >```
    - `POST /api/v1/auth/mfa/setup-verify`
        - 権限：全従業員
        - 入力
        >```json
        >{
        >   "totpCode":"str"
        >}
        >```
        - 出力（成功時）
        >```json
        >{
        >   // 204 No Content
        >}
        >```
        - 出力（未ログイン/トークン不正）
        >```json
        >{
        >   // 401
        >   "code":"not_authenticated",
        >   "detail":"この操作にはログインが必要です。"
        >}
        >```
        - 出力（まだ`/mfa/setup-init`が呼ばれておらず、設定用シークレットが存在していない）
        >```json
        >{
        >   // 400
        >   "code":"mfa_not_initialized",
        >   "detail":"二段階認証の設定を開始してから確認コードを入力してください。"
        >}
        >```
        - 出力（TOTPコード不正）
        >```json
        >{
        >   // 400
        >   "code":"invalid_totp_code",
        >   "detail":"ワンタイムパスワードが正しくありません。"
        >}
        >```
        - 出力（内部エラー）
        >```json
        >{
        >   // 500
        >   "code":"internal_server_error",
        >   "detail":"二段階認証の設定確認中にエラーが発生しました。時間をおいて再度お試しください。"
        >}
        >```

## `/password-reset-requests`リソース&`/admin/password-reset-requests`リソース
### 1. そのAPIを使えるのはだれか
- ログインしていない状態の全ユーザー
- 管理者（ログイン済み）

### 2. 何ができるか
- ユーザー（未ログイン）
    - 「自分はこの社員コード・この事業所の職員です」という形でパスワードリセット依頼を登録する
- 管理者（ログイン済み）
    - リセット依頼一覧を確認する（未処理/処理済みなど）
    - 依頼に応じてパスワードを一時パスワードをリセットする（ここは`/employees/{employeeId}/reset-password`と連携）
    - リセット依頼を「処理済み」に更新する（いつ・誰が処理したか記録）


### 3. それをどのように行うか
- ユースケース１：従業員がパスワード忘れを申告
    - ログイン画面で「パスワードを忘れた方へ」をクリック
    - 画面で「社員コード」と「事業所」を入力（選択）し、送信
    - サーバー側で：
        - 該当の`employeeCode`+`officeId`の組み合わせが存在するかチェック（ただし、存在しなくても存在有無を外部に漏らさない）
        - `PasswordResetRequest`レコードを1件作成
    - 従業員には「リセット依頼を受け付けました。本部または所属事業所からの案内をお待ちください。」と表示
- ユースケース２：管理者がリセット依頼を処理
    - 管理者が管理画面の「パスワードリセット依頼一覧」を開く
    - 事業所・ステータス（未処理など）でフィルタして一覧取得
    - 対象の依頼を選び「一時パスワードを発行」ボタンを押す
    - フロントが以下を順に呼ぶ：
        - `POST /employees/{employeesId}/reset-password`で一時パスワードを発行
        - `PATCH /admin/password-reset-requests/{requestId}`でステータスを`processed`に変更し、`processedBy`や`processedAt`を記録
    - 管理者が発行した一時パスワードを本人に伝える
    - 本人は一時パスワードでログイン
    - `/auth/change-password`で本番パスワードに変更させる

### 4.5. 入力と出力
- `POST /password-reset-requests`
    - 入力
    >```json
    >{
    >   "employeeCode":"str",
    >   "officeId":"str",
    >   "note":"str"  //備考（任意）
    >}
    >```
    - 出力（成功時）
    >```json
    >{
    >   "message":"パスワードリセットの依頼を受け付けました。本部または所属事業所からの案内をお待ちください。"
    >}
    >```
    - 出力（エラー）
    >```json
    >{
    >   //400
    >   //入力が明らかに変（空文字など）
    >   "code":"invalid_input",
    >   "detail":"社員コードと事業所を入力してください。",
    >   "fieldErrors":{
    >       "employeeCode":["社員コードを入力してください。"],
    >       "officeId":["事業所を選択してください。"]
    >       },
    >
    >   //429 Too Many Requests
    >   //短時間に同一の社員コードと事業所から大量のリクエスト
    >   "code":"too_many_reset_requests",
    >   "detail":"パスワードのリセットが上限を超えました。しばらく時間をおいてから再度お試しください。",
    >
    >   //500
    >   //内部エラー
    >   "code":"Internal_server_error",
    >   "detail":"パスワードのリセット依頼の送信にエラーが発生しました。しばらく時間をおいてから再度お試しください。"
    >}

- `GET /admin/password-reset-requests`
    - 入力:なし（クエリつけてもいい）
    - 出力（成功時）
    >```json
    >{
    >   // 構造を変えてもいい
    >   "requestId":"str",
    >   "employeeId":"str",
    >   "employeeCode":"str",
    >   "employeeName":"str",
    >   "officeId":"str",
    >   "officeName":"str",
    >   "status":"pending"|"processed"|"rejected",
    >   "note":"str"|null,
    >   "adminNote":"str"|null,
    >   "createdAt":"str",  //この申請がされたのはいつか
    >   "processedAt":"str"|null,  //申請に対して処理をしたのはいつか
    >   "processedBy":{
    >       "employeeId":"str",
    >       "employeeName":"str"
    >       } | null,
    >}
    - 出力（エラー時）
    >```json
    >{
    >   //401 未ログイン
    >   "code":"not_authenticated",
    >   "detail":"この操作にはログインが必要です。",
    >
    >   //403 権限不足
    >   "code":"permission_denied",
    >   "detail":"この操作を行う権限がありません。",
    >}

- `PATCH /admin/password-reset-requests/{requestId}`
    - 入力
    >```json
    >{
    >   "status":"processed"|"rejected",
    >   "adminNote":"str"|null  //任意：「本人確認済み」「電話で対応」など
    >}
    - 出力（成功時）
    >```json
    >{
    >   "requestId":"str",
    >   "employeeId":"str",
    >   "employeeCode":"str",
    >   "employeeName":"str",
    >   "officeId":"str",
    >   "officeName":"str",
    >   "status":"processed"|"rejected",
    >   "note":"str"|null,
    >   "adminNote":"str"|null,
    >   "createdAt":"str",  //この申請がされたのはいつか
    >   "processedAt":"str"|null,  //申請に対して処理をしたのはいつか
    >   "processedBy":{
    >       "employeeId":"str",
    >       "employeeName":"str"
    >       } | null,
    >}
    - 出力（エラー時）
    >```json
    >{
    >   //401 not_authenticated
    >   //403 permission_denied
    >   
    >   //404 Not Found
    >   "code":"password_reset_request_not_found",
    >   "detail":"指定されたパスワード依頼が見つかりません。",
    >
    >   //400 すでにprocessedのものを再度更新
    >   "code":"invalid_status_transition",
    >   "detail":"このパスワードリセット依頼はすでに処理済みのため、状態を更新できません。",
    >
    >   //400 入力フォーマット不正
    >   "code":"invalid_input",
    >   "detail":"入力内容が不正です。",
    >   "fieldErrors":{
    >       "status":["状態には「処理済み」または「拒否」を指定してください。"]
    >       },
    >
    >   //500 内部エラー
    >}

- (`POST /employees/{employeeId}/reset-password`)
    - 管理者が対象従業員に「一時パスワード」を発行する
    - 入力:なし（サーバー側で自動生成）
    - 出力（成功時）
    >```json
    >{
    >   "employeeId":"str",
    >   "temporaryPassword":"str",
    >   "mustChangePasswordAtNextLogin":true  // 必ずtrue、`/auth/login`でログインに成功したユーザーがこのフラグを持っていれば`/auth/change-password`を必須で踏ませる導線にする
    >}
    - 出力（エラー時）
    >```json
    >{
    >   // 401 not_authenticated
    >   // 403 permisson_denied
    >   // 404 employee_not_found
    >
    >   // 403 
    >   // 退職など
    >   "code":"employee_disabled",
    >   "detail":"この従業員のアカウントは無効化されています。",
    >
    >   // 429
    >   "code":"too_many_password_resets",
    >   "detail":"この従業員のパスワードリセットが短時間に複数回行われています。しばらくしてから再度お試しください。",
    >
    >   // 500 internal_server_error
    >}


## `/employees`リソース
### 1. そのAPIを使えるのはだれか
- 施設長（自施設内のみ）
- 役員・管理者

### 2. 何ができるか
- 従業員一覧の取得（検索・フィルタ付き）
- 特定従業員の詳細取得
- 従業員の新規登録
- 従業員情報の更新
- 一時パスワードの発行

### 4.5. 入力・出力
- `GET /employees`
    - 権限
        - 施設長：クエリの`siteId`は無視し、現在のユーザーの`siteId`で固定
        - 役員・管理者：全従業員可
    - 入力（クエリ）
    >```ts
    >{
    >   siteId:string;  // 施設をしぼる
    >   occupation:string;
    >   grade:string;
    >   status:"avtive"|"inactive"|"on_leave"  // 在職|退職|休職
    >   search:string;  // 氏名・社員コードなどの部分一致
    >   page:number; // デフォルト１
    >   pageSize:number; // デフォルト20など
    >}
    - 出力（成功時）
    >```json
    >{
    >   "items":[],  // 中身は未定
    >   "page":1,
    >   "pageSize":20,
    >   "totalCount":2
    >}
    - 出力（エラー）
    >```json
    >{
    >   // 401
    >   // 403
    >   // 400
    >   // 500
    >}

- `GET /employees/{employeeId}`
    - 権限
        - 施設長：自分のsiteの従業員のみ可
        - 役員・管理者：全従業員
    - 入力（パスパラメータ）
    >`employeeId:string`
    - 出力（成功時）
    >```json
    >{
    >   // 未定
    >}
    - 出力（エラー時）
    >```json
    >{
    >   // 401
    >   // 403
    >   // 404
    >   // 500
    >}

- `POST /employees`
    - 権限：管理者のみ
    - 入力
    >```json
    >{
    >   // 未定
    >   // バリデーション必須
    >}
    - 出力（成功時）
    >```json
    >{
    >   // GET employees/{employeeId}と同じ
    >}
    - 出力（エラー時）
    >```json
    >{
    >   // 401
    >   // 403
    >   // 400
    >   // 409
    >   // 500
    >}

- `PATCH employees/{employeeId}`
    - 権限：管理者のみ
    - 入力
    > 更新したいキーとバリュー
    - 出力（成功時）
    >```json
    >{
    >   // GET employees/{employeeId}と同じ
    >}
    - 出力（エラー時）
    >```json
    >{
    >   // 401
    >   // 403
    >   // 400
    >   // 500
    >}

- `POST /employees/{employeeId}/reset-password`
    - 管理者のみ
    - `/auth`リソース参照


## `/sites`リソース（拠点/施設）
### 1. 誰が使うか
- 管理者・役員
- 施設長
- 一般従業員

### 2. 何ができるか
- 拠点一覧の取得
- 特定拠点の詳細取得
- 拠点の新規登録
- 拠点情報の更新

### 4.5. 入力・出力
- `GET /sites`
    - 権限：役員・管理者のみ
    - 入力（クエリ）
    >```ts
    >status:"active"|"inactive"  // 省略時は全件
    - 出力（成功時）
    >```json
    >{
    >   "items":[]
    >}

- `GET /sites/{siteId}`
    - 権限
        - 一般従業員・施設長：自分の施設のみ
        - 役員・管理者：全施設
    - 入力（パスパラメータ）
    >`siteId:string`
    - 出力（成功時）
    >```json
    >{
    >   "detail":[]
    >}

- `POST /sites`
    - 権限：管理者のみ
    - 入力
    >```json
    >{
    >   "siteName":"str",
    >   "status":"active"|"inactive"|null,  // 省略時"active"
    >   "address":"str"|null,
    >   "phoneNumber":"str"|null
    >   // その他未定
    >}
    - 出力（成功時）
    >```json
    >{
    >   "detail":[]
    >}

- `PATCH /sites/{siteId}`
    - 権限
        - 施設長：自分の施設のみ
        - 管理者：全施設
    - 入力
    >更新したいキーとバリュー
    - 出力（成功時）
    >```json
    >{
    >   "detail":[]
    >}
- エラー時の出力は適当に


## `/offices`リソース
- `/sites`リソースとほとんど同じ
- `siteId`が従属する


## `/assignments`リソース
### 1. 誰が使うか
- 施設長
    - 自分の施設（site）配下のofficeに所属する従業員について今期の「被考課者リスト（誰を評価対象にするか）」を作成・更新・閲覧
- 役員・管理者
    - 全事業所のassignmentsの操作

### 2. 何ができるか
- 評価期×事業所ごとの被考課者リストの管理
- 個別被考課者のassignmentsの参照・更新
- `evaluation-tasks`の親
    - `assignmentId`をキーに、働き方の指針・業務考課の二つの`taskId`がぶら下がる

### 3. それをどのように行うか
- ユースケースA-1：期初に事業所ごとの被考課者リストを作成する
    - 目的
        - 施設長が、今期の評価対象者をoffice単位で登録する
    - 事前条件
        - 評価期（period）がperiodマスタに登録済み
        - `site,office,employees`が登録済み
        - ログイン済みで施設長は自分の`site`に対する管理権限を持つ
    - 基本フロー
        - 施設長が割り当てページで対象の`period`と`office`を選択する
        - フロントは`GET /employees?officeId=...&status=active`を叩き、候補従業員リストを取得
        - UI上で「今期の被考課者」に含める従業員にチェックを入れる
        - 送信ボタンを押し、チェックされた従業員について、フロントから`POST /assignments`を実行
        - サーバーはバリデーションを行い、`assignment`レコードを作成
        - （内部処理）このassignmentを起点にevaluation_tasksを自動生成する

- ユースケースA-2：退職・長期休職などで被考課者を評価対象から外す
    - 目的
        - 施設長または管理者が期の途中で被考課者を「今期は評価対象外」にする
    - 事前条件
        - 対象従業員のassignmentが`active`として存在している
        - 退職・休職などの事実が人事システム側で確定している
    - 基本フロー
        - 施設長が割り当てページで対象従業員を選択する
        - 詳細画面で「今期の評価対象から外す」ボタンを押す
        - フロントが`PATCH /assignments/{assignmentId}`を送る：`status="inactive"`
        - サーバーはassignmentのstatusを更新
        - （内部処理）assignmentに紐づくevaluation_tasksを取得し、`status="cancelled"`などに一括更新する

- ユースケースA-3：組織変更・異動に伴いassignmentを見直す
    - 目的
        - 管理者が期の途中で被考課者のoffice/siteの所属が変更された場合、assignmentを確認・調整する
    - 事前条件
        - employees側で異動（officeIdの変更）が登録済み
        - 対象従業員に対するassignmentが存在する
    - 基本フロー
        - 管理者が「異動者一覧」画面を開く
        - 対象periodについて、異動した従業員のassignmentを一覧表示
        - 各従業員について、どのofficeのassignmentが適切か判断する
        - 原則として,旧officeのassignmentを`inactive`にする
        - （内部処理）旧assignmentに紐づくevaluation_tasksをキャンセルし、新assignment用にevaluation_tasksを生成する
    - 例外
        - すでに一次評価がかなり進んでおり、途中でofficeだけ変えるのはむしろ弊害というケースでは、今期は旧officeのassignmentのまま評価完了させ、次期から新officeでassignmentを作成する運用もあり

- ユースケースA-4：被考課者一覧の確認・監査
    - 目的
        - 施設長・役員・管理者が期ごと・事業所ごとに「誰が評価対象か」を定期的に確認する
    - 事前条件
        - assignmentが作成済み
    - 基本フロー
        - 管理画面などで`periodId`と`officeId`を選択
        - フロントが`GET /assignments?periodId=...&officeId=...&status=active`を呼び出し、一覧を表示
        - 必要に応じてemployeeリスト（全従業員）と突き合わせ、漏れがないかチェック
        - 漏れがあればA-1のフローでassignmentを追加作成

- ユースケースA-5：assignmentを起点にevaluation_tasksを一括生成する（内部処理）
    - 目的
        - 期初またはassignment作成後に、カテゴリ×段階の具体的なタスクを自動生成する
    - 事前条件
        - assignmentsが揃っている
        - カテゴリ（働き方の指針・業務考課）とそれぞれのデフォルト評価者ロジックが決まっている
    - 基本フロー
        - `GET /assignments?periodId=...&status=active`で対象assignment群を取得
        - 各assignmentについて：
            - カテゴリ×段階の組み合わせを決定
            - 評価者（evaluatorEmployeeId）をルールやUIで決定済みに情報から拾う
        - `evaluation_tasks`テーブルにレコードを作成
        - 以降、評価者ブラウザ側はevaluation_tasksだけを意識すればよくなる

### 4.5. 入力・出力
- `GET /assignments`
    - 入力（クエリ）
    >```ts
    >   siteId:string  // 施設長の場合は無視してサーバー側で固定
    >   officeId:string;
    >   periodId:string;
    >   subjectEmployeeId:string;  //特定の被考課者
    >   status:"active"|"inasctive";
    >   page:number;
    >   pageSize:number

- `GET /assignments/{assignmentId}`
    - 入力（パス）
    >```ts   
    >   assignmentId:string;
    >   // 施設長はassignment.siteIdが自分のsiteIdの場合のみ許可

- `POST /assignments`
    - 入力
    >```json
    >{
    >   "periodId":"str",  // 必須
    >   "siteId":"str",  // 必須
    >   "officeId":"str",  // 必須
    >   "subjectEmployeeId":"str",  // 必須：被考課者のemployeeId
    >   "status":"active"|"inasctive",  // 任意：省略時"active"
    >}

- `PATCH /assignments/{assignmentId}`
    - 入力
    >```json
    >{
    >   // periodId,siteId,officeId,subjectEmployeeIdは原則更新不可にし、変更が必要なケース（誤登録など）はstatus="inactive"にし再作成のほうがいいかもしれない
    >   "status": "active"|"inactive"
    >}


## `/evaluation-tasks`リソース
### 1. 誰が使うか
- 考課者
    - 自分のタスク一覧を取得
    - 個々のタスクの状態（未開始・進行中・完了）を更新
- 施設長
    - 自施設のタスクの進捗を一覧・集計
    - 必要に応じてタスクをキャンセル・スキップ
- 管理者
    - 全事業所でタスク進捗をモニタリング
    - 組織変更・誤設定の修正でタスクをキャンセル・再割り当てなど

### 2. 何ができるか
- 評価タスクの取得
- 単一タスクの詳細取得
- タスクのステータス更新

### 3. それをどのように行うか
- ユースケースT-1：考課者が自分のタスク一覧を確認する
    - 目的
        - 考課者が「自分がやるべき評価」が何かを一覧で確認する
    - 事前条件
        - evaluation_tasksが生成済みで、`evaluatorEmployeeId`が設定されている
    - 基本フロー
        - 考課者が「マイ評価タスク」的なのを開く
        - フロントまたはサーバーで`GET /evaluation-tasks?evaluationEmployeeId=currentUser&periodId=...`に相当する検索
        - サーバーが`EvaluationTaskSummary[]`を返す
        - UIで被考課者名・カテゴリ・段階・ステータスなどを表示

- ユースケースT-2：考課者がタスクを開き、評価を入力して提出する
    - 目的
        -  考課者が、タスク単位で設問に回答し、タスクを完了状態にする
    - 事前条件
        - 該当taskIdのevaluation_taskが`not_started or in_progress`
        - 前段階のフェーズのタスクが完了済み（phaseがsecond以降なら）
    - 基本フロー
        - 考課者がタスク一覧から。対象タスクをクリック
        - フロントが`GET /evaluation-tasks/{taskId}`を叩く
        - サーバーは`EvaluationTaskDetail`（＋必要に応じてform/answers）を返す：`evaluationFormId`でフォーム定義を取得し、設問表示
        - 考課者が各設問にスコアを入力し、「一時保存」または「提出」ボタンを押す
        - フロントは`/evaluation-results`API（別リソース）で回答を保存
        - 提出ボタンの場合、続けて`PATCH /evaluation-tasks/{taskId}`を送信：`status="completed"`
        - サーバー側で：
            - ステータス遷移の妥当性チェック
            - 前段階タスクのcompleted状態を確認
            - OKならステータスを更新し、`submittedAt`を現在時刻で埋める
        - 更新後のEvaluationTaskDetailを返す

- ユースケースT-3：施設長・役員・管理者がタスク進捗をモニタリングする
    - 目的
        - period,site,office,category,phaseごとの完了状態を把握し、遅れている個所を特定する
    - 事前条件
        - evaluation_tasksが生成済み
    - 基本フロー
        - 進捗画面的なのを開く
        - フロントは`GET /evaluation-tasks?periodId=...&siteid=...&officeId=...`を叩く
        - サーバーから`EvaluationTaskSummary[]`を取得
        - フロントで集計処理：
            - 被考課者×caetgory×phaseのステータス
            - `completed,in_progress,not_started`の件数・割合
        - UIで表示

- ユースケースT-4：評価画面用に「タスク＋フォーム＋回答」をまとめて取得する
    - 目的
        - 考課者の画面で、1回のAPI呼び出しで「タスク情報・フォーム（設問）・既存回答」をまとめて取得できるようにする
    - 事前条件
        - taskIdが有効で、ログインユーザーがevaluatorである
    - 基本フロー
        - フロントが`GET /evaluation-tasks/{teskId}`を叩く
        - サーバー内部で：
            - `evaluation_tasks`から`EvaluationTaskDetail`を取得
            - `evaluationFormId`から設問フォームを取得
            - `taskId`から既存回答（evaluation_results）を取得
        - レスポンスとしてこんな感じ
        >```json
        >{
        >   "task":{ ...EvaluationTaskDetail },
        >   "form":{ ...EvaluationFormDetail },
        >   "answers":[ ... ]
        >}
        - フロントはこの1レスポンスを元に評価画面をレンダリング

### 4.5. 入力・出力
- 必要なら`evaluation_tasks`に`previousTaskId:string|null`のようなフィールドを持たせると実装が楽
- `GET /evaluation-tasks`
    - 入力（クエリ）
    >
    - 出力（成功時）
    >```ts
    >   items: EvaluationTaskSummary[];
    >   page:number; 
    >   pageSize:number;
    >   totalCount:number;
    例）
    >```json
    >   {
    >        "items": [
    >           {
    >            "taskId": "et_001",
    >            "assignmentId": "asg_001",
    >            "periodId": "2025-H1",
    >            "siteId": "site_001",
    >            "officeId": "office_001",
    >            "subjectEmployeeId": "emp_101",
    >            "evaluatorEmployeeId": "emp_201",
    >            "category": "work_attitude",
    >            "phase": "first",
    >            "status": "in_progress"
    >            },
    >            {
    >            "taskId": "et_002",
    >            "assignmentId": "asg_001",
    >            "periodId": "2025-H1",
    >            "siteId": "site_001",
    >            "officeId": "office_001",
    >            "subjectEmployeeId": "emp_101",
    >            "evaluatorEmployeeId": "emp_301",
    >            "category": "job_performance",
    >            "phase": "first",
    >            "status": "not_started"
    >            }
    >        ],
    >        "page": 1,
    >        "pageSize": 20,
    >        "totalCount": 2
    >        }

- `GET /evaluation-tasks/{taskId}`
    - 入力（パス）
    >```ts
    >   taskId:string;
    - 出力（成功時）
    >```ts
    >   task: EvaluationTaskDetail;
    例）
    >```json
    >   {
    >        "task": {
    >            "taskId": "et_001",
    >            "assignmentId": "asg_001",
    >            "periodId": "2025-H1",
    >            "siteId": "site_001",
    >            "officeId": "office_001",
    >            "subjectEmployeeId": "emp_101",
    >            "evaluatorEmployeeId": "emp_201",
    >            "category": "work_attitude",
    >            "phase": "first",
    >            "status": "in_progress",
    >            "evaluationFormId": "form_work_attitude_G03",
    >            "subjectName": "田中 太郎",
    >            "evaluatorName": "佐藤 花子",
    >            "officeName": "仙台第1事業所",
    >            "siteName": "仙台拠点",
    >            "editable": true,
    >            "createdAt": "2025-03-01T10:00:00+09:00",
    >            "updatedAt": "2025-03-10T14:30:00+09:00",
    >            "submittedAt": null
    >        }
    >        }


- `PATCH /evaluation-tasks/{taskId}`
    - 入力
    >```ts
    >   status:
    - 出力（成功時）
    >```ts
    >   task: EvaluationTaskDetail;


## `periods`リソース
### 1. 誰が使うか
- 管理者
- 施設長

### 2. 何ができるか
- 評価期（年度・上期/下期）の定義・一覧・詳細の管理
- 開始日・終了日の管理
- 締切り状態・ロック状態の管理

### 4.5. 入力・出力
- 共通型
>```ts
>   type PeriodStatus = "planned" | "open"| "closed";  // 考課前・考課実施中・完全締め切り
>
>   type Period = {
>        periodId: string;         // 例: "2025-H1", "2025-H2", "2025-FY"
>        name: string;             // 表示名: "2025年度 上期" など
>        startDate: string;        // "2025-04-01" (ISO8601 日付)
>        endDate: string;          // "2025-09-30"
>        status: PeriodStatus;     // planned/open/closed
>        isActive: boolean;        // UIでの選択対象かどうか（過去期を非表示にするなど）
>        lockAssignmentsAt?: string | null;  // 被考課者登録を締め切る日時
>        lockEvaluationsAt?: string | null;  // 評価入力を締め切る日時
>        createdAt: string;
>        updatedAt: string;
>        createdBy: string;
>        updatedBy: string;
>        };

- `GET /periods`
    - 入力（クエリ）
    >```ts
    >   // 施設長や一般従業員も参照可能
    >   status: PeriodStatus;
    >   page: number;
    >   pageSize: number;
    - 出力（成功時）
    >```json
    >{
    >   "items": "Periods[]",
    >   "page": "number",
    >   "pageSize": "number",
    >   "totalCount": "number"
    >}

- `GET /periods/{periodId}`
    - 入力（パス）
    >```ts
    >   periodId: string;
    - 出力（成功時）
    >```json


- `POST /periods`
    - 入力
    >```json
    >   "periodId": "str",  // 必須
    >   "periodName": "str" // 必須
    >   "startDate": "str", // 必須
    >   "endDate": "str",   // 必須
    >   "status": PeriodStatus,  // 任意：デフォルト"planned"
    >   "lockAssignmentAt": "str"|null,
    >   "lockEvaluationAt": "str"|null
    - 出力（成功時）
    >```json

- `PATCH /periods/{periodsId}`
    - 入力
    >```json
    >   "periodName": "str" 
    >   "startDate": "str", 
    >   "endDate": "str",   
    >   "status": PeriodStatus,  
    >   "lockAssignmentAt": "str"|null, 
    >   "lockEvaluationAt": "str"|null,  
    - 出力（成功時）
    >```json

## `evaluation-results`リソース
### 1. 誰が使うか
- 考課者全般
- 管理者？

### 2. 何ができるか
- evaluation_task1件に対する回答データを管理
- タスクごとの回答（設問IDごとの点数・コメント）の保存・更新
> ワークフロー（誰が・どこまで進んでいるか）は`evaluation-tasks`の責務。回答内容（何点・どんなコメントか）は`evaluation-results`の責務。

### 3. 
- 人事考課機能全般のユースケース

仕様：

> 前段階の考課者が評価した結果を、次の段階の考課者は見て
> それを編集して保存して提出する。
> つまり **taskId は違う** けど、次の段階の評価は前段階の結果から始まる。

この仕様は、**今の「phase ごとに taskId を分ける設計」と両立します**。
ただし、「どうやって前段階の結果を引き継ぐか」をきちんと決める必要があります。

### データ構造的に必要な前提

* 同じ assignmentId + category の下に

  * `phase = "first"` のタスク（taskId = T1）
  * `phase = "second"` のタスク（taskId = T2）
  * `phase = "final"` のタスク（taskId = T3）
    が存在する。

* evaluation-results は

  * T1 に対して result1
  * T2 に対して result2
  * T3 に対して result3
    を保存する。

### 画面の動き（ロジック）のイメージ

1. 二次評価者が自分のタスク T2 を開く：

   * `GET /evaluation-tasks/{taskId=T2}` で T2 の情報を取得
   * バックエンドで「同じ assignmentId + category の `phase="first"` のタスク T1 を検索」
   * `GET /evaluation-results/{taskId=T2}` で T2 の結果を探す

     * まだなければ「二次評価は未入力」と判断
   * `GET /evaluation-results/{taskId=T1}` で一次評価結果 result1 を取得

2. API レスポンスとして、例えばこう返す：

   ```jsonc
   {
     "task": { ...T2 },
     "form": { ... },          // 設問シート
     "baseResult": { ... },    // 一次評価結果（T1 の result）
     "result": { ... }         // 二次評価者自身の結果（T2 の result、まだ無ければ null）
   }
   ```

3. フロント側では：

   * `result` が存在すればそれでフォームを初期化
   * まだ `result` が無ければ `baseResult` でフォームを初期化（＝一次の内容をコピーした状態で表示）

4. 二次評価者が編集・保存したとき：

   * `PUT /evaluation-results/{taskId=T2}` に「自分の回答」を送って保存
   * 一次の result1 は **そのまま残る**（上書きしない）

### ポイント

* **「一次を上書きする」のではなく、「一次結果をコピーして二次用の結果を作る」**
  → それぞれ独立した結果として保持される。
* `taskId` は phase ごとに違うが、
  「同じ assignmentId + category で前段階を辿る」ことで、いくらでもチェーンできる。
* したがって、**ロジックとしては問題なく通ります**。
  実装上は、「前段階の task/result をどう探して API レスポンスに含めるか」をきちんと決めればよいだけです。

必要なら `evaluation_tasks` に

```ts
previousTaskId?: string | null;
```

のようなフィールドを持たせておくと

* second → first
* final → second

の対応が O(1) で引けて、実装が楽になります。

---

## 3. 関連ユースケース

### 3-1. 一次評価者が評価を入力・提出する（基礎）

**目的**
一次評価者が、自分の担当タスクに対して評価結果を入力し、提出する。

**フロー（簡略）**

1. 一次評価者がタスク一覧から対象タスク T1 を選択。
2. `GET /evaluation-tasks/T1` → task + form を取得。
3. `GET /evaluation-results/T1` → 結果がなければ 404（未入力）。
4. フォームで回答を入力し、「保存」ボタン：

   * `PUT /evaluation-results/T1`（ドラフトも同じ）
   * `/evaluation-tasks/T1` の status は `in_progress`（別 API で更新）
5. 「提出」ボタンで：

   * 再度 `PUT /evaluation-results/T1`（最終版を保存）
   * `PATCH /evaluation-tasks/T1` で status=`completed` に更新

---

### 3-2. 二次評価者が、一次の結果を見て編集し、自分の評価を提出する

**目的**
二次評価者が、一次評価を参考にしながら、自分の評価を入力・提出する。

**フロー**

1. 二次評価者がタスク一覧からタスク T2 を選択。

2. バックエンドは以下を行う：

   * `T2.assignmentId` と `T2.category`、`T2.phase="second"` をキーに、前段階（phase="first"）のタスク T1 を検索。
   * `GET /evaluation-results/T2`：まだ結果がなければ 404。
   * `GET /evaluation-results/T1`：一次の結果 result1 を取得。

3. `GET /evaluation-tasks/T2` へのレスポンス例：

   ```jsonc
   {
     "task": { ...T2 },
     "form": { ... },
     "baseResult": { ...result1 },  // 一次評価
     "result": null                 // 二次はまだ
   }
   ```

4. フロント：

   * `result` が null なので `baseResult` でフォーム初期化。
   * 一次評価のスコア・コメントを初期値として表示。

5. 二次評価者が必要に応じてスコア・コメントを変更し、「保存」「提出」：

   * `PUT /evaluation-results/T2` で二次の回答を保存。
   * `PATCH /evaluation-tasks/T2` で status=`completed` に更新。

6. 一次結果（T1 の result）は変更されない。
   → 「一次はこう評価したが、二次ではこう修正した」という履歴を残せる。

---

### 3-3. 最終評価者が一次・二次の結果を踏まえて評価し、最終結果を出す

**目的**
最終評価者が、一次・二次評価を見ながら最終評価を行う。

**フロー**

1. 最終評価タスク T3 を開く。

2. バックエンドで：

   * `assignmentId + category + phase="final"` → T3
   * 前段階 T2（phase="second"）、その前段階 T1（phase="first"）取得
   * `GET /evaluation-results/T3`、`/T2`、`/T1` の結果を取得

3. レスポンス例：

   ```jsonc
   {
     "task": { ...T3 },
     "form": { ... },
     "previousResults": {
       "first": { ...result1 },
       "second": { ...result2 }
     },
     "result": null // final はまだ
   }
   ```

4. UI では、一次・二次結果を比較表示しつつ、最終評価を入力・提出。

5. `PUT /evaluation-results/T3` → 最終結果を保存。

6. `PATCH /evaluation-tasks/T3` → status=`completed`。

---

### 3-4. 最終評価確定後にフィードバック（feedbacks）を登録する

**目的**
最終評価に基づいて、被考課者本人へのフィードバック（面談内容など）を記録する。

**前提**

* assignment（A）が存在
* 最終評価タスク T3 が `completed`
* feedbacks を別リソースとして持つ設計とする

**feedbacks のイメージ**

```ts
type Feedback = {
  feedbackId: string;
  assignmentId: string;            // この期のこの人へのフィードバック
  givenByEmployeeId: string;       // フィードバック実施者（多くは最終評価者）
  givenAt: string;                 // フィードバック日（1on1 実施日）
  summary: string;                 // フィードバックの要約（本人向け）
  strengths?: string | null;       // 強み
  improvements?: string | null;    // 改善点・期待
  nextGoals?: string | null;       // 次期の目標・アクション
  createdAt: string;
  updatedAt: string;
};
```

**フロー**

1. 最終評価者が「フィードバック登録」画面を開く。

   * `GET /assignments/{assignmentId}` から被考課者情報
   * `GET /evaluation-results/{T3}` から最終評価結果
2. 画面上で最終評価を確認しながら、

   * summary / strengths / improvements / nextGoals を入力。
3. `POST /feedbacks` で上記情報を保存。
4. 被考課者本人用の画面では：

   * `GET /feedbacks?assignmentId=...` で自分のフィードバックを取得・閲覧
   * 必要なら本人コメントを残すための別フィールド（`employeeComment` など）を評価後に追加することも可能。

---

### 3-5. 人事・管理者による「評価プロセス＋フィードバックの総覧」

**目的**
人事や拠点長が、「評価プロセス（一次〜最終）」と「本人へのフィードバック」が正しく実施されているか確認する。

**フロー（サマリ）**

1. `GET /assignments?periodId=...&siteId=...` で被考課者一覧。
2. 各 assignment に対して：

   * `GET /evaluation-tasks?assignmentId=...` で一次〜二次〜最終のタスクと status
   * 各タスクの `evaluation-results` で内容確認（必要な権限を持つ場合）
   * `GET /feedbacks?assignmentId=...` でフィードバック有無と内容確認
3. ダッシュボード上で：

   * 「最終評価完了済みだがフィードバック未実施」のケースを抽出
   * 「フィードバック済みだが記録が無い」などの漏れを検出

---

このように整理すると：

* **evaluation-results**
  → 各 phase の評価者の「採点・コメント」をタスク単位（taskId）で管理

* **feedbacks**
  → 最終的な評価結果を踏まえた「本人へのフィードバック」を assignment 単位で管理

* **フェーズ間の引き継ぎ**
  → assignmentId + category + phase（＋previousTaskId）を手掛かりに
  前段階の result を「初期値／参照情報」として次段階が利用する

という構造で、仕様もロジックもきちんと通ります。



### 4.5.
- 共通型
>```ts
>   type AnswerItem = {
>        questionId: string;           // 設問マスタ／フォームで定義されたID
>        score?: number | null;        // 数値評価（5段階など）。なし／null も許容
>        comment?: string | null;      // 任意コメント
>        };
>
>   type SectionScore = {
>        sectionId: string;            // フォーム内セクションID
>        score?: number | null;        // 該当セクションの集計スコア（任意）
>        };
>
>   type EvaluationResult = {
>        taskId: string;               // FK: evaluation_tasks.taskId
>
>        answers: AnswerItem[];        // 設問ごとの回答
>        sectionScores?: SectionScore[]; // セクション別集計（必要なら）
>        totalScore?: number | null;   // 合計点（必要なら）
>
>        overallComment?: string | null; // 総評コメント
>
>        createdAt: string;
>        updatedAt: string;
>        createdBy: string;            // 評価者 employeeId
>        updatedBy: string;            // 同上（基本）
>        };

- `GET /evaluation-results`
    - 入力（クエリ）（taskId指定用？）

- `GET /evaluation-results/{taskId}`
    - 入力（パス）
    >```ts
    >   taskId: string;
    - 出力（成功時）
    例）
    >```json
    >   {
    >        "result": {
    >            "taskId": "et_001",
    >            "answers": [
    >            { "questionId": "q_1", "score": 4, "comment": "概ね良好" },
    >            { "questionId": "q_2", "score": 3, "comment": null }
    >            ],
    >            "sectionScores": [
    >            { "sectionId": "sec_1", "score": 3.5 }
    >            ],
    >            "totalScore": 3.5,
    >            "overallComment": "コミュニケーション面の改善余地あり。",
    >            "createdAt": "2025-03-10T10:00:00+09:00",
    >            "updatedAt": "2025-03-10T10:15:00+09:00",
    >            "createdBy": "emp_201",
    >            "updatedBy": "emp_201"
    >        }
    >        }


- `PUT(PATCH) /evaluation-results/{taskId}`
    - 入力
    >```ts
    >   answers: AnswerItem[];


## `/questions`リソースと`/evaluation-form-templates`
了解です。
ここまで出てきた `taskId / questionId / sectionId / evaluationFormId` との整合を取りながら、

* `question-master` → `/questions`
* `evaluation-form-templates` → `/evaluation-form-templates`

の2リソースを設計します。
どちらも「設問シートを作るためのマスタ／テンプレート」という位置づけです。

---

# 1. question-master リソース（/questions）

## 1. 誰が使うか

* **hr_admin / システム管理者**

  * 全社共通で使える設問（質問）のマスタを定義・更新する
* **site_admin**

  * 原則参照のみ（編集権限を持たせるかは運用次第）
* **評価者・従業員**

  * 直接 `/questions` を叩くことはなく、フォーム経由で間接利用

---

## 2. 何ができるか（責務）

* 人事考課で使う「設問」の**共通マスタ**を管理
* 設問文、選択肢、スコアレンジ、適用対象（職種・等級など）を一元管理
* `evaluation-form-templates` から参照される「ベース情報」

---

## 3. どのように行うか（エンドポイント）

* `GET    /api/v1/questions`
* `GET    /api/v1/questions/{questionId}`
* `POST   /api/v1/questions`
* `PATCH  /api/v1/questions/{questionId}`

削除は基本 `isActive=false` で論理削除にしておくと安全です。

---

## 4. 入力（リクエスト仕様）

### 4-0. 型定義

```ts
type QuestionType =
  | "rating"      // 数値評価（例：1〜5）
  | "checkbox"    // 複数選択
  | "radio"       // 単一選択
  | "text";       // 自由記述のみ（評価シートに混ぜる場合）

type QuestionStatus = "active" | "inactive";
```

```ts
type Question = {
  questionId: string;       // "Q_WORK_ATT_001" など
  code: string;             // 社内コード（人事用任意）
  category: string;         // "work_attitude" / "job_performance" など
  label: string;            // 質問文（表示用）
  description?: string | null; // 補足説明（任意）

  type: QuestionType;       // rating / checkbox / radio / text
  maxScore?: number | null; // rating の場合の満点（例：5）
  minScore?: number | null; // 必要なら（例：1）

  options?: {               // checkbox / radio 用の選択肢
    value: string;          // "A", "B", ...
    label: string;          // "常にできている", ...
    score?: number | null;  // 選択肢ごとのスコア（必要な場合）
  }[];

  weight?: number | null;   // 集計時のウェイト（フォーム側で上書き可）

  applicableJobTypes?: string[]; // 適用職種コード（nullなら全職種）
  applicableGrades?: string[];   // 適用等級コード（["G03","G04"]など）
  applicableCategories?: string[]; // "work_attitude" など

  status: QuestionStatus;   // active / inactive
  isDeprecated?: boolean;   // 将来的に使用停止する場合など

  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
};
```

---

### 4-1. `GET /questions`

```ts
type ListQuestionsQuery = {
  category?: string;         // work_attitude / job_performance ...
  type?: QuestionType;
  status?: QuestionStatus;   // active のみ、など
  jobType?: string;          // 適用職種で絞る
  grade?: string;            // 適用等級で絞る

  page?: number;
  pageSize?: number;
};
```

---

### 4-2. `POST /questions`（新規作成）

```ts
type CreateQuestionRequest = {
  questionId?: string;     // サーバ側生成にしても良い
  code: string;
  category: string;
  label: string;
  description?: string | null;

  type: QuestionType;
  maxScore?: number | null;
  minScore?: number | null;
  options?: {
    value: string;
    label: string;
    score?: number | null;
  }[];
  weight?: number | null;

  applicableJobTypes?: string[];
  applicableGrades?: string[];
  applicableCategories?: string[];

  status?: QuestionStatus; // 省略時 "active"
};
```

バリデーション例：

* `type="rating"` の場合は `maxScore` 必須
* `type="checkbox" | "radio"` の場合は `options` 必須
* `code` はユニーク推奨

権限：

* `hr_admin / system` のみ作成可

---

### 4-3. `PATCH /questions/{questionId}`（更新）

```ts
type UpdateQuestionRequest = {
  code?: string;
  category?: string;
  label?: string;
  description?: string | null;

  type?: QuestionType;           // 原則変更しないことを推奨
  maxScore?: number | null;
  minScore?: number | null;
  options?: {
    value: string;
    label: string;
    score?: number | null;
  }[];
  weight?: number | null;

  applicableJobTypes?: string[];
  applicableGrades?: string[];
  applicableCategories?: string[];

  status?: QuestionStatus;
};
```

* 既に運用中の質問の「type」を変えるのは危険なので、
  API的には許容しても、UI ではロックしておく運用が無難です。

---

## 5. 出力（レスポンス仕様）

* `GET /questions` → `items: Question[] + page情報`
* `GET /questions/{questionId}` → `{ question: Question }`
* `POST` / `PATCH` → `{ question: Question }`

エラー形式はこれまでと同様：

```ts
type ErrorResponse = {
  code: string;
  detail: string;
  fieldErrors?: { [field: string]: string[] };
};
```

---

## 6. 入力ソース

* 人事部（hr_admin）が「設問を追加・修正」する管理画面
* 既存の紙の評価シートやExcelからの移行時は、CSV/Excelインポート画面から一括登録することも想定可

---

## 7. 出力の用途

* `evaluation-form-templates` を作るときの「設問候補リスト」として使用
* 分析時に、「どの質問に対してどのような評価がされたか」をラベル付きで集計する際に利用

---

# 2. evaluation-form-templates リソース（/evaluation-form-templates）

「職種・等級ごとにどういう設問を並べたシートにするか」を定義するテンプレートです。
`evaluation_tasks.evaluationFormId` がこのテンプレートIDを指します。

---

## 1. 誰が使うか

* **hr_admin / システム管理者**

  * 職種・等級ごとに評価シートのテンプレートを設計・バージョン管理
* **site_admin**

  * 参照＋（場合によって）一部ローカル調整の提案
* **評価者・従業員**

  * 直接は触らないが、実際の評価画面はこのテンプレートに基づいて生成される

---

## 2. 何ができるか（責務）

* 「設問マスタ（/questions）を組み合わせてシートを構成」する
* セクション構成、設問の並び順、設問ごとのウェイトなどを定義
* 職種・等級ごとにフォームを分ける（例：介護職G03の働き方の指針、看護職G04の業務考課 等）
* 将来的にバージョン管理（`draft` / `published` / `archived`）を行う

---

## 3. エンドポイント構成

* `GET    /api/v1/evaluation-form-templates`
* `GET    /api/v1/evaluation-form-templates/{formTemplateId}`
* `POST   /api/v1/evaluation-form-templates`
* `PATCH  /api/v1/evaluation-form-templates/{formTemplateId}`

（将来的に `POST /evaluation-form-templates/{id}/publish` のような専用APIを追加してもよい）

---

## 4. 入力（リクエスト仕様）

### 4-0. 型定義

```ts
type FormTemplateStatus = "draft" | "published" | "archived";
```

```ts
type FormTemplateQuestion = {
  itemId: string;              // フォーム内での一意ID（"item-1" 等）
  questionId: string;          // /questions の questionId
  order: number;               // セクション内での表示順
  weight?: number | null;      // このフォーム内でのウェイト（question-master の weight を上書き可）
  required?: boolean;          // 必須かどうか
  maxScoreOverride?: number | null; // question.masterの maxScore を上書きしたい場合
};
```

```ts
type FormTemplateSection = {
  sectionId: string;           // "sec_work_attitude_basic" など
  title: string;
  description?: string | null;
  order: number;               // フォーム内のセクション順
  weight?: number | null;      // セクション全体のウェイト（集計用）

  questions: FormTemplateQuestion[];
};
```

```ts
type EvaluationFormTemplate = {
  formTemplateId: string;      // "form_work_attitude_G03_v1" など
  name: string;                // "働き方の指針（介護職 G03）v1"
  description?: string | null;

  category: string;            // "work_attitude" / "job_performance" など
  jobType?: string | null;     // 職種コード（介護、看護など）
  grade?: string | null;       // G03, G04 ...
  siteScope?: "all" | "specific_site"; // 全社共通or特定site向け
  siteId?: string | null;      // siteScope = specific_site の場合に使用

  status: FormTemplateStatus;  // draft/published/archived
  version: number;             // 1,2,3...

  sections: FormTemplateSection[];

  totalScore?: number | null;  // このフォームの満点（計算しても良い）

  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy: string;
};
```

---

### 4-1. `GET /evaluation-form-templates`

```ts
type ListFormTemplatesQuery = {
  category?: string;          // work_attitude / job_performance ...
  jobType?: string;
  grade?: string;
  siteId?: string;            // siteScope="specific_site" のものを含めて絞る
  status?: FormTemplateStatus;
  version?: number;           // 最新版のみ / 特定版など

  page?: number;
  pageSize?: number;
};
```

---

### 4-2. `POST /evaluation-form-templates`（新規作成）

```ts
type CreateFormTemplateRequest = {
  formTemplateId?: string;     // サーバ生成でも可
  name: string;
  description?: string | null;

  category: string;
  jobType?: string | null;
  grade?: string | null;
  siteScope?: "all" | "specific_site";
  siteId?: string | null;

  status?: FormTemplateStatus; // 省略時 "draft"
  version?: number;            // 省略時 1

  sections: {
    sectionId?: string;        // 無指定ならサーバ生成可
    title: string;
    description?: string | null;
    order: number;
    weight?: number | null;
    questions: {
      itemId?: string;         // 無指定ならサーバ生成可
      questionId: string;      // /questions に存在するID必須
      order: number;
      weight?: number | null;
      required?: boolean;
      maxScoreOverride?: number | null;
    }[];
  }[];

  totalScore?: number | null;  // サーバ側で計算してもよい
};
```

バリデーション例：

* `questionId` は全て `/questions` に存在していること
* section.order / question.order は整数・重複しないように（サーバ側でソートし直しでもよい）
* `siteScope="specific_site"` の場合は `siteId` 必須

権限：

* `hr_admin / system` のみ作成可

---

### 4-3. `PATCH /evaluation-form-templates/{formTemplateId}`

```ts
type UpdateFormTemplateRequest = {
  name?: string;
  description?: string | null;

  category?: string;
  jobType?: string | null;
  grade?: string | null;
  siteScope?: "all" | "specific_site";
  siteId?: string | null;

  status?: FormTemplateStatus; // draft→published→archived など
  // version は別の「コピーして新バージョン作成」操作で扱う想定

  sections?: FormTemplateSection[]; // 丸ごと差し替え or patch方式どちらでも設計可
  totalScore?: number | null;
};
```

ビジネスルール：

* `status="published"` のテンプレートは基本的に section/question 構成の大きな変更を禁止し、
  新しい `formTemplateId`（version+1）としてコピー作成させた方が安全。
* 期の途中でテンプレートを変えるかどうかは period と絡むので、運用で制約する。

---

## 5. 出力（レスポンス仕様）

* `GET /evaluation-form-templates` → `items: EvaluationFormTemplate[] + page情報`
* `GET /evaluation-form-templates/{id}` → `{ formTemplate: EvaluationFormTemplate }`
* `POST` / `PATCH` → `{ formTemplate: EvaluationFormTemplate }`

これをそのままフロントに渡せば、評価画面で必要な `sections / questions / questionId` がすべて取れる構造です。

---

## 6. 入力ソース

* hr_admin 用の「フォームテンプレート編集画面」：

  * 左側に `/questions` から取得した設問マスタ一覧
  * 右側に「このフォームに含める設問リスト（セクションごと）」の UI
  * ドラッグ＆ドロップで並び替え、削除、追加
* 「職種・等級ごとテンプレート一覧画面」：

  * jobType / grade でフィルタしながら、各フォームテンプレートを編集・バージョンアップ

---

## 7. 出力の用途

* `evaluation_tasks.evaluationFormId` がこの `formTemplateId` を参照：

  * タスク表示時に：

    * `GET /evaluation-tasks/{taskId}` で `evaluationFormId` を受け取り
    * `GET /evaluation-form-templates/{formTemplateId}` でセクション＆設問構成を取得
    * `GET /evaluation-results/{taskId}` で回答を取得
      → これらをまとめて評価画面をレンダリング

* 分析時に：

  * 「どのフォーム（職種・等級・バージョン）で、どの質問にどんな評価が付いたか」を
    `formTemplateId + questionId` 単位で集計

* 将来拡張：

  * 「今期は G03 は v2 のフォーム、G04 は v1 のフォームを使う」など、
    period ごとに formTemplate を紐づける設計にも拡張しやすい。

---

ここまでで、

* `questions`：設問マスタ（atomic な質問）
* `evaluation-form-templates`：それを組み合わせた職種等級別シート構成

が整理できました。


了解です。
`question-master` と `evaluation-form-templates` それぞれについて、代表的なユースケースを整理します。

---

# 1. question-master（/questions）のユースケース

## Q-1. 新しい設問をマスタに追加する

**目的**
人事が新しい評価項目（質問）を全社共通マスタとして追加する。

**アクター**

* 主：hr_admin

**事前条件**

* 評価制度の見直しで、新設問を追加することが決まっている。

**基本フロー**

1. hr_admin が「設問マスタ管理」画面を開く。
2. 「新規追加」ボタンから、以下を入力：

   * `category`（働き方の指針 / 業務考課など）
   * `label`（質問文）
   * `type`（rating / radio / checkbox / text）
   * `maxScore` などスコア情報（rating の場合）
   * 職種・等級の適用範囲（applicableJobTypes / applicableGrades）
3. フロントが `POST /questions` を呼び出す。
4. サーバがバリデーションの上、question を作成し、作成結果を返す。
5. 新しい設問が、フォームテンプレート編集画面の「設問候補一覧」に出てくるようになる。

---

## Q-2. 既存設問の文言・適用範囲を修正する

**目的**
文言の微修正や、適用等級の変更などを行う。

**アクター**

* 主：hr_admin

**事前条件**

* `questionId` が既に存在していること。

**基本フロー**

1. hr_admin が設問一覧から対象設問を選択。
2. 「編集」画面で以下を修正：

   * 質問文（label）
   * 説明文（description）
   * 適用職種・等級（applicableJobTypes / applicableGrades）
3. フロントが `PATCH /questions/{questionId}` を送信。
4. サーバが更新し、更新後の question を返す。

**補足**

* type や maxScore など、構造に影響が大きい項目は原則変えない運用にしておく（どうしても必要なら新しい question を追加）。

---

## Q-3. 古い設問を非推奨／非アクティブにする

**目的**
もう使わない設問を新しいフォームからは選べないようにしたいが、過去データのために完全削除はしたくない。

**アクター**

* 主：hr_admin

**事前条件**

* 過去の評価で使われた questionId である可能性がある。

**基本フロー**

1. hr_admin が設問詳細画面を開く。
2. ステータスを `status="inactive"` に変更するチェックボックス等を操作。
3. フロントが `PATCH /questions/{questionId}`（status 更新）を送信。
4. 以降、フォームテンプレート編集画面では、デフォルトで `status="active"` の設問だけを候補表示する。

**結果**

* 過去の evaluation-results は questionId を参照し続けるが、新規フォーム作成では使われなくなる。

---

## Q-4. 職種・等級別に使える設問候補を一覧表示する

**目的**
フォームテンプレートを組む際に、「この職種G03で使える設問」を絞り込みたい。

**アクター**

* 主：hr_admin

**事前条件**

* `questions` に適用職種・等級が設定済み。

**基本フロー**

1. hr_admin がフォームテンプレート編集画面を開き、jobType / grade を選択。
2. フロントが `GET /questions?status=active&jobType=...&grade=...` を呼び出す。
3. サーバから、該当職種・等級向けにマークされた設問一覧が返る。
4. hr_admin はその中から、テンプレに載せる設問をドラッグ＆ドロップで選択していく。

---

# 2. evaluation-form-templates（/evaluation-form-templates）のユースケース

## F-1. 新しい職種・等級向け評価シートテンプレートを作成する

**目的**
「介護職 G03 の働き方の指針」など、職種・等級・カテゴリごとの評価シートを設計する。

**アクター**

* 主：hr_admin

**事前条件**

* question-master に、使いたい設問が登録済みである。

**基本フロー**

1. hr_admin が「評価フォームテンプレート管理」画面を開く。
2. 「新規テンプレート作成」ボタンで、以下を入力：

   * name（例：「働き方の指針（介護職G03）」）
   * category（work_attitude 等）
   * jobType / grade
   * status: draft
3. セクションを追加（例：「基本行動」「チームワーク」など）。
4. 左側に `/questions` から取得した設問候補リスト（Q-4）を表示。
5. 必要な設問を各セクションにドラッグ＆ドロップし、順番・ウェイト・必須を設定。
6. フロントが `POST /evaluation-form-templates` を送信。
7. サーバがバリデーションしてテンプレートを作成、`formTemplateId` を返す。

**結果**

* 作成したテンプレートが `status="draft"` で保存される。
* 後でレビューし、問題なければ `published` に更新して運用に使う。

---

## F-2. 既存テンプレートをバージョンアップする（v1→v2）

**目的**
既に運用中のフォーム（v1）を改訂して v2 を作りたい（設問追加・削除・修正）。

**アクター**

* 主：hr_admin

**事前条件**

* 既に `status="published"` のフォームテンプレート（v1）が存在している。

**基本フロー（推奨パターン）**

1. hr_admin が対象テンプレート（v1）を選択。
2. 「このテンプレートをコピーして新バージョンを作成」ボタンを押す。
3. サーバが v1 をコピーして v2 を生成：

   * `formTemplateId` を変更
   * `version = v1.version + 1`
   * `status = "draft"`
4. hr_admin が v2 の内容（セクション・設問・weight など）を編集。
5. 確認が取れたら `PATCH /evaluation-form-templates/{v2}` で `status="published"` に変更。
6. assignments / evaluation-tasks を生成するロジックを v2 に切り替える（period単位で選択）。

**結果**

* 旧期は v1 を参照したまま、次期からは v2 を使用、という運用が可能になる。
* 過去の評価結果がどのバージョンのフォームに基づいているか、`formTemplateId / version` で追える。

---

## F-3. 期ごとに「どのフォームを使うか」を決定し、タスク生成に使う

**目的**
例えば「2025年度上期・介護職G03・働き方の指針」の評価には、
どの `formTemplateId` を使うかを決め、それに基づき evaluation_tasks を作る。

※ ここは evaluation-tasks 側のユースケースとまたがりますが、フォームテンプレの役割がよくわかる場面なので含めます。

**アクター**

* 主：hr_admin / system
* 協力：site_admin（現場との調整）

**事前条件**

* `periods` で対象期（2025-H1など）が作成済み
* `evaluation-form-templates` に jobType / grade ごとの `published` テンプレートが存在している

**基本フロー**

1. hr_admin が「期 × 職種 × 等級 ごとのフォーム割当」画面を開く。
2. 例えば：

   * 期：2025-H1
   * jobType：介護職
   * grade：G03
   * category：work_attitude
     に対して `formTemplateId = form_work_attitude_G03_v2` を選択。
3. 期初に assignments を作成する際、システム内部で：

   * 被考課者の jobType / grade を見て該当 `formTemplateId` を選択。
   * evaluation_tasks を作成する際に、`evaluationFormId = formTemplateId` をセット。
4. 評価者がタスクを開くと：

   * `/evaluation-tasks/{taskId}` → `evaluationFormId` を取得
   * `/evaluation-form-templates/{evaluationFormId}` → セクション・設問構成を取得
   * `/evaluation-results/{taskId}` → 回答を取得
     → これらを組み合わせて評価画面をレンダリング。

---

## F-4. 評価シートのプレビュー・テスト表示を行う

**目的**
テンプレートを `published` にする前に、実際の評価画面と同じ見た目でプレビューしたい。

**アクター**

* 主：hr_admin

**事前条件**

* evaluation-form-template が `status="draft"` または `published` で存在。

**基本フロー**

1. hr_admin がテンプレート詳細画面から「プレビュー」ボタンを押す。
2. フロントは：

   * `GET /evaluation-form-templates/{formTemplateId}` でテンプレを取得。
   * 仮の taskId（ダミー）・ダミーの evaluation-results を使って、評価画面と同じ UI をレンダリング。
3. hr_admin は：

   * 設問の順序・文言・セクションタイトル・レイアウトを確認。
   * 必要ならテンプレートを修正し、再度プレビュー。

---

## F-5. テンプレートをアーカイブして新規には使えないようにする

**目的**
古いバージョンのフォームを「新しい期では使わせたくない」が、過去期のために残しておきたい。

**アクター**

* 主：hr_admin

**事前条件**

* 既に v2 など新バージョンが `published` で運用開始済み。

**基本フロー**

1. hr_admin が v1 テンプレートの詳細画面を開く。
2. ステータスを `archived` に変更する操作を行う。
3. フロントが `PATCH /evaluation-form-templates/{formTemplateId_v1}` を送信。
4. 以降：

   * 新しい period への割り当て候補から v1 を除外（UI／サーバ側フィルタ）。
   * 過去の evaluation_tasks / evaluation_results は引き続き v1 を参照。

---

このように整理すると：

* **question-master (/questions)**
  → 個々の「設問」のライフサイクル（追加・修正・廃止）に関するユースケース。

* **evaluation-form-templates (/evaluation-form-templates)**
  → 設問を組み合わせた「シート構成」のライフサイクル（作成・バージョンアップ・割当・アーカイブ）に関するユースケース。

がはっきり分かれます。



# `/feedbacks` リソース設計

## 1. その API を使えるのはだれか

### 読み取り（GET）

- ログイン済みの全従業員
  - `employeeScope=self` 指定時、自分に紐づくフィードバックのみ閲覧可
- 面談者・評価者・施設長・管理者
  - `employeeId` / `officeId` などを指定して部下・配下職員のフィードバックを取得可

### 書き込み（PUT / PATCH / POST）

- 被考課者（本人）
  - 自己面談票（self-sheet）の回答保存・更新
  - 公開済みフィードバックに対する「確認済み」フラグの付与
- 面談者・評価者・施設長・管理者
  - 面談コメント（managerComment）の作成・更新・公開・撤回（運用ルールに応じて制限）

---

## 2. 何ができるか

- 今期および過去の人事考課の結果とフィードバックの一覧・詳細表示
- 被考課者が、決められた質問（面談票）に対する回答を記入・更新（自己フィードバック）
- 面談者が、面談結果に基づくコメントを記入・公開（フィードバックコメント）
- 被考課者が、公開された面談コメントを読んだことを「確認済み」として記録

---

## 3. どのように行うか（ユースケース）

### ユースケース1：被考課者が「今期＋過去」の結果一覧を閲覧

1. 被考課者がマイフィードバックページを開く。
2. フロントが以下を呼び出す：

   - `GET /api/v1/feedbacks?employeeScope=self&includeHistory=true`

3. サーバーは `current_user.employeeId` に紐づく、今期＋過去のフィードバック要約を返す。
4. フロントは各期の評価要約・面談票有無・コメント状態・確認済み状態を一覧表示する。

---

### ユースケース2：被考課者が今期の面談票（自己フィードバック）を記入

1. 今期の行をクリックして詳細画面を開く。
2. フロントが以下を呼び出す：

   - `GET /api/v1/feedbacks/self-sheet?periodId={currentPeriodId}`

3. サーバーは：
   - `current_user.employeeId` と `periodId` から `feedback` を取得（なければ仮想的に新規扱い）
   - 面談票用の質問マスタと回答（存在する場合）を組み合わせて返す。
4. 被考課者がフォームに回答を入力し、「保存」ボタンを押す。
5. フロントが以下を呼び出す：

   - `PUT /api/v1/feedbacks/self-sheet`

6. サーバーは `feedbacks` と `interview_sheet_answers` を upsert し、更新結果を返す。

---

### ユースケース3：面談者が面談コメントを記入・公開

1. 面談者がフィードバックページで部下一覧から対象者と期を選択。
2. フロントが以下を呼び出す：

   - `GET /api/v1/feedbacks?employeeId={empId}&periodId={periodId}`  
     （必要に応じて単一件を返すように実装）

3. サーバーは対象の `Feedback` を返す（評価結果・自己面談票・既存コメントなど）。
4. 面談者は自己面談票を確認しながら対面で面談を実施し、コメントを入力。
5. 「下書き保存」ボタンで：

   - `PATCH /api/v1/feedbacks/{feedbackId}/manager-comment`（status=`"draft"`）

6. 「公開」ボタンで：

   - 同エンドポイントを `status="published"` で呼び出し、被考課者に公開。

---

### ユースケース4：被考課者がフィードバックを「確認済み」にする

1. 被考課者が詳細画面で公開済みコメントを読む。
2. 「確認しました」ボタンを押す。
3. フロントが以下を呼び出す：

   - `POST /api/v1/feedbacks/{feedbackId}/acknowledge`

4. サーバーは `feedback.employeeId == current_user.employeeId` を確認し、`acknowledgedAt` を更新。

---

## 4. 入力（リクエスト定義）

### 4-1. 一覧取得：`GET /api/v1/feedbacks`

- クエリパラメータ例

```text
# 被考課者本人用（マイページ）
GET /api/v1/feedbacks?employeeScope=self&includeHistory=true

# 被考課者本人の今期のみ
GET /api/v1/feedbacks?employeeScope=self&periodId=2025-Q1

# 面談者・管理者が特定の従業員＋期を参照
GET /api/v1/feedbacks?employeeId=emp_001&periodId=2025-Q1

# 面談者・施設長が事業所内を閲覧
GET /api/v1/feedbacks?officeId=ofc_01&periodId=2025-Q1
```
---

### 4-2. 詳細取得：`GET /api/v1/feedbacks/{feedbackId}`

* パスパラメータのみ。
* 被考課者本人がアクセスする場合は、自分宛てかつ `managerComment.status = "published"` のみ。

---

### 4-3. 自己面談票取得：`GET /api/v1/feedbacks/self-sheet`

* クエリパラメータ（必須）

```text
GET /api/v1/feedbacks/self-sheet?periodId=2025-Q1
```

---

### 4-4. 自己面談票保存：`PUT /api/v1/feedbacks/self-sheet`

* 入力（被考課者が決められた質問に回答する）

```json
{
  "periodId": "2025-Q1",
  "answers": [
    {
      "questionId": "q1",
      "answer": "今期は○○業務の効率化に取り組み、処理時間を△△％短縮しました。"
    },
    {
      "questionId": "q2",
      "answer": "□□に関する専門知識を強化したいと考えています。"
    }
  ]
}
```

* `employeeId` は body には含めず、`current_user.employeeId` をサーバー側で使用。

---

### 4-5. 面談者コメントの新規作成：`POST /api/v1/feedbacks/manager-comment`

（初回のみ必要で、実装を簡略化したければスキップし、最初から `feedbackId` を生成する実装でもよい）

* 入力

```json
{
  "employeeId": "emp_001",
  "periodId": "2025-Q1",
  "comment": "前期に比べて○○の改善が見られたため、次期は□□に挑戦してほしい。",
  "status": "draft"
}
```

---

### 4-6. 面談者コメントの更新：`PATCH /api/v1/feedbacks/{feedbackId}/manager-comment`

* 入力

```json
{
  "comment": "面談の結果として、次期は□□に重点的に取り組んでほしいと考えています。",
  "status": "draft" | "published" | "retracted"
}
```

---

### 4-7. 本人による確認：`POST /api/v1/feedbacks/{feedbackId}/acknowledge`

* 入力ボディなし

```json
{}
```

---

## 5. 出力（レスポンス定義）

### 5-1. 共通 Feedback モデル

```json
{
  "feedbackId": "fb_123",
  "employeeId": "emp_001",
  "employeeCode": "000123",
  "employeeName": "山田 太郎",
  "officeId": "ofc_01",
  "officeName": "仙台事業所",
  "periodId": "2025-Q1",
  "periodName": "2025年度上期",

  "evaluationSummary": {
    "overallGrade": "B",
    "finalScore": 3.4
  },

  "selfSheet": {
    "questions": [
      {
        "questionId": "q1",
        "text": "今期、最も力を入れた業務・取り組みは何ですか？",
        "required": true,
        "answer": "○○業務の効率化に取り組み…",
        "updatedAt": "2025-07-01T12:34:56+09:00"
      },
      {
        "questionId": "q2",
        "text": "今後の成長に向けて強化したいスキルは何ですか？",
        "required": true,
        "answer": "□□に関する知識を深めたい…",
        "updatedAt": null
      }
    ]
  },

  "managerComment": {
    "comment": "今期は○○の改善が確認できました。次期は□□にも挑戦してほしいです。",
    "status": "draft",  // draft | published | retracted
    "managerId": "mgr_001",
    "managerName": "上司 花子",
    "updatedAt": "2025-07-10T09:00:00+09:00"
  },

  "acknowledgedAt": "2025-07-11T10:00:00+09:00",

  "createdAt": "2025-06-30T10:00:00+09:00",
  "updatedAt": "2025-07-10T09:00:00+09:00"
}
```

---

### 5-2. 一覧レスポンス：`GET /api/v1/feedbacks`

#### 被考課者本人用（簡易版）

```json
{
  "items": [
    {
      "feedbackId": "fb_123",
      "periodId": "2025-Q1",
      "periodName": "2025年度上期",
      "evaluationSummary": {
        "overallGrade": "B",
        "finalScore": 3.4
      },
      "selfSheetExists": true,
      "managerCommentStatus": "published",
      "acknowledgedAt": null
    },
    {
      "feedbackId": "fb_122",
      "periodId": "2024-Q2",
      "periodName": "2024年度下期",
      "evaluationSummary": {
        "overallGrade": "C",
        "finalScore": 2.8
      },
      "selfSheetExists": true,
      "managerCommentStatus": "published",
      "acknowledgedAt": "2025-01-10T..."
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

---

### 5-3. 自己面談票取得：`GET /api/v1/feedbacks/self-sheet`

```json
{
  "feedbackId": "fb_123",
  "periodId": "2025-Q1",
  "periodName": "2025年度上期",
  "questions": [
    {
      "questionId": "q1",
      "text": "今期、最も力を入れた業務・取り組みは何ですか？",
      "required": true,
      "answer": "○○業務の効率化に取り組み、処理時間を△△％短縮しました。",
      "updatedAt": "2025-07-01T..."
    },
    {
      "questionId": "q2",
      "text": "今後の成長に向けて強化したいスキルは何ですか？",
      "required": true,
      "answer": null,
      "updatedAt": null
    }
  ]
}
```

---

### 5-4. 自己面談票保存：`PUT /api/v1/feedbacks/self-sheet`

```json
{
  "feedbackId": "fb_123",
  "periodId": "2025-Q1",
  "questions": [
    {
      "questionId": "q1",
      "answer": "…",
      "updatedAt": "2025-07-01T..."
    },
    {
      "questionId": "q2",
      "answer": "…",
      "updatedAt": "2025-07-01T..."
    }
  ]
}
```

---

### 5-5. 面談者コメント更新：`PATCH /api/v1/feedbacks/{feedbackId}/manager-comment`

```json
{
  "feedback": {
    /* 上記「共通 Feedback モデル」と同じ構造。managerComment 部分が更新済み */
  }
}
```

---

### 5-6. 本人による確認：`POST /api/v1/feedbacks/{feedbackId}/acknowledge`

```json
{
  "feedbackId": "fb_123",
  "acknowledgedAt": "2025-07-11T10:00:00+09:00"
}
```

---

## 6. バリデーション・エラー仕様（抜粋）

### 認証・認可

```json
{
  "code": "not_authenticated",
  "detail": "この操作にはログインが必要です。"
}
```

```json
{
  "code": "permission_denied",
  "detail": "このフィードバックを操作する権限がありません。"
}
```

### 自己面談票

* 今期以外の period に self-sheet を書こうとした場合：

```json
{
  "code": "invalid_period_for_self_sheet",
  "detail": "自己面談票を記入できるのは今期のみです。"
}
```

* 入力内容が明らかに不正（回答がすべて空など）：

```json
{
  "code": "invalid_input",
  "detail": "自己面談票の内容を入力してください。",
  "fieldErrors": {
    "answers": ["少なくとも1問以上は回答してください。"]
  }
}
```

### 面談者コメント

* 評価がまだ最終確定していないのに `status="published"` にしようとした場合：

```json
{
  "code": "evaluation_not_completed",
  "detail": "評価が完了していないため、フィードバックを公開できません。"
}
```

* 存在しない `feedbackId`：

```json
{
  "code": "feedback_not_found",
  "detail": "指定されたフィードバックが見つかりません。"
}
```

### 確認済み

* 他人宛てのフィードバックを `acknowledge` しようとした場合：

```json
{
  "code": "permission_denied",
  "detail": "このフィードバックに対する確認操作は行えません。"
}
```

* コメントが `published` になっていないのに `acknowledge` しようとした場合：

```json
{
  "code": "feedback_not_published",
  "detail": "このフィードバックはまだ公開されていません。"
}
```

---

## 7. 認可・ルーティング方針（FastAPI 想定）

### Router

```python
router = APIRouter(
    prefix="/api/v1/feedbacks",
    tags=["feedbacks"],
    dependencies=[Depends(require_current_user)],
)
```

### エンドポイントごとの認可

* `GET /feedbacks`

  * `employeeScope=self` の場合：

    * `employeeId = current_user.employeeId` に強制
  * `employeeId` / `officeId` 指定の場合：

    * 評価者・施設長・管理者ロールが必要
* `GET /feedbacks/self-sheet`, `PUT /feedbacks/self-sheet`

  * 常に `employeeId = current_user.employeeId` を使用
* `GET /feedbacks/{feedbackId}`

  * 被考課者本人：

    * `feedback.employeeId == current_user.employeeId`
    * かつ `managerComment.status == "published"` のみ閲覧可
  * 面談者・管理者：

    * 担当者・施設長・管理者ロールであれば閲覧可
* `POST /feedbacks/manager-comment`, `PATCH /feedbacks/{feedbackId}/manager-comment`

  * 評価者・施設長・管理者ロールのみ
* `POST /feedbacks/{feedbackId}/acknowledge`

  * `feedback.employeeId == current_user.employeeId`
  * `managerComment.status == "published"`

---

※ 質問マスタ（`interview_sheet_questions`）および回答テーブル（`interview_sheet_answers`）は、
この `/feedbacks` リソースの裏側で使用する内部リソースとして設計し、
API からは「selfSheet.questions」としてまとめて扱う方針です。



# `/site-results` リソース設計（施設・事業所別サマリ）

## 1. その API を使えるのはだれか

- 管理者（人事・本部）
- 施設長・事業所長クラス
  - 自施設のみ／全社閲覧可否はロール・権限で制御

一般従業員や通常の評価者はアクセス不可。

---

## 2. 何ができるか

- 評価期ごとに、施設・事業所単位で `evaluation-results` を集計・可視化する。
  - 対象者数
  - 平均スコア・中央値・標準偏差
  - 評価ランク（S/A/B/C 等）の構成比
  - 前期との比較、全社平均との差（甘辛度） など
- 施設間での比較ランキングを取得する。
- 等級別・職種別など、施設内部の分布を確認する。

---

## 3. どのように行うか（ユースケース）

### ユースケース1：全施設のサマリ一覧（ダッシュボード）

1. 管理者が「施設別結果ダッシュボード」を開く。
2. フロントエンドが以下を呼び出す：

   - `GET /api/v1/site-results/overview?periodId=2025-Q1&unit=facility`

3. サーバーは `evaluation-results` から集計し、各施設のサマリを返す。
4. フロントはカード／テーブル／チャートで一覧表示。

---

### ユースケース2：特定施設の詳細（等級別・職種別）

1. 管理者／施設長が一覧から施設を選択。
2. フロントエンドが以下を呼び出す：

   - `GET /api/v1/site-results/{facilityId}?periodId=2025-Q1&groupBy=grade`

3. サーバーは指定施設の `evaluation-results` を `grade` 単位で集計し、分布・平均などを返す。
4. フロントは「等級別の箱ひげ図」「ヒストグラム」等を表示。

---

### ユースケース3：施設間ランキング

1. 管理者が「甘辛度ランキング」画面を開く。
2. フロントエンドが以下を呼び出す：

   - `GET /api/v1/site-results/ranking?periodId=2025-Q1&metric=overallScore&unit=facility`

3. サーバーは全社平均スコアを算出し、施設ごとの乖離を計算してランキング形式で返す。

---

## 4. 入力（リクエスト仕様）

### 4-1. 概要一覧：`GET /api/v1/site-results/overview`

```text
GET /api/v1/site-results/overview?periodId=2025-Q1&unit=facility&includeHistory=false
```

* クエリパラメータ

  * `periodId` (必須): 対象評価期 ID
  * `unit` (任意): `"facility"` or `"office"`
    → 施設単位か事業所単位か
  * `includeHistory` (任意, bool): 過去数期分もまとめて返すか

---

### 4-2. 施設詳細：`GET /api/v1/site-results/{facilityId}`

```text
GET /api/v1/site-results/{facilityId}?periodId=2025-Q1&groupBy=grade
```

* パスパラメータ

  * `facilityId`: 対象施設（事業所）ID
* クエリパラメータ

  * `periodId` (必須)
  * `groupBy` (任意):

    * `"grade"`（等級別）
    * `"jobType"`（職種別）
    * `"department"`（部署別）など

---

### 4-3. ランキング：`GET /api/v1/site-results/ranking`

```text
GET /api/v1/site-results/ranking?periodId=2025-Q1&metric=overallScore&unit=facility&limit=20
```

* クエリパラメータ

  * `periodId` (必須)
  * `metric` (必須):

    * `"overallScore"`（総合評価スコア）
    * `"growthScore"`（成長度合いスコア）など、定義に応じて拡張
  * `unit` (必須): `"facility"` or `"office"`
  * `limit` (任意): 何位まで取得するか（デフォルト 50 等）

---

## 5. 出力（レスポンス仕様）

### 5-1. 概要一覧：`GET /site-results/overview`

```json
{
  "periodId": "2025-Q1",
  "unit": "facility",
  "items": [
    {
      "facilityId": "fac_01",
      "facilityName": "仙台本部",
      "employeeCount": 120,
      "averageScore": 3.4,
      "medianScore": 3.0,
      "scoreStdDev": 0.6,
      "gradeDistribution": {
        "S": 0.05,
        "A": 0.25,
        "B": 0.50,
        "C": 0.20
      },
      "diffFromCompanyAverage": 0.0,
      "previousPeriod": {
        "periodId": "2024-Q2",
        "averageScore": 3.2
      }
    }
  ]
}
```

---

### 5-2. 施設詳細：`GET /site-results/{facilityId}`

```json
{
  "facilityId": "fac_01",
  "facilityName": "仙台本部",
  "periodId": "2025-Q1",
  "groupBy": "grade",
  "groups": [
    {
      "groupKey": "G03",
      "groupLabel": "等級 G03",
      "employeeCount": 40,
      "averageScore": 3.5,
      "medianScore": 3.0,
      "scoreStdDev": 0.5,
      "scoreHistogram": [
        { "bin": "1.0-1.9", "count": 1 },
        { "bin": "2.0-2.9", "count": 10 },
        { "bin": "3.0-3.9", "count": 20 },
        { "bin": "4.0-4.9", "count": 9 }
      ],
      "gradeDistribution": {
        "S": 0.10,
        "A": 0.30,
        "B": 0.45,
        "C": 0.15
      }
    }
  ]
}
```

---

### 5-3. ランキング：`GET /site-results/ranking`

```json
{
  "periodId": "2025-Q1",
  "unit": "facility",
  "metric": "overallScore",
  "items": [
    {
      "rank": 1,
      "facilityId": "fac_03",
      "facilityName": "東京事業所",
      "employeeCount": 150,
      "averageScore": 3.8,
      "diffFromCompanyAverage": 0.4
    },
    {
      "rank": 2,
      "facilityId": "fac_01",
      "facilityName": "仙台本部",
      "employeeCount": 120,
      "averageScore": 3.4,
      "diffFromCompanyAverage": 0.0
    }
  ]
}
```

---

## 6. バリデーション・エラー

* 権限不足

```json
{
  "code": "permission_denied",
  "detail": "施設別の結果を見る権限がありません。"
}
```

* 不正な期

```json
{
  "code": "invalid_period",
  "detail": "指定された評価期が存在しません。"
}
```

* 無効な集計単位・メトリクス

```json
{
  "code": "invalid_aggregation_param",
  "detail": "指定された集計条件が不正です。"
}
```

---

## 7. 認可・ルーター

* ルーター例（FastAPI）

```python
router = APIRouter(
    prefix="/api/v1/site-results",
    tags=["site-results"],
    dependencies=[Depends(require_current_user), Depends(require_role(["admin", "facility_head"]))],
)
```

* 施設長が自施設のみ見られるようにする場合は、`facilityId` を `current_user` の所属でフィルタするガードを追加。

---

# `/analysis` リソース設計（設問・評価項目別分析）

## 1. その API を使えるのはだれか

* 管理者（人事・人事企画）
* 分析担当（経営企画など）
* 必要に応じて施設長（自施設のみ・特定設問のみ等の制限付き）

一般従業員・通常の評価者には基本的に非公開。

---

## 2. 何ができるか

* 評価項目や面談票の「質問」単位で、`evaluation-results`（＋面談票回答）を集計する。

  * 全社平均・分布（ヒストグラム）
  * 施設別・等級別・職種別の平均・分布
* 設問の経年推移を取得する。
* 設問ごとの「ばらつき」「難易度」等を把握し、評価制度や教育施策の検討材料にする。

---

## 3. どのように行うか（ユースケース）

### ユースケース1：特定の評価項目の分布を確認

1. 人事が「設問別分析」画面を開き、評価項目（questionId）を1つ選ぶ。

2. フロントエンドが以下を呼び出す：

   * `GET /api/v1/analysis/questions/{questionId}?periodId=2025-Q1`

3. サーバーは対象設問について、全社・等級別などの集計結果を返す。

---

### ユースケース2：設問ごとの施設別の差を確認

1. 「設問×施設マトリクス」画面で、特定の questionId を指定。

2. フロントエンドが以下を呼び出す：

   * `GET /api/v1/analysis/questions/{questionId}/by-site?periodId=2025-Q1`

3. サーバーは施設ごとの平均値・標準偏差・回答者数を返す。

---

### ユースケース3：設問の経年推移を分析

1. 「トレンド分析」画面で questionId と期間範囲を指定。

2. フロントエンドが以下を呼び出す：

   * `GET /api/v1/analysis/questions/{questionId}/trend?fromPeriodId=2023-Q1&toPeriodId=2025-Q1`

3. サーバーは各期ごとの平均スコア・回答者数等を返す。

---

## 4. 入力（リクエスト仕様）

### 4-1. 設問の期別集計：`GET /api/v1/analysis/questions/{questionId}`

```text
GET /api/v1/analysis/questions/{questionId}?periodId=2025-Q1&unit=company
```

* パスパラメータ

  * `questionId`: 評価項目 or 面談票質問の ID
* クエリパラメータ

  * `periodId` (必須): 対象期 ID
  * `unit` (任意): `"company" | "facility" | "office"`

    * `"company"`: 全社集計
    * `"facility"`: 施設別の配列を含める など

---

### 4-2. 設問の施設別集計：`GET /api/v1/analysis/questions/{questionId}/by-site`

```text
GET /api/v1/analysis/questions/{questionId}/by-site?periodId=2025-Q1
```

* パスパラメータ

  * `questionId`
* クエリパラメータ

  * `periodId` (必須)

---

### 4-3. 設問のトレンド：`GET /api/v1/analysis/questions/{questionId}/trend`

```text
GET /api/v1/analysis/questions/{questionId}/trend?fromPeriodId=2023-Q1&toPeriodId=2025-Q1
```

* パスパラメータ

  * `questionId`
* クエリパラメータ

  * `fromPeriodId` (必須)
  * `toPeriodId` (必須)

---

## 5. 出力（レスポンス仕様）

### 5-1. 設問の期別集計：`GET /analysis/questions/{questionId}`

```json
{
  "questionId": "q_behavior_01",
  "questionText": "職務遂行に必要な知識やスキルを身につけているか",
  "periodId": "2025-Q1",
  "overall": {
    "respondentCount": 800,
    "averageScore": 3.2,
    "medianScore": 3.0,
    "scoreStdDev": 0.7,
    "scoreHistogram": [
      { "score": 1, "count": 20 },
      { "score": 2, "count": 120 },
      { "score": 3, "count": 400 },
      { "score": 4, "count": 220 },
      { "score": 5, "count": 40 }
    ]
  },
  "byGrade": [
    {
      "grade": "G03",
      "respondentCount": 300,
      "averageScore": 3.0
    },
    {
      "grade": "G04",
      "respondentCount": 200,
      "averageScore": 3.4
    }
  ]
}
```

---

### 5-2. 設問の施設別集計：`GET /analysis/questions/{questionId}/by-site`

```json
{
  "questionId": "q_behavior_01",
  "questionText": "職務遂行に必要な知識やスキルを身につけているか",
  "periodId": "2025-Q1",
  "sites": [
    {
      "facilityId": "fac_01",
      "facilityName": "仙台本部",
      "respondentCount": 120,
      "averageScore": 3.1,
      "scoreStdDev": 0.6
    },
    {
      "facilityId": "fac_02",
      "facilityName": "東京事業所",
      "respondentCount": 200,
      "averageScore": 3.5,
      "scoreStdDev": 0.5
    }
  ]
}
```

---

### 5-3. 設問のトレンド：`GET /analysis/questions/{questionId}/trend`

```json
{
  "questionId": "q_behavior_01",
  "questionText": "職務遂行に必要な知識やスキルを身につけているか",
  "periods": [
    {
      "periodId": "2023-Q1",
      "periodName": "2023年度上期",
      "respondentCount": 700,
      "averageScore": 3.0
    },
    {
      "periodId": "2024-Q1",
      "periodName": "2024年度上期",
      "respondentCount": 750,
      "averageScore": 3.1"
    },
    {
      "periodId": "2025-Q1",
      "periodName": "2025年度上期",
      "respondentCount": 800,
      "averageScore": 3.2
    }
  ]
}
```

---

## 6. バリデーション・エラー

* 権限不足

```json
{
  "code": "permission_denied",
  "detail": "設問分析にアクセスする権限がありません。"
}
```

* 設問 ID 不正

```json
{
  "code": "question_not_found",
  "detail": "指定された設問が見つかりません。"
}
```

* 期間指定不正

```json
{
  "code": "invalid_period_range",
  "detail": "期間の指定が不正です。fromPeriodId と toPeriodId を確認してください。"
}
```

---

## 7. 認可・ルーター

* ルーター例（FastAPI）

```python
router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["analysis"],
    dependencies=[Depends(require_current_user), Depends(require_role(["admin", "hr_analyst"]))],
)
```

* 施設長などに一部開放する場合は、`facilityId` を `current_user` の所属に限定するなどのガードをサービス層で追加する。




# `/progress` リソース設計（人事考課の進捗状況）

> 役割イメージ：  
> `evaluation-tasks` / `evaluation-results` を元に  
> 「どこまで評価が進んでいるか？」を  
> 期・施設・評価段階・評価者別に集計して返す **進捗ビュー専用リソース**。

---

## 1. その API を使えるのはだれか

### 共通前提
- ログイン済みユーザーのみ

### 想定ロールごとの権限

- 一般従業員
  - 自分自身の被考課としての進捗（「一次評価完了／二次評価待ち」など）を参照
- 評価者（一次・二次・最終）
  - 自分に割り当てられている評価タスクの進捗（「未着手／下書き／提出済み」件数など）を参照
- 施設長・事業所長
  - 自施設の進捗状況（施設内の評価タスク・従業員の完了率）を参照
- 管理者（人事・本部）
  - 全社の進捗ダッシュボード（期別・施設別・評価段階別など）を参照

`/progress` は基本的に **読み取り専用（GETのみ）** を想定。

---

## 2. 何ができるか

- 評価期ごとの「全体の進捗状況」を一覧表示する
  - 例：全社で何％の評価が最終提出まで完了しているか
- 施設ごと・事業所ごとの進捗を可視化する
  - 例：仙台事業所は一次評価完了 80％、二次評価完了 60％ など
- 評価者個人の「担当タスクの進捗」を表示する
  - 例：一次評価タスク 30件中 20件完了・10件未着手
- 被考課者本人の視点で「自分の評価が今どの段階か」を表示する
  - 例：「一次評価完了 → 二次評価待ち」「最終評価済み」など

---

## 3. どのように行うか（ユースケース）

### ユースケース1：管理者ダッシュボード（全社進捗）

1. 管理者がダッシュボード画面を開く。
2. フロントが以下を呼ぶ：

   - `GET /api/v1/progress/overview?periodId=2025-Q1`

3. サーバーは `evaluation_tasks` / `evaluation_results` から集計し、
   - 期別の全社進捗
   - 施設別の完了率サマリ
   を返す。

---

### ユースケース2：施設長ダッシュボード（自施設の進捗）

1. 施設長が自施設の進捗画面を開く。
2. フロントが以下を呼ぶ：

   - `GET /api/v1/progress/facility?periodId=2025-Q1&facilityScope=self`

3. サーバーは `current_user` の所属施設を元に、
   - 被考課者数
   - 各評価段階（一次・二次・最終）の完了率
   - 等級別の進捗
   を返す。

---

### ユースケース3：評価者マイページ（自分のタスク進捗）

1. 評価者が「自分の評価タスク」画面を開く。
2. フロントが以下を呼ぶ：

   - `GET /api/v1/progress/my?periodId=2025-Q1`

3. サーバーは `evaluation_tasks` から
   - ログイン中の評価者に割り当てられたタスク数
   - 状態別（未着手／編集中／提出済み）の件数
   を返す。

---

### ユースケース4：被考課者本人が「自分の評価の進捗」を見る

1. 被考課者がマイページで「評価の状況」を開く。
2. フロントが以下を呼ぶ：

   - `GET /api/v1/progress/self-evaluation?periodId=2025-Q1`

3. サーバーは `evaluation_results`・`evaluation_tasks` から
   - 自分に対する一次／二次／最終評価の完了状況
   - 評価確定日など
   を返す。

---

## 4. 入力（リクエスト仕様）

### 4-1. 全社・施設別サマリ：`GET /api/v1/progress/overview`

```text
GET /api/v1/progress/overview?periodId=2025-Q1
```

* クエリパラメータ

  * `periodId` (必須): 対象評価期
  * `includeFacilities` (任意, bool): 施設別サマリも含めるか
  * `includeHistory` (任意, bool): 過去数期分も含めるか

---

### 4-2. 施設別詳細：`GET /api/v1/progress/facility`

```text
# 自施設のみ（施設長など）
GET /api/v1/progress/facility?periodId=2025-Q1&facilityScope=self

# 特定施設ID
GET /api/v1/progress/facility?periodId=2025-Q1&facilityId=fac_01
```

* クエリパラメータ

  * `periodId` (必須)
  * `facilityScope` (任意): `"self"` → current_user の施設を自動適用
  * `facilityId` (任意): 明示的に指定する場合（admin 用）
  * `groupBy` (任意): `"grade" | "jobType"` など（等級別・職種別の進捗）

---

### 4-3. 評価者本人のタスク進捗：`GET /api/v1/progress/my`

```text
GET /api/v1/progress/my?periodId=2025-Q1
```

* クエリパラメータ

  * `periodId` (必須)
  * `stage` (任意): `"first" | "second" | "final"`（評価段階を絞りたい場合）

---

### 4-4. 被考課者本人の評価進捗：`GET /api/v1/progress/self-evaluation`

```text
GET /api/v1/progress/self-evaluation?periodId=2025-Q1
```

* クエリパラメータ

  * `periodId` (必須)

---

## 5. 出力（レスポンス仕様）

### 5-1. 全社サマリ：`GET /progress/overview`

```json
{
  "periodId": "2025-Q1",
  "overall": {
    "totalEmployees": 800,
    "totalEvaluationTargets": 780,
    "firstStage": {
      "totalTasks": 780,
      "completedTasks": 700,
      "completionRate": 0.90
    },
    "secondStage": {
      "totalTasks": 780,
      "completedTasks": 600,
      "completionRate": 0.77
    },
    "finalStage": {
      "totalTasks": 780,
      "completedTasks": 450,
      "completionRate": 0.58
    }
  },
  "byFacility": [
    {
      "facilityId": "fac_01",
      "facilityName": "仙台本部",
      "totalTargets": 120,
      "firstStageCompletionRate": 0.92,
      "secondStageCompletionRate": 0.80,
      "finalStageCompletionRate": 0.60
    },
    {
      "facilityId": "fac_02",
      "facilityName": "東京事業所",
      "totalTargets": 200,
      "firstStageCompletionRate": 0.88,
      "secondStageCompletionRate": 0.70,
      "finalStageCompletionRate": 0.55
    }
  ]
}
```

---

### 5-2. 施設別詳細：`GET /progress/facility`

```json
{
  "facilityId": "fac_01",
  "facilityName": "仙台本部",
  "periodId": "2025-Q1",
  "summary": {
    "totalTargets": 120,
    "firstStage": { "totalTasks": 120, "completedTasks": 110, "completionRate": 0.92 },
    "secondStage": { "totalTasks": 120, "completedTasks": 96,  "completionRate": 0.80 },
    "finalStage": { "totalTasks": 120, "completedTasks": 72,  "completionRate": 0.60 }
  },
  "byGroup": [
    {
      "groupKey": "G03",
      "groupLabel": "等級 G03",
      "totalTargets": 40,
      "firstStageCompletionRate": 0.95,
      "secondStageCompletionRate": 0.85,
      "finalStageCompletionRate": 0.65
    },
    {
      "groupKey": "G04",
      "groupLabel": "等級 G04",
      "totalTargets": 50,
      "firstStageCompletionRate": 0.90,
      "secondStageCompletionRate": 0.78,
      "finalStageCompletionRate": 0.58
    }
  ]
}
```

---

### 5-3. 評価者本人のタスク進捗：`GET /progress/my`

```json
{
  "periodId": "2025-Q1",
  "evaluatorId": "emp_999",
  "evaluatorName": "上司 花子",
  "stages": [
    {
      "stage": "first",
      "totalTasks": 30,
      "notStarted": 5,
      "inProgress": 10,
      "submitted": 15,
      "completionRate": 0.50
    },
    {
      "stage": "second",
      "totalTasks": 10,
      "notStarted": 3,
      "inProgress": 4,
      "submitted": 3,
      "completionRate": 0.30
    }
  ]
}
```

---

### 5-4. 被考課者本人の評価進捗：`GET /progress/self-evaluation`

```json
{
  "periodId": "2025-Q1",
  "employeeId": "emp_001",
  "employeeName": "山田 太郎",
  "stages": [
    {
      "stage": "first",
      "status": "completed",
      "completedAt": "2025-06-20T10:00:00+09:00",
      "evaluatorId": "emp_101",
      "evaluatorName": "一次 上司"
    },
    {
      "stage": "second",
      "status": "in_progress",
      "completedAt": null,
      "evaluatorId": "emp_201",
      "evaluatorName": "二次 上司"
    },
    {
      "stage": "final",
      "status": "not_started",
      "completedAt": null,
      "evaluatorId": "emp_301",
      "evaluatorName": "施設長"
    }
  ],
  "finalResultStatus": "not_finalized"  // or "finalized"
}
```

---

## 6. バリデーション・エラー

代表的なもの：

* 認証エラー

```json
{
  "code": "not_authenticated",
  "detail": "この操作にはログインが必要です。"
}
```

* 権限不足（一般従業員が overview を見ようとした場合など）

```json
{
  "code": "permission_denied",
  "detail": "この進捗情報を閲覧する権限がありません。"
}
```

* 期間指定不正

```json
{
  "code": "invalid_period",
  "detail": "指定された評価期が存在しません。"
}
```

* 施設ID指定不正

```json
{
  "code": "facility_not_found",
  "detail": "指定された施設が見つかりません。"
}
```

---

## 7. 認可・ルーター（FastAPI 想定）

```python
router = APIRouter(
    prefix="/api/v1/progress",
    tags=["progress"],
    dependencies=[Depends(require_current_user)],
)

@router.get("/overview")
def get_overview_progress(..., current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr"])  # 進捗全体は管理者のみ
    ...

@router.get("/facility")
def get_facility_progress(..., current_user: CurrentUser = Depends(require_current_user)):
    # facilityScope=self のときは current_user の facility に限定
    # facilityId 明示指定は admin or hr のみ許可 など
    ...

@router.get("/my")
def get_my_progress(..., current_user: CurrentUser = Depends(require_current_user)):
    # 評価者であれば、割り当て済みタスクから集計
    ...

@router.get("/self-evaluation")
def get_self_evaluation_progress(..., current_user: CurrentUser = Depends(require_current_user)):
    # current_user.employeeId を使って、自分の評価段階の進捗を返す
    ...
```

---

## まとめ

* `progress` は **書き込みを一切持たない「集計ビュー専用」リソース** として設計すると綺麗です。
* 実データ（誰がどの評価ステージまで書いたか）は `evaluation_tasks` / `evaluation-results` にあり、
  それを「誰の視点でどう見せるか？」を `overview` / `facility` / `my` / `self-evaluation` という 4 つのエンドポイントで切り出すイメージです。

この形でよければ、次は `evaluation_tasks` と `progress` の関係（どの status をどうカウントするか）まで、もう一段階だけ具体化してもよいと思います。



# `/notices` リソース設計（お知らせ）

評価システム内での「お知らせ・周知事項」を扱うリソースです。
評価スケジュール、締切、メンテナンス、仕様変更などを、対象ユーザーごとに配信して既読管理まで行います。

---

## 1. その API を使えるのはだれか

### 閲覧系（GET）

* 全従業員（ログイン済み）

  * 自分が対象となるお知らせ一覧・詳細を閲覧
  * 未読件数の取得
* 施設長・管理者

  * 自分が作成した／自施設向け／全社向けのお知らせの管理用一覧も閲覧

### 作成・更新系（POST / PATCH / DELETE）

* 管理者（人事・システム管理者）

  * 全社向け・施設向け・ロール向け・個別向けなどすべて作成可
* 施設長（facility_head）

  * 自施設を対象とするお知らせのみ作成・更新可（全社向けは不可）

---

## 2. 何ができるか

* システム内のお知らせ（タイトル・本文）の作成・更新・公開・非公開・アーカイブ
* 対象の絞り込み

  * 全社向け
  * 特定施設向け（facilityId 単位）
  * 特定ロール向け（例：評価者だけ、管理者だけ）
  * 特定従業員向け（ピンポイントの案内）
* 表示制御

  * 公開期間（publishAt ～ expireAt）
  * 重要度（info / warning / critical）
  * カテゴリ（evaluation_schedule / system_maintenance など）
  * pinned（ダッシュボード上部へのピン留め）
* 既読管理

  * 各ユーザーごとの既読日時
  * 未読件数バッジの表示

---

## 3. どのように行うか（ユースケース）

### ユースケース1：人事が「評価開始のお知らせ」を配信

1. 管理者がお知らせ管理画面から内容を入力

   * タイトル、本文、対象（例：全社）、関連 periodId、level、category など
2. `POST /api/v1/notices` で作成（status = `draft` or `published`）
3. 必要なら `PATCH /api/v1/notices/{noticeId}` で `status = "published"` にして公開

### ユースケース2：従業員がダッシュボードで未読を確認

1. ダッシュボード表示時に `GET /api/v1/notices/unread-count` で未読件数取得
2. お知らせ一覧パネルで `GET /api/v1/notices?scope=self&onlyActive=true&limit=10`
3. 個別お知らせを開くとき `GET /api/v1/notices/{noticeId}`
4. 同時に `POST /api/v1/notices/{noticeId}/read` で既読登録

### ユースケース3：施設長が自施設向けのお知らせを出す

1. 施設長が作成画面で対象に「自施設」を指定
2. `POST /api/v1/notices`（audienceType="facility", facilityIds=[自施設ID]）
3. 施設長ロールでは自施設以外の facilityIds は指定不可

---

## 4. 入力（主なエンドポイント）

### 4-1. 一覧取得：`GET /api/v1/notices`

例）

* 自分宛てのみ（従業員側）
  `GET /api/v1/notices?scope=self&onlyActive=true&limit=20&offset=0`
* 管理画面用（管理者）
  `GET /api/v1/notices?scope=admin&status=published&periodId=2025-Q1`

主なクエリパラメータ

* `scope`: `"self" | "admin"`
* `onlyActive`: bool（publishAt/expireAt に基づき現在有効なもののみ）
* `category`: カテゴリで絞り込み
* `level`: `"info" | "warning" | "critical"`
* `status`: `"draft" | "published" | "archived"`（admin 用）
* `periodId`: 特定期に紐づくお知らせだけ
* `limit`, `offset`: ページネーション

---

### 4-2. 詳細取得：`GET /api/v1/notices/{noticeId}`

* パスパラメータ

  * `noticeId`: お知らせID

---

### 4-3. 作成：`POST /api/v1/notices`

（管理者・施設長のみ）

リクエストボディ例：

```json
{
  "title": "2025年度上期 人事考課開始のお知らせ",
  "body": "2025年度上期の人事考課を開始します。一次評価の締切は○月○日です。",
  "level": "info",                 // info | warning | critical
  "category": "evaluation_schedule",
  "periodId": "2025-Q1",
  "audienceType": "all",           // all | facility | role | employee
  "facilityIds": null,             // audienceType=facility の場合のみ
  "roleFilter": {
    "includeRoles": ["evaluator_first", "evaluator_second"],
    "minGrade": null,
    "maxGrade": null
  },
  "targetEmployeeIds": null,       // audienceType=employee の場合のみ
  "publishAt": "2025-06-01T09:00:00+09:00",
  "expireAt": "2025-07-31T23:59:59+09:00",
  "status": "draft",               // draft | published | archived
  "pinned": true
}
```

---

### 4-4. 更新：`PATCH /api/v1/notices/{noticeId}`

* タイトル・本文・対象・公開状態・pinned などを部分更新
* 例：下書き→公開（`status: "draft" → "published"`）

---

### 4-5. アーカイブ／削除：`DELETE /api/v1/notices/{noticeId}` or `PATCH` で status 書き換え

* 運用としては `status = "archived"` にする方が安全（物理削除は基本しない）

---

### 4-6. 既読登録：`POST /api/v1/notices/{noticeId}/read`

* ボディなしで OK
* サーバー側で `current_user.employeeId` に対する `readAt` を記録

レスポンス例：

```json
{
  "noticeId": "ntc_001",
  "readAt": "2025-06-01T10:30:00+09:00"
}
```

---

### 4-7. 未読件数：`GET /api/v1/notices/unread-count`

レスポンス例：

```json
{
  "unreadCount": 3
}
```

---

## 5. 出力（代表的レスポンス）

### 5-1. 一覧：`GET /api/v1/notices`

```json
{
  "items": [
    {
      "noticeId": "ntc_001",
      "title": "2025年度上期 人事考課開始のお知らせ",
      "summary": "一次評価の締切は○月○日です。",
      "level": "info",
      "category": "evaluation_schedule",
      "periodId": "2025-Q1",
      "publishAt": "2025-06-01T09:00:00+09:00",
      "expireAt": "2025-07-31T23:59:59+09:00",
      "status": "published",
      "pinned": true,
      "isRead": false,
      "createdAt": "2025-05-30T10:00:00+09:00",
      "createdBy": {
        "employeeId": "emp_admin",
        "employeeName": "人事 管理者"
      }
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

### 5-2. 詳細：`GET /api/v1/notices/{noticeId}`

```json
{
  "noticeId": "ntc_001",
  "title": "2025年度上期 人事考課開始のお知らせ",
  "body": "2025年度上期の人事考課を開始します。一次評価の締切は○月○日です。…",
  "level": "info",
  "category": "evaluation_schedule",
  "periodId": "2025-Q1",
  "audienceType": "all",
  "facilityIds": null,
  "roleFilter": null,
  "targetEmployeeIds": null,
  "publishAt": "2025-06-01T09:00:00+09:00",
  "expireAt": "2025-07-31T23:59:59+09:00",
  "status": "published",
  "pinned": true,
  "isRead": false,
  "createdAt": "2025-05-30T10:00:00+09:00",
  "updatedAt": "2025-05-31T15:00:00+09:00",
  "createdBy": {
    "employeeId": "emp_admin",
    "employeeName": "人事 管理者"
  }
}
```

---

## 6. エラー・バリデーション

* 認証エラー

```json
{
  "code": "not_authenticated",
  "detail": "この操作にはログインが必要です。"
}
```

* 権限不足（一般従業員が POST / PATCH / DELETE）

```json
{
  "code": "permission_denied",
  "detail": "このお知らせの管理操作を行う権限がありません。"
}
```

* 対象指定の不整合（audienceType と facilityIds / targetEmployeeIds の矛盾）

```json
{
  "code": "invalid_audience",
  "detail": "対象の指定が不正です。audienceType と facilityIds / targetEmployeeIds を確認してください。"
}
```

* `noticeId` 不存在

```json
{
  "code": "notice_not_found",
  "detail": "指定されたお知らせが見つかりません。"
}
```

---

## 7. 認可・ルーティング方針（FastAPI イメージ）

* ルーター

```python
router = APIRouter(
    prefix="/api/v1/notices",
    tags=["notices"],
    dependencies=[Depends(require_current_user)],
)
```

* 閲覧系（GET `/notices`, `/notices/{id}`, `/unread-count`）

  * 全ログインユーザー可
  * ただし返す notices は current_user に配信対象のものだけ

* 作成・更新系（POST / PATCH / DELETE）

  * `require_role(["admin", "hr", "facility_head"])`
  * facility_head は facilityIds が自施設内かをサービス側でチェック



`login-ip-policies` は、
「どの IP アドレスからのログインを許可するか」を管理者画面から設定・管理するためのリソースとして設計します。
/ auth で出てきた `LoginIpPolicy` テーブルに対応する API です。

---

## 1. その API を使えるのはだれか

* システム管理者（admin / hr_admin など）

  * すべての IP ポリシーを閲覧・登録・変更・削除できる
* 施設長（facility_head）

  * 自施設に関するポリシーのみ閲覧・登録・変更・削除できる（会社全体・他施設には触れられない）
* 一般従業員・通常の評価者

  * 原則アクセス不可（IP ポリシーは「認可の根幹」なので、閲覧も制限）

---

## 2. 何ができるか

* ログイン許可 IP のポリシーを管理する

  * グローバル（会社共通）の許可 IP
  * 施設（事業所）単位の許可 IP
  * 特定従業員単位の例外許可 IP（リモートワークなど）
* ポリシーの有効・無効化、期間制限
* 管理画面での一覧表示・検索
  -（オプション）テスト用 API で「この従業員＋この IP が許可されるか？」を事前確認

---

## 3. どう使うか（ユースケース）

### ユースケース1：本社ネットワークの IP を許可する（グローバル）

1. システム管理者が「ログイン許可 IP 管理」画面を開く。
2. 「新規ポリシー追加」で以下を入力：

   * 名称：`本社ネットワーク`
   * scopeType：`global`
   * ipCidrs：`["203.0.113.0/24"]`
3. `POST /api/v1/login-ip-policies` を呼び出して登録。
4. `/auth/login` からのログイン時、`clientIp` が `203.0.113.0/24` に含まれていれば「IP 許可」と判定。

---

### ユースケース2：仙台事業所だけ別 IP 範囲を許可する

1. 施設長 or 管理者が、「仙台事業所用」のポリシーを作成。

   * scopeType：`facility`
   * facilityIds：`["fac_sendai"]`
   * ipCidrs：`["10.0.10.0/24"]`
2. `POST /api/v1/login-ip-policies`
3. `/auth/login` 実行時に：

   * ユーザーの facilityId が `fac_sendai`
   * clientIp が `10.0.10.0/24` 内
     → 許可

---

### ユースケース3：特定社員の在宅勤務用に IP を一時的に許可する

1. 人事管理者が「個別例外ポリシー」を作成。

   * scopeType：`employee`
   * employeeIds：`["emp_001234"]`
   * ipCidrs：`["198.51.100.42/32"]`  // 固定回線のグローバル IP
   * validFrom / validTo を 1 ヶ月などに設定
2. `POST /api/v1/login-ip-policies`
3. その社員は在宅 IP から `/auth/login` を通過できる。

---

### ユースケース4：管理画面で「この条件だとログイン可か？」をテスト

1. 管理者がテスト画面に、employeeCode と 仮の IP アドレスを入力。
2. `POST /api/v1/login-ip-policies/test` を叩く。
3. 「allowed: true/false」「どのポリシーにマッチしたか」を返す。

※このテスト API は必須ではないですが、運用上かなり便利なので候補として入れておきます。

---

## 4. 入力（エンドポイント・リクエスト）

### 4-1. 一覧取得：`GET /api/v1/login-ip-policies`

例：

* 全体一覧（管理者用）
  `GET /api/v1/login-ip-policies?scope=admin&limit=50&offset=0`

* 自施設用（施設長）
  `GET /api/v1/login-ip-policies?scope=my-facility&limit=50`

主なクエリパラメータ：

* `scope`: `"admin" | "my-facility"`

  * admin: 全ポリシー（権限で制限）
  * my-facility: current_user の facility に関係するポリシーだけ
* `scopeType`: `"global" | "facility" | "employee"`（絞り込み）
* `facilityId`: 特定施設に紐づくポリシーだけ
* `employeeId`: 特定従業員に紐づくポリシーだけ
* `isActive`: bool
* `limit`, `offset`: ページネーション

---

### 4-2. 詳細取得：`GET /api/v1/login-ip-policies/{policyId}`

* パスパラメータ

  * `policyId`: ポリシー ID

---

### 4-3. ポリシー作成：`POST /api/v1/login-ip-policies`

リクエストボディ例：

```json
{
  "name": "本社ネットワーク",
  "description": "本社内からのアクセスを許可",
  "scopeType": "global",           // global | facility | employee
  "facilityIds": null,             // scopeType=facility のときだけ使用
  "employeeIds": null,             // scopeType=employee のときだけ使用
  "ipCidrs": [
    "203.0.113.0/24"
  ],
  "allowMode": "allow",            // 今回は allow 前提で OK（将来的に deny も足すなら enum 化）
  "isActive": true,
  "validFrom": "2025-06-01T00:00:00+09:00",
  "validTo": null                  // 期限なし
}
```

ポイント：

* `scopeType` によって、必須フィールドが変わる

  * global: facilityIds / employeeIds 共に null
  * facility: facilityIds 必須
  * employee: employeeIds 必須
* `ipCidrs` は CIDR 表記の配列（`/32` を使えば 1 IP 固定）

---

### 4-4. ポリシー更新：`PATCH /api/v1/login-ip-policies/{policyId}`

* 名前、説明、ipCidrs、isActive、validFrom/validTo などを部分更新
* `scopeType` は基本的には変更不可にしておく方が安全（変えたいときは新規作成）

---

### 4-5. ポリシー削除 or 無効化

* 物理削除：`DELETE /api/v1/login-ip-policies/{policyId}`
* 運用面では、基本は `isActive = false` にする PATCH を推奨

---

### 4-6. テスト用：`POST /api/v1/login-ip-policies/test`（オプション）

管理者が「この IP でこの社員は OK か？」を確認するための API。

リクエスト例：

```json
{
  "employeeCode": "A12345",
  "facilityId": "fac_sendai",   // あれば
  "ipAddress": "203.0.113.10"
}
```

レスポンス例：

```json
{
  "allowed": true,
  "matchedPolicies": [
    {
      "policyId": "lip_001",
      "name": "本社ネットワーク",
      "scopeType": "global"
    }
  ]
}
```

このロジックは /auth/login と共通のサービスを使う。

---

## 5. 出力（レスポンス例）

### 5-1. 一覧：`GET /login-ip-policies`

```json
{
  "items": [
    {
      "policyId": "lip_001",
      "name": "本社ネットワーク",
      "description": "本社内からのアクセスを許可",
      "scopeType": "global",
      "facilityIds": [],
      "employeeIds": [],
      "ipCidrs": [
        "203.0.113.0/24"
      ],
      "allowMode": "allow",
      "isActive": true,
      "validFrom": "2025-06-01T00:00:00+09:00",
      "validTo": null,
      "createdAt": "2025-05-20T10:00:00+09:00",
      "createdBy": {
        "employeeId": "emp_admin",
        "employeeName": "システム 管理者"
      },
      "updatedAt": "2025-05-21T15:00:00+09:00"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

### 5-2. 詳細：`GET /login-ip-policies/{policyId}`

```json
{
  "policyId": "lip_001",
  "name": "本社ネットワーク",
  "description": "本社内からのアクセスを許可",
  "scopeType": "global",
  "facilityIds": [],
  "employeeIds": [],
  "ipCidrs": [
    "203.0.113.0/24"
  ],
  "allowMode": "allow",
  "isActive": true,
  "validFrom": "2025-06-01T00:00:00+09:00",
  "validTo": null,
  "createdAt": "2025-05-20T10:00:00+09:00",
  "createdBy": {
    "employeeId": "emp_admin",
    "employeeName": "システム 管理者"
  },
  "updatedAt": "2025-05-21T15:00:00+09:00"
}
```

---

## 6. バリデーション・エラー

代表的なものだけ列挙します。

* 認証エラー

```json
{
  "code": "not_authenticated",
  "detail": "この操作にはログインが必要です。"
}
```

* 権限不足（一般従業員、権限のない施設長）

```json
{
  "code": "permission_denied",
  "detail": "ログイン許可IPポリシーを管理する権限がありません。"
}
```

* audience（scopeType と facilityIds / employeeIds）の不整合

```json
{
  "code": "invalid_scope",
  "detail": "scopeType に対する facilityIds / employeeIds の指定が不正です。"
}
```

* IP フォーマット不正

```json
{
  "code": "invalid_ip_cidr",
  "detail": "IP アドレスまたは CIDR の形式が正しくありません。"
}
```

* policyId 不存在

```json
{
  "code": "login_ip_policy_not_found",
  "detail": "指定されたログインIPポリシーが見つかりません。"
}
```

---

## 7. 認可・ルーター（イメージ）

FastAPI ならこんな感じのイメージです。

```python
router = APIRouter(
    prefix="/api/v1/login-ip-policies",
    tags=["login-ip-policies"],
    dependencies=[Depends(require_current_user)],
)

@router.get("")
def list_policies(..., current_user: CurrentUser = Depends(require_current_user)):
    # admin or facility_head だけ
    require_role(current_user, ["admin", "hr_admin", "facility_head"])
    ...

@router.post("")
def create_policy(..., current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr_admin", "facility_head"])
    # facility_head の場合は facilityIds が自施設に限定されているかチェック
    ...

@router.post("/test")
def test_policy(..., current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr_admin"])
    ...
```

---

全体として：

* `/auth/login` の IP チェックの裏側で使う「マスタ管理リソース」
* scopeType（global / facility / employee）＋ ipCidrs でシンプルに設計
* 削除よりも `isActive` と `validFrom/validTo` で運用する

という方針にしておくと、後から拡張しやすいと思います。



以下の前提で `/dashboard` を設計します。

* エンドポイントは **1 本だけ**：`GET /api/v1/dashboard/home`
* バックエンドが `currentUser`（等級・権限）を見て

  * 返す「ウィジェット」とその中身を変える
* 主要ウィジェット：**お知らせ・タスク・進捗**（＋権限に応じた施設/全社サマリ）

---

## 1. エンドポイント概要

### `GET /api/v1/dashboard/home`

* 認証必須：`require_current_user`
* リクエストボディなし（クエリも基本不要）
* サーバ側で `currentUser` を見てレスポンスを組み立てる

---

## 2. 役割ごとの表示イメージ

### 2-1. 一般従業員（評価対象のみ・評価権限なし）

* `grade`: G01〜G03 など
* `isAdmin`: false
* `isEvaluator`: false（一次/二次/最終評価者ではない）
* `isFacilityHead`: false

→ 表示したい内容

* `notices`：自分宛てのお知らせ（上位 N 件）
* `myProgress`：

  * 自分の評価進捗（一次/二次/最終がどこまで終わっているか）
* `myTasks`：

  * 「やるべきこと」

    * 自己面談票の未記入
    * フィードバックの未確認（acknowledge していないもの）
    * 一時パスワードログイン中なら「パスワード変更タスク」
* （必要なら）`myRecentFeedbacks`：直近の評価結果・フィードバック概要

### 2-2. 評価者（一次・二次・最終）

* `isEvaluator`: true
* 等級は G03〜G05 くらいを想定

→ 一般従業員向けに加えて：

* `myEvaluationTasks`：

  * 自分に割り当てられている評価タスクの件数・ステータス
  * 「未着手」「編集中」「提出済み」など
* `myProgressAsEvaluator`：

  * 自分の担当タスクの完了率（一次/二次別）

### 2-3. 施設長（facility_head）

* `isFacilityHead`: true
* `grade`: G06 など

→ 評価者向けに加えて：

* `facilityProgress`：

  * 自施設の評価進捗（一次/二次/最終の完了率）
* `facilityAlerts`：

  * 期限切れ・遅延しているタスク件数（例：一次評価期限を過ぎている対象者数）
* `facilityNotices`：（オプション）

  * 自施設限定のお知らせ（自分が作ったもの含む）

### 2-4. 管理者（admin / hr）

* `isAdmin`: true

→ 施設長向けに加えて：

* `companyProgress`：

  * 全社の評価進捗サマリ
* `siteResultsSummary`：

  * 施設間の進捗・評価結果のシンプルなランキング（詳細は `/site-results` 側）
* `adminTasks`：（任意）

  * 未処理の `/admin/password-reset-requests` 件数
  * ログインエラーやポリシー関連の警告

---

## 3. レスポンス全体構造

`GET /api/v1/dashboard/home` のレスポンスを、
「共通ヘッダ」＋「ウィジェット」の集合として定義します。

```json
{
  "currentUser": {
    "employeeId": "emp_001",
    "name": "山田 太郎",
    "grade": "G03",
    "facilityId": "fac_01",
    "facilityName": "仙台事業所",
    "roles": {
      "isAdmin": false,
      "isEvaluator": true,
      "isFacilityHead": false
    }
  },
  "layout": {
    "variant": "employee_with_evaluator", 
    "visibleWidgets": [
      "notices",
      "myTasks",
      "myProgress",
      "myEvaluationTasks"
    ]
  },
  "widgets": {
    "notices": { ... },
    "myTasks": { ... },
    "myProgress": { ... },
    "myEvaluationTasks": { ... },
    "facilityProgress": null,
    "companyProgress": null,
    "adminTasks": null
  }
}
```

ポイント：

* **必ず同じ key を返し、使わないウィジェットは `null` にする**とフロントが楽
  （もしくは `widgets` 内で存在しない key は描画しない運用でも可）
* `layout.visibleWidgets` は、フロントでカードの配置を切り替えるヒントとして利用

---

## 4. 各ウィジェットの仕様

### 4-1. `widgets.notices`（全ロール共通）

元データ：`/notices`

```json
"notices": {
  "unreadCount": 3,
  "items": [
    {
      "noticeId": "ntc_001",
      "title": "2025年度上期 人事考課開始のお知らせ",
      "level": "info",
      "category": "evaluation_schedule",
      "periodId": "2025-Q1",
      "publishAt": "2025-06-01T09:00:00+09:00",
      "isRead": false
    },
    {
      "noticeId": "ntc_002",
      "title": "システムメンテナンスのお知らせ",
      "level": "warning",
      "category": "system_maintenance",
      "publishAt": "2025-06-10T22:00:00+09:00",
      "isRead": true
    }
  ]
}
```

* 全ユーザー共通で返す
* 裏では `GET /notices?scope=self&onlyActive=true&limit=5` を叩くイメージ

---

### 4-2. `widgets.myTasks`（全ユーザーだが中身が変わる）

**「自分が今やるべき ToDo」だけをまとめた一覧**。

代表的なタスクタイプ：

* `change_password`：一時パスワードログイン中
* `fill_self_feedback`：今期の自己面談票が未完
* `acknowledge_feedback`：公開済みフィードバック未確認
* 評価者であれば：`complete_evaluation`（一次/二次/最終）

```json
"myTasks": {
  "items": [
    {
      "taskType": "fill_self_feedback",
      "label": "今期の面談票を記入してください",
      "periodId": "2025-Q1",
      "dueDate": "2025-06-30",
      "link": "/my-feedbacks/2025-Q1"
    },
    {
      "taskType": "acknowledge_feedback",
      "label": "前期のフィードバックを確認してください",
      "periodId": "2024-Q2",
      "link": "/my-feedbacks/2024-Q2"
    }
  ]
}
```

* taskType は enum 的に決めておく：

  * `"fill_self_feedback" | "acknowledge_feedback" | "change_password" | "complete_evaluation"` など
* タスクの元データは：

  * `/feedbacks/self-sheet` のステータス
  * `/feedbacks/{id}` の `acknowledgedAt`
  * `/auth/me` の `mustChangePasswordAtNextLogin`
  * `/progress/my` や `evaluation_tasks` のステータス
    を見てサーバ側で生成する。

---

### 4-3. `widgets.myProgress`（被考課者としての進捗）

元データ：`/progress/self-evaluation`

```json
"myProgress": {
  "periodId": "2025-Q1",
  "statusSummary": "in_progress",   // not_started | in_progress | completed
  "stages": [
    {
      "stage": "first",
      "status": "completed",
      "completedAt": "2025-06-20T10:00:00+09:00",
      "evaluatorName": "一次 上司"
    },
    {
      "stage": "second",
      "status": "in_progress",
      "completedAt": null,
      "evaluatorName": "二次 上司"
    },
    {
      "stage": "final",
      "status": "not_started",
      "completedAt": null,
      "evaluatorName": "施設長"
    }
  ]
}
```

* 全社員に対して返す
* カードでは「今、自分の評価はどこまで来ているか？」を一目で示す

---

### 4-4. `widgets.myEvaluationTasks`（評価者だけ）

元データ：`/progress/my`（＋`evaluation_tasks`）

```json
"myEvaluationTasks": {
  "periodId": "2025-Q1",
  "stages": [
    {
      "stage": "first",
      "totalTasks": 20,
      "submitted": 12,
      "inProgress": 5,
      "notStarted": 3,
      "completionRate": 0.6
    },
    {
      "stage": "second",
      "totalTasks": 5,
      "submitted": 1,
      "inProgress": 2,
      "notStarted": 2,
      "completionRate": 0.2
    }
  ],
  "highlight": {
    "stage": "first",
    "message": "一次評価の締切まであと 5 日です。"
  }
}
```

* `currentUser.roles.isEvaluator === true` のときだけ中身を返す
  （それ以外は `null` で OK）

---

### 4-5. `widgets.facilityProgress`（施設長・管理者）

元データ：`/progress/facility`

```json
"facilityProgress": {
  "facilityId": "fac_01",
  "facilityName": "仙台事業所",
  "periodId": "2025-Q1",
  "summary": {
    "totalTargets": 120,
    "firstStageCompletionRate": 0.92,
    "secondStageCompletionRate": 0.80,
    "finalStageCompletionRate": 0.60
  },
  "delayedCount": {
    "firstStageOverdue": 3,
    "secondStageOverdue": 5,
    "finalStageOverdue": 10
  }
}
```

* `currentUser.roles.isFacilityHead || currentUser.roles.isAdmin` のときだけ返す

---

### 4-6. `widgets.companyProgress`（管理者専用）

元データ：`/progress/overview`

```json
"companyProgress": {
  "periodId": "2025-Q1",
  "overall": {
    "totalTargets": 800,
    "firstStageCompletionRate": 0.90,
    "secondStageCompletionRate": 0.77,
    "finalStageCompletionRate": 0.58
  },
  "topFacilitiesByCompletion": [
    {
      "facilityId": "fac_03",
      "facilityName": "東京事業所",
      "finalStageCompletionRate": 0.75
    },
    {
      "facilityId": "fac_01",
      "facilityName": "仙台事業所",
      "finalStageCompletionRate": 0.60
    }
  ]
}
```

* `currentUser.roles.isAdmin === true` のときのみ

---

### 4-7. `widgets.adminTasks`（管理者用の「タスク」）

例：未処理のパスワードリセット依頼など。

元データ：`/admin/password-reset-requests` など

```json
"adminTasks": {
  "items": [
    {
      "taskType": "password_reset_request",
      "label": "未処理のパスワードリセット依頼が 4 件あります。",
      "link": "/admin/password-reset-requests",
      "count": 4
    }
  ]
}
```

* `currentUser.roles.isAdmin === true` のときのみ

---

## 5. 等級・権限による出し分けロジック（サーバ側）

サーバ側でのイメージ（疑似コード）：

```python
def get_dashboard_home(current_user: CurrentUser):
    widgets = {
        "notices": build_notices_widget(current_user),
        "myTasks": build_my_tasks_widget(current_user),
        "myProgress": build_my_progress_widget(current_user),
        "myEvaluationTasks": None,
        "facilityProgress": None,
        "companyProgress": None,
        "adminTasks": None,
    }

    visible = ["notices", "myTasks", "myProgress"]

    if current_user.is_evaluator:
        widgets["myEvaluationTasks"] = build_my_evaluation_tasks_widget(current_user)
        visible.append("myEvaluationTasks")

    if current_user.is_facility_head:
        widgets["facilityProgress"] = build_facility_progress_widget(current_user)
        visible.append("facilityProgress")

    if current_user.is_admin:
        widgets["facilityProgress"] = build_facility_progress_widget_for_admin(current_user)
        widgets["companyProgress"] = build_company_progress_widget(current_user)
        widgets["adminTasks"] = build_admin_tasks_widget(current_user)
        visible.extend(["facilityProgress", "companyProgress", "adminTasks"])

    layout_variant = decide_layout_variant(current_user, visible)

    return {
        "currentUser": current_user_summary(current_user),
        "layout": {
            "variant": layout_variant,
            "visibleWidgets": visible,
        },
        "widgets": widgets,
    }
```

* 等級（`grade`）と権限（`isEvaluator`, `isFacilityHead`, `isAdmin`）を元に分岐
* 例えば：

  * `grade >= G04` ならデフォルトで `isEvaluator=True` など、ポリシーに応じて決める

---

## 6. まとめ

* `/dashboard/home` は **読み取り専用の Facade API** として設計
* 中身は：

  * 全ユーザー共通：`notices`, `myTasks`, `myProgress`
  * 評価者のみ：`myEvaluationTasks`
  * 施設長：`facilityProgress`
  * 管理者：`facilityProgress`, `companyProgress`, `adminTasks`
* API のレスポンスは

  * `currentUser`
  * `layout`（どのウィジェットを表示するか）
  * `widgets`（お知らせ・タスク・進捗などの実データ）

この形であれば、**等級・権限に応じた出し分け**をサーバ側で吸収しつつ、
フロント側では「`visibleWidgets` をループしてカードを描画するだけ」という、比較的シンプルな実装にできます。



監査ログリソースとエクスポート系リソース、それぞれきちんと切って設計しておくのは良いと思います。
以下、今までのスタイルに合わせて 2 本まとめます。

---

# `/audit-logs` リソース（監査ログ・操作履歴）

評価結果や権限まわりなど「後から誰が何をしたか」を追えるようにするための参照専用リソースです。

## 1. その API を使えるのはだれか

* 管理者（人事・システム管理者）

  * 全社の監査ログを検索・参照できる
* 施設長（必要に応じて）

  * 自施設に関係するログのみ参照可能（option）
* 一般従業員

  * 原則アクセス不可
  * 必要なら、自分の操作履歴だけを返す `/audit-logs/my` を限定公開してもよい

CRUD としては **GET のみ（読み取り専用）**。
ログの記録（POST 相当）はサーバ内部からのみ行い、API 経由では行わない前提にします。

---

## 2. 何ができるか

* 誰が／いつ／どの IP から／どのリソースに対して／どんな操作をしたか を検索・参照
* 代表的なログ対象：

  * 評価結果（`evaluation-results`）の作成・更新・提出
  * 割り当て（`assignments`）の変更
  * フィードバック（`feedbacks`）の公開・編集
  * ログイン IP ポリシー（`login-ip-policies`）の変更
  * パスワードリセット（`/employees/{id}/reset-password`）の実行
  * 管理者によるアカウント無効化・権限変更 など

---

## 3. どのように行うか（ユースケース）

### ユースケース1：特定の評価結果がいつ書き換えられたか調べる

1. 管理者が「個票の変更履歴」画面で employeeId と periodId を指定
2. フロントが以下を呼ぶ：

   * `GET /api/v1/audit-logs?entityType=evaluation-result&entityId=er_123`
3. 返ってきたログ一覧を時系列で表示（誰が・いつ・どの項目を変更したか）

### ユースケース2：施設長が自施設の評価提出状況の「編集履歴」を確認

1. 施設長が「施設の監査ログ」画面を開く
2. フロントが以下を呼ぶ：

   * `GET /api/v1/audit-logs?facilityId=fac_01&dateFrom=2025-06-01&dateTo=2025-06-30`
3. 自施設の従業員に関係するログのみ表示（facilityId でサーバ側がフィルタ）

---

## 4. 入力（リクエスト仕様）

### 4-1. 一覧取得：`GET /api/v1/audit-logs`

```text
GET /api/v1/audit-logs?entityType=evaluation-result&entityId=er_123&dateFrom=2025-06-01&dateTo=2025-06-30&limit=50&offset=0
```

クエリパラメータ（代表例）：

* 絞り込み条件

  * `entityType`：`"evaluation-result" | "assignment" | "feedback" | "login-ip-policy" | "employee" | "auth" | ...`
  * `entityId`：対象エンティティの ID（`evaluationResultId` など）
  * `actorEmployeeId`：実行者の社員 ID
  * `action`：`"create" | "update" | "submit" | "publish" | "reset_password" | ...`
  * `facilityId`：対象従業員の所属施設（ログ保存時に持たせる）
  * `dateFrom`, `dateTo`：期間絞り込み（ISO8601 日付 or datetime）
* ページング

  * `limit`：1 ページあたり件数（デフォルト 50、最大 200 など）
  * `offset`：オフセット

※ `entityType` + `entityId` または `actorEmployeeId` + 日付範囲、あたりが現実的なユースケース。

---

### 4-2. 詳細取得：`GET /api/v1/audit-logs/{logId}`

個別ログ 1 件の詳細表示用。

```text
GET /api/v1/audit-logs/{logId}
```

---

### 4-3. 自分の操作履歴（任意）：`GET /api/v1/audit-logs/my`

必要なら用意：

```text
GET /api/v1/audit-logs/my?dateFrom=...&dateTo=...
```

---

## 5. 出力（レスポンス仕様）

### 5-1. 一覧：`GET /audit-logs`

```json
{
  "items": [
    {
      "logId": "al_0001",
      "timestamp": "2025-06-20T10:15:30+09:00",
      "actor": {
        "employeeId": "emp_101",
        "employeeName": "一次 上司"
      },
      "actorIp": "203.0.113.10",
      "action": "submit",                   // enum
      "entityType": "evaluation-result",
      "entityId": "er_123",
      "relatedEmployee": {
        "employeeId": "emp_001",
        "employeeName": "山田 太郎",
        "facilityId": "fac_01",
        "facilityName": "仙台事業所"
      },
      "metadata": {
        "periodId": "2025-Q1",
        "stage": "first",
        "before": {
          "status": "in_progress"
        },
        "after": {
          "status": "submitted"
        }
      }
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

ポイント：

* `metadata` は JSON フリーフォームにしておけば、
  各リソースに応じた付加情報（stage、periodId、変更前後のステータスなど）を自由に持てる。

---

### 5-2. 詳細：`GET /audit-logs/{logId}`

一覧と同じ構造で 1 件だけ返せば十分です。

---

## 6. エラー

代表例：

* 認証なし

```json
{
  "code": "not_authenticated",
  "detail": "この操作にはログインが必要です。"
}
```

* 権限なし（一般従業員が全社ログを見ようとした）

```json
{
  "code": "permission_denied",
  "detail": "監査ログを閲覧する権限がありません。"
}
```

* 日付範囲の指定が不正

```json
{
  "code": "invalid_date_range",
  "detail": "dateFrom と dateTo の指定が不正です。"
}
```

---

## 7. 認可・ルーター（イメージ）

```python
router = APIRouter(
    prefix="/api/v1/audit-logs",
    tags=["audit-logs"],
    dependencies=[Depends(require_current_user)],
)

@router.get("")
def list_audit_logs(..., current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr_admin", "facility_head"])
    # facility_head の場合は、自施設のログに自動フィルタ
    ...

@router.get("/my")
def list_my_audit_logs(..., current_user: CurrentUser = Depends(require_current_user)):
    # 自分の操作履歴だけ
    ...

@router.get("/{log_id}")
def get_audit_log(log_id: str, current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr_admin", "facility_head"])
    ...
```

ログの「記録」は各サービス（evaluation-results 更新など）の中で共通関数 `audit_log.record(...)` を呼び出す形にするときれいです。

---

# `/exports` リソース（エクスポート系）

次に、評価結果やフィードバック等を CSV / Excel で出すためのリソースです。

ここでは、まずは **同期レスポンスで CSV を返すシンプル版** を前提にします（社内システム・人数規模的にも現実的そうなので）。
必要になれば将来「ジョブ型（export-jobs）」に拡張できるようにしておきます。

---

## 1. その API を使えるのはだれか

* 管理者（人事・本部）

  * 全社データのエクスポート可
* 施設長

  * 自施設分のみエクスポート可（facilityId を自動固定）
* 一般従業員・通常評価者

  * 原則アクセス不可

---

## 2. 何ができるか

* 評価結果の一括ダウンロード

  * `/exports/evaluation-results`
* フィードバック（面談票＋コメント）の一括ダウンロード

  * `/exports/feedbacks`
* 施設別集計結果のダウンロード

  * `/exports/site-results`
* （将来的に）分析結果や progress を CSV 出力 なども追加可能

形式：

* デフォルト：CSV（`text/csv`）
* 必要なら `format=xlsx` で Excel も検討

---

## 3. どのように行うか（ユースケース）

### ユースケース1：人事が全社の評価結果一覧を CSV で取る

1. 管理者が「エクスポート」画面で期と絞り込み条件を指定

   * 期：2025-Q1
   * 絞り込み：全社、または施設・等級別など
2. フロントで：

   * `GET /api/v1/exports/evaluation-results?periodId=2025-Q1&format=csv`
3. ブラウザがダウンロードを開始（Content-Disposition でファイル名指定）

---

### ユースケース2：施設長が自施設の結果だけを出す

1. 施設長が同様の画面で「自施設のみ」を指定
2. フロントで：

   * `GET /api/v1/exports/evaluation-results?periodId=2025-Q1&facilityScope=self&format=csv`
3. サーバ側で facilityId を current_user の施設に固定して CSV 作成

---

## 4. 入力（エンドポイント・クエリ）

### 4-1. 評価結果エクスポート：`GET /api/v1/exports/evaluation-results`

```text
GET /api/v1/exports/evaluation-results?periodId=2025-Q1&facilityId=fac_01&grade=G03&format=csv
```

クエリパラメータ：

* `periodId`（必須）：対象評価期
* 絞り込み：

  * `facilityId`（任意）
  * `facilityScope=self`（任意）… 施設長用。指定時は facilityId ではなく current_user の施設に固定
  * `grade`（任意）
  * `jobType`（任意）
* 出力形式：

  * `format`：`"csv"`（デフォルト） / `"xlsx"`（将来用）
* 列の粒度（必要なら）：

  * `detailLevel`: `"summary" | "sections" | "raw"` など

レスポンスは **CSV バイナリ**。
設計書上は JSON ではなく「CSV の列定義」を書いておくイメージです。

#### CSV カラム例

* `periodId`
* `employeeId`
* `employeeCode`
* `employeeName`
* `facilityId`
* `facilityName`
* `grade`
* `jobType`
* `finalScore`
* `finalGrade`
* `firstStageEvaluatorName`
* `secondStageEvaluatorName`
* `finalEvaluatorName`
* セクションスコア（列を広げる or 別ファイルにするのもあり）

---

### 4-2. フィードバックエクスポート：`GET /api/v1/exports/feedbacks`

```text
GET /api/v1/exports/feedbacks?periodId=2025-Q1&facilityId=fac_01&format=csv
```

クエリパラメータ類は `evaluation-results` とほぼ同じ。
CSV カラム例：

* `periodId`
* `employeeId`
* `employeeName`
* `facilityId`
* `overallGrade`
* `selfSheetQuestion1`
* `selfSheetAnswer1`
* `selfSheetQuestion2`
* `selfSheetAnswer2`
* …
* `managerComment`
* `managerCommentPublishedAt`
* `acknowledgedAt`

※ 質問数が固定なら列を固定。可変なら row を複数行にする構造も検討の余地あり。

---

### 4-3. 施設別サマリエクスポート：`GET /api/v1/exports/site-results`

```text
GET /api/v1/exports/site-results?periodId=2025-Q1&unit=facility&format=csv
```

クエリパラメータ：

* `periodId`（必須）
* `unit`: `"facility" | "office"`
* `format`: `"csv"` など

CSV カラム例：

* `periodId`
* `unit`（facility / office）
* `unitId`
* `unitName`
* `employeeCount`
* `averageScore`
* `medianScore`
* `scoreStdDev`
* `gradeShare_S`
* `gradeShare_A`
* `gradeShare_B`
* `gradeShare_C`

---

## 5. 出力（レスポンスイメージ）

### 5-1. HTTP レスポンスヘッダ例（CSV）

* `200 OK`
* `Content-Type: text/csv; charset=utf-8`
* `Content-Disposition: attachment; filename="evaluation-results_2025-Q1_fac-01.csv"`

ボディ（例）：

```csv
periodId,employeeId,employeeCode,employeeName,facilityId,facilityName,grade,jobType,finalScore,finalGrade
2025-Q1,emp_001,A0001,山田太郎,fac_01,仙台事業所,G03,介護職,3.4,B
2025-Q1,emp_002,A0002,佐藤花子,fac_01,仙台事業所,G04,看護職,3.8,A
...
```

---

## 6. エラー

* 認証なし

```json
{
  "code": "not_authenticated",
  "detail": "この操作にはログインが必要です。"
}
```

* 権限なし（一般従業員など）

```json
{
  "code": "permission_denied",
  "detail": "データのエクスポートを行う権限がありません。"
}
```

* 期間未指定などの不正入力

```json
{
  "code": "invalid_input",
  "detail": "periodId を指定してください。",
  "fieldErrors": {
    "periodId": ["必須項目です。"]
  }
}
```

* 該当データなし

```json
{
  "code": "no_data",
  "detail": "指定された条件に一致するデータがありません。"
}
```

* サーバ内部エラー（SQL タイムアウトなど）

```json
{
  "code": "internal_server_error",
  "detail": "エクスポート処理中にエラーが発生しました。時間をおいて再度お試しください。"
}
```

---

## 7. 認可・ルーター（イメージ）

```python
router = APIRouter(
    prefix="/api/v1/exports",
    tags=["exports"],
    dependencies=[Depends(require_current_user)],
)

@router.get("/evaluation-results")
def export_evaluation_results(..., current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr_admin", "facility_head"])
    # facility_head の場合は facilityScope=self を使って自施設に限定
    # CSV を生成して StreamingResponse などで返す

@router.get("/feedbacks")
def export_feedbacks(..., current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr_admin", "facility_head"])
    ...

@router.get("/site-results")
def export_site_results(..., current_user: CurrentUser = Depends(require_current_user)):
    require_role(current_user, ["admin", "hr_admin"])
    ...
```

---


