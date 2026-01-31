# 실행 방법: uvicorn example-01:app --reload
# 상품 조회 API - 경로 파라미터와 쿼리 파라미터 활용 예제

from enum import Enum
from typing import Optional

from fastapi import FastAPI

app = FastAPI(title="상품 조회 API", description="경로/쿼리 파라미터 예제")

# 임시 상품 데이터 (데이터베이스 대신 사용)
PRODUCTS = [
    {"id": 1, "name": "노트북", "category": "electronics", "price": 1200000},
    {"id": 2, "name": "키보드", "category": "electronics", "price": 89000},
    {"id": 3, "name": "파이썬 교재", "category": "books", "price": 32000},
    {"id": 4, "name": "모니터", "category": "electronics", "price": 450000},
    {"id": 5, "name": "마우스", "category": "electronics", "price": 45000},
    {"id": 6, "name": "자바 교재", "category": "books", "price": 28000},
    {"id": 7, "name": "책상", "category": "furniture", "price": 350000},
    {"id": 8, "name": "의자", "category": "furniture", "price": 280000},
]


class Category(str, Enum):
    """상품 카테고리 열거형"""
    electronics = "electronics"
    books = "books"
    furniture = "furniture"


@app.get("/products", tags=["상품"])
def get_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[Category] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
):
    """상품 목록을 조회합니다.

    쿼리 파라미터를 사용하여 필터링, 페이지네이션을 적용할 수 있습니다.

    - skip: 건너뛸 항목 수 (페이지네이션)
    - limit: 반환할 최대 항목 수
    - category: 카테고리 필터 (electronics, books, furniture)
    - min_price: 최소 가격 필터
    - max_price: 최대 가격 필터
    """
    result = PRODUCTS.copy()

    # 카테고리 필터링
    if category:
        result = [p for p in result if p["category"] == category.value]

    # 가격 범위 필터링
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    # 페이지네이션 적용
    total = len(result)
    result = result[skip : skip + limit]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "products": result,
    }


@app.get("/products/{product_id}", tags=["상품"])
def get_product(product_id: int):
    """특정 상품을 조회합니다.

    경로 파라미터로 상품 ID를 받아 해당 상품 정보를 반환합니다.
    """
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return {"error": "상품을 찾을 수 없습니다", "product_id": product_id}


@app.get("/products/category/{category}", tags=["상품"])
def get_products_by_category(category: Category):
    """카테고리별 상품을 조회합니다.

    Enum을 사용하여 허용된 카테고리 값만 받습니다.
    """
    result = [p for p in PRODUCTS if p["category"] == category.value]
    return {
        "category": category.value,
        "count": len(result),
        "products": result,
    }
