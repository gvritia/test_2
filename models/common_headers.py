from pydantic import BaseModel, Field, field_validator
import re


class CommonHeaders(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v):
        """
        Простая проверка формата:
        en-US,en;q=0.9,es;q=0.8
        """
        pattern = r"^[a-zA-Z]{2}(-[a-zA-Z]{2})?(,[a-zA-Z]{2}(-[a-zA-Z]{2})?(;q=\d(\.\d)?)?)*$"

        if not re.match(pattern, v):
            raise ValueError("Invalid Accept-Language format")

        return v