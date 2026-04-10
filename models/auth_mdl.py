from pydantic import BaseModel
import uuid


class LoginRequest(BaseModel):
    username: str
    password: str

# Задание 5.3 (Модель для данных пользователя в БД)
class UserInDB(BaseModel):
    id: uuid.UUID
    username: str
    hashed_password: str