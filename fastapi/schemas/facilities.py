# schemas/facilities.py
from pydantic import BaseModel

# 施設取得用のスキーマ
class FacilityOption(BaseModel):
    value: str
    label: str
