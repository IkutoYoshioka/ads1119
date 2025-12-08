# app/api/v1/feedbacks.py
from fastapi import APIRouter

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])


@router.get("")
def list_feedbacks():
    """
    役員・施設長・考課者が閲覧可能な評価結果（assignment）の一覧。
    """
    # TODO: 実装
    pass


@router.get("/{assignment_id}")
def get_feedback_detail(assignment_id: int):
    """
    1人分の詳細結果 + 面談票を取得。
    """
    # TODO: 実装
    pass


@router.put("/{assignment_id}/interview-sheet")
def update_interview_sheet_by_interviewer(assignment_id: int):
    """
    面談担当者が面談票にコメントや面談日時を記入する。
    """
    # TODO: 実装
    pass
