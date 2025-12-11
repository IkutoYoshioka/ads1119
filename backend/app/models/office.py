from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Office(Base):
    __tablename__ = "offices"

    id = Column(Integer, primary_key=True, index=True)

    office_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)

    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # Site との関係
    site = relationship("Site", back_populates="offices")

    # 1事業所に複数社員
    employees = relationship("Employee", back_populates="office")
