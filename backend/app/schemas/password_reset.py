# schemas/password_reset.py
from app.schemas.base import CamelModel


# パスワードリセット用のスキーマ
class PasswordResetRequest(CamelModel):
    employee_code: str
    facility: str

class PasswordResetResponse(CamelModel):
    message: str
