# app/api/v1/evaluation_forms.py
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation-forms", tags=["evaluation-forms"])


@router.get("")
def list_evaluation_form_templates():
    """
    評価フォームテンプレート一覧を取得。
    クエリ: period, grade など。
    """
    # TODO: 実装
    pass


@router.get("/{formId}")
def get_evaluation_form_template(formId: str):
    """
    評価フォームテンプレート詳細を取得。
    セクション・設問構成を含む。
    """
    # TODO: 実装
    pass


@router.post("")
def create_evaluation_form_template():
    """
    評価フォームテンプレートを新規作成。
    """
    # TODO: 実装
    pass


@router.patch("/{formId}")
def update_evaluation_form_template(formId: str):
    """
    評価フォームテンプレートを更新。
    """
    # TODO: 実装
    pass


@router.delete("/{formId}")
def delete_evaluation_form_template(formId: str):
    """
    評価フォームテンプレートを削除（または無効化）。
    """
    # TODO: 実装
    pass

