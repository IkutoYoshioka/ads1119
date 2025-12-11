# app/api/v1/login_ip_policies.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps.auth import get_current_admin_user  # get_db, get_current_admin_user など
from app.crud import crud_login_ip_policy
from app.models.employee import Employee
from app.models.login_ip_policy import LoginIpPolicy as LoginIpPolicyModel
from app.schemas.login_ip_policy import (
    LoginIpPolicy,
    LoginIpPolicyCreate,
    LoginIpPolicyUpdate,
    LoginIpPolicyList,
)

router = APIRouter(
    prefix="/login-ip-policies",
    tags=["login-ip-policies"],
)


def _decode_allowed_cidrs_for_response(policy: LoginIpPolicyModel) -> LoginIpPolicy:
    """
    DBモデルから Pydantic スキーマに変換する際に、
    allowed_cidrs を JSON文字列 → list[str] に変換する。
    """
    from app.crud import crud_login_ip_policy as crud

    data = {
        "id": policy.id,
        "name": policy.name,
        "description": policy.description,
        "allowed_cidrs": crud._decode_cidrs(policy.allowed_cidrs),
        "is_default": policy.is_default,
        "for_admin_only": policy.for_admin_only,
        "created_at": policy.created_at,
        "updated_at": policy.updated_at,
    }
    return LoginIpPolicy(**data)


@router.get(
    "",
    response_model=LoginIpPolicyList,
    summary="ログインIPポリシー一覧取得（管理者用）",
)
def list_login_ip_policies(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_admin_user),
) -> LoginIpPolicyList:
    total, items = crud_login_ip_policy.get_multi(db, skip=skip, limit=limit)
    return LoginIpPolicyList(
        total=total,
        items=[_decode_allowed_cidrs_for_response(p) for p in items],
    )


@router.get(
    "/{policy_id}",
    response_model=LoginIpPolicy,
    summary="ログインIPポリシー詳細取得（管理者用）",
)
def get_login_ip_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_admin_user),
) -> LoginIpPolicy:
    db_obj = crud_login_ip_policy.get(db, policy_id=policy_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Login IP policy not found",
        )
    return _decode_allowed_cidrs_for_response(db_obj)


@router.post(
    "",
    response_model=LoginIpPolicy,
    status_code=status.HTTP_201_CREATED,
    summary="ログインIPポリシー作成（管理者用）",
)
def create_login_ip_policy(
    policy_in: LoginIpPolicyCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_admin_user),
) -> LoginIpPolicy:
    # name の一意性チェック
    existing = crud_login_ip_policy.get_by_name(db, name=policy_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login IP policy with this name already exists",
        )

    db_obj = crud_login_ip_policy.create(db, obj_in=policy_in)
    return _decode_allowed_cidrs_for_response(db_obj)


@router.patch(
    "/{policy_id}",
    response_model=LoginIpPolicy,
    summary="ログインIPポリシー更新（管理者用）",
)
def update_login_ip_policy(
    policy_id: int,
    policy_in: LoginIpPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_admin_user),
) -> LoginIpPolicy:
    db_obj = crud_login_ip_policy.get(db, policy_id=policy_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Login IP policy not found",
        )

    # name を変更する場合、重複チェック
    if policy_in.name and policy_in.name != db_obj.name:
        existing = crud_login_ip_policy.get_by_name(db, name=policy_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login IP policy with this name already exists",
            )

    db_obj = crud_login_ip_policy.update(db, db_obj=db_obj, obj_in=policy_in)
    return _decode_allowed_cidrs_for_response(db_obj)


@router.delete(
    "/{policy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ログインIPポリシー削除（管理者用）",
)
def delete_login_ip_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_admin_user),
) -> None:
    db_obj = crud_login_ip_policy.get(db, policy_id=policy_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Login IP policy not found",
        )

    crud_login_ip_policy.remove(db, db_obj=db_obj)
    return
