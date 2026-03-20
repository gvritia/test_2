from fastapi import FastAPI, Query, Response, Request, Header, HTTPException
from typing import Optional
import uvicorn
import models
import uuid
import time
from itsdangerous import Signer, BadSignature
from datetime import datetime

app = FastAPI()


# Задание 3.1
@app.post("/create_user", response_model=models.UserCreate, tags=["Task 3.1"])
def task_3_1(user_create: models.UserCreate):
    return user_create


# Задание 3.2
products_db = [
    models.Product(product_id=123, name="Smartphone", category="Electronics", price=599.99),
    models.Product(product_id=456, name="Laptop", category="Electronics", price=999.99),
    models.Product(product_id=789, name="Iphone", category="Electronics", price=1299.99),
    models.Product(product_id=101, name="T-Shirt", category="Clothing", price=29.99),
    models.Product(product_id=102, name="Jeans", category="Clothing", price=79.99),
    models.Product(product_id=103, name="Novel", category="Books", price=15.99),
    models.Product(product_id=104, name="Headphones", category="Electronics", price=89.99),
    models.Product(product_id=105, name="Sneakers", category="Footwear", price=120.00)
]


# Эндпоинт 1: Получение информации о продукте по ID
@app.get("/product/{product_id}", response_model=models.Product, tags=["Task 3.2"])
def get_product(product_id: int):
    for product in products_db:
        if product.product_id == product_id:
            return product


# Эндпоинт 2: Поиск товаров
@app.get("/products/search", response_model=list[models.Product], tags=["Task 3.2"])
def search_products(
        keyword: str = Query(..., description="Ключевое слово для поиска"),
        category: Optional[str] = Query(None, description="Категория для фильтрации"),
        limit: int = Query(10, ge=1, le=100, description="Максимальное количество товаров")
):
    results = []
    keyword_lower = keyword.lower()

    for product in products_db:
        if keyword_lower in product.name.lower():
            if category is None or product.category.lower() == category.lower():
                results.append(product)

        if len(results) >= limit:
            break

    return results


# Дополнительный эндпоинт для получения всех продуктов
@app.get("/products", response_model=list[models.Product], tags=["Task 3.2"])
def get_all_products():
    return products_db


# Задание 5.1-5.3
SECRET_KEY = "super-secret-key"
signer = Signer(SECRET_KEY)
SESSION_MAX_AGE = 300
SESSION_REFRESH_THRESHOLD = 180

# ФЕЙКОВАЯ БАЗА ПОЛЬЗОВАТЕЛЕЙ
users_db = {
    "admin": {
        "password": "1234",
        "user_id": str(uuid.uuid4())  # UUID генерируется один раз
    }
}


# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
def create_session_token(user_id: str) -> str:
    timestamp = int(time.time())

    data = f"{user_id}.{timestamp}"

    signed_data = signer.sign(data.encode())

    return signed_data.decode()


def verify_session_token(token: str):
    try:
        unsigned_data = signer.unsign(token.encode()).decode()

        user_id, timestamp = unsigned_data.split(".")

        return user_id, int(timestamp)

    except BadSignature:
        return None, None


# Задание 5.1 — LOGIN
@app.post("/login", tags=["Task 5.1 - 5.3"])
def login(username: str, password: str, response: Response):
    user = users_db.get(username)

    if not user or user["password"] != password:
        response.status_code = 401
        return {"message": "Invalid credentials"}

    user_id = user["user_id"]

    session_token = create_session_token(user_id)

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        max_age=SESSION_MAX_AGE
    )

    return {"message": "Login successful"}


# Задание 5.2-5.3 — PROFILE (защищённый маршрут)
@app.get("/profile", tags=["Task 5.1 - 5.3"])
def profile(request: Request, response: Response):
    token = request.cookies.get("session_token")

    if not token:
        response.status_code = 401
        return {"message": "Unauthorized"}

    user_id, timestamp = verify_session_token(token)

    if not user_id:
        response.status_code = 401
        return {"message": "Invalid session"}

    current_time = int(time.time())
    time_diff = current_time - timestamp

    if time_diff > SESSION_MAX_AGE:
        response.status_code = 401
        return {"message": "Session expired"}

    if SESSION_REFRESH_THRESHOLD <= time_diff <= SESSION_MAX_AGE:
        new_token = create_session_token(user_id)

        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            max_age=SESSION_MAX_AGE
        )

    return {
        "message": "Profile data",
        "user_id": user_id
    }


# Задание 5.4-5.5
# Задание 5.4 — HEADERS (без DRY)
@app.get("/headers_raw", tags=["Task 5.4"])
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
@app.get("/headers", tags=["Task 5.5"])
def get_headers(headers: models.CommonHeaders = Header(...)):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


# Задание 5.5 — INFO
@app.get("/info", tags=["Task 5.5"])
def get_info(
        headers: models.CommonHeaders = Header(...),
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


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
