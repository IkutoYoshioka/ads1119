# routers/facilities.py
from fastapi import APIRouter

from app.schemas.facilities import FacilityOption

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.get("/", response_model=list[FacilityOption])
async def list_facilities() -> list[FacilityOption]:
  """
  施設一覧を返すエンドポイント。
  将来的にはDBから取得する想定。
  """
  # TODO: 実際にはDBから取得する
  facilities = [
      FacilityOption(value="はちまんの風", label="はちまんの風"),
      FacilityOption(value="八幡デイ・サービスセンター", label="八幡デイ・サービスセンター"),
      FacilityOption(value="エクレール青葉", label="エクレール青葉"),
      FacilityOption(value="本部", label="本部"),
  ]
  return facilities
