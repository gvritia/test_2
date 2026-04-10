from fastapi import APIRouter, HTTPException, Response, Request, Depends, status
from pydantic import BaseModel
import uuid
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import time
from datetime import datetime, timezone

SECRET_KEY = "super-secret-key"
serializer = URLSafeTimedSerializer(secret_key=SECRET_KEY, salt="session-cookie")

SESSION_DURATION = 300      # 5 минут
RENEWAL_THRESHOLD = 180     # продлеваем после 3 минут

router = APIRouter(tags=["Задания 5.1–5.3 — Аутентификация"])

class LoginRequest(BaseModel):
    username: str
    password: str

fake_users_db = {
    "user123": {"id": uuid.uuid4(), "username": "user123", "password": "password123"},
    "alice": {"id": uuid.uuid4(), "username": "alice", "password": "password123"},
}

def create_session_token(user_id: uuid.UUID, timestamp: int = None) -> str:
    if timestamp is None:
        timestamp = int(time.time())
    data = {"user_id": str(user_id), "timestamp": timestamp}
    return serializer.dumps(data)

def parse_and_verify_session_token(token: str):
    try:
        data = serializer.loads(token, max_age=SESSION_DURATION)
        return {"user_id": uuid.UUID(data["user_id"]), "timestamp": data["timestamp"]}
    except SignatureExpired:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})
    except (BadSignature, Exception):
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})

def should_renew_session(timestamp: int) -> bool:
    elapsed = int(time.time()) - timestamp
    return RENEWAL_THRESHOLD <= elapsed < SESSION_DURATION

# Исправленная зависимость (теперь умеет обновлять куку)
async def get_current_user_from_cookie(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Unauthorized"}
        )

    user_data = parse_and_verify_session_token(token)
    timestamp = user_data["timestamp"]

    # Продление сессии по правилам 5.3
    if should_renew_session(timestamp):
        new_token = create_session_token(user_data["user_id"])
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=SESSION_DURATION,
            secure=False,
            samesite="lax"
        )

    return user_data

# ====================== РОУТЫ ======================

@router.post("/login")
async def login(login_data: LoginRequest, response: Response):
    user = fake_users_db.get(login_data.username)
    if not user or user["password"] != login_data.password:
        raise HTTPException(
            status_code=401,
            detail={"message": "Incorrect username or password"}
        )

    session_token = create_session_token(user["id"])
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=SESSION_DURATION,
        secure=False,
        samesite="lax"
    )
    return {"message": "Login successful"}

@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """Защищённый маршрут (5.1–5.3)"""
    return {
        "message": "Добро пожаловать в ваш профиль!",
        "user_id": str(current_user["user_id"]),
        "last_activity": datetime.fromtimestamp(current_user["timestamp"], tz=timezone.utc).isoformat()
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}