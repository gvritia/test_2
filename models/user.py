from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


# Задание 3.1
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Имя пользователя, обязательное поле")
    email: EmailStr = Field(..., description="Email, должен быть валидного формата")
    age: Optional[int] = Field(None, gt=0, description="Возраст, должен быть положительным числом")
    is_subscribed: Optional[bool] = Field(False, description="Флаг подписки на рассылку")

    @field_validator("name")
    def name_not_empty(cls, v):
        if not v or not v.strip():
            return ValueError('Name cannot be empty')
        return v.strip()

    @field_validator("age")
    def age_positive(cls, v):
        if v is not None and v <= 0:
            return ValueError('Age must be positive')
        return v

    @field_validator("email")
    def email_not_empty(cls, v):
        if not v or not v.strip():
            return ValueError('Email cannot be empty')
        return v