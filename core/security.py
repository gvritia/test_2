import time
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import HTTPException

SECRET_KEY = "your-very-secret-key"
serializer = URLSafeTimedSerializer(SECRET_KEY, salt="session-salt")

def create_signed_token(user_id: str):
    # Формат: <user_id>.<timestamp>
    timestamp = int(time.time())
    return serializer.dumps({"user_id": user_id, "timestamp": timestamp})

def verify_token(token: str):
    try:
        # Проверка подписи и целостности
        data = serializer.loads(token, max_age=300) # 5 минут лимит
        return data
    except SignatureExpired:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})
    except BadSignature:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})