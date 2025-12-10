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


@router.get("/{assignmentId}")
def get_assignment(assignmentId: str):
    """
    特定の割り当て詳細を取得。
    """
    # TODO: 実装
    pass


@router.post("")
def create_assignment():
    """
    新しい割り当てを作成する。
    """
    # TODO: 実装
    pass


@router.patch("/{assignmentId}")
def update_assignment(assignmentId: str):
    """
    割り当ての編集（評価者変更・「実施しない」設定など）。
    """
    # TODO: 実装
    pass


@router.delete("/{assignmentId}")
def delete_assignment(assignmentId: str):
    """
    割り当ての削除。
    実務上はソフトデリートでもよい。
    """
    # TODO: 実装
    pass
