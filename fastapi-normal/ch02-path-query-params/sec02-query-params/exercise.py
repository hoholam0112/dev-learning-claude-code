# 섹션 02: 쿼리 매개변수 - 연습 문제
# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

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


# TODO: GET /items 엔드포인트를 작성하세요
# 매개변수:
#   - skip: int (기본값 0) - 건너뛸 항목 수
#   - limit: int (기본값 10) - 반환할 최대 항목 수
#   - q: str | None (기본값 None) - 검색 키워드
# 동작:
#   1. q가 주어지면 상품 이름에 q가 포함된 항목만 필터링
#   2. 필터링 결과에 skip, limit 적용
#   3. 반환: {"items": [...], "total": 전체개수(필터링 후)}


# TODO: GET /items/search 엔드포인트를 작성하세요
# 매개변수:
#   - q: str (필수) - 검색 키워드
#   - min_price: int | None (기본값 None) - 최소 가격
#   - max_price: int | None (기본값 None) - 최대 가격
# 동작:
#   1. q로 상품 이름 필터링 (q가 이름에 포함된 항목)
#   2. min_price가 주어지면 해당 가격 이상인 상품만 포함
#   3. max_price가 주어지면 해당 가격 이하인 상품만 포함
#   4. 반환: {"query": q, "results": [...]}


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
