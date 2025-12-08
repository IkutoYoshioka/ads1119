# app/api/v1/analysis.py
from fastapi import APIRouter

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/score-distribution")
def get_score_distribution():
    """
    条件（year, term, groupBy, category 等）に応じてスコア分布を返す。
    """
    # TODO: 実装
    pass


@router.get("/question/{question_id}")
def get_question_analysis(question_id: str):
    """
    特定設問について、施設別・等級別などのスコア比較を返す。
    """
    # TODO: 実装
    pass
