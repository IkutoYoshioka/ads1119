# app/db/base.py
# Base をここから import できるようにする
from app.db.base_class import Base

# ここで全モデルを import しておく（型チェック抑制のために # noqa を付ける）
from app.models.user import User  # noqa
# 他のモデルも同様に:
# from app.models.facility import Facility  # noqa
# from app.models.xxx import Xxx  # noqa
