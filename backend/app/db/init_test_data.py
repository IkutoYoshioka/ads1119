# app/db/init_test_data.py

from datetime import datetime
import json

from app.db.session import SessionLocal
from app.core.security import get_password_hash

from app.models.site import Site
from app.models.office import Office
from app.models.employee import Employee
from app.models.user import User
from app.models.login_ip_policy import LoginIpPolicy


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

    # モデルによっては allowed_cidrs は Text(JSON) かもしれないので、
    # そこはあなたの定義に合わせて。
    policy = LoginIpPolicy(
        name=name,
        description=f"Test policy: {name}",
        allowed_cidrs=json.dumps(allowed_cidrs),
        is_default=is_default,
        for_admin_only=for_admin_only,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(policy)
    db.flush()
    return policy


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
) -> tuple[Employee, User]:
    # すでに Employee があればそれを使う
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
    db.commit()

    print(
        f"Created user {employee_code} "
        f"(grade={grade}, admin={is_admin}, password={password})"
    )
    return employee, user


def init_test_data() -> None:
    db = SessionLocal()
    try:
        # 1. 拠点と事業所
        main_site = get_or_create_site(db, site_code="S01", name="テスト本部")
        main_office = get_or_create_office(db, office_code="O01", name="テスト事業所A", site=main_site)

        # 2. ログインIPポリシー
        # Swagger からは 127.0.0.1 でアクセスするので、テスト用には 127.0.0.1 を許可しておく
        default_policy = get_or_create_login_ip_policy(
            db,
            name="default-internal",
            allowed_cidrs=["127.0.0.1/32"],   # 開発環境用
            is_default=True,
            for_admin_only=False,
        )

        admin_anywhere_policy = get_or_create_login_ip_policy(
            db,
            name="admin-anywhere",
            allowed_cidrs=["0.0.0.0/0"],      # どこからでもOK（テスト用）
            is_default=False,
            for_admin_only=True,
        )

        # 3. テストユーザー（従業員＋ログイン）
        # 役員（管理者）
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
        )

        # 施設長（管理者権限あり）
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
        )

        # 一般考課者
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
        )

        # 非考課者（一般職）
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
        )

        # IP制限で落ちるテストユーザー（あえて 127.0.0.1 を含まないポリシー）
        restricted_policy = get_or_create_login_ip_policy(
            db,
            name="restricted-only-private",
            allowed_cidrs=["10.0.0.0/8"],  # 127.0.0.1 は含まない
            is_default=False,
            for_admin_only=False,
        )
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
        )

        print("=== Test data initialization finished. ===")

    finally:
        db.close()


if __name__ == "__main__":
    init_test_data()
