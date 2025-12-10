# app/models/login_ip_policies.py
from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import Base


class User(Base):
    __tablename__ = "login_ip_policies"

    