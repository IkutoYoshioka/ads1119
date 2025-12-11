# app/api/v1/employees.py
from fastapi import APIRouter

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("")
def list_employees():
    """
    従業員一覧の取得。
    クエリで facilityId, grade, search などでフィルタ。

    """
    # TODO: 実装
    pass


@router.get("/{employeeId}")
def get_employee(employeeId: str):
    """
    特定の従業員情報を取得。
    """
    # TODO: 実装
    pass


@router.post("")
def create_employee():
    """
    従業員を新規登録する。
    -admin のみ許可（require_admin）
    """
    # TODO: 実装
    pass


@router.patch("/{employeeId}")
def update_employee(employeeId: str):
    """
    従業員情報を更新する。
    -admin のみ許可（require_admin）
    """
    # TODO: 実装
    pass


@router.delete("/{employeeId}")
def delete_employee(employeeId: str):
    """
    従業員を削除（または無効化）する。
    -admin のみ許可（require_admin）
    """
    # TODO: 実装
    pass
