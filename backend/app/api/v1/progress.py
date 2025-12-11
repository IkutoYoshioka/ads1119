# app/api/v1/progress.py
from fastapi import APIRouter

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/overview")
def get_progress_overview(periodId: str):
    """
    全施設 × 各フェーズの完了状況を返す。
    """
    # TODO: 実装
    pass


@router.get("/facility")
def get_facility_progress(periodId: str):
    """
    特定施設における被考課者ごとの進捗一覧を返す。
    """
    # TODO: 実装
    pass

@router.get("/my")
def get_my_progress(periodId: str):
    """
    自分の進捗状況を返す。
    """
    # TODO: 実装
    pass

@router.get("/self-evaluation")
def get_self_evaluation_progress(periodId: str):
    """
    被考課者自身の評価進捗。
    """
    # TODO: 実装
    pass