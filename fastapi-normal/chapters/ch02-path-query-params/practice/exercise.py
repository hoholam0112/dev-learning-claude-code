# 실행 방법: uvicorn exercise:app --reload
# 챕터 02 연습 문제 - 직접 코드를 작성해보세요!

from enum import Enum
from typing import Optional

from fastapi import FastAPI, Path, Query

app = FastAPI(
    title="챕터 02 연습 문제",
    description="경로 파라미터와 쿼리 파라미터 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 사용자 프로필 조회 API
# GET /users/{user_id} — 사용자 ID로 프로필 조회
# GET /users/{user_id}/posts — 특정 사용자의 게시글 목록 (페이지네이션)
# user_id는 1 이상의 정수 (Path() 사용)
# 게시글은 skip, limit 쿼리 파라미터로 페이지네이션
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
    # TODO: user_id가 USERS에 있으면 해당 사용자 반환, 없으면 에러 메시지 반환
    pass


@app.get("/users/{user_id}/posts", tags=["사용자"])
def get_user_posts(
    user_id: int = Path(..., title="사용자 ID", ge=1),
    skip: int = Query(default=0, ge=0, title="건너뛸 항목 수"),
    limit: int = Query(default=5, ge=1, le=50, title="반환할 항목 수"),
):
    """특정 사용자의 게시글 목록을 조회합니다."""
    # TODO: USER_POSTS에서 게시글을 가져와 skip/limit으로 슬라이싱하여 반환
    # 반환 형식: {"user_id": ..., "skip": ..., "limit": ..., "posts": [...]}
    pass


# ============================================================
# 문제 2: 도서 검색 API
# GET /books — 도서 목록 조회 (다양한 쿼리 파라미터로 필터링)
# q: 검색 키워드 (선택, 2~100자)
# author: 저자명 필터 (선택)
# min_price, max_price: 가격 범위 (선택)
# page: 페이지 번호 (기본 1), page_size: 페이지 크기 (기본 10, 최대 50)
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
    ),
    max_price: Optional[int] = Query(
        default=None,
        ge=0,
        title="최대 가격",
    ),
    page: int = Query(default=1, ge=1, title="페이지 번호"),
    page_size: int = Query(default=10, ge=1, le=50, title="페이지 크기"),
):
    """도서를 검색합니다."""
    # TODO: 다음 순서로 필터링을 구현하세요
    # 1. q가 있으면 제목 또는 저자명에 키워드가 포함된 도서만 필터링
    # 2. author가 있으면 해당 저자의 도서만 필터링
    # 3. min_price가 있으면 최소 가격 이상인 도서만 필터링
    # 4. max_price가 있으면 최대 가격 이하인 도서만 필터링
    # 5. 페이지네이션 적용
    # 반환 형식: {"total": ..., "page": ..., "page_size": ..., "books": [...]}
    pass


# ============================================================
# 문제 3: Enum 기반 카테고리 필터링
# ProductCategory Enum: electronics, clothing, food, books
# SortOrder Enum: price_asc, price_desc, name_asc, name_desc
# GET /shop/products — 상품 목록 (카테고리, 정렬, 재고 필터)
# GET /shop/categories — 카테고리 목록 반환
# ============================================================


# TODO: ProductCategory Enum을 정의하세요 (str, Enum 상속)
# 값: electronics, clothing, food, books


# TODO: SortOrder Enum을 정의하세요 (str, Enum 상속)
# 값: price_asc, price_desc, name_asc, name_desc


SHOP_PRODUCTS = [
    {"id": 1, "name": "노트북", "category": "electronics", "price": 1200000, "in_stock": True},
    {"id": 2, "name": "티셔츠", "category": "clothing", "price": 29000, "in_stock": True},
    {"id": 3, "name": "사과", "category": "food", "price": 5000, "in_stock": False},
    {"id": 4, "name": "파이썬 책", "category": "books", "price": 32000, "in_stock": True},
    {"id": 5, "name": "이어폰", "category": "electronics", "price": 89000, "in_stock": True},
]


# TODO: GET /shop/products 엔드포인트를 구현하세요
# 파라미터: category(선택, Enum), sort(선택, Enum, 기본값 name_asc), in_stock(bool, 기본값 True)
# 카테고리 필터링 → 재고 필터링 → 정렬 순서로 처리
# 반환 형식: {"category": ..., "sort": ..., "count": ..., "products": [...]}


# TODO: GET /shop/categories 엔드포인트를 구현하세요
# 반환 형식: {"categories": ["electronics", "clothing", "food", "books"]}
