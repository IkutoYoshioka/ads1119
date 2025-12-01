# app/crud/crud_user.py
from sqlalchemy.orm import Session
from app.models.user import User

class CRUDUser:
    def get_by_employee_code(self, db: Session, employee_code: str) -> User | None:
        return (
            db.query(User)
            .filter(User.employee_code == employee_code)
            .first()
        )

crud_user = CRUDUser()
