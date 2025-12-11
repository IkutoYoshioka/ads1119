# app/schemas/user.py
from app.schemas.base import CamelModel


class UserBase(CamelModel):
    employee_code: str
    last_name: str
    first_name: str
    grade: str
    office_id: int
    is_admin: bool = False
    is_active: bool = True

class UserCreate(UserBase):
    password: str  # 平文パスワード（本来はハッシュにする）

class UserUpdate(CamelModel):
    last_name: str | None = None
    first_name: str | None = None
    grade: str | None = None
    office_id: int | None = None
    is_admin: bool | None = None
    is_active: bool | None = None


class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # SQLAlchemy モデルからの変換を許可
