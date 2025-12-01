# routers/password_reset.py
from fastapi import APIRouter, HTTPException, status

from app.schemas.password_reset import (
    PasswordResetRequest,
    PasswordResetResponse,
)

router = APIRouter(prefix="/password-reset", tags=["password-reset"])


@router.post("/request", response_model=PasswordResetResponse)
async def request_password_reset(
    payload: PasswordResetRequest,
) -> PasswordResetResponse:
    """
    パスワードリセット申請エンドポイント。
    実際にはここで

    - 社員コードと施設の組み合わせの妥当性チェック
    - 管理者・本部宛のメール送信 or DBに申請レコード作成

    などを行う想定。
    """

    # TODO: DB でユーザー存在確認（例）
    # user = await get_user_by_employee_code_and_facility(
    #     payload.employeeCode, payload.facility
    # )
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid employeeCode or facility",
    #     )

    # ここでは成功したものとして扱う
    return PasswordResetResponse(
        message="Password reset request has been received."
    )
