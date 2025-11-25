# schemas/auth.py
from pydantic import BaseModel

class LoginRequest(BaseModel):
    employeeCode: str
    password: str

class LoginResponse(BaseModel):
    employeeId: str
    grade: str
    isAdmin: bool
    redirectPath: str  # フロントがこのパスに遷移すればよい
