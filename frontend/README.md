## 全体方針

* `app/` は **ルート構造（URL）単位**
* 業務ロジック・API 呼び出しは **`features/*`** に集約
* 汎用 UI は **`components/ui`**（shadcn/ui など）
* 認可レベルでルートグループを分ける：

  * `(auth)`：ログイン系
  * `(main)`：一般ユーザー（従業員・評価者・施設長を含む）
  * `(admin)`：管理者専用

---

## 1. `app/` 配下のルート構成案

```text
app/
  (auth)/
    login/
      page.tsx
    mfa/
      verify/
        page.tsx
    reset-password/
      request/
        page.tsx        // /password-reset-requests 連携フォーム

  (main)/
    layout.tsx          // require_current_user() を使うレイアウト
    dashboard/
      page.tsx          // GET /dashboard/home
    notices/
      page.tsx          // 一覧 + 詳細モーダル
    feedbacks/
      my/
        page.tsx        // マイフィードバック（自己面談票＋確認）
      [periodId]/
        [employeeId]/
          page.tsx      // 特定期・特定被考課者のフィードバック詳細（評価者用）
    evaluations/
      my-tasks/
        page.tsx        // 自分が評価者として持っているタスク一覧 (/progress/my)
      [periodId]/
        [employeeId]/
          page.tsx      // 個票編集画面 (/evaluation-results, /evaluation-tasks)
    profile/
      page.tsx          // /auth/change-password, /auth/mfa/setup-* など

  (admin)/
    layout.tsx          // require_admin() 的なガード
    dashboard/
      page.tsx          // 管理者向けダッシュボード（全社進捗など）
    employees/
      page.tsx
      [employeeId]/
        page.tsx
    facilities/
      page.tsx
      [facilityId]/
        page.tsx
    assignments/
      page.tsx
    evaluation-forms/
      page.tsx
      [formId]/
        page.tsx
    question-master/
      page.tsx
    password-reset-requests/
      page.tsx          // /admin/password-reset-requests
    login-ip-policies/
      page.tsx
    notices/
      page.tsx          // お知らせ作成・編集
    site-results/
      page.tsx          // 施設間比較
    analysis/
      page.tsx          // 設問別分析など
    progress/
      overview/
        page.tsx        // /progress/overview + /progress/facility
    exports/
      page.tsx          // /exports/* ダウンロード UI
    audit-logs/
      page.tsx          // /audit-logs 検索画面
```

ポイントだけ補足します。

### `(auth)` グループ

* 全部 **未ログイン前提** の画面：

  * `/login` → `/api/v1/auth/login` 呼び出し
  * `/mfa/verify` → `/api/v1/auth/mfa/verify-login`
  * `/reset-password/request` → `/password-reset-requests`
* layout は「ログイン済みなら `/dashboard` にリダイレクト」でいいです。

### `(main)` グループ

* `layout.tsx` で

  * `get_current_user_or_null` → 未ログインなら `/login` へリダイレクト
  * 共通ヘッダー・サイドバー（「ダッシュボード / 評価タスク / マイフィードバック / お知らせ / プロフィール」）
* ページごとの役割：

  * `/dashboard`：`GET /dashboard/home` を叩いてウィジェットを描画
  * `/evaluations/my-tasks`：評価者としてのタスク一覧（`/progress/my` or `/evaluation-tasks`）
  * `/evaluations/[periodId]/[employeeId]`：個票編集（`/evaluation-results`＋`/evaluation-tasks`）
  * `/feedbacks/my`：被考課者向けマイフィードバック（自己面談票 + フィードバック確認）
  * `/feedbacks/[periodId]/[employeeId]`：評価者側からフィードバック詳細を見る画面
  * `/notices`：お知らせ一覧 + 既読 API 呼び出し
  * `/profile`：

    * パスワード変更 (`/auth/change-password`)
    * MFA 設定 (`/auth/mfa/setup-init` / `setup-verify`)

### `(admin)` グループ

* `layout.tsx` で `require_admin` 的なチェック
* メニューのイメージ：

  * マスタ管理：`employees`, `facilities`, `question-master`, `evaluation-forms`, `assignments`
  * 運用・サポート：`password-reset-requests`, `login-ip-policies`, `notices`, `audit-logs`
  * 分析・集計：`site-results`, `analysis`, `progress/overview`, `exports`, `dashboard`

---

## 2. `features/` 配下の機能別構成

Next.js の `app/` はルーティングに集中させて、
API 呼び出し・ドメインロジックは `features` 単位でまとめると保守しやすくなります。

