# app/crud/crud_employee.py
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.employee import Employee


class CRUDEmployee:
    def get(self, db: Session, employee_id: int) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.id == employee_id).first()

    def get_by_code(self, db: Session, *, employee_code: str) -> Optional[Employee]:
        return (
            db.query(Employee)
            .filter(Employee.employee_code == employee_code)
            .first()
        )

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Employee]:
        return db.query(Employee).offset(skip).limit(limit).all()


crud_employee = CRUDEmployee()
