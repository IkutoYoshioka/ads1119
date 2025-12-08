# app/api/v1/login_ip_policies.py

from fastapi import APIRouter

router = APIRouter(prefix="/admin/login-ip-policies", tags=["login-ip-policies"])

@router.get("")
def list_login_ip_policies():
    """
    本部用: ログイン許可IPポリシー一覧を取得。
    """
    # TODO: 実装
    pass

@router.post("")
def create_login_ip_policy():
    """
    本部用: ログイン許可IPポリシーを新規作成。
    """
    # TODO: 実装
    pass

@router.put("/{policy_id}")
def update_login_ip_policy(policy_id: int):
    """
    本部用: ログイン許可IPポリシーを更新。
    """
    # TODO: 実装
    pass

@router.delete("/{policy_id}")
def delete_login_ip_policy(policy_id: int):
    """
    本部用: ログイン許可IPポリシーを削除。
    """
    # TODO: 実装
    pass