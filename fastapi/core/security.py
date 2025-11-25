# core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt  # pip install PyJWT

SECRET_KEY = "YOUR_SECRET_KEY"  # 環境変数で管理すべき
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8時間など

def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
