# app/api/v1/evaluation_results.py
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation-results", tags=["evaluation-results"])

@router.get("")
def get_evaluation_results():
    """
    評価結果一覧を取得。
    """
    # TODO: 実装
    pass

@router.get("/{resultId}")
def get_evaluation_result(resultId: str):
    """
    指定された評価結果IDに紐づく評価結果詳細を取得。
    """
    # TODO: 実装
    pass

@router.patch("/{resultId}")
def update_evaluation_result(resultId: str):
    """
    評価結果の更新。
    """
    # TODO: 実装
    pass

@router.post("/{resultId}/submit")
def submit_evaluation_result(resultId: str):
    """
    評価結果の提出。
    """
    # TODO: 実装
    pass