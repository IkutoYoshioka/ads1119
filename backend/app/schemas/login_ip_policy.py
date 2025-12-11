# app/schemas/login_ip_policy.py
from typing import List, Optional
from datetime import datetime

from pydantic import Field
from app.schemas.base import CamelModel


class LoginIpPolicyBase(CamelModel):
    name: str = Field(..., max_length=100, description="ポリシー名")
    description: Optional[str] = Field(None, description="説明")
    allowed_cidrs: List[str] = Field(
        ...,
        description="許可するIPアドレス範囲（CIDR表記）のリスト",
        example=["192.168.0.0/16", "10.0.0.0/8"],
    )
    is_default: bool = Field(False, description="デフォルトポリシーかどうか")
    for_admin_only: bool = Field(
        False, description="管理者ユーザー専用ポリシーかどうか"
    )


class LoginIpPolicyCreate(LoginIpPolicyBase):
    pass


class LoginIpPolicyUpdate(CamelModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    allowed_cidrs: Optional[List[str]] = None
    is_default: Optional[bool] = None
    for_admin_only: Optional[bool] = None


class LoginIpPolicyInDBBase(LoginIpPolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LoginIpPolicy(LoginIpPolicyInDBBase):
    """レスポンス用スキーマ"""
    pass


class LoginIpPolicyList(CamelModel):
    total: int
    items: list[LoginIpPolicy]
