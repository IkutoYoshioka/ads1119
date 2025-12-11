# app/services/auth/mfa_service.py

from datetime import datetime, timedelta, timezone
from typing import Optional

import pyotp
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.user_mfa import UserMfa


# MFA ログイン用 temporaryToken の有効期限（分）
MFA_CHALLENGE_EXPIRE_MINUTES = 5
MFA_SCOPE = "mfa_challenge"


class MfaExpired(Exception):
    """
    temporaryToken が不正 / 期限切れなどで使用できない場合に投げる内部例外。
    API レイヤーで捕まえて HTTPException に変換する想定。
    """
    pass


def get_active_mfa(db: Session, user: User) -> Optional[UserMfa]:
    """
    有効な UserMfa を1件取得する。存在しなければ None。
    """
    return (
        db.query(UserMfa)
        .filter(
            UserMfa.user_id == user.id,
            UserMfa.is_enabled == True,  # noqa: E712
        )
        .first()
    )


def user_has_mfa(db: Session, user: User) -> bool:
    """
    ユーザーに有効な MFA 設定があるかどうか。
    """
    return get_active_mfa(db, user) is not None


def create_temporary_token(user: User) -> str:
    """
    MFA ログイン用の temporaryToken を JWT で発行する。

    - scope: "mfa_challenge"
    - exp : 現在時刻 + MFA_CHALLENGE_EXPIRE_MINUTES
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=MFA_CHALLENGE_EXPIRE_MINUTES)

    payload = {
        "sub": str(user.id),
        "scope": MFA_SCOPE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def decode_temporary_token(token: str) -> int:
    """
    temporaryToken を検証し、そこから user_id を取得して返す。

    - トークンの有効期限切れ・改ざん・scope 不一致などの場合は MfaExpired を送出。
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        raise MfaExpired() from e

    scope = payload.get("scope")
    if scope != MFA_SCOPE:
        raise MfaExpired()

    sub = payload.get("sub")
    if sub is None:
        raise MfaExpired()

    try:
        user_id = int(sub)
    except (TypeError, ValueError) as e:
        raise MfaExpired() from e

    return user_id


def verify_totp(mfa: UserMfa, code: str, window: int = 1) -> bool:
    """
    TOTP コードを検証する。

    - window: 許容ステップ幅（1なら ±1ステップ ≒ ±30秒 を許容）
    """
    totp = pyotp.TOTP(mfa.secret)
    return totp.verify(code, valid_window=window)
