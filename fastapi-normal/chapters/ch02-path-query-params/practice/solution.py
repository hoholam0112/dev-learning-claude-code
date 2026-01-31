# 실행 방법: uvicorn solution:app --reload
# 챕터 02 연습 문제 모범 답안

from enum import Enum
from typing import Optional

from fastapi import FastAPI, Path, Query

app = FastAPI(
    title="챕터 02 연습 문제 답안",
    description="경로 파라미터와 쿼리 파라미터 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 사용자 프로필 조회 API
# ============================================================

# 임시 사용자 데이터
USERS = {
    1: {"user_id": 1, "name": "사용자_1", "email": "user1@example.com"},
    2: {"user_id": 2, "name": "사용자_2", "email": "user2@example.com"},
    3: {"user_id": 3, "name": "사용자_3", "email": "user3@example.com"},
}

# 임시 게시글 데이터
USER_POSTS = {
    1: [
        {"id": 1, "title": "첫 번째 글"},
        {"id": 2, "title": "두 번째 글"},
        {"id": 3, "title": "세 번째 글"},
    ],
    2: [
        {"id": 4, "title": "사용자2의 글"},
    ],
    3: [],
}


@app.get("/users/{user_id}", tags=["사용자"])
def get_user(
    user_id: int = Path(
        ...,
        title="사용자 ID",
        description="조회할 사용자의 고유 번호",
        ge=1,
    ),
):
    """사용자 프로필을 조회합니다."""
    if user_id in USERS:
        return USERS[user_id]
    return {"error": "사용자를 찾을 수 없습니다", "user_id": user_id}


@app.get("/users/{user_id}/posts", tags=["사용자"])
def get_user_posts(
    user_id: int = Path(..., title="사용자 ID", ge=1),
    skip: int = Query(default=0, ge=0, title="건너뛸 항목 수"),
    limit: int = Query(default=5, ge=1, le=50, title="반환할 항목 수"),
):
    """특정 사용자의 게시글 목록을 조회합니다."""
    posts = USER_POSTS.get(user_id, [])
    paginated_posts = posts[skip : skip + limit]

    return {
        "user_id": user_id,
        "skip": skip,
        "limit": limit,
        "posts": paginated_posts,
    }


# ============================================================
# 문제 2: 도서 검색 API
# ============================================================

BOOKS = [
    {"id": 1, "title": "파이썬 입문", "author": "김파이", "price": 25000},
    {"id": 2, "title": "FastAPI 마스터", "author": "이패스트", "price": 32000},
    {"id": 3, "title": "데이터 분석", "author": "김파이", "price": 28000},
    {"id": 4, "title": "웹 개발 기초", "author": "박웹", "price": 22000},
    {"id": 5, "title": "머신러닝 입문", "author": "최머신", "price": 35000},
]


@app.get("/books", tags=["도서"])
def search_books(
    q: Optional[str] = Query(
        default=None,
        min_length=2,
        max_length=100,
        title="검색 키워드",
        description="도서 제목 또는 저자명에서 검색",
    ),
    author: Optional[str] = Query(
        default=None,
        title="저자명",
        description="저자명으로 필터링",
    ),
    min_price: Optional[int] = Query(
        default=None,
        ge=0,
        title="최소 가격",
        description="최소 가격 필터",
    ),
    max_price: Optional[int] = Query(
        default=None,
        ge=0,
        title="최대 가격",
        description="최대 가격 필터",
    ),
    page: int = Query(
        default=1,
        ge=1,
        title="페이지 번호",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=50,
        title="페이지 크기",
    ),
):
    """도서를 검색합니다.

    다양한 쿼리 파라미터를 조합하여 도서를 필터링할 수 있습니다.
    """
    result = BOOKS.copy()

    # 키워드 검색 (제목 또는 저자명에 포함)
    if q:
        result = [
            book for book in result
            if q in book["title"] or q in book["author"]
        ]

    # 저자 필터링
    if author:
        result = [book for book in result if book["author"] == author]

    # 가격 필터링
    if min_price is not None:
        result = [book for book in result if book["price"] >= min_price]
    if max_price is not None:
        result = [book for book in result if book["price"] <= max_price]

    # 페이지네이션
    total = len(result)
    skip = (page - 1) * page_size
    paginated = result[skip : skip + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "books": paginated,
    }


# ============================================================
# 문제 3: Enum 기반 카테고리 필터링
# ============================================================


class ProductCategory(str, Enum):
    """상품 카테고리"""
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    books = "books"


class SortOrder(str, Enum):
    """정렬 순서"""
    price_asc = "price_asc"
    price_desc = "price_desc"
    name_asc = "name_asc"
    name_desc = "name_desc"


SHOP_PRODUCTS = [
    {"id": 1, "name": "노트북", "category": "electronics", "price": 1200000, "in_stock": True},
    {"id": 2, "name": "티셔츠", "category": "clothing", "price": 29000, "in_stock": True},
    {"id": 3, "name": "사과", "category": "food", "price": 5000, "in_stock": False},
    {"id": 4, "name": "파이썬 책", "category": "books", "price": 32000, "in_stock": True},
    {"id": 5, "name": "이어폰", "category": "electronics", "price": 89000, "in_stock": True},
]


@app.get("/shop/products", tags=["쇼핑"])
def get_shop_products(
    category: Optional[ProductCategory] = Query(
        default=None,
        title="카테고리",
        description="상품 카테고리로 필터링",
    ),
    sort: SortOrder = Query(
        default=SortOrder.name_asc,
        title="정렬 순서",
        description="상품 정렬 기준",
    ),
    in_stock: bool = Query(
        default=True,
        title="재고 여부",
        description="True면 재고 있는 상품만, False면 전체",
    ),
):
    """상품 목록을 조회합니다.

    Enum을 활용한 카테고리 및 정렬 필터링 예제입니다.
    """
    result = SHOP_PRODUCTS.copy()

    # 카테고리 필터링
    if category:
        result = [p for p in result if p["category"] == category.value]

    # 재고 필터링 (in_stock이 True이면 재고 있는 것만)
    if in_stock:
        result = [p for p in result if p["in_stock"]]

    # 정렬 적용
    if sort == SortOrder.price_asc:
        result = sorted(result, key=lambda x: x["price"])
    elif sort == SortOrder.price_desc:
        result = sorted(result, key=lambda x: x["price"], reverse=True)
    elif sort == SortOrder.name_asc:
        result = sorted(result, key=lambda x: x["name"])
    elif sort == SortOrder.name_desc:
        result = sorted(result, key=lambda x: x["name"], reverse=True)

    return {
        "category": category.value if category else "all",
        "sort": sort.value,
        "count": len(result),
        "products": result,
    }


@app.get("/shop/categories", tags=["쇼핑"])
def get_categories():
    """사용 가능한 카테고리 목록을 반환합니다."""
    return {"categories": [c.value for c in ProductCategory]}
