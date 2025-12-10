# app/api/v1/password_reset.py
from fastapi import APIRouter

router = APIRouter(prefix="/password-reset-requests", tags=["password-reset-requests"])


@router.post("")
def request_password_reset():
    """
    「パスワードを忘れた方へ」から、本部にパスワードリセット申請を送信する。
    社員コード・施設などを受け取って記録する。
    """
    # TODO: 実装
    pass


