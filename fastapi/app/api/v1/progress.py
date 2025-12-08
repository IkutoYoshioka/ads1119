# app/api/v1/progress.py
from fastapi import APIRouter

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/overview")
def get_progress_overview():
    """
    全施設 × 各フェーズの完了状況を返す。
    """
    # TODO: 実装
    pass


@router.get("/facility/{facility_id}")
def get_facility_progress(facility_id: int):
    """
    特定施設における被考課者ごとの進捗一覧を返す。
    """
    # TODO: 実装
    pass
