# app/models/user.py
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    """
    認証・権限管理用のアカウント情報。
    従業員情報（Employee）とは分離して管理する。
    """

    __tablename__ = "users"

    # 内部ID（PK）
    id = Column(Integer, primary_key=True, index=True)

    # ログインID：現時点では「社員コード」を流用
    # ここを username などに変えたくなったら、カラム名だけ変えれば良い
    employee_code = Column(String(50), unique=True, index=True, nullable=False)

    # 従業員プロファイルへの紐付け（任意）
    # 管理者専用アカウントなどは employee_id = NULL もありうる
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    # 認証関連
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)

    is_admin = Column(Boolean, nullable=False, default=False)
    
    must_change_password = Column(Boolean, nullable=False, default=False)

    # ログインIPポリシー（任意）
    login_ip_policy_id = Column(
        Integer,
        ForeignKey("login_ip_policies.id"),
        nullable=True,
    )

    # 監査・ログ用
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    # ---- リレーション（後続ステップで相手側も整える） ----

    # 従業員プロファイル
    employee = relationship(
        "Employee",
        back_populates="user",
        uselist=False,
    )

    # IPポリシー
    login_ip_policy = relationship(
        "LoginIpPolicy",
        back_populates="users",
    )

    # 多要素認証設定
    mfa = relationship("UserMfa", uselist=False, back_populates="user")

    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    admin_password_reset_requests_created = relationship(
        "AdminPasswordResetRequest",
        back_populates="requested_by",
        foreign_keys="AdminPasswordResetRequest.requested_by_user_id",
    )
    admin_password_reset_requests_target = relationship(
        "AdminPasswordResetRequest",
        back_populates="target_user",
        foreign_keys="AdminPasswordResetRequest.target_user_id",
    )
