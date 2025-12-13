from sqlalchemy.orm import Session

from app.crud.crud_user import crud_user
from app.crud.password_reset_request import create_admin_password_reset_request

def submit_password_reset_request(
    db: Session,
    *,
    employee_code: str,
    office_id: int,
) -> bool:
    """
    申請を「受理」したかどうかの内部結果を返す（APIレスポンスには出さない）。
    - 推測防止のため、外部レスポンスは常に accepted を返す想定。
    - 既存テーブル制約により、対象ユーザーが特定できない場合はDBに作れない。
    """

    user = crud_user.get_by_employee_code(db, employee_code=employee_code)
    if not user:
        return False

    # inactive ユーザーの扱い：
    # ここを False にするか True にするかは運用次第。
    # 推測防止を強めるなら “inactiveでもDBに作る” より “inactiveは作らない” でも
    # 外部レスポンスは同じなので情報漏洩は起きにくい。
    if not user.is_active:
        return False

    # ユーザーが employee に紐づいている前提（管理者専用アカウント等は None あり得る）
    if not user.employee:
        return False

    if user.employee.office_id != office_id:
        return False

    # 申請作成
    create_admin_password_reset_request(
        db,
        target_user_id=user.id,
        requested_by_user_id=None,  # ログイン前申請なので None
        reason="Forgot password request",
    )
    return True
