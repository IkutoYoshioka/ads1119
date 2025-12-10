# app/api/v1/auth.py
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, LoginResponse
from app.db.session import get_db
from app.crud.crud_user import crud_user  # あなたのCRUD層に合わせて

router = APIRouter(prefix="/auth", tags=["auth"])

# 考課者系のグレード（役員・施設長・考課者など）
EVALUATOR_GRADES = {"X01", "G06", "G04", "G05", "T01"}


def get_redirect_path(grade: str, is_admin: bool) -> str:
    """
    ログイン直後にどこへ飛ばすかを決める。
    基本方針：
      - 全ユーザとも /dashboard に行く
      - 「どの機能が見えるか」はフロントのサイドバーで制御
    """
    # 将来、管理者だけ別ページに飛ばしたくなったらここで分岐すればOK
    return "/dashboard"


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    ログイン処理:
      1. employeeCode からユーザをDB検索
      2. パスワードハッシュを検証
      3. JWTを発行し、HttpOnly Cookie に保存
      4. フロント用に employeeId / grade / isAdmin / redirectPath を返却
    """

    # 1. ユーザ取得（employee_code で一意）
    user = crud_user.get_by_employee_code(db, employee_code=payload.employeeCode)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employeeCode or password",
        )

    # 2. パスワード検証（平文 vs ハッシュ）
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employeeCode or password",
        )

    # 3. JWT 作成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.employee_id,  # ← JWTのsubjectとしてemployee_idを使う
            "grade": user.grade,
            "is_admin": user.is_admin,
        },
        expires_delta=access_token_expires,
    )

    # 4. HttpOnly Cookie に保存（JSからは直接読めない）
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,       # 本番は HTTPS 前提なので True 推奨
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    # 補助的な Cookie（フロントから見たい場合）
    login_type = "admin" if user.is_admin else "user"
    response.set_cookie(
        key="loginType",
        value=login_type,
        httponly=False,   # フロントから読める
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    redirect_path = get_redirect_path(user.grade, user.is_admin)

    return LoginResponse(
        employeeId=user.employee_id,
        grade=user.grade,
        isAdmin=user.is_admin,
        redirectPath=redirect_path,
    )

@router.post("/mfa/setup-init")
def setup_mfa_init():
    """
    多要素認証セットアップ初期化処理。
    フロント/account/mfaページから呼ばれる。
    """
    # TODO: 実装
    pass

@router.post("/mfa/setup-verify")
def setup_mfa_verify():
    """
    多要素認証セットアップ検証処理。
    フロント/account/mfaページから呼ばれる。
    """
    # TODO: 実装
    pass

@router.post("/mfa/verify-login")
def verify_mfa_login():
    """
    多要素認証ログイン検証処理。
    ログイン直後、多要素認証が有効な場合に呼ばれる。
    """
    # TODO: 実装
    pass


@router.post("/logout")
def logout(response: Response):
    """
    ログアウト:
      - access_token, loginType の Cookie を削除
    """
    # access_token を削除
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax",
        secure=False,   # ← login 時と合わせる（本番は True）
    )
    # loginType も削除
    response.delete_cookie(
        key="loginType",
        path="/",
        samesite="lax",
        secure=False,
    )

    return {"detail": "Logged out"}



@router.get("/me")
def get_me():
    """
    現在ログイン中のユーザー情報を返す。
    （実装時は Depends(get_current_user) などを利用）
    """
    # TODO: 実装
    pass


@router.post("/change-password")
def change_password():
    """
    パスワード変更処理。
    """
    # TODO: 実装
    pass
