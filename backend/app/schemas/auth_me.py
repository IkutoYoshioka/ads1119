# app/schemas/auth_me.py
# employee の情報を含む /auth/me のレスポンススキーマ
from typing import Optional
from app.schemas.base import CamelModel

class MeResponse(CamelModel):
    user_id: int
    employee_id: Optional[int] = None
    employee_code: Optional[str] = None

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None

    grade_code: Optional[str] = None
    grade_name: Optional[str] = None
    grade_rank_order: Optional[int] = None

    office_id: Optional[int] = None
    office_name: Optional[str] = None

    site_id: Optional[int] = None
    site_name: Optional[str] = None

    is_admin: bool
    must_change_password: bool
    mfa_enabled: bool

    role_key: str
    can_evaluate_menu: bool
    default_participates: bool
    participates_in_evaluation: bool
    evaluated_as_grade_code: Optional[str] = None