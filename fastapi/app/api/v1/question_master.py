# app/api/v1/question_master.py
from fastapi import APIRouter

router = APIRouter(prefix="/question-master", tags=["question-master"])

@router.get("")
def get_question_master():
    """
    質問マスターデータを取得。
    """
    # TODO: 実装
    pass

@router.post("")
def create_question():
    """
    質問を新規作成。
    """
    # TODO: 実装
    pass

@router.patch("/{questionId}")
def update_question(questionId: str):
    """
    質問を更新。
    """
    # TODO: 実装
    pass

@router.delete("/{questionId}")
def delete_question(questionId: str):
    """
    質問を削除。
    """
    # TODO: 実装
    pass