# app/schemas/auth.py
from typing import Optional
from app.schemas.base import CamelModel


class LoginRequest(CamelModel):
    employee_code: str
    password: str


class LoginResponse(CamelModel):
    """
    /auth/login のレスポンス

    - 通常ログイン成功:
      employee_id, grade_code, is_admin, redirect_path,
      requires_mfa=false, temporary_token=None

    - MFAチャレンジ（外部IPなどでMFAが必要）:
      requires_mfa=true, temporary_token を返す
      （cookie はまだセットしない）
    """
    employee_id: Optional[int] = None

    # Gradeテーブル導入後は "G06" / "EXEC" のような code を返すのが安定
    grade_code: Optional[str] = None

    is_admin: Optional[bool] = None
    redirect_path: Optional[str] = None

    requires_mfa: bool = False
    temporary_token: Optional[str] = None

    must_change_password_at_next_login: Optional[bool] = None


class MfaVerifyLoginRequest(CamelModel):
    temporary_token: str
    totp_code: str


class MfaVerifyLoginResponse(CamelModel):
    """
    /auth/mfa/verify-login のレスポンス（MFAを通過してログイン成立）
    """
    employee_id: int
    grade_code: str
    is_admin: bool
    redirect_path: str
    must_change_password_at_next_login: bool


class MfaSetupInitResponse(CamelModel):
    otpauth_url: str
    # 開発用に返すなら optional に（本番は返さない運用が安全）
    secret: Optional[str] = None
    issuer: Optional[str] = None
    account_name: Optional[str] = None
    already_enabled: bool = False

class MfaSetupVerifyRequest(CamelModel):
    totp_code: str

class MfaSetupVerifyResponse(CamelModel):
    mfa_enabled: bool
