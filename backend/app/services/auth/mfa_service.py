from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import pyotp
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.user_mfa import UserMfa


# ===== MFA challenge token (login) =====

MFA_CHALLENGE_EXPIRE_MINUTES = 5
MFA_SCOPE = "mfa_challenge"


class MfaExpired(Exception):
    """temporaryToken が不正 / 期限切れ等で使用できない場合"""
    pass


class MfaAlreadyEnabled(Exception):
    """既に MFA が有効なユーザーに対して setup を開始しようとした場合"""
    pass


def get_active_mfa(db: Session, user: User) -> Optional[UserMfa]:
    """有効化済み (is_enabled=True) の UserMfa を1件返す"""
    return (
        db.query(UserMfa)
        .filter(
            UserMfa.user_id == user.id,
            UserMfa.is_enabled == True,  # noqa: E712
        )
        .first()
    )


def get_mfa_any(db: Session, user: User) -> Optional[UserMfa]:
    """有効/無効を問わず UserMfa を1件返す（setup 検証で使う）"""
    return db.query(UserMfa).filter(UserMfa.user_id == user.id).first()


def user_has_mfa(db: Session, user: User) -> bool:
    """ログイン時に「MFAが有効か」を判定する用途"""
    return get_active_mfa(db, user) is not None


def create_temporary_token(user: User) -> str:
    """MFAログイン用の temporaryToken を JWT で発行する"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=MFA_CHALLENGE_EXPIRE_MINUTES)

    payload = {
        "sub": str(user.id),
        "scope": MFA_SCOPE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_temporary_token(token: str) -> int:
    """temporaryToken を検証し、user_id を返す（不正なら MfaExpired）"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        raise MfaExpired() from e

    if payload.get("scope") != MFA_SCOPE:
        raise MfaExpired()

    sub = payload.get("sub")
    if sub is None:
        raise MfaExpired()

    try:
        return int(sub)
    except (TypeError, ValueError) as e:
        raise MfaExpired() from e


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """
    TOTP コードを検証する。
    - window=1 なら ±1ステップ（だいたい±30秒）を許容
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=window)


# ===== MFA setup (QR -> verify -> enable) =====

def get_or_create_mfa_for_setup(db: Session, user: User) -> UserMfa:
    """
    セットアップ用に UserMfa を用意する（再セットアップ抑止）。

    - 既に is_enabled=True なら MfaAlreadyEnabled を送出
    - レコードがあれば secret を維持（再発行しない）
    - 無ければ新規作成（is_enabled=False, is_confirmed=False）
    """
    existing = get_mfa_any(db, user)
    if existing:
        if existing.is_enabled:
            raise MfaAlreadyEnabled()
        return existing

    now = datetime.now(timezone.utc)
    secret = pyotp.random_base32()

    mfa = UserMfa(
        user_id=user.id,
        secret=secret,
        is_enabled=False,
        is_confirmed=False,
        last_verified_at=None,
        created_at=now,
        updated_at=now,
    )
    db.add(mfa)
    db.flush()
    return mfa


def build_otpauth_url(user: User, secret: str) -> str:
    """
    Google Authenticator 等に登録するための otpauth URL を生成する。
    """
    issuer = getattr(settings, "MFA_ISSUER", "AobaHR")
    account_name = user.employee_code  # 表示名（わかりやすい識別子）
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=account_name, issuer_name=issuer)


def enable_mfa_after_verify(db: Session, mfa: UserMfa) -> None:
    """setup-verify 成功後に有効化フラグ等を更新する"""
    now = datetime.now(timezone.utc)
    mfa.is_confirmed = True
    mfa.is_enabled = True
    mfa.last_verified_at = now
    mfa.updated_at = now
    db.add(mfa)
