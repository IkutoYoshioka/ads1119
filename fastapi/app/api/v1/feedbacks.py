# app/api/v1/feedbacks.py
from fastapi import APIRouter

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])


@router.get("")
def list_feedbacks():
    """
    面談票一覧を取得。
    """
    # TODO: 実装
    pass


@router.get("/{feedbackId}")
def get_feedback(feedbackId: str):
    """
    面談票詳細を取得。
    """
    # TODO: 実装
    pass

@router.patch("/{feedbackId}/self-sheet")
def update_self_sheet(feedbackId: str):
    """
    面談票の自己評価シートを更新。
    """
    # TODO: 実装
    pass

@router.patch("/{feedbackId}/manager-comment")
def update_manager_comment(feedbackId: str):
    """
    面談者がコメントを更新。
    """
    # TODO: 実装
    pass

@router.patch("/{feedbackId}/acknowledge")
def acknowledge_feedback(feedbackId: int):
    """
    被考課者が内容を確認しましたフラグを立てる。
    """
    # TODO: 実装
    pass