# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Settings 側のフィールド名に合わせる（database_url）
DATABASE_URL = settings.database_url

# SQLite のときだけ connect_args を追加
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        future=True,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


def get_db():
    """
    FastAPI の Depends で使う DB セッション依存関数。
    エンドポイント側で: db: Session = Depends(get_db) のように利用する。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
