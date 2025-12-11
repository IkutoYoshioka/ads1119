# app/db/base.py
# Base をここから import できるようにする
from .base_class import Base

# ここで全モデルを import しておく（型チェック抑制のために # noqa を付ける）
from app.models.user import User  # noqa
from app.models.employee import Employee  # noqa
from app.models.office import Office  # noqa
from app.models.site import Site  # noqa
from app.models.password_reset_token import PasswordResetToken  # noqa
from app.models.admin_password_reset_request import AdminPasswordResetRequest  # noqa
from app.models.user_mfa import UserMfa  # noqa
from app.models.login_ip_policy import LoginIpPolicy  # noqa
