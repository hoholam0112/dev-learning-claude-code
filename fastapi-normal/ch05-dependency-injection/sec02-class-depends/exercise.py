# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI, Depends, Query
from fastapi.testclient import TestClient

app = FastAPI()

# 가상 도서 데이터
fake_books = [
    {"id": 1, "title": "파이썬 기초", "author": "김작가", "genre": "프로그래밍", "price": 25000},
    {"id": 2, "title": "FastAPI 입문", "author": "이작가", "genre": "프로그래밍", "price": 30000},
    {"id": 3, "title": "데이터 분석", "author": "박작가", "genre": "프로그래밍", "price": 28000},
    {"id": 4, "title": "별의 여행", "author": "최소설가", "genre": "소설", "price": 15000},
    {"id": 5, "title": "바다의 노래", "author": "최소설가", "genre": "소설", "price": 18000},
    {"id": 6, "title": "산의 이야기", "author": "정소설가", "genre": "소설", "price": 16000},
    {"id": 7, "title": "한국사 개론", "author": "한역사가", "genre": "역사", "price": 22000},
    {"id": 8, "title": "세계사 탐험", "author": "한역사가", "genre": "역사", "price": 24000},
    {"id": 9, "title": "경제학 원론", "author": "강교수", "genre": "경제", "price": 35000},
    {"id": 10, "title": "주식 투자", "author": "강교수", "genre": "경제", "price": 20000},
    {"id": 11, "title": "요리의 기술", "author": "오셰프", "genre": "요리", "price": 19000},
    {"id": 12, "title": "건강한 식단", "author": "오셰프", "genre": "요리", "price": 17000},
]


# ============================================================
# 문제 1: PaginationParams 클래스 의존성
# ============================================================

# TODO: PaginationParams 클래스를 작성하세요
# __init__ 매개변수:
#   - skip: int, 기본값 0, 최솟값 0
#   - limit: int, 기본값 10, 최솟값 1, 최댓값 100
# 메서드:
#   - apply(items: list) -> list: 리스트에 페이지네이션 적용
#   - get_info(total: int) -> dict: {"total", "skip", "limit", "has_more"} 반환


# TODO: GET /books 엔드포인트를 작성하세요
# PaginationParams를 의존성으로 사용 (Depends() 축약 문법 권장)
# 반환값: {"books": 페이지네이션 적용된 도서 목록, "pagination": get_info 결과}


# ============================================================
# 문제 2: BookFilter 클래스 의존성
# ============================================================

# TODO: BookFilter 클래스를 작성하세요
# __init__ 매개변수:
#   - genre: str | None, 기본값 None (장르 필터)
#   - min_price: int, 기본값 0 (최소 가격)
#   - max_price: int, 기본값 100000 (최대 가격)
#   - author: str | None, 기본값 None (저자 이름 검색)
# 메서드:
#   - apply(books: list[dict]) -> list[dict]: 도서 목록에 필터 적용


# TODO: GET /books/search 엔드포인트를 작성하세요
# BookFilter와 PaginationParams를 동시에 의존성으로 사용
# 1) fake_books에 BookFilter 적용
# 2) 필터링된 결과에 PaginationParams 적용
# 반환값: {"books": 결과, "pagination": get_info 결과 (total은 필터링된 전체 수)}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 테스트
    print("=" * 50)
    print("문제 1: PaginationParams 클래스 의존성 테스트")
    print("=" * 50)

    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data["books"]) == 10
    assert data["pagination"]["total"] == 12
    assert data["pagination"]["has_more"] is True
    print("  [통과] 기본 도서 목록 조회 (10개, has_more: true)")

    response = client.get("/books?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["books"]) == 5
    assert data["pagination"]["has_more"] is True
    print("  [통과] limit=5 도서 목록 조회")

    response = client.get("/books?skip=10&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["books"]) == 2
    assert data["pagination"]["has_more"] is False
    print("  [통과] skip=10 도서 목록 조회 (남은 2개, has_more: false)")

    # 문제 2 테스트
    print()
    print("=" * 50)
    print("문제 2: BookFilter 클래스 의존성 테스트")
    print("=" * 50)

    response = client.get("/books/search?genre=소설")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 3
    assert all(book["genre"] == "소설" for book in data["books"])
    print("  [통과] 장르 필터링 테스트 (소설 3권)")

    response = client.get("/books/search?author=작가")
    assert response.status_code == 200
    data = response.json()
    # "작가"가 포함된 저자: 김작가, 이작가, 박작가 = 3명
    assert data["pagination"]["total"] == 3
    print("  [통과] 저자 필터링 테스트")

    response = client.get("/books/search?min_price=20000&max_price=30000")
    assert response.status_code == 200
    data = response.json()
    assert all(20000 <= book["price"] <= 30000 for book in data["books"])
    print("  [통과] 가격 범위 필터링 테스트")

    response = client.get("/books/search?genre=프로그래밍&min_price=28000")
    assert response.status_code == 200
    data = response.json()
    # 프로그래밍 장르 AND 가격 >= 28000: FastAPI 입문(30000), 데이터 분석(28000)
    assert data["pagination"]["total"] == 2
    print("  [통과] 장르 + 가격 복합 필터링 테스트")

    response = client.get("/books/search?genre=소설&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["books"]) == 2
    assert data["pagination"]["total"] == 3
    assert data["pagination"]["has_more"] is True
    print("  [통과] 필터링 + 페이지네이션 복합 테스트")

    print()
    print("모든 테스트를 통과했습니다!")
