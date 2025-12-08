# app/api/v1/question_master.py
from fastapi import APIRouter

router = APIRouter(prefix="/question-master", tags=["question-master"])


# Section マスタ
@router.get("/sections")
def list_question_sections():
    """
    設問セクションマスタ一覧を取得。
    クエリで category, grade, jobCode などをフィルタ。
    """
    # TODO: 実装
    pass


@router.get("/sections/{section_id}")
def get_question_section(section_id: int):
    """
    設問セクションマスタ詳細を取得。
    """
    # TODO: 実装
    pass


@router.post("/sections")
def create_question_section():
    """
    設問セクションマスタを新規作成。
    """
    # TODO: 実装
    pass


@router.put("/sections/{section_id}")
def update_question_section(section_id: int):
    """
    設問セクションマスタを更新。
    """
    # TODO: 実装
    pass


@router.delete("/sections/{section_id}")
def delete_question_section(section_id: int):
    """
    設問セクションマスタを削除（または無効化）。
    """
    # TODO: 実装
    pass


# Question マスタ
@router.get("/questions")
def list_question_master():
    """
    設問マスタ一覧を取得。
    クエリで sectionId, grade, jobCode などをフィルタ。
    """
    # TODO: 実装
    pass


@router.get("/questions/{question_id}")
def get_question_master(question_id: int):
    """
    設問マスタ詳細を取得。
    """
    # TODO: 実装
    pass


@router.post("/questions")
def create_question_master():
    """
    設問マスタを新規作成。
    """
    # TODO: 実装
    pass


@router.put("/questions/{question_id}")
def update_question_master(question_id: int):
    """
    設問マスタを更新。
    """
    # TODO: 実装
    pass


@router.delete("/questions/{question_id}")
def delete_question_master(question_id: int):
    """
    設問マスタを削除（または無効化）。
    """
    # TODO: 実装
    pass
