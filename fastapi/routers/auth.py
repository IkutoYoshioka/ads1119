# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import Optional

from schemas.auth import LoginRequest, LoginResponse
from core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# ダミーのユーザー情報
class User:
    def __init__(self, employee_id: str, employee_code: str, password: str,
                 grade: str, is_admin: bool):
        self.employee_id = employee_id
        self.employee_code = employee_code
        self.password = password  # 実際はハッシュ化すべき
        self.grade = grade
        self.is_admin = is_admin

# 仮のユーザーデータベース
FAKE_USERS = [
    User("6061", "E11241", "password", "G02", False),  # 非考課者
    User("6033", "E98916", "password", "G06", False),  # 施設長
    User("6076", "E27338", "password", "X01", True),   # 役員（管理者）
    User("6048", "E94275", "password", "G04", False),  # 考課者
]

def authenticate_user(employee_code: str, password: str) -> Optional[User]:
    for u in FAKE_USERS:
        if u.employee_code == employee_code and u.password == password:
            return u
    return None

EVALUATOR_GRADES = {"X01", "G06", "G04", "G05", "T01"}

@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    response: Response,
) -> LoginResponse:
    user = authenticate_user(payload.employeeCode, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employeeCode or password",
        )

    # JWT に必要な情報を詰める（最低限 employee_id と grade）
    access_token = create_access_token(
        {
            "sub": user.employee_id,
            "grade": user.grade,
            "is_admin": user.is_admin,
        }
    )

    # HttpOnly Cookie にトークンを保存（JSから直接触れさせない運用）
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,      # 本番は True 推奨（HTTPS前提）
        samesite="lax",   # 必要に応じて調整
        path="/",
        max_age=60 * 60 * 8,
    )

    # 管理者ログイン／通常ログインの区別をつけたい場合
    login_type = "admin" if user.is_admin else "user"
    response.set_cookie(
        key="loginType",
        value=login_type,
        httponly=False,   # フロントから見たいなら False でもよい
        path="/",
        max_age=60 * 60 * 8,
    )

    # 等級に応じて遷移先を決定（ここをバックエンドでやる）
    if user.grade in EVALUATOR_GRADES:
        redirect_path = "/eval"
    else:
        redirect_path = "/non_eval"

    return LoginResponse(
        employeeId=user.employee_id,
        grade=user.grade,
        isAdmin=user.is_admin,
        redirectPath=redirect_path,
    )
