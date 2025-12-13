# app/core/auth_errors.py
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


def _detail(
    *,
    code: str,
    message: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    d: Dict[str, Any] = {"code": code, "message": message}
    if extra:
        d.update(extra)
    return d


# ---- 401: 認証失敗（資格情報やトークンが不正） ----

def invalid_credentials() -> HTTPException:
    """
    employee_code / password が不正、ユーザーが存在しない等。
    推測を防ぐため、常に同じ文言にする。
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=_detail(
            code="INVALID_CREDENTIALS",
            message="社員コードまたはパスワードが正しくありません。",
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


def mfa_challenge_expired() -> HTTPException:
    """
    MFA temporary_token が期限切れ・改ざん等で無効。
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=_detail(
            code="MFA_CHALLENGE_EXPIRED",
            message="二段階認証チャレンジの有効期限が切れました。再度ログインをやり直してください。",
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


def invalid_mfa_code() -> HTTPException:
    """
    TOTP コード不正。
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=_detail(
            code="INVALID_MFA_CODE",
            message="認証コードが正しくありません。",
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


def invalid_token() -> HTTPException:
    """
    access token 等が不正。
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=_detail(
            code="INVALID_TOKEN",
            message="トークンが無効または期限切れです。",
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )


# ---- 403: 認可失敗（資格情報はあるが許可されない） ----

def ip_not_allowed() -> HTTPException:
    """
    許可されていないIPからのログイン。
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=_detail(
            code="IP_NOT_ALLOWED",
            message="このIPアドレスからのアクセスは許可されていません。",
        ),
    )




def mfa_not_enabled() -> HTTPException:
    """
    MFA verify を要求されたが、ユーザーにMFA設定が存在しない／無効。
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=_detail(
            code="MFA_NOT_ENABLED",
            message="二段階認証が有効化されていません。",
        ),
    )


def inactive_user() -> HTTPException:
    """
    アカウント無効化など。
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=_detail(
            code="USER_INACTIVE",
            message="このアカウントは無効化されています。",
        ),
    )

def mfa_already_enabled() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": "MFA_ALREADY_ENABLED", "message": "既にMFAが有効です。再セットアップはできません。"},
    )

