# app/crud/crud_login_ip_policy.py
import json
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.login_ip_policy import LoginIpPolicy
from app.schemas.login_ip_policy import (
    LoginIpPolicyCreate,
    LoginIpPolicyUpdate,
)


def _encode_cidrs(cidrs: List[str]) -> str:
    return json.dumps(cidrs, ensure_ascii=False)


def _decode_cidrs(raw: str) -> List[str]:
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x) for x in data]
        return []
    except Exception:
        return []


def get(db: Session, policy_id: int) -> Optional[LoginIpPolicy]:
    return db.get(LoginIpPolicy, policy_id)


def get_by_name(db: Session, name: str) -> Optional[LoginIpPolicy]:
    stmt = select(LoginIpPolicy).where(LoginIpPolicy.name == name)
    return db.scalar(stmt)


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
) -> tuple[int, List[LoginIpPolicy]]:
    stmt = select(LoginIpPolicy).offset(skip).limit(limit)
    items = db.scalars(stmt).all()

    total_stmt = select(func.count(LoginIpPolicy.id))
    total = db.scalar(total_stmt) or 0

    # allowed_cidrs の decode は schema 側でやるならここでは不要だが、
    # 今回は model の値を書き換えず、schema 側でそのまま扱うのでここでは何もしない。
    return total, items


def create(
    db: Session,
    *,
    obj_in: LoginIpPolicyCreate,
) -> LoginIpPolicy:
    # is_default を true にする場合、既存の default を解除する
    if obj_in.is_default:
        _unset_default(db)

    db_obj = LoginIpPolicy(
        name=obj_in.name,
        description=obj_in.description,
        allowed_cidrs=_encode_cidrs(obj_in.allowed_cidrs),
        is_default=obj_in.is_default,
        for_admin_only=obj_in.for_admin_only,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session,
    *,
    db_obj: LoginIpPolicy,
    obj_in: LoginIpPolicyUpdate,
) -> LoginIpPolicy:
    data = obj_in.dict(exclude_unset=True)

    if "name" in data:
        db_obj.name = data["name"]
    if "description" in data:
        db_obj.description = data["description"]
    if "allowed_cidrs" in data and data["allowed_cidrs"] is not None:
        db_obj.allowed_cidrs = _encode_cidrs(data["allowed_cidrs"])
    if "is_default" in data and data["is_default"] is not None:
        if data["is_default"]:
            _unset_default(db)
        db_obj.is_default = data["is_default"]
    if "for_admin_only" in data and data["for_admin_only"] is not None:
        db_obj.for_admin_only = data["for_admin_only"]

    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, db_obj: LoginIpPolicy) -> None:
    db.delete(db_obj)
    db.commit()


def _unset_default(db: Session) -> None:
    """既存のデフォルトポリシーを全て is_default = False にする"""
    stmt = select(LoginIpPolicy).where(LoginIpPolicy.is_default == True)  # noqa: E712
    defaults = db.scalars(stmt).all()
    for policy in defaults:
        policy.is_default = False
    if defaults:
        db.commit()
