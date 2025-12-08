# app/api/v1/facility_results.py
from fastapi import APIRouter

router = APIRouter(prefix="/facility-results", tags=["facility-results"])


@router.get("/summary")
def get_facility_results_summary():
    """
    施設別サマリー一覧（件数・平均スコアなど）を取得。
    """
    # TODO: 実装
    pass


@router.get("/{facility_id}")
def get_facility_result_detail(facility_id: int):
    """
    特定施設の詳細集計（カテゴリ別・等級別など）を取得。
    """
    # TODO: 実装
    pass
