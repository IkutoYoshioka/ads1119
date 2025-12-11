# app/api/v1/sites.py
from fastapi import APIRouter

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("")
def list_sites():
    """
    施設一覧の取得。
    """
    # TODO: 実装
    pass


@router.get("/{siteId}")
def get_site(siteId: int):
    """
    特定の施設情報を取得。
    """
    # TODO: 実装
    pass


@router.post("")
def create_site():
    """
    施設を新規登録する。
    管理者
    """
    # TODO: 実装
    pass


@router.patch("/{siteId}")
def update_site(siteId: int):
    """
    施設情報を更新する。
    管理者
    """
    # TODO: 実装
    pass


@router.delete("/{siteId}")
def delete_site(siteId: int):
    """
    施設を削除（または無効化）する。
    管理者
    """
    # TODO: 実装
    pass
