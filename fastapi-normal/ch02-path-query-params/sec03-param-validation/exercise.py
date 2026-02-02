# 섹션 03: 매개변수 검증 - 연습 문제
# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

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


# TODO: GET /items/{item_id} 엔드포인트를 작성하세요
# 매개변수:
#   - item_id: int, Path() 사용
#     - title: "상품 ID"
#     - ge=1, le=10000
#   - q: str | None, Query() 사용
#     - default=None
#     - title: "검색 키워드"
#     - min_length=2, max_length=50
# 동작:
#   - fake_items_db에서 item_id로 상품 조회
#   - 상품이 없으면 {"error": "상품을 찾을 수 없습니다"} 반환
#   - q가 주어지면 결과 딕셔너리에 "q": q 추가
# 힌트: *를 첫 번째 매개변수로 사용하면 순서 문제를 해결할 수 있습니다


# TODO: GET /items 엔드포인트를 작성하세요
# 매개변수:
#   - skip: int, Query() 사용, default=0, ge=0
#   - limit: int, Query() 사용, default=10, ge=1, le=100
#   - min_price: int | None, Query() 사용, default=None, ge=0
#   - max_price: int | None, Query() 사용, default=None, ge=0
#   - name: str | None, Query() 사용, default=None, min_length=1, max_length=100
# 동작:
#   1. fake_items_db의 값들을 리스트로 변환
#   2. name이 주어지면 상품 이름에 name이 포함된 항목만 필터링
#   3. min_price가 주어지면 해당 가격 이상인 항목만 포함
#   4. max_price가 주어지면 해당 가격 이하인 항목만 포함
#   5. skip과 limit 적용
#   6. 반환: {"items": [...], "total": 전체개수(필터 후, 페이지네이션 전)}


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
