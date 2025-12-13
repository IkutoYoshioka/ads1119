# app/crud/crud_auth.py
# /auth/me などで使う、User と関連情報をまとめて取得する CRUD クラス
from sqlalchemy.orm import Session, selectinload

from app.models.user import User
from app.models.employee import Employee
from app.models.office import Office
from app.models.site import Site
from app.models.grade import Grade

class CRUDAuth:
    def get_user_with_profile(self, db: Session, user_id: int) -> User | None:
        """
        /auth/me などで必要な「表示用プロフィール」をまとめて取得。
        N+1 を避けるため、必要なリレーションを eager load する。
        """
        return (
            db.query(User)
            .options(
                selectinload(User.employee)
                .selectinload(Employee.grade),
                selectinload(User.employee)
                .selectinload(Employee.office)
                .selectinload(Office.site),
                selectinload(User.mfa),
            )
            .filter(User.id == user_id)
            .first()
        )

crud_auth = CRUDAuth()
