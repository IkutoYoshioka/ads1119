# app/crud/user.py
from typing import Optional, List

from sqlalchemy.orm import Session

from app import models, schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_employee_code(db: Session, employee_code: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.employee_code == employee_code).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: schemas.user.UserCreate) -> models.User:
    # 本来はここでパスワードをハッシュ化する
    db_user = models.User(
        employee_id=user_in.employeeId,
        employee_code=user_in.employeeCode,
        grade=user_in.grade,
        is_admin=user_in.isAdmin,
        hashed_password=user_in.password,  # 仮
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
