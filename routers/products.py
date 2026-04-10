from fastapi import APIRouter, HTTPException
from typing import Optional, List
from models.product import (Product)

router = APIRouter()

# Тестовые данные (sample_products) из задания [cite: 52, 83]
sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]

# Дополнительный эндпоинт для получения всех продуктов
@router.get("/products", response_model=List[Product])
def get_all_products():
    return sample_products

# Эндпоинт для поиска товаров [cite: 46]
@router.get("/products/search", response_model=List[Product])
async def search_products(
        keyword: str,
        category: Optional[str] = None,
        limit: int = 10
):
    """
    Поиск товаров по ключевому слову и категории[cite: 49, 50].
    """
    if limit < 0:
        raise HTTPException(status_code=400, detail={"message": "Limit must be >= 0"})
    results = []
    for product in sample_products:
        # Проверка ключевого слова в названии
        if keyword.lower() in product["name"].lower():
            # Если категория указана, фильтруем и по ней
            if category:
                if product["category"].lower() == category.lower():
                    results.append(product)
            else:
                results.append(product)

    # Ограничение количества результатов [cite: 50]
    return results[:limit]


# Эндпоинт для получения одного товара по ID [cite: 39]
@router.get("/product/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """
    Возвращает информацию о продукте по его идентификатору
    """
    product = next((p for p in sample_products if p["product_id"] == product_id), None)

    if product is None:
        # Если продукт не найден, возвращаем 404
        raise HTTPException(
            status_code=404,
            detail={"message": "Product not found"}
        )
    return product