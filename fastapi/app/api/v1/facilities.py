# app/api/v1/facilities.py
from fastapi import APIRouter

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.get("")
def list_facilities():
    """
    施設一覧の取得。
    """
    # TODO: 実装
    pass


@router.get("/{facility_id}")
def get_facility(facility_id: int):
    """
    特定の施設情報を取得。
    """
    # TODO: 実装
    pass


@router.post("")
def create_facility():
    """
    施設を新規登録する。
    """
    # TODO: 実装
    pass


@router.put("/{facility_id}")
def update_facility(facility_id: int):
    """
    施設情報を更新する。
    """
    # TODO: 実装
    pass


@router.delete("/{facility_id}")
def delete_facility(facility_id: int):
    """
    施設を削除（または無効化）する。
    """
    # TODO: 実装
    pass
