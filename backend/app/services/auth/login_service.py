from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.crud.crud_user import crud_user
from app.core.security import create_access_token, verify_password
from app.services.auth.ip_policy_service import is_ip_allowed_for_user
from app.services.auth.mfa_service import user_has_mfa, create_temporary_token
from app.core.auth_errors import (
    invalid_credentials,
    ip_not_allowed,
    mfa_required_but_not_enabled,
)


EXTERNAL_ALLOWED_GRADES = {"X01", "G06"}


@dataclass
class NormalLoginResult:
    user: User
    access_token: str


@dataclass
class MfaChallengeResult:
    user: User
    temporary_token: str


LoginResult = NormalLoginResult | MfaChallengeResult


def _is_privileged_for_external(user: User) -> bool:
    grade = user.employee.grade if user.employee else None
    return user.is_admin or (grade in EXTERNAL_ALLOWED_GRADES)


def login_with_password(
    db: Session,
    employee_code: str,
    password: str,
    client_ip: str,
) -> LoginResult:
    # 1. 社員コード・パスワードチェック
    user = crud_user.get_by_employee_code(db, employee_code)
    if not user or not verify_password(password, user.hashed_password):
        raise invalid_credentials()

    # 2. IP 判定
    if is_ip_allowed_for_user(db, user, client_ip):
        # 通常ログイン
        token = create_access_token_for_user(user)
        return NormalLoginResult(user=user, access_token=token)

    # 3. IP 不許可 → 特権チェック
    if not _is_privileged_for_external(user):
        raise ip_not_allowed()

    # 4. 特権ユーザーだが MFA 無効 → エラー
    if not user_has_mfa(db, user):
        raise mfa_required_but_not_enabled()

    # 5. MFA チャレンジ開始
    temp_token = create_temporary_token(user)
    return MfaChallengeResult(user=user, temporary_token=temp_token)


def create_access_token_for_user(user: User) -> str:
    grade = user.employee.grade if user.employee else None
    return create_access_token(
        data={
            "sub": str(user.id),
            "is_admin": user.is_admin,
            "employee_id": user.employee_id,
            "grade": grade,
        }
    )
