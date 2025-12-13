from sqlalchemy.orm import Session
from app.models.admin_password_reset_request import AdminPasswordResetRequest

def create_admin_password_reset_request(
    db: Session,
    *,
    target_user_id: int,
    requested_by_user_id: int | None,
    reason: str | None = None,
) -> AdminPasswordResetRequest:
    row = AdminPasswordResetRequest(
        target_user_id=target_user_id,
        requested_by_user_id=requested_by_user_id,
        status="pending",
        reason=reason,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
