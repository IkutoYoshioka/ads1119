# app/crud/crud_user.py
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.user import User


class CRUDUser:
    """
    User テーブル（認証アカウント）のための CRUD クラス。
    認証・権限・IPポリシーなどはここから扱う。
    """

    def get(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_employee_code(
        self,
        db: Session,
        *,
        employee_code: str,
    ) -> Optional[User]:
        """
        ログインIDとしての employee_code から User を1件取得する。
        /auth/login で利用。
        """
        return (
            db.query(User)
            .filter(User.employee_code == employee_code)
            .first()
        )

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    # 将来、管理画面などで使う想定の create/update/remove も定義しておくと便利
    def create(self, db: Session, *, obj_in) -> User:
        """
        obj_in は後で UserCreate スキーマに差し替える想定。
        いまは最低限の形だけにしておいてもよい。
        """
        db_obj = User(
            employee_code=obj_in.employee_code,
            employee_id=obj_in.employee_id,
            hashed_password=obj_in.hashed_password,
            is_active=obj_in.is_active,
            is_admin=obj_in.is_admin,
            must_change_password=obj_in.must_change_password,
            login_ip_policy_id=obj_in.login_ip_policy_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in) -> User:
        data = obj_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, db_obj: User) -> User:
        db.delete(db_obj)
        db.commit()
        return db_obj


crud_user = CRUDUser()
