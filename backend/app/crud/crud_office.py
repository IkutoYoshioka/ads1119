from sqlalchemy.orm import Session
from app.models.office import Office

def list_active(db: Session) -> list[Office]:
    return (
        db.query(Office)
        .filter(Office.is_active == True)  # noqa: E712
        .order_by(Office.name.asc())
        .all()
    )
