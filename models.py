from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
import re

# Задание 3.1
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    age: Optional[int] = Field(None, description="User's age", ge=1)
    is_subscribed: Optional[bool] = Field(False, description="Newsletter subscription status")

    @validator("name")
    def name_not_empty(cls, v):
        if not v or not v.strip():
            return ValueError('Name cannot be empty')
        return v.strip()

    @validator("age")
    def age_positive(cls, v):
        if v is not None and v <= 0:
            return ValueError('Age must be positive')
        return v

    @validator("email")
    def email_not_empty(cls, v):
        if not v or not v.strip():
            return ValueError('Email cannot be empty')
        return v

# Задание 3.2
class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

# Задание 5.4-5.5
class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")

    @validator("accept_language")
    def validate_accept_language(cls, v):
        """
        Простая проверка формата:
        en-US,en;q=0.9,es;q=0.8
        """
        pattern = r"^[a-zA-Z]{2}(-[a-zA-Z]{2})?(,[a-zA-Z]{2}(-[a-zA-Z]{2})?(;q=\d(\.\d)?)?)*$"

        if not re.match(pattern, v):
            raise ValueError("Invalid Accept-Language format")

        return v