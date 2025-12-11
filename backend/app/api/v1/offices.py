# app/api/v1/offices.py
from fastapi import APIRouter

router = APIRouter(prefix="/offices", tags=["offices"])

@router.get("")
def list_offices():
    """
    施設一覧の取得。
    """
    # TODO: 実装
    pass


@router.get("/{officeId}")
def get_office(officeId: int):
    """
    特定の施設情報を取得。
    """
    # TODO: 実装
    pass


@router.post("")
def create_office():
    """
    施設を新規登録する。
    管理者
    """
    # TODO: 実装
    pass


@router.patch("/{officeId}")
def update_office(officeId: int):
    """
    施設情報を更新する。
    管理者
    """
    # TODO: 実装
    pass


@router.delete("/{officeId}")
def delete_office(officeId: int):
    """
    施設を削除（または無効化）する。
    管理者
    """
    # TODO: 実装
    pass
