# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI, Depends, Query
from fastapi.testclient import TestClient

app = FastAPI()

# 가상 데이터
fake_items = [{"name": f"상품_{i}", "price": i * 1000} for i in range(1, 21)]


# ============================================================
# 문제 1: 공통 페이지네이션 의존성
# ============================================================

# TODO: common_pagination 의존성 함수를 작성하세요
# 매개변수: skip (int, 기본값 0, 최솟값 0), limit (int, 기본값 10, 최솟값 1, 최댓값 100)
# 반환값: {"skip": skip, "limit": limit}


# TODO: GET /items 엔드포인트를 작성하세요
# common_pagination 의존성을 사용하여 페이지네이션 적용
# 반환값: fake_items에서 skip부터 limit개만큼 슬라이싱한 결과


# TODO: GET /items/count 엔드포인트를 작성하세요
# common_pagination 의존성을 사용 (같은 의존성 재사용)
# 반환값: {"total": 전체 개수, "skip": skip, "limit": limit, "count": 슬라이싱된 개수}


# ============================================================
# 문제 2: 공통 필터링 의존성
# ============================================================

# TODO: common_filter 의존성 함수를 작성하세요
# 매개변수:
#   - keyword: str | None, 기본값 None (상품 이름 검색)
#   - min_price: int, 기본값 0 (최소 가격)
#   - max_price: int, 기본값 100000 (최대 가격)
# 반환값: {"keyword": keyword, "min_price": min_price, "max_price": max_price}


# TODO: GET /items/search 엔드포인트를 작성하세요
# common_filter와 common_pagination을 동시에 사용
# 1) fake_items에서 필터 조건에 맞는 항목만 선택
#    - keyword가 None이 아니면: 이름에 keyword가 포함된 항목만
#    - min_price <= price <= max_price 조건
# 2) 필터링된 결과에 페이지네이션 적용
# 반환값: {"results": 필터+페이지네이션 결과, "total_filtered": 필터만 적용한 전체 수}


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
    # 가격 5000~10000 사이: 상품_5(5000), 상품_6(6000), ..., 상품_10(10000) = 6개
    assert data["total_filtered"] == 6
    print("  [통과] 가격 필터링 테스트")

    response = client.get("/items/search?keyword=1")
    assert response.status_code == 200
    data = response.json()
    # 이름에 "1" 포함: 상품_1, 상품_10, 상품_11, ..., 상품_19 = 11개 (limit 10이므로 10개 반환)
    assert data["total_filtered"] == 11
    assert len(data["results"]) == 10
    print("  [통과] 키워드 필터링 테스트")

    response = client.get("/items/search?keyword=상품_2&min_price=0&max_price=5000")
    assert response.status_code == 200
    data = response.json()
    # 이름에 "상품_2" 포함 AND 가격 0~5000: 상품_2(2000) = 1개
    assert data["total_filtered"] == 1
    assert data["results"][0]["name"] == "상품_2"
    print("  [통과] 키워드 + 가격 복합 필터링 테스트")

    print()
    print("모든 테스트를 통과했습니다!")
