# app/api/v1/auth.py
from __future__ import annotations

from datetime import timedelta
from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.deps.auth import get_current_user

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MfaVerifyLoginRequest,
    MfaVerifyLoginResponse,
    MfaSetupInitResponse,
    MfaSetupVerifyRequest,
    MfaSetupVerifyResponse,
)
from app.schemas.auth_me import MeResponse

from app.services.auth.ip_policy_service import get_client_ip
from app.services.auth.login_service import (
    login_with_password,
    NormalLoginResult,
    MfaChallengeResult,
    create_access_token_for_user,
)

from app.services.auth.mfa_service import (
    decode_temporary_token,
    get_active_mfa,
    get_mfa_any,
    verify_totp,
    MfaExpired,
    get_or_create_mfa_for_setup,
    build_otpauth_url,
    enable_mfa_after_verify,
    MfaAlreadyEnabled,
    user_has_mfa,
)

from app.services.auth.me_service import auth_me_service

from app.core.auth_errors import (
    mfa_challenge_expired,
    invalid_mfa_code,
    mfa_not_enabled,
    invalid_token,
    mfa_already_enabled,
)

from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

RETURN_MFA_SECRET = getattr(settings, "RETURN_MFA_SECRET", True)  # 開発用（本番は False 推奨）


def _set_auth_cookies(response: Response, access_token: str, is_admin: bool) -> None:
    max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=getattr(settings, "COOKIE_SECURE", False),
        samesite="lax",
        path="/",
        max_age=max_age,
    )

    response.set_cookie(
        key="loginType",
        value="admin" if is_admin else "user",
        httponly=False,
        path="/",
        max_age=max_age,
    )


def _grade_code(user: User) -> str | None:
    if user.employee and user.employee.grade:
        return user.employee.grade.code
    return None


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> LoginResponse:
    client_ip = get_client_ip(request)

    result = login_with_password(
        db=db,
        employee_code=payload.employee_code,
        password=payload.password,
        client_ip=client_ip,
    )

    user = result.user
    redirect_path = "/dashboard"

    if isinstance(result, NormalLoginResult):
        _set_auth_cookies(response, result.access_token, user.is_admin)
        return LoginResponse(
            employee_id=user.employee_id,
            grade_code=_grade_code(user),
            is_admin=user.is_admin,
            redirect_path=redirect_path,
            requires_mfa=False,
            temporary_token=None,
            must_change_password_at_next_login=user.must_change_password,
        )

    if isinstance(result, MfaChallengeResult):
        # cookie はまだセットしない（MFA verify-login を通すまで未ログイン扱い）
        return LoginResponse(
            employee_id=user.employee_id,
            grade_code=_grade_code(user),
            is_admin=user.is_admin,
            redirect_path=redirect_path,
            requires_mfa=True,
            temporary_token=result.temporary_token,
            must_change_password_at_next_login=user.must_change_password,
        )

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid login result")


@router.post("/mfa/setup-init", response_model=MfaSetupInitResponse)
def setup_mfa_init(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MfaSetupInitResponse:
    """
    MFAセットアップ開始：
    - 既に is_enabled=True なら 409（再セットアップ抑止）
    - 未有効なら secret を（無ければ作って）otpauth_url を返す
    """
    try:
        mfa = get_or_create_mfa_for_setup(db, user)
    except MfaAlreadyEnabled:
        raise mfa_already_enabled()

    otpauth_url = build_otpauth_url(user, mfa.secret)
    db.commit()

    return MfaSetupInitResponse(
        otpauth_url=otpauth_url,
        secret=mfa.secret if RETURN_MFA_SECRET else None,
        issuer=getattr(settings, "MFA_ISSUER", "AobaHR"),
        account_name=user.employee_code,
        already_enabled=False,
    )


@router.post("/mfa/setup-verify", response_model=MfaSetupVerifyResponse)
def setup_mfa_verify(
    payload: MfaSetupVerifyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MfaSetupVerifyResponse:
    """
    MFAセットアップ確定：
    - secret で totp_code を検証
    - 成功したら is_confirmed/is_enabled/last_verified_at を更新
    """
    mfa = get_mfa_any(db, user)
    if not mfa:
        raise mfa_not_enabled()

    if not verify_totp(mfa.secret, payload.totp_code, window=1):
        raise invalid_mfa_code()

    enable_mfa_after_verify(db, mfa)
    db.commit()

    return MfaSetupVerifyResponse(mfa_enabled=True)


@router.post("/mfa/verify-login", response_model=MfaVerifyLoginResponse)
def verify_mfa_login(
    payload: MfaVerifyLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> MfaVerifyLoginResponse:
    # 1) temporary_token から user_id を復元
    try:
        user_id = decode_temporary_token(payload.temporary_token)
    except MfaExpired:
        raise mfa_challenge_expired()

    # 2) user と mfa 設定の取得
    user: User | None = db.get(User, user_id)
    if not user:
        raise invalid_token()

    mfa = get_active_mfa(db, user)
    if not mfa:
        raise mfa_not_enabled()

    # 3) TOTP 検証
    if not verify_totp(mfa.secret, payload.totp_code, window=1):
        raise invalid_mfa_code()

    # 4) last_verified_at 更新（任意だが監査的に有用）
    # enable_mfa_after_verify と同じ更新だと “毎回 enable” になるので、ログイン用は軽く更新のみ
    mfa.last_verified_at = getattr(settings, "NOW_FUNC", None) or None  # 使わないなら削除でOK
    # ↑ここはシンプルに datetime.now(timezone.utc) にする方が分かりやすい。必要なら後で整備。

    # 5) access_token 発行 & cookie セット
    token = create_access_token_for_user(user)
    _set_auth_cookies(response, token, user.is_admin)

    return MfaVerifyLoginResponse(
        employee_id=user.employee_id,
        grade_code=_grade_code(user) or "",
        is_admin=user.is_admin,
        redirect_path="/dashboard",
        mfa_enabled=True,
        must_change_password_at_next_login=user.must_change_password,
    )



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
        secure=getattr(settings, "COOKIE_SECURE", False)
    )
    response.delete_cookie(
        key="loginType",
        path="/",
        samesite="lax",
        secure=False,
    )

    return {"detail": "Logged out"}


@router.get("/me", response_model=MeResponse)
def me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MeResponse:
    me_res = auth_me_service.build_me_response(db, user_id=user.id)
    if not me_res:
        # JWTはあるのに user が取れないケース（削除済み等）
        raise invalid_token()
    return me_res


@router.post("/change-password")
def change_password():
    """
    パスワード変更処理。
    """
    # TODO: 実装
    pass
