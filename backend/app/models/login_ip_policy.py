from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class LoginIpPolicy(Base):
    __tablename__ = "login_ip_policies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # 許可IPのCIDR一覧をJSON文字列で保存する想定
    # 例: '["192.168.0.0/16", "10.0.0.0/8"]'
    allowed_cidrs = Column(Text, nullable=False)

    is_default = Column(Boolean, nullable=False, default=False)
    for_admin_only = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    users = relationship("User", back_populates="login_ip_policy")
