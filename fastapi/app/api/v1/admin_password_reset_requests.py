# app/api/v1/admin_password_reset_requests.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/admin/password-reset-requests",
    tags=["admin-password-reset-requests"],
)


@router.get("")
def list_password_reset_requests():
    """
    本部用: パスワードリセット申請一覧を取得。
    クエリで status=pending 等をフィルタ。
    admin-password-reset-requests のエンドポイントにadminが付いているのは管理者以外アクセス禁止を明記するため。
    """
    # TODO: 実装
    pass


@router.get("/{request_id}")
def get_password_reset_request(request_id: int):
    """
    本部用: 特定のパスワードリセット申請の詳細を取得。
    """
    # TODO: 実装
    pass


@router.post("/{request_id}/complete")
def complete_password_reset_request(request_id: int):
    """
    本部用: パスワードリセット申請を処理済みにする。
    （必要に応じて新パスワードの設定も行う）
    """
    # TODO: 実装
    pass
