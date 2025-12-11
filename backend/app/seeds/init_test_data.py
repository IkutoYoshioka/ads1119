# app/seeds/init_test_data.py

from datetime import datetime
import json

import pyotp  # MFA用。不要なら削除して固定secretにしてもOK

from app.db.session import SessionLocal
from app.core.security import get_password_hash

from app.models.site import Site
from app.models.office import Office
from app.models.employee import Employee
from app.models.user import User
from app.models.login_ip_policy import LoginIpPolicy
from app.models.user_mfa import UserMfa  

from app.models.password_reset_token import PasswordResetToken
from app.models.admin_password_reset_request import AdminPasswordResetRequest


# ---------- 基本的な get_or_create 群 ----------

def get_or_create_site(db, site_code: str, name: str) -> Site:
    site = db.query(Site).filter(Site.site_code == site_code).first()
    if site:
        return site

    site = Site(
        site_code=site_code,
        name=name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(site)
    db.flush()
    return site


def get_or_create_office(db, office_code: str, name: str, site: Site) -> Office:
    office = db.query(Office).filter(Office.office_code == office_code).first()
    if office:
        return office

    office = Office(
        office_code=office_code,
        name=name,
        site_id=site.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(office)
    db.flush()
    return office


def get_or_create_login_ip_policy(
    db,
    name: str,
    allowed_cidrs: list[str],
    is_default: bool = False,
    for_admin_only: bool = False,
) -> LoginIpPolicy:
    policy = db.query(LoginIpPolicy).filter(LoginIpPolicy.name == name).first()
    if policy:
        return policy

    policy = LoginIpPolicy(
        name=name,
        description=f"Test policy: {name}",
        allowed_cidrs=json.dumps(allowed_cidrs),  # Text(JSON) 想定
        is_default=is_default,
        for_admin_only=for_admin_only,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(policy)
    db.flush()
    return policy


# ---------- UserMfa 用の helper ----------

def get_or_create_user_mfa(
    db,
    user: User,
    enabled: bool = True,
) -> UserMfa:
    """
    ユーザーに対応する UserMfa を1件だけ作る。
    すでにあればそれを返す。
    """

    mfa = db.query(UserMfa).filter(UserMfa.user_id == user.id).first()
    if mfa:
        return mfa

    # secret はランダムに生成（Google Authenticator 用）
    secret = pyotp.random_base32()

    mfa = UserMfa(
        user_id=user.id,
        secret=secret,
        is_enabled=enabled,  # ← モデルに合わせてフィールド名を修正
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(mfa)
    db.flush()

    print(f"[MFA] user={user.employee_code}, secret={secret}")
    return mfa


# ---------- Employee + User 作成 helper ----------

def create_employee_and_user_if_not_exists(
    db,
    employee_code: str,
    first_name: str,
    last_name: str,
    grade: str,
    office: Office,
    password: str,
    is_admin: bool,
    login_ip_policy: LoginIpPolicy | None,
    create_mfa: bool = False,
) -> tuple[Employee, User]:
    # Employee があればそれを使う
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )
    if not employee:
        employee = Employee(
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            grade=grade,
            office_id=office.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(employee)
        db.flush()

    # User があればそのまま返す
    user = db.query(User).filter(User.employee_code == employee_code).first()
    if user:
        print(f"User {employee_code} already exists, skip.")
        # 既存ユーザーに対してMFAだけ後から作りたい場合もある
        if create_mfa:
            get_or_create_user_mfa(db, user, enabled=True)
        return employee, user

    user = User(
        employee_code=employee_code,
        employee_id=employee.id,  # FK: Employee.id
        hashed_password=get_password_hash(password),
        is_active=True,
        is_admin=is_admin,
        must_change_password=False,
        login_ip_policy_id=login_ip_policy.id if login_ip_policy else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()

    print(
        f"Created user {employee_code} "
        f"(grade={grade}, admin={is_admin}, password={password})"
    )

    # 必要なユーザーだけ MFA を作る
    if create_mfa:
        get_or_create_user_mfa(db, user, enabled=True)

    db.commit()
    return employee, user


# ---------- エントリーポイント ----------

def init_test_data() -> None:
    db = SessionLocal()
    try:
        # 1. 拠点と事業所
        main_site = get_or_create_site(db, site_code="S01", name="テスト本部")
        main_office = get_or_create_office(
            db,
            office_code="O01",
            name="テスト事業所A",
            site=main_site,
        )

        # 2. ログインIPポリシー
        # Swagger / ローカル開発環境から 127.0.0.1 でアクセスする前提のポリシー
        default_policy = get_or_create_login_ip_policy(
            db,
            name="default-internal",
            allowed_cidrs=["127.0.0.1/32"],
            is_default=True,
            for_admin_only=False,
        )

        # 管理者で、どこからでもログインテストできるポリシー
        admin_anywhere_policy = get_or_create_login_ip_policy(
            db,
            name="admin-anywhere",
            allowed_cidrs=["0.0.0.0/0"],  # 全許可（完全テスト用）
            is_default=False,
            for_admin_only=True,
        )

        # IP制限テスト用ポリシー（あえて 127.0.0.1 を含まない）
        restricted_policy = get_or_create_login_ip_policy(
            db,
            name="restricted-only-private",
            allowed_cidrs=["10.0.0.0/8"],  # 127.0.0.1 は含まない
            is_default=False,
            for_admin_only=False,
        )

        # 3. テストユーザー（従業員＋ログイン）

        # 役員（管理者 / どこからでもログインOK + MFAあり）
        create_employee_and_user_if_not_exists(
            db,
            employee_code="X01-TEST",
            first_name="Exec",
            last_name="User",
            grade="X01",
            office=main_office,
            password="password123",
            is_admin=True,
            login_ip_policy=admin_anywhere_policy,
            create_mfa=True,  # ← MFA セットアップ検証用
        )

        # 施設長（管理者権限あり / 内部IPから + MFAあり）
        create_employee_and_user_if_not_exists(
            db,
            employee_code="G06-TEST",
            first_name="Manager",
            last_name="User",
            grade="G06",
            office=main_office,
            password="password123",
            is_admin=True,
            login_ip_policy=default_policy,
            create_mfa=True,
        )

        # 一般考課者（内部IPから / MFAなし）
        create_employee_and_user_if_not_exists(
            db,
            employee_code="G05-TEST",
            first_name="Evaluator",
            last_name="User",
            grade="G05",
            office=main_office,
            password="password123",
            is_admin=False,
            login_ip_policy=default_policy,
            create_mfa=False,
        )

        # 非考課者（一般職 / 内部IPから / MFAなし）
        create_employee_and_user_if_not_exists(
            db,
            employee_code="G02-TEST",
            first_name="Staff",
            last_name="User",
            grade="G02",
            office=main_office,
            password="password123",
            is_admin=False,
            login_ip_policy=default_policy,
            create_mfa=False,
        )

        # IP制限で落ちることを確認するためのユーザー（127.0.0.1非許可）
        create_employee_and_user_if_not_exists(
            db,
            employee_code="IPNG-TEST",
            first_name="Ip",
            last_name="Ng",
            grade="G05",
            office=main_office,
            password="password123",
            is_admin=False,
            login_ip_policy=restricted_policy,
            create_mfa=False,
        )

        print("=== Test data initialization finished. ===")

    finally:
        db.close()


if __name__ == "__main__":
    init_test_data()
