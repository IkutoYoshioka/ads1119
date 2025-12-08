# app/api/v1/assignments.py
from fastapi import APIRouter

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("")
def list_assignments():
    """
    割り当て一覧の取得。
    クエリ: facilityId, year, term など。
    """
    # TODO: 実装
    pass


@router.get("/{assignment_id}")
def get_assignment(assignment_id: int):
    """
    特定の割り当て詳細を取得。
    （必要に応じて使用）
    """
    # TODO: 実装
    pass


@router.post("")
def create_assignment():
    """
    新しい割り当て（被考課者 + カテゴリ別評価者）を作成する。
    """
    # TODO: 実装
    pass


@router.put("/{assignment_id}")
def update_assignment(assignment_id: int):
    """
    割り当ての編集（評価者変更・「実施しない」設定など）。
    """
    # TODO: 実装
    pass


@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int):
    """
    割り当ての削除。
    実務上はソフトデリートでもよい。
    """
    # TODO: 実装
    pass


@router.get("/{assignment_id}/summary")
def get_assignment_summary(assignment_id: int):
    """
    （オプション）被考課者単位で一次・二次・最終などの状況をまとめて返す。
    """
    # TODO: 実装
    pass
