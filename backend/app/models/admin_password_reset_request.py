from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class AdminPasswordResetRequest(Base):
    __tablename__ = "admin_password_reset_requests"

    id = Column(Integer, primary_key=True, index=True)

    target_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    requested_by_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # "pending" / "approved" / "rejected" / "completed"
    status = Column(String(20), nullable=False, default="pending")

    reason = Column(String(255), nullable=True)
    admin_comment = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    target_user = relationship(
        "User",
        back_populates="admin_password_reset_requests_target",
        foreign_keys=[target_user_id],
    )
    requested_by = relationship(
        "User",
        back_populates="admin_password_reset_requests_created",
        foreign_keys=[requested_by_user_id],
    )
