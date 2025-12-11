# app/api/v1/auth.py
from datetime import timedelta
from typing import Optional, List

import ipaddress

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, LoginResponse, MfaVerifyLoginRequest, MfaVerifyLoginResponse
from app.db.session import get_db
from app.crud.crud_user import crud_user  # あなたのCRUD層に合わせて
from app.models.employee import Employee
from app.models.user import User
from app.models.login_ip_policy import LoginIpPolicy as LoginIpPolicyModel
from app.crud import crud_login_ip_policy

router = APIRouter(prefix="/auth", tags=["auth"])

# 考課者系のグレード（役員・施設長・考課者など）
EVALUATOR_GRADES = {"X01", "G06", "G04", "G05", "T01"}

# 外部からのMFAログインを許可するグレード
EXTERNAL_LOGIN_PRIVILEGED_GRADES = {"X01", "G06"}

# 一時トークンの有効期限（分）
MFA_CHALLENGE_EXPIRE_MINUTES = 5


def get_redirect_path(grade: str, is_admin: bool) -> str:
    """
    ログイン直後にどこへ飛ばすかを決める。
    基本方針：
      - 全ユーザーとも /dashboard に行く
      - 「どの機能が見えるか」はフロントのサイドバーで制御
    """
    # 将来、管理者だけ別ページに飛ばしたくなったらここで分岐すればOK
    return "/dashboard"


def _get_client_ip(request: Request) -> str:
    """
    クライアントIPを取得するヘルパー。
    将来リバースプロキシ配下に置くときは X-Forwarded-For をここで解釈する。
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # "client, proxy1, proxy2" 形式なので先頭だけ使う
        return xff.split(",")[0].strip()
    return request.client.host


def _is_ip_allowed(client_ip: str, cidrs: List[str]) -> bool:
    """
    client_ip が allowed_cidrs のどれかに含まれているか判定する。
    CIDR が壊れている場合はそのエントリは無視する。
    """
    try:
        ip_obj = ipaddress.ip_address(client_ip)
    except ValueError:
        # IP として解釈できない場合は拒否
        return False

    for cidr in cidrs:
        try:
            net = ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            # 管理画面から誤ったCIDRが登録されていても、他のCIDRで判定を続行
            continue
        if ip_obj in net:
            return True
    return False


def _resolve_login_ip_policy(db: Session, user: Employee) -> Optional[LoginIpPolicyModel]:
    """
    ユーザーに適用すべき LoginIpPolicy を解決する。
      1. user.login_ip_policy_id があればそのポリシー
      2. なければ is_default=True のポリシー（複数ある場合は最初の1件）
      3. それもなければ None（この場合はIP制限はスキップ）
    """
    # 1. ユーザーに明示的に紐付いているポリシー
    if getattr(user, "login_ip_policy_id", None):
        policy = db.get(LoginIpPolicyModel, user.login_ip_policy_id)
        if policy:
            return policy

    # 2. デフォルトポリシー
    stmt = select(LoginIpPolicyModel).where(LoginIpPolicyModel.is_default == True)  # noqa: E712
    policy = db.scalar(stmt)
    if policy:
        return policy

    # 3. 何も見つからなければ None
    return None


def _is_privileged_for_external_login(user: User) -> bool:
    """
    施設長と役員または管理者に該当するか判定する。
    """
    grade = user.employee.grade if user.employee else None
    return user.is_admin or (grade in EXTERNAL_LOGIN_PRIVILEGED_GRADES)

def _user_has_enabled_mfa(db: Session, user: User) -> bool:
    """
    MFAが有効になっているか判定する。
    """
    


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    ログイン処理:
      1. employeeCode からユーザをDB検索
      2. パスワードハッシュを検証
      3. IPポリシーに基づきクライアントIPをチェック
      4. JWTを発行し、HttpOnly Cookie に保存
      5. フロント用に employeeId / grade / isAdmin / redirectPath を返却
    """

    # 1. ユーザー取得（employee_code で一意）
    user: User | None = crud_user.get_by_employee_code(db, employee_code=payload.employee_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employeeCode or password",
        )

    # 2. パスワード検証（平文 vs ハッシュ）
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employeeCode or password",
        )

    # 3. IP ポリシーチェック
    client_ip = _get_client_ip(request)
    policy = _resolve_login_ip_policy(db, user)

    if policy is not None:
        cidrs = crud_login_ip_policy._decode_cidrs(policy.allowed_cidrs)

        # allowed_cidrs が空リストなら「制限なし」と解釈してスキップ
        if cidrs:
            if not _is_ip_allowed(client_ip, cidrs):
                # 将来的にはここで「MFAログインにフォールバック」などの分岐も可能
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Login from this IP address is not allowed",
                )
    # policy が None の場合は、IP 制限は現時点では適用しない（将来締める余地あり）

    # 4. JWT 作成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "is_admin": user.is_admin,
            "employee_id": user.employee_id,
            "grade": user.employee.grade if user.employee else None,
        },
        expires_delta=access_token_expires,
    )

    # 5. HttpOnly Cookie に保存（JSからは直接読めない）
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,       # 本番は HTTPS 前提なので True 推奨
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # 補助的な Cookie（フロントから見たい場合）
    login_type = "admin" if user.is_admin else "user"
    response.set_cookie(
        key="loginType",
        value=login_type,
        httponly=False,   # フロントから読める
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    redirect_path = get_redirect_path(user.employee.grade, user.is_admin)

    return LoginResponse(
        employeeId=user.employee_id,
        grade=user.employee.grade,
        isAdmin=user.is_admin,
        redirectPath=redirect_path,
    )


@router.post("/mfa/setup-init")
def setup_mfa_init():
    """
    多要素認証セットアップ初期化処理。
    フロント/account/mfaページから呼ばれる。
    """
    # TODO: 実装
    pass


@router.post("/mfa/setup-verify")
def setup_mfa_verify():
    """
    多要素認証セットアップ検証処理。
    フロント/account/mfaページから呼ばれる。
    """
    # TODO: 実装
    pass


@router.post("/mfa/verify-login")
def verify_mfa_login():
    """
    多要素認証ログイン検証処理。
    ログイン直後、多要素認証が有効な場合に呼ばれる。
    """
    # TODO: 実装
    pass


@router.post("/logout")
def logout(response: Response):
    """
    ログアウト:
      - access_token, loginType の Cookie を削除
    """
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax",
        secure=False,   # ← login 時と合わせる（本番は True）
    )
    response.delete_cookie(
        key="loginType",
        path="/",
        samesite="lax",
        secure=False,
    )

    return {"detail": "Logged out"}


@router.get("/me")
def get_me():
    """
    現在ログイン中のユーザー情報を返す。
    （実装時は Depends(get_current_user) などを利用）
    """
    # TODO: 実装
    pass


@router.post("/change-password")
def change_password():
    """
    パスワード変更処理。
    """
    # TODO: 実装
    pass
