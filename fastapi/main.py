# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, facilities, password_reset

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

@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}
