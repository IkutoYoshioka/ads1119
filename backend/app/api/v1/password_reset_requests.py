from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.password_reset_request import (
    PasswordResetRequestIn,
    PasswordResetRequestAcceptedOut,
)
from app.services.auth.password_reset_request import submit_password_reset_request

router = APIRouter(prefix="/password-reset-requests", tags=["password-reset-requests"])

@router.post("", response_model=PasswordResetRequestAcceptedOut, status_code=status.HTTP_202_ACCEPTED)
def create_password_reset_request(
    payload: PasswordResetRequestIn,
    db: Session = Depends(get_db),
):
    # 外部レスポンスは常に accepted（推測防止）
    submit_password_reset_request(
        db,
        employee_code=payload.employee_code,
        office_id=payload.office_id,
    )
    return {"status": "accepted"}
