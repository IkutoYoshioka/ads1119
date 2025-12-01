# app/models/user.py
from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    employee_code = Column(String, unique=True, index=True, nullable=False)

    grade = Column(String, index=True, nullable=False)  # G02, G06, X01 など
    is_admin = Column(Boolean, default=False, nullable=False)
    

    hashed_password = Column(String, nullable=False)
