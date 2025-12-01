# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, facilities, password_reset
from app.api.v1 import users
from app.db.session import engine
from app.db.base import Base

app = FastAPI()

# 開発中に許可するフロントエンドのオリジン
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 必ず "*" ではなく明示的に書く（credentials を使うため）
    allow_credentials=True,      # Cookie を送受信するなら True
    allow_methods=["*"],         # 必要なら絞ってもよい
    allow_headers=["*"],         # 必要なら絞ってもよい
)

app.include_router(auth.router)
app.include_router(facilities.router)
app.include_router(password_reset.router)
app.include_router(users.router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    # 開発用：起動時にテーブルを自動作成
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}
