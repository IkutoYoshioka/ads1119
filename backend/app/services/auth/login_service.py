# app/services/auth/login_service.py
from dataclasses import dataclass
from typing import Union

from sqlalchemy.orm import Session

from app.models.user import User
from app.crud.crud_user import crud_user
from app.core.security import create_access_token, verify_password
from app.services.auth.ip_policy_service import is_ip_allowed_for_user
from app.services.auth.mfa_service import user_has_mfa, create_temporary_token
from app.core.auth_errors import (
    invalid_credentials,
    ip_not_allowed,
    mfa_not_enabled,
)

# 外部IPからのログインを「MFA前提で許可」する等級コード
# ※ Gradeテーブル導入後は "X01" ではなく "EXEC" を推奨
EXTERNAL_ALLOWED_GRADE_CODES = {"EXEC", "G06"}


@dataclass
class NormalLoginResult:
    user: User
    access_token: str


@dataclass
class MfaChallengeResult:
    user: User
    temporary_token: str


LoginResult = Union[NormalLoginResult, MfaChallengeResult]


def _get_grade_code(user: User) -> str | None:
    # user.employee.grade は Grade オブジェクト
    if not user.employee or not user.employee.grade:
        return None
    return user.employee.grade.code


def _is_privileged_for_external(user: User) -> bool:
    grade_code = _get_grade_code(user)
    return user.is_admin or (grade_code in EXTERNAL_ALLOWED_GRADE_CODES)


def create_access_token_for_user(user: User) -> str:
    grade_code = _get_grade_code(user)
    return create_access_token(
        data={
            "sub": str(user.id),  # IDを文字列化して格納
            "is_admin": user.is_admin,
            "employee_id": user.employee_id,
            "grade": grade_code,  # 文字列コードを入れる
        }
    )


def login_with_password(
    db: Session,
    employee_code: str,
    password: str,
    client_ip: str,
) -> LoginResult:
    # 1) 認証
    user = crud_user.get_by_employee_code(db, employee_code=employee_code)
    if not user or not verify_password(password, user.hashed_password):
        raise invalid_credentials()

    # 2) IP判定（許可なら通常ログイン）
    if is_ip_allowed_for_user(db, user, client_ip):
        token = create_access_token_for_user(user)
        return NormalLoginResult(user=user, access_token=token)

    # 3) IP不許可 → 特権ユーザーか？
    if not _is_privileged_for_external(user):
        raise ip_not_allowed()

    # 4) 特権ユーザーはMFA必須：未有効ならエラー
    if not user_has_mfa(db, user):
        raise mfa_not_enabled()

    # 5) MFAチャレンジ発行
    temp_token = create_temporary_token(user)
    return MfaChallengeResult(user=user, temporary_token=temp_token)
