# app/api/v1/analysis.py
from fastapi import APIRouter

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/questions/{questionId}")
def get_question_analysis(questionId: str):
    """
    特定設問について、施設別・等級別などのスコア比較を返す。
    """
    # TODO: 実装
    pass

@router.get("/categories/{categoryId}")
def get_category_analysis(categoryId: str):
    """
    特定カテゴリについて、施設別・等級別などのスコア比較を返す。
    """
    # TODO: 実装
    pass

