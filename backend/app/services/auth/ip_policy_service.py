# app/services/auth/ip_policy_service.py

from typing import Optional, List
import ipaddress

from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.login_ip_policy import LoginIpPolicy
from app.crud import crud_login_ip_policy


def get_client_ip(request: Request) -> str:
    """
    クライアントIPを取得するヘルパー。

    将来、リバースプロキシ配下に置く場合も、ここだけを修正すればよい。
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # "client, proxy1, proxy2" の形式なので先頭要素を採用
        return xff.split(",")[0].strip()
    return request.client.host


def _is_ip_in_cidrs(ip: str, cidrs: List[str]) -> bool:
    """
    文字列 ip が、cidrs のいずれかのネットワークに含まれているか判定する。
    CIDR が壊れている場合はそのエントリは無視する。
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        # IP として解釈できない場合は拒否扱い
        return False

    for cidr in cidrs:
        try:
            net = ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            # 誤ったCIDRはスキップ
            continue

        if ip_obj in net:
            return True

    return False


def resolve_login_ip_policy(db: Session, user: User) -> Optional[LoginIpPolicy]:
    """
    ユーザーに適用すべき LoginIpPolicy を解決する。

      1. user.login_ip_policy_id があればそのポリシー
      2. なければ is_default=True のポリシー
      3. それもなければ None（IP制限スキップ）
    """
    # 1. ユーザーに直接紐付いたポリシー
    if getattr(user, "login_ip_policy_id", None):
        policy = db.get(LoginIpPolicy, user.login_ip_policy_id)
        if policy:
            return policy

    # 2. デフォルトポリシー
    stmt = select(LoginIpPolicy).where(LoginIpPolicy.is_default == True)  # noqa: E712
    policy = db.scalar(stmt)
    if policy:
        if policy.for_admin_only and not user.is_admin:
            # 管理者専用ポリシーが非管理者ユーザーに適用されることはない
            return None
        return policy

    # 3. 見つからなければ None
    return None


def is_ip_allowed_for_user(db: Session, user: User, client_ip: str) -> bool:
    """
    User + client_ip から、最終的に「このユーザーにとってこのIPを許可するか」を判定する。

    - ポリシーが存在しない場合は「現時点では許可」とする。
    - allowed_cidrs が空（[]）の場合も「制限なし」と解釈して許可する。
    """
    policy = resolve_login_ip_policy(db, user)

    if policy is None:
        # ポリシーが設定されていない場合、現時点では IP 制限なしとみなす
        return True

    cidrs = crud_login_ip_policy._decode_cidrs(policy.allowed_cidrs)

    if not cidrs:
        # 空リスト → 制限なし
        return True

    return _is_ip_in_cidrs(client_ip, cidrs)
