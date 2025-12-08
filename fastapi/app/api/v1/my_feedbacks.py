# app/api/v1/my_feedbacks.py
from fastapi import APIRouter

router = APIRouter(prefix="/my-feedbacks", tags=["my-feedbacks"])


@router.get("")
def list_my_feedbacks():
    """
    自分が被考課者の評価結果一覧を取得。
    """
    # TODO: 実装
    pass


@router.get("/{assignment_id}")
def get_my_feedback_detail(assignment_id: int):
    """
    自分の評価結果 + 面談票を取得。
    """
    # TODO: 実装
    pass


@router.put("/{assignment_id}/interview-sheet")
def update_my_interview_sheet(assignment_id: int):
    """
    被考課者本人が面談票を記入・更新する。
    """
    # TODO: 実装
    pass


@router.post("/{assignment_id}/acknowledge")
def acknowledge_my_feedback(assignment_id: int):
    """
    被考課者本人が「評価結果を確認しました」フラグを立てる。
    """
    # TODO: 実装
    pass
