# schemas/auth.py
from app.schemas.base import CamelModel
from typing import Optional

class LoginRequest(CamelModel):
    employee_code: str
    password: str

class LoginResponse(CamelModel):
    """
    - 通常ログイン成功時：
    employee_id, grade, is_admin, redirect_path, requires_mfa=false, must_change_password_at_next_login
    - MFA有効ユーザーのMFA認証成功時：
    requires_mfa=true, temporary_token
    """
    employee_id: Optional[int] = None
    grade: Optional[str] = None
    is_admin: Optional[bool] = None
    redirect_path: Optional[str] = None
    requires_mfa: bool = False
    temporary_token: Optional[str] = None
    must_change_password_at_next_login: Optional[bool] = None


class MfaVerifyLoginRequest(CamelModel):
    """
    /auth/mfa/verify-login エンドポイント用リクエストスキーマ
    """
    temporary_token: str
    totp_code: str

class MfaVerifyLoginResponse(CamelModel):
    """
    /auth/mfa/verify-login エンドポイント用レスポンススキーマ
    """
    employee_id: int
    grade: str
    is_admin: bool
    redirect_path: str
    mfa_enabled: bool
    must_change_password_at_next_login: bool