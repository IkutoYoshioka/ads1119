from app.schemas.base import CamelModel

class OfficeOut(CamelModel):
    id: int
    office_code: str
    name: str

    class Config:
        from_attributes = True  # SQLAlchemy モデルからの変換を許可