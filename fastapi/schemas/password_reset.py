# schemas/password_reset.py
from pydantic import BaseModel


# パスワードリセット用のスキーマ
class PasswordResetRequest(BaseModel):
    employeeCode: str
    facility: str

class PasswordResetResponse(BaseModel):
    message: str
