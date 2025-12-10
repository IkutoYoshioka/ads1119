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


@router.get("/{noticeId}")
def get_notice(noticeId: str):
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


@router.patch("/{noticeId}")
def update_notice(noticeId: str):
    """
    お知らせを更新。
    """
    # TODO: 実装
    pass


@router.delete("/{noticeId}")
def delete_notice(noticeId: str):
    """
    お知らせを削除。
    """
    # TODO: 実装
    pass

@router.post("/{noticeId}/read")
def mark_notice_as_read(noticeId: str):
    """
    お知らせを既読にする。
    """
    # TODO: 実装
    pass

@router.get("/unread-count")
def get_unread_notice_count():
    """
    未読お知らせの件数を取得。
    """
    # TODO: 実装
    pass