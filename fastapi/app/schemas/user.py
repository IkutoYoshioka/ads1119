# app/schemas/user.py
from pydantic import BaseModel


class UserBase(BaseModel):
    employeeId: str
    employeeCode: str
    grade: str
    isAdmin: bool


class UserCreate(UserBase):
    password: str  # 平文パスワード（本来はハッシュにする）


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # SQLAlchemy モデルからの変換を許可
