from fastapi import APIRouter, Depends, Response, Header, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from models.common_headers import CommonHeaders
from typing import Annotated

router = APIRouter(tags=["Задания 5.4–5.5 — Заголовки"])

@router.get("/headers_raw")
def get_headers_raw(request: Request):
    user_agent = request.headers.get("User-Agent")
    accept_language = request.headers.get("Accept-Language")

    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Missing required headers")

    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


#  Задание 5.5 — HEADERS через модель
@router.get("/headers")
def get_headers(headers: CommonHeaders = Header(...)):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


# Задание 5.5 — INFO
@router.get("/info")
def get_info(
        headers: CommonHeaders = Header(...),
        response: Response = None
):
    server_time = datetime.now().isoformat()

    response.headers["X-Server-Time"] = server_time

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }

