# schemas/password_reset_request.py
from app.schemas.base import CamelModel
from pydantic import Field


# パスワードリセット用のスキーマ
class PasswordResetRequestIn(CamelModel):
    employee_code: str
    office_id: int = Field(..., ge=1)

class PasswordResetRequestAcceptedOut(CamelModel):
    status: str = "accepted"
