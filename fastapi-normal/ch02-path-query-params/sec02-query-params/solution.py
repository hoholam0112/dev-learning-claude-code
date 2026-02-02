# 섹션 02: 쿼리 매개변수 - 모범 답안
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

# 더미 상품 데이터베이스
fake_items_db = [
    {"id": 1, "name": "노트북", "price": 1500000},
    {"id": 2, "name": "마우스", "price": 35000},
    {"id": 3, "name": "키보드", "price": 89000},
    {"id": 4, "name": "노트북 파우치", "price": 25000},
    {"id": 5, "name": "모니터", "price": 450000},
]


# GET /items 엔드포인트
# - 경로에 포함되지 않은 매개변수는 자동으로 쿼리 매개변수로 인식됩니다
# - 기본값이 있으므로 모두 선택적 매개변수입니다
# - q: str | None = None 은 "선택적 문자열 매개변수"를 의미합니다
@app.get("/items")
async def read_items(
    skip: int = 0,
    limit: int = 10,
    q: str | None = None,
):
    """
    상품 목록을 조회합니다.

    - skip: 건너뛸 항목 수 (기본값: 0)
    - limit: 반환할 최대 항목 수 (기본값: 10)
    - q: 검색 키워드 (선택)
    """
    # 1단계: 키워드 필터링
    results = fake_items_db
    if q:
        results = [item for item in results if q in item["name"]]

    # 전체 개수 (필터링 후, 페이지네이션 전)
    total = len(results)

    # 2단계: 페이지네이션 적용
    paginated = results[skip : skip + limit]

    return {"items": paginated, "total": total}


# GET /items/search 엔드포인트
# - q: str 은 기본값이 없으므로 필수 매개변수입니다
# - min_price, max_price는 None이 기본값이므로 선택적입니다
# - "is not None"으로 값이 전달되었는지 확인합니다
@app.get("/items/search")
async def search_items(
    q: str,
    min_price: int | None = None,
    max_price: int | None = None,
):
    """
    상품을 검색합니다.

    - q: 검색 키워드 (필수)
    - min_price: 최소 가격 (선택)
    - max_price: 최대 가격 (선택)
    """
    # 1단계: 이름으로 필터링
    results = fake_items_db
    if q:
        results = [item for item in results if q in item["name"]]

    # 2단계: 최소 가격 필터링
    if min_price is not None:
        results = [item for item in results if item["price"] >= min_price]

    # 3단계: 최대 가격 필터링
    if max_price is not None:
        results = [item for item in results if item["price"] <= max_price]

    return {"query": q, "results": results}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 1: 기본 상품 목록 조회
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    print("통과: /items 기본 조회")

    # 테스트 2: 페이지네이션
    response = client.get("/items?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == 2  # 두 번째 상품부터
    print("통과: /items?skip=1&limit=2 페이지네이션")

    # 테스트 3: 키워드 검색
    response = client.get("/items?q=노트북")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # "노트북", "노트북 파우치"
    for item in data["items"]:
        assert "노트북" in item["name"]
    print("통과: /items?q=노트북 키워드 검색")

    # 테스트 4: 필수 매개변수 검색
    response = client.get("/items/search?q=노트북")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "노트북"
    assert len(data["results"]) == 2
    print("통과: /items/search?q=노트북 필수 매개변수")

    # 테스트 5: 필수 매개변수 누락
    response = client.get("/items/search")
    assert response.status_code == 422
    print("통과: /items/search 필수 매개변수 누락 시 422")

    # 테스트 6: 가격 범위 필터
    response = client.get("/items/search?q=&min_price=30000&max_price=100000")
    assert response.status_code == 200
    data = response.json()
    for item in data["results"]:
        assert 30000 <= item["price"] <= 100000
    print("통과: 가격 범위 필터")

    print("\n모든 테스트를 통과했습니다!")
