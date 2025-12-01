# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLite のときはこのオプションが必要
if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        connect_args={"check_same_thread": False},
        future=True,
    )
else:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
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
