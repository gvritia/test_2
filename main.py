from fastapi import FastAPI
from routers import users, products, auth, headers

app = FastAPI(title="Control Work 2")

# Подключаем модули
app.include_router(users.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(headers.router)