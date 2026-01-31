# 실행 방법: uvicorn example-01:app --reload
# 공통 쿼리 파라미터 의존성 예제

from typing import List, Optional

from fastapi import Depends, FastAPI, Query

app = FastAPI(title="의존성 주입 예제", description="공통 쿼리 파라미터 의존성")

# ============================================================
# 임시 데이터
# ============================================================

ITEMS = [
    {"id": 1, "name": "노트북", "category": "전자기기", "price": 1200000},
    {"id": 2, "name": "키보드", "category": "전자기기", "price": 89000},
    {"id": 3, "name": "파이썬 책", "category": "도서", "price": 32000},
    {"id": 4, "name": "모니터", "category": "전자기기", "price": 450000},
    {"id": 5, "name": "마우스", "category": "전자기기", "price": 45000},
    {"id": 6, "name": "자바 책", "category": "도서", "price": 28000},
    {"id": 7, "name": "책상", "category": "가구", "price": 350000},
    {"id": 8, "name": "의자", "category": "가구", "price": 280000},
    {"id": 9, "name": "이어폰", "category": "전자기기", "price": 150000},
    {"id": 10, "name": "백팩", "category": "잡화", "price": 89000},
]

USERS = [
    {"id": 1, "name": "홍길동", "role": "admin"},
    {"id": 2, "name": "김철수", "role": "user"},
    {"id": 3, "name": "이영희", "role": "user"},
    {"id": 4, "name": "박지민", "role": "moderator"},
    {"id": 5, "name": "최수진", "role": "user"},
]


# ============================================================
# 함수 의존성 정의
# ============================================================


def common_pagination(
    skip: int = Query(default=0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(default=10, ge=1, le=100, description="최대 반환 항목 수"),
):
    """공통 페이지네이션 파라미터 의존성

    여러 엔드포인트에서 동일한 페이지네이션 로직을 재사용합니다.
    """
    return {"skip": skip, "limit": limit}


def common_search(
    q: Optional[str] = Query(default=None, min_length=1, description="검색 키워드"),
    sort_by: str = Query(default="id", description="정렬 기준 필드"),
    order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="정렬 순서 (asc/desc)",
    ),
):
    """공통 검색/정렬 파라미터 의존성"""
    return {"q": q, "sort_by": sort_by, "order": order}


# ============================================================
# API 엔드포인트
# ============================================================


@app.get("/items", tags=["아이템"])
def get_items(
    pagination: dict = Depends(common_pagination),
    search: dict = Depends(common_search),
):
    """아이템 목록을 조회합니다.

    페이지네이션과 검색 파라미터를 공통 의존성으로 처리합니다.
    """
    result = ITEMS.copy()

    # 검색 키워드 필터링
    if search["q"]:
        result = [
            item for item in result
            if search["q"].lower() in item["name"].lower()
            or search["q"].lower() in item["category"].lower()
        ]

    # 정렬
    sort_key = search["sort_by"]
    if sort_key in ("id", "name", "price", "category"):
        reverse = search["order"] == "desc"
        result = sorted(result, key=lambda x: x.get(sort_key, 0), reverse=reverse)

    # 페이지네이션
    total = len(result)
    skip = pagination["skip"]
    limit = pagination["limit"]
    result = result[skip : skip + limit]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": result,
    }


@app.get("/users", tags=["사용자"])
def get_users(
    pagination: dict = Depends(common_pagination),
    search: dict = Depends(common_search),
):
    """사용자 목록을 조회합니다.

    아이템 API와 동일한 의존성을 재사용하여
    페이지네이션과 검색을 처리합니다.
    """
    result = USERS.copy()

    # 검색 키워드 필터링
    if search["q"]:
        result = [
            user for user in result
            if search["q"].lower() in user["name"].lower()
            or search["q"].lower() in user["role"].lower()
        ]

    # 정렬
    sort_key = search["sort_by"]
    if sort_key in ("id", "name", "role"):
        reverse = search["order"] == "desc"
        result = sorted(result, key=lambda x: x.get(sort_key, ""), reverse=reverse)

    # 페이지네이션
    total = len(result)
    skip = pagination["skip"]
    limit = pagination["limit"]
    result = result[skip : skip + limit]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "users": result,
    }


@app.get("/items/categories", tags=["아이템"])
def get_categories(pagination: dict = Depends(common_pagination)):
    """카테고리 목록을 조회합니다.

    페이지네이션 의존성만 재사용하는 예제입니다.
    """
    categories = list(set(item["category"] for item in ITEMS))
    categories.sort()

    total = len(categories)
    skip = pagination["skip"]
    limit = pagination["limit"]

    return {
        "total": total,
        "categories": categories[skip : skip + limit],
    }
