# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from fastapi import FastAPI, Depends, Query
from fastapi.testclient import TestClient

app = FastAPI()

# 가상 데이터
fake_items = [{"name": f"상품_{i}", "price": i * 1000} for i in range(1, 21)]


# ============================================================
# 문제 1 해답: 공통 페이지네이션 의존성
# ============================================================

def common_pagination(
    skip: int = Query(default=0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(default=10, ge=1, le=100, description="조회할 항목 수"),
) -> dict:
    """
    공통 페이지네이션 의존성 함수.
    여러 엔드포인트에서 재사용할 수 있는 페이지네이션 매개변수를 제공합니다.
    """
    return {"skip": skip, "limit": limit}


@app.get("/items")
def read_items(pagination: dict = Depends(common_pagination)):
    """
    상품 목록 조회 엔드포인트.
    common_pagination 의존성을 사용하여 페이지네이션을 적용합니다.
    """
    skip = pagination["skip"]
    limit = pagination["limit"]
    return fake_items[skip : skip + limit]


@app.get("/items/count")
def read_items_count(pagination: dict = Depends(common_pagination)):
    """
    상품 개수 조회 엔드포인트.
    같은 common_pagination 의존성을 재사용합니다.
    """
    skip = pagination["skip"]
    limit = pagination["limit"]
    sliced = fake_items[skip : skip + limit]
    return {
        "total": len(fake_items),
        "skip": skip,
        "limit": limit,
        "count": len(sliced),
    }


# ============================================================
# 문제 2 해답: 공통 필터링 의존성
# ============================================================

def common_filter(
    keyword: str | None = Query(default=None, description="상품 이름 검색 키워드"),
    min_price: int = Query(default=0, ge=0, description="최소 가격"),
    max_price: int = Query(default=100000, ge=0, description="최대 가격"),
) -> dict:
    """
    공통 필터링 의존성 함수.
    키워드 검색과 가격 범위 필터를 제공합니다.
    """
    return {"keyword": keyword, "min_price": min_price, "max_price": max_price}


@app.get("/items/search")
def search_items(
    pagination: dict = Depends(common_pagination),
    filter_params: dict = Depends(common_filter),
):
    """
    상품 검색 엔드포인트.
    common_filter와 common_pagination을 동시에 사용합니다.

    처리 순서:
    1. 필터 조건으로 항목 선택 (키워드 + 가격 범위)
    2. 필터링된 결과에 페이지네이션 적용
    """
    # 1단계: 필터링
    filtered = fake_items

    # 키워드 필터: keyword가 None이 아니면 이름에 포함된 항목만 선택
    if filter_params["keyword"] is not None:
        filtered = [
            item for item in filtered
            if filter_params["keyword"] in item["name"]
        ]

    # 가격 범위 필터
    filtered = [
        item for item in filtered
        if filter_params["min_price"] <= item["price"] <= filter_params["max_price"]
    ]

    total_filtered = len(filtered)

    # 2단계: 페이지네이션
    skip = pagination["skip"]
    limit = pagination["limit"]
    results = filtered[skip : skip + limit]

    return {
        "results": results,
        "total_filtered": total_filtered,
    }


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 테스트
    print("=" * 50)
    print("문제 1: 공통 페이지네이션 의존성 테스트")
    print("=" * 50)

    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 10
    print("  [통과] 기본 페이지네이션 테스트 (10개 반환)")

    response = client.get("/items?skip=5&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "상품_6"
    print("  [통과] skip/limit 페이지네이션 테스트")

    response = client.get("/items/count?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 20
    assert data["count"] == 5
    print("  [통과] 카운트 엔드포인트 테스트")

    response = client.get("/items/count")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 20
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert data["count"] == 10
    print("  [통과] 카운트 기본값 테스트")

    # 문제 2 테스트
    print()
    print("=" * 50)
    print("문제 2: 공통 필터링 의존성 테스트")
    print("=" * 50)

    response = client.get("/items/search?min_price=5000&max_price=10000")
    assert response.status_code == 200
    data = response.json()
    assert data["total_filtered"] == 6
    print("  [통과] 가격 필터링 테스트")

    response = client.get("/items/search?keyword=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total_filtered"] == 11
    assert len(data["results"]) == 10
    print("  [통과] 키워드 필터링 테스트")

    response = client.get("/items/search?keyword=상품_2&min_price=0&max_price=5000")
    assert response.status_code == 200
    data = response.json()
    assert data["total_filtered"] == 1
    assert data["results"][0]["name"] == "상품_2"
    print("  [통과] 키워드 + 가격 복합 필터링 테스트")

    print()
    print("모든 테스트를 통과했습니다!")
