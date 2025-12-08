# app/api/v1/evaluation_forms.py
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation-form-templates", tags=["evaluation-form-templates"])


@router.get("")
def list_evaluation_form_templates():
    """
    評価フォームテンプレート一覧を取得。
    クエリ: category, grade, jobCode, year など。
    """
    # TODO: 実装
    pass


@router.get("/{form_id}")
def get_evaluation_form_template(form_id: int):
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


@router.put("/{form_id}")
def update_evaluation_form_template(form_id: int):
    """
    評価フォームテンプレートを更新。
    """
    # TODO: 実装
    pass


@router.delete("/{form_id}")
def delete_evaluation_form_template(form_id: int):
    """
    評価フォームテンプレートを削除（または無効化）。
    """
    # TODO: 実装
    pass


@router.get("/resolve")
def resolve_evaluation_form_template():
    """
    category × grade × jobCode × year 等から、
    適用すべき評価フォームテンプレートを解決する。
    """
    # TODO: 実装
    pass
