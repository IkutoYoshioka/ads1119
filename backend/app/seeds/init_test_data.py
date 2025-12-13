# app/seeds/init_test_data.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import pyotp

from app.db.session import SessionLocal
from app.core.security import get_password_hash

from app.models.site import Site
from app.models.office import Office
from app.models.grade import Grade
from app.models.employee import Employee
from app.models.user import User
from app.models.login_ip_policy import LoginIpPolicy
from app.models.user_mfa import UserMfa
from app.models.password_reset_token import PasswordResetToken
from app.models.admin_password_reset_request import AdminPasswordResetRequest


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ---------- get_or_create masters ----------

def get_or_create_site(db, site_code: str, name: str) -> Site:
    site = db.query(Site).filter(Site.site_code == site_code).first()
    if site:
        # 再実行耐性（名前変更など）
        if site.name != name:
            site.name = name
            site.updated_at = now_utc()
            db.add(site)
        return site

    site = Site(site_code=site_code, name=name, created_at=now_utc(), updated_at=now_utc())
    db.add(site)
    db.flush()
    return site


def get_or_create_office(db, office_code: str, name: str, site: Site) -> Office:
    office = db.query(Office).filter(Office.office_code == office_code).first()
    if office:
        changed = False
        if office.name != name:
            office.name = name
            changed = True
        if office.site_id != site.id:
            office.site_id = site.id
            changed = True
        if changed:
            office.updated_at = now_utc()
            db.add(office)
        return office

    office = Office(
        office_code=office_code,
        name=name,
        site_id=site.id,
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    db.add(office)
    db.flush()
    return office


def get_or_create_grade(db, code: str, name: str, rank_order: int, *, role_key: str = "employee", can_evaluate: bool = False, default_participates: bool = True, evaluated_as_grade_code: str | None = None) -> Grade:
    grade = db.query(Grade).filter(Grade.code == code).first()
    if grade:
        changed = False
        if grade.name != name:
            grade.name = name
            changed = True
        if grade.rank_order != rank_order:
            grade.rank_order = rank_order
            changed = True

        if getattr(grade, "role_key", None) != role_key:
            grade.role_key = role_key; changed = True
        if getattr(grade, "can_evaluate", None) != can_evaluate:
            grade.can_evaluate = can_evaluate; changed = True
        if getattr(grade, "default_participates", None) != default_participates:
            grade.default_participates = default_participates; changed = True
        if getattr(grade, "evaluated_as_grade_code", None) != evaluated_as_grade_code:
            grade.evaluated_as_grade_code = evaluated_as_grade_code; changed = True


        if changed:
            db.add(grade)
        return grade

    grade = Grade(code=code, name=name, rank_order=rank_order, is_active=True, role_key=role_key, can_evaluate=can_evaluate, default_participates=default_participates, evaluated_as_grade_code=evaluated_as_grade_code)
    db.add(grade)
    db.flush()
    return grade


def get_or_create_login_ip_policy(
    db,
    name: str,
    allowed_cidrs: list[str],
    is_default: bool = False,
    for_admin_only: bool = False,
) -> LoginIpPolicy:
    policy = db.query(LoginIpPolicy).filter(LoginIpPolicy.name == name).first()
    allowed_cidrs_json = json.dumps(allowed_cidrs)

    if policy:
        # 再実行耐性（設定変更がすぐ反映される）
        changed = False
        if policy.allowed_cidrs != allowed_cidrs_json:
            policy.allowed_cidrs = allowed_cidrs_json
            changed = True
        if bool(policy.is_default) != bool(is_default):
            policy.is_default = is_default
            changed = True
        if bool(policy.for_admin_only) != bool(for_admin_only):
            policy.for_admin_only = for_admin_only
            changed = True

        if changed:
            policy.updated_at = now_utc()
            db.add(policy)
        return policy

    policy = LoginIpPolicy(
        name=name,
        description=f"Test policy: {name}",
        allowed_cidrs=allowed_cidrs_json,
        is_default=is_default,
        for_admin_only=for_admin_only,
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    db.add(policy)
    db.flush()
    return policy


# ---------- MFA helper ----------

def upsert_user_mfa(
    db,
    user: User,
    *,
    enabled: bool,
    confirmed: bool,
    secret: str | None = None,
) -> UserMfa:
    """
    1ユーザー1レコードを維持しつつ、状態（enabled/confirmed）を作り分けられるようにする。
    - secret を指定しなければ、既存があれば維持、無ければ新規生成
    """
    mfa = db.query(UserMfa).filter(UserMfa.user_id == user.id).first()
    if mfa:
        # secret は基本維持（勝手に回すとAuthenticator側とズレる）
        if secret is not None and mfa.secret != secret:
            mfa.secret = secret

        changed = False
        if bool(mfa.is_enabled) != bool(enabled):
            mfa.is_enabled = enabled
            changed = True
        if bool(mfa.is_confirmed) != bool(confirmed):
            mfa.is_confirmed = confirmed
            changed = True
        if changed:
            mfa.updated_at = now_utc()
            db.add(mfa)
        return mfa

    mfa_secret = secret or pyotp.random_base32()
    mfa = UserMfa(
        user_id=user.id,
        secret=mfa_secret,
        is_enabled=enabled,
        is_confirmed=confirmed,
        last_verified_at=None,
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    db.add(mfa)
    db.flush()
    print(f"[MFA] user={user.employee_code}, secret={mfa_secret}, enabled={enabled}, confirmed={confirmed}")
    return mfa


# ---------- Employee + User upsert ----------

GRADE_MASTER = {
    "A01": ("アルバイト・パート", 0, "employee", False, False, None),
    "G01": ("1等級", 1, "employee", False, True, None),
    "G02": ("2等級", 2, "employee", False, True, None),
    "G03": ("3等級", 3, "employee", False, True, None),
    "G04": ("4等級", 4, "employee", True, True, None),
    "S04": ("4等級スペシャリスト", 4, "employee", False, True, "G04"),
    "G05": ("5等級", 5, "employee", True, True, None),
    "S05": ("5等級スペシャリスト", 5, "employee", False, True, "G05"),
    "G06": ("6等級（施設長）", 6, "site_head", True, True, None),
    "EXEC": ("役員", 99, "executive", True, True, None),
}

@dataclass(frozen=True)
class SeedUserSpec:
    employee_code: str
    first_name: str
    last_name: str
    grade_code: str
    password: str
    is_admin: bool
    must_change_password: bool
    is_active: bool
    login_ip_policy: LoginIpPolicy | None
    # MFA state
    mfa_mode: str  # "none" | "enabled" | "pending"


def upsert_employee_and_user(
    db,
    spec: SeedUserSpec,
    office: Office,
) -> tuple[Employee, User]:
    if spec.grade_code not in GRADE_MASTER:
        raise ValueError(f"Unknown grade_code: {spec.grade_code}")

    grade_name, rank_order, role_key, can_evaluate, default_participates, evaluated_as_grade_code = GRADE_MASTER[spec.grade_code]
    grade = get_or_create_grade(db, code=spec.grade_code, name=grade_name, rank_order=rank_order, role_key=role_key, can_evaluate=can_evaluate, default_participates=default_participates, evaluated_as_grade_code=evaluated_as_grade_code)

    # Employee
    employee = db.query(Employee).filter(Employee.employee_code == spec.employee_code).first()
    if not employee:
        employee = Employee(
            employee_code=spec.employee_code,
            first_name=spec.first_name,
            last_name=spec.last_name,
            grade_id=grade.id,
            office_id=office.id,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        db.add(employee)
        db.flush()
    else:
        changed = False
        if employee.first_name != spec.first_name:
            employee.first_name = spec.first_name; changed = True
        if employee.last_name != spec.last_name:
            employee.last_name = spec.last_name; changed = True
        if employee.grade_id != grade.id:
            employee.grade_id = grade.id; changed = True
        if employee.office_id != office.id:
            employee.office_id = office.id; changed = True
        if changed:
            employee.updated_at = now_utc()
            db.add(employee)
            db.flush()

    # User
    user = db.query(User).filter(User.employee_code == spec.employee_code).first()
    if not user:
        user = User(
            employee_code=spec.employee_code,
            employee_id=employee.id,
            hashed_password=get_password_hash(spec.password),
            is_active=spec.is_active,
            is_admin=spec.is_admin,
            must_change_password=spec.must_change_password,
            login_ip_policy_id=spec.login_ip_policy.id if spec.login_ip_policy else None,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        db.add(user)
        db.flush()
        print(f"[USER] Created {spec.employee_code} admin={spec.is_admin} mfa={spec.mfa_mode}")
    else:
        # 再実行耐性：テスト条件変更を即反映
        changed = False
        if user.is_active != spec.is_active:
            user.is_active = spec.is_active; changed = True
        if user.is_admin != spec.is_admin:
            user.is_admin = spec.is_admin; changed = True
        if user.must_change_password != spec.must_change_password:
            user.must_change_password = spec.must_change_password; changed = True
        policy_id = spec.login_ip_policy.id if spec.login_ip_policy else None
        if getattr(user, "login_ip_policy_id", None) != policy_id:
            user.login_ip_policy_id = policy_id; changed = True

        # パスワードはテスト用に上書きしておく方が便利
        user.hashed_password = get_password_hash(spec.password)
        changed = True

        if changed:
            user.updated_at = now_utc()
            db.add(user)
            db.flush()
        print(f"[USER] Updated {spec.employee_code} admin={spec.is_admin} mfa={spec.mfa_mode}")

    # MFA
    if spec.mfa_mode == "none":
        pass
    elif spec.mfa_mode == "enabled":
        upsert_user_mfa(db, user, enabled=True, confirmed=True)
    elif spec.mfa_mode == "pending":
        upsert_user_mfa(db, user, enabled=False, confirmed=False)
    else:
        raise ValueError(f"Unknown mfa_mode: {spec.mfa_mode}")

    db.commit()
    return employee, user


# ---------- Entry point ----------

def init_test_data() -> None:
    db = SessionLocal()
    try:
        # Site / Office
        main_site = get_or_create_site(db, site_code="S01", name="テスト本部")
        main_office = get_or_create_office(db, office_code="O01", name="テスト事業所A", site=main_site)

        # Policies
        default_policy = get_or_create_login_ip_policy(
            db,
            name="default-internal",
            allowed_cidrs=["127.0.0.1/32"],
            is_default=True,
            for_admin_only=False,
        )
        admin_anywhere_policy = get_or_create_login_ip_policy(
            db,
            name="admin-anywhere",
            allowed_cidrs=["0.0.0.0/0"],
            is_default=False,
            for_admin_only=True,
        )
        restricted_policy = get_or_create_login_ip_policy(
            db,
            name="restricted-only-private",
            allowed_cidrs=["10.0.0.0/8"],
            is_default=False,
            for_admin_only=False,
        )

        # Users (patterns)
        specs: list[SeedUserSpec] = [
            # A: normal login
            SeedUserSpec("USER-INTERNAL", "User", "Internal", "G02", "password123", False, False, True, default_policy, "none"),
            SeedUserSpec("ADMIN-INTERNAL", "Admin", "Internal", "G06", "password123", True, False, True, default_policy, "none"),

            # B: ip deny -> 403
            SeedUserSpec("USER-IP-DENY", "User", "IpDeny", "G05", "password123", False, False, True, restricted_policy, "none"),

            # C: ip deny -> mfa challenge
            SeedUserSpec("EXEC-MFA-ENABLED", "Exec", "MfaEnabled", "EXEC", "password123", True, False, True, restricted_policy, "enabled"),
            SeedUserSpec("G06-MFA-ENABLED", "Manager", "MfaEnabled", "G06", "password123", True, False, True, restricted_policy, "enabled"),

            # D: privileged but mfa not enabled
            SeedUserSpec("EXEC-MFA-NOT-ENABLED", "Exec", "NoMfa", "EXEC", "password123", True, False, True, restricted_policy, "none"),
            SeedUserSpec("G06-MFA-PENDING", "Manager", "MfaPending", "G06", "password123", True, False, True, restricted_policy, "pending"),

            # E: must change password
            SeedUserSpec("USER-MUST-CHANGE-PW", "User", "MustChange", "G02", "password123", False, True, True, default_policy, "none"),

            # F: inactive user
            SeedUserSpec("USER-INACTIVE", "User", "Inactive", "G02", "password123", False, False, False, default_policy, "none"),

            # Admin anywhere (IP allow even from outside)
            SeedUserSpec("EXEC-ANYWHERE", "Exec", "Anywhere", "EXEC", "password123", True, False, True, admin_anywhere_policy, "enabled"),
        ]

        for spec in specs:
            upsert_employee_and_user(db, spec, main_office)

        print("=== Test data initialization finished. ===")

    finally:
        db.close()


if __name__ == "__main__":
    init_test_data()
