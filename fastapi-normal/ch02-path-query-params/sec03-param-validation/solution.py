# 섹션 03: 매개변수 검증 - 모범 답안
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from fastapi import FastAPI, Path, Query
from fastapi.testclient import TestClient

app = FastAPI()

# 더미 상품 데이터베이스
fake_items_db = {
    1: {"name": "노트북", "price": 1500000},
    2: {"name": "마우스", "price": 35000},
    3: {"name": "키보드", "price": 89000},
    4: {"name": "노트북 파우치", "price": 25000},
    5: {"name": "모니터", "price": 450000},
}


# GET /items/{item_id} 엔드포인트
# - Path()로 경로 매개변수에 검증 규칙을 추가합니다
# - Query()로 쿼리 매개변수에 검증 규칙을 추가합니다
# - *를 첫 번째 인자로 사용하면 이후 매개변수가 키워드 전용이 됩니다
#   이렇게 하면 기본값이 있는 Path()와 기본값이 없는 매개변수의 순서 문제를 해결합니다
@app.get("/items/{item_id}")
async def read_item(
    *,
    item_id: int = Path(
        title="상품 ID",
        ge=1,       # 1 이상 (greater than or equal)
        le=10000,   # 10000 이하 (less than or equal)
    ),
    q: str | None = Query(
        default=None,       # 기본값 None -> 선택적 매개변수
        title="검색 키워드",
        min_length=2,       # 최소 2글자
        max_length=50,      # 최대 50글자
    ),
):
    """
    상품을 조회합니다.

    - item_id: 1~10000 범위의 정수 (경로 매개변수)
    - q: 2~50글자 검색 키워드 (쿼리 매개변수, 선택)
    """
    # 상품 조회
    if item_id in fake_items_db:
        result = dict(fake_items_db[item_id])  # 원본 데이터를 변경하지 않도록 복사
    else:
        result = {"error": "상품을 찾을 수 없습니다"}

    # q가 주어지면 결과에 추가
    if q:
        result["q"] = q

    return result


# GET /items 엔드포인트
# - 모든 쿼리 매개변수에 Query()를 사용하여 검증 규칙을 적용합니다
# - ge (greater than or equal): 이상
# - le (less than or equal): 이하
# - min_length: 최소 문자열 길이
# - max_length: 최대 문자열 길이
@app.get("/items")
async def list_items(
    skip: int = Query(
        default=0,
        ge=0,               # 0 이상 (음수 불가)
    ),
    limit: int = Query(
        default=10,
        ge=1,               # 1 이상
        le=100,             # 100 이하
    ),
    min_price: int | None = Query(
        default=None,
        ge=0,               # 0 이상 (음수 불가)
    ),
    max_price: int | None = Query(
        default=None,
        ge=0,               # 0 이상 (음수 불가)
    ),
    name: str | None = Query(
        default=None,
        min_length=1,       # 최소 1글자
        max_length=100,     # 최대 100글자
    ),
):
    """
    상품 목록을 조회합니다 (검증 규칙 적용).

    - skip: 건너뛸 항목 수 (0 이상)
    - limit: 반환 항목 수 (1~100)
    - min_price: 최소 가격 필터 (0 이상, 선택)
    - max_price: 최대 가격 필터 (0 이상, 선택)
    - name: 상품명 검색 (1~100글자, 선택)
    """
    # 1단계: 딕셔너리 값을 리스트로 변환
    items = list(fake_items_db.values())

    # 2단계: 이름 필터링
    if name is not None:
        items = [item for item in items if name in item["name"]]

    # 3단계: 최소 가격 필터링
    if min_price is not None:
        items = [item for item in items if item["price"] >= min_price]

    # 4단계: 최대 가격 필터링
    if max_price is not None:
        items = [item for item in items if item["price"] <= max_price]

    # 전체 개수 (필터 후, 페이지네이션 전)
    total = len(items)

    # 5단계: 페이지네이션 적용
    paginated = items[skip : skip + limit]

    return {"items": paginated, "total": total}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # === 문제 1 테스트 ===

    # 테스트 1: 정상 상품 조회
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"name": "노트북", "price": 1500000}
    print("통과: /items/1 정상 조회")

    # 테스트 2: item_id 범위 미달 (0)
    response = client.get("/items/0")
    assert response.status_code == 422
    print("통과: /items/0 -> 422 (ge=1 위반)")

    # 테스트 3: q 최소 길이 미달
    response = client.get("/items/1?q=a")
    assert response.status_code == 422
    print("통과: /items/1?q=a -> 422 (min_length=2 위반)")

    # 테스트 4: q 정상 전달
    response = client.get("/items/1?q=검색어")
    assert response.status_code == 200
    data = response.json()
    assert data["q"] == "검색어"
    assert data["name"] == "노트북"
    print("통과: /items/1?q=검색어 정상 조회")

    # 테스트 5: 존재하지 않는 상품
    response = client.get("/items/999")
    assert response.status_code == 200
    assert response.json() == {"error": "상품을 찾을 수 없습니다"}
    print("통과: /items/999 상품 없음")

    # === 문제 2 테스트 ===

    # 테스트 6: 기본 목록 조회
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    print("통과: /items 기본 조회")

    # 테스트 7: limit 범위 위반 (0)
    response = client.get("/items?limit=0")
    assert response.status_code == 422
    print("통과: /items?limit=0 -> 422 (ge=1 위반)")

    # 테스트 8: skip 범위 위반 (-1)
    response = client.get("/items?skip=-1")
    assert response.status_code == 422
    print("통과: /items?skip=-1 -> 422 (ge=0 위반)")

    # 테스트 9: min_price 범위 위반
    response = client.get("/items?min_price=-100")
    assert response.status_code == 422
    print("통과: /items?min_price=-100 -> 422 (ge=0 위반)")

    # 테스트 10: 이름 + 가격 필터 복합 조건
    response = client.get("/items?name=노트북&min_price=100000")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "노트북"
    assert data["items"][0]["price"] >= 100000
    print("통과: /items?name=노트북&min_price=100000 복합 필터")

    # 테스트 11: 페이지네이션
    response = client.get("/items?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    print("통과: /items?skip=1&limit=2 페이지네이션")

    print("\n모든 테스트를 통과했습니다!")
