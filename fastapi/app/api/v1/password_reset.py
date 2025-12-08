# app/api/v1/password_reset.py
from fastapi import APIRouter

router = APIRouter(prefix="/password-reset", tags=["password-reset"])


@router.post("/request")
def request_password_reset():
    """
    「パスワードを忘れた方へ」から、本部にパスワードリセット申請を送信する。
    社員コード・施設などを受け取って記録する。
    """
    # TODO: 実装
    pass


@router.post("/confirm")
def confirm_password_reset():
    """
    本部側で発行したリセットトークンを用いて、
    新しいパスワードを設定する処理。
    （運用によっては使わない可能性もある）
    """
    # TODO: 実装
    pass
