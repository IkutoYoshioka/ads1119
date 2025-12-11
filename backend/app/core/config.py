# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "青葉福祉会HRシステム"

    # Docker 外でローカルから接続する用
    database_url: str = (
        "postgresql+psycopg2://ads_user:ads_password@localhost:5432/ads_db"
    )

    # ==== ここから追加（認証 / JWT 用）====
    SECRET_KEY: str = "change-me"  # 本番では .env に必ず上書きする
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8時間
    # ==== 追加ここまで ====

    class Config:
        env_file = ".env"


settings = Settings()
