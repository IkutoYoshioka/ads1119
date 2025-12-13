# app/services/auth/me_service.py
# employee の情報を含む /auth/me のレスポンスを構築するサービス

from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.crud_auth import crud_auth
from app.schemas.auth_me import MeResponse
from app.services.auth.mfa_service import user_has_mfa


class AuthMeService:
    def build_me_response(self, db: Session, user_id: int) -> MeResponse | None:
        user = crud_auth.get_user_with_profile(db, user_id=user_id)
        if not user:
            return None

        emp = user.employee
        grade = emp.grade if emp else None
        office = emp.office if emp else None
        site = office.site if office else None

        # --- 表示名 ---
        full_name = None
        if emp and emp.first_name and emp.last_name:
            full_name = f"{emp.last_name} {emp.first_name}"

        # --- grade由来の権限/表示フラグ（今回の追加） ---
        role_key = getattr(grade, "role_key", None) if grade else None
        role_key = role_key or "employee"

        can_evaluate_menu = bool(getattr(grade, "can_evaluate", False)) if grade else False
        default_participates = bool(getattr(grade, "default_participates", True)) if grade else True
        evaluated_as_grade_code = getattr(grade, "evaluated_as_grade_code", None) if grade else None

        # employees.participates_in_evaluation (nullable) がある前提
        # Noneなら grade.default_participates に従う
        participates_override = getattr(emp, "participates_in_evaluation", None) if emp else None
        participates_in_evaluation = (
            bool(participates_override)
            if participates_override is not None
            else bool(default_participates)
        )

        # --- MFA ---
        mfa_enabled = user_has_mfa(db, user)

        # --- 役員は is_admin 強制 ---
        is_admin = bool(user.is_admin)
        if role_key == "executive":
            is_admin = True

        return MeResponse(
            user_id=user.id,
            employee_id=emp.id if emp else None,
            # ⚠️ ここは user.employee_code を返すのが自然（emp.employee_code でも一致するがUser基準が安全）
            employee_code=user.employee_code if getattr(user, "employee_code", None) else (emp.employee_code if emp else None),

            first_name=emp.first_name if emp else None,
            last_name=emp.last_name if emp else None,
            full_name=full_name,

            grade_code=grade.code if grade else None,
            grade_name=grade.name if grade else None,
            grade_rank_order=grade.rank_order if grade else None,

            office_id=office.id if office else None,
            office_name=office.name if office else None,

            site_id=site.id if site else None,
            site_name=site.name if site else None,

            is_admin=is_admin,
            must_change_password=bool(user.must_change_password),
            mfa_enabled=bool(mfa_enabled),

            role_key=role_key,
            can_evaluate_menu=can_evaluate_menu,
            default_participates=default_participates,
            participates_in_evaluation=participates_in_evaluation,
            evaluated_as_grade_code=evaluated_as_grade_code,
        )


auth_me_service = AuthMeService()