```text
features/
  auth/
    api.ts           // /auth 系の fetch ラッパー
    server.ts        // require_current_user, require_admin など
    hooks.ts         // useLogin, useLogout など
    components/
      LoginForm.tsx
      MfaVerifyForm.tsx

  dashboard/
    api.ts           // GET /dashboard/home
    types.ts
    components/
      DashboardLayout.tsx
      WidgetNotices.tsx
      WidgetMyTasks.tsx
      WidgetMyProgress.tsx
      WidgetFacilityProgress.tsx
      WidgetAdminTasks.tsx

  evaluations/
    api.ts           // /evaluation-results, /evaluation-tasks
    types.ts
    components/
      EvaluationTaskList.tsx
      EvaluationForm.tsx
      ResultSectionCard.tsx

  feedbacks/
    api.ts           // /feedbacks
    types.ts
    components/
      SelfFeedbackForm.tsx
      ManagerFeedbackForm.tsx
      FeedbackTimeline.tsx

  notices/
    api.ts           // /notices
    types.ts
    components/
      NoticeList.tsx
      NoticeDetailDialog.tsx

  employees/
    api.ts           // /employees, /employees/{id}/reset-password
    components/
      EmployeeTable.tsx
      EmployeeForm.tsx

  facilities/
    api.ts
    components/
      FacilityTable.tsx

  assignments/
    api.ts
    components/
      AssignmentTable.tsx

  evaluationForms/
    api.ts           // /evaluation-forms, /question-master
    components/
      EvaluationFormTable.tsx
      EvaluationFormEditor.tsx

  siteResults/
    api.ts           // /site-results
    components/
      SiteResultsTable.tsx
      SiteResultsChart.tsx

  analysis/
    api.ts           // /analysis/*
    components/
      QuestionStatsChart.tsx

  progress/
    api.ts           // /progress/*
    components/
      MyProgressCard.tsx
      FacilityProgressCard.tsx
      CompanyProgressCard.tsx

  loginIpPolicies/
    api.ts           // /login-ip-policies
    components/
      LoginIpPolicyTable.tsx
      LoginIpPolicyForm.tsx

  passwordResetRequests/
    api.ts           // /password-reset-requests, /admin/password-reset-requests
    components/
      PasswordResetRequestForm.tsx
      PasswordResetRequestTable.tsx

  exports/
    api.ts           // /exports/*
    components/
      ExportControls.tsx

  auditLogs/
    api.ts           // /audit-logs
    components/
      AuditLogSearchForm.tsx
      AuditLogTable.tsx
```

ページ側の `page.tsx` は、

* サーバコンポーネントで `await` する or
* クライアントコンポーネント＋ `useEffect` / React Query

いずれかで `features/*/api.ts` を呼び出すだけ、という形にできます。

---

## 3. 共通ライブラリ・UI

```text
lib/
  api/
    client.ts        // fetch wrapper（Base URL, 認証ヘッダなど）
    errors.ts        // API エラー型・ハンドリング
  utils/
    date.ts
    format.ts
    zodSchemas.ts    // バリデーションなど

components/
  ui/                // shadcn/ui (button, card, dialog...)
  layout/
    AppShell.tsx     // サイドバー + ヘッダー
    MainSidebar.tsx
    AdminSidebar.tsx
  common/
    DataTable.tsx
    Pagination.tsx
    LoadingSpinner.tsx
    ErrorAlert.tsx
```

* `features/*` からは基本的に `lib/api/client.ts` 経由で API を叩く
* 汎用 UI は `components/ui` + `components/common`
* レイアウト系は `components/layout` で共通化し、`(main)/layout.tsx`, `(admin)/layout.tsx` から使い回し

---

## 4. どのページがどの API を使うか（ざっくり対応表）

* `/dashboard` → `GET /dashboard/home`
* `/evaluations/my-tasks` → `/progress/my` or `/evaluation-tasks`
* `/evaluations/[periodId]/[employeeId]` → `/evaluation-results`, `/evaluation-tasks`
* `/feedbacks/my` → `/feedbacks`（employeeScope=self）
* `/feedbacks/[periodId]/[employeeId]` → `/feedbacks/{id}`
* `/notices` → `/notices`, `/notices/{id}`, `/notices/{id}/read`
* `/profile` → `/auth/me`, `/auth/change-password`, `/auth/mfa/*`
* `/admin/employees` → `/employees`, `/employees/{id}`, `/employees/{id}/reset-password`
* `/admin/facilities` → `/facilities`
* `/admin/assignments` → `/assignments`
* `/admin/evaluation-forms` → `/evaluation-forms`, `/question-master`
* `/admin/password-reset-requests` → `/admin/password-reset-requests`
* `/admin/login-ip-policies` → `/login-ip-policies`
* `/admin/notices` → `/notices`（管理系）
* `/admin/site-results` → `/site-results`
* `/admin/analysis` → `/analysis/*`
* `/admin/progress/overview` → `/progress/overview`, `/progress/facility`
* `/admin/exports` → `/exports/*`
* `/admin/audit-logs` → `/audit-logs`

---

この構成にしておけば、

* API リソースの構造と 1 対 1 で頭の中で対応が取りやすい
* フロントは `app`（ルーティング）と `features`（ドメイン）で分離され、後から機能追加しやすい
* 権限による画面の分岐も `(main)` / `(admin)` グループで明確

という形になります。
