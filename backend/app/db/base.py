# app/db/base.py

import app.db.base  # noqa: F401  # モデル登録の副作用が目的

from .base_class import Base

from app.models.site import Site  # noqa
from app.models.office import Office  # noqa
from app.models.grade import Grade  # noqa
from app.models.employee import Employee  # noqa
from app.models.login_ip_policy import LoginIpPolicy  # noqa
from app.models.user_mfa import UserMfa  # noqa
from app.models.password_reset_token import PasswordResetToken  # noqa
from app.models.admin_password_reset_request import AdminPasswordResetRequest  # noqa

from app.models.user import User  # noqa  ← 最後
