# app/api/v1/notices.py
from fastapi import APIRouter

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("")
def list_notices():
    """
    お知らせ一覧を取得。
    """
    # TODO: 実装
    pass


@router.get("/{notice_id}")
def get_notice(notice_id: int):
    """
    お知らせ詳細を取得。
    """
    # TODO: 実装
    pass


@router.post("")
def create_notice():
    """
    お知らせを新規作成。
    """
    # TODO: 実装
    pass


@router.put("/{notice_id}")
def update_notice(notice_id: int):
    """
    お知らせを更新。
    """
    # TODO: 実装
    pass


@router.delete("/{notice_id}")
def delete_notice(notice_id: int):
    """
    お知らせを削除。
    """
    # TODO: 実装
    pass
