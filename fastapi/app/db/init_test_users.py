# app/db/init_test_users.py

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash  # すでにあるはず

def create_user_if_not_exists(
    db,
    employee_id: str,
    employee_code: str,
    grade: str,
    password: str,
    is_admin: bool = False,
):
    user = db.query(User).filter(User.employee_code == employee_code).first()
    if user:
        print(f"User {employee_code} already exists, skip.")
        return

    user = User(
        employee_id=employee_id,
        employee_code=employee_code,
        grade=grade,
        is_admin=is_admin,
        hashed_password=get_password_hash(password),
    )
    db.add(user)
    db.commit()
    print(f"User {employee_code} created.")

def init_test_users():
    db = SessionLocal()
    try:
        # 役員
        create_user_if_not_exists(
            db,
            employee_id="E0001",
            employee_code="X01-TEST",
            grade="X01",
            password="password123",
            is_admin=True,
        )

        # 施設長
        create_user_if_not_exists(
            db,
            employee_id="E0002",
            employee_code="G06-TEST",
            grade="G06",
            password="password123",
            is_admin=False,
        )

        # 一般の考課者
        create_user_if_not_exists(
            db,
            employee_id="E0003",
            employee_code="G05-TEST",
            grade="G05",
            password="password123",
            is_admin=False,
        )

        # 非考課者
        create_user_if_not_exists(
            db,
            employee_id="E0004",
            employee_code="G02-TEST",
            grade="G02",
            password="password123",
            is_admin=False,
        )

        # 管理者（権限確認用）
        create_user_if_not_exists(
            db,
            employee_id="E0005",
            employee_code="ADMIN-TEST",
            grade="G06",  # 施設長 + 管理者 という想定
            password="admin123",
            is_admin=True,
        )

    finally:
        db.close()

if __name__ == "__main__":
    init_test_users()
