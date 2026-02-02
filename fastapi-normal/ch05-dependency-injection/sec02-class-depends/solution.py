# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

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
# 문제 1 해답: PaginationParams 클래스 의존성
# ============================================================

class PaginationParams:
    """
    페이지네이션 매개변수를 관리하는 클래스 의존성.
    apply() 메서드로 리스트에 페이지네이션을 적용하고,
    get_info() 메서드로 페이지네이션 메타 정보를 제공합니다.
    """

    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="건너뛸 항목 수"),
        limit: int = Query(default=10, ge=1, le=100, description="조회할 항목 수"),
    ):
        self.skip = skip
        self.limit = limit

    def apply(self, items: list) -> list:
        """리스트에 페이지네이션을 적용하여 슬라이싱된 결과를 반환"""
        return items[self.skip : self.skip + self.limit]

    def get_info(self, total: int) -> dict:
        """페이지네이션 메타 정보를 딕셔너리로 반환"""
        return {
            "total": total,
            "skip": self.skip,
            "limit": self.limit,
            "has_more": self.skip + self.limit < total,
        }


@app.get("/books")
def read_books(pagination: PaginationParams = Depends()):
    """
    도서 목록 조회 엔드포인트.
    PaginationParams 클래스 의존성을 사용합니다.
    Depends() 축약 문법으로 타입 힌트에서 자동 추론합니다.
    """
    return {
        "books": pagination.apply(fake_books),
        "pagination": pagination.get_info(len(fake_books)),
    }


# ============================================================
# 문제 2 해답: BookFilter 클래스 의존성
# ============================================================

class BookFilter:
    """
    도서 필터 클래스 의존성.
    장르, 가격 범위, 저자 이름으로 도서 목록을 필터링합니다.
    """

    def __init__(
        self,
        genre: str | None = Query(default=None, description="장르 필터"),
        min_price: int = Query(default=0, ge=0, description="최소 가격"),
        max_price: int = Query(default=100000, ge=0, description="최대 가격"),
        author: str | None = Query(default=None, description="저자 이름 검색"),
    ):
        self.genre = genre
        self.min_price = min_price
        self.max_price = max_price
        self.author = author

    def apply(self, books: list[dict]) -> list[dict]:
        """도서 목록에 필터 조건을 적용하여 반환"""
        result = books

        # 장르 필터: 정확히 일치하는 장르만 선택
        if self.genre is not None:
            result = [book for book in result if book["genre"] == self.genre]

        # 가격 범위 필터
        result = [
            book for book in result
            if self.min_price <= book["price"] <= self.max_price
        ]

        # 저자 필터: 저자 이름에 검색어가 포함된 항목 선택
        if self.author is not None:
            result = [
                book for book in result
                if self.author in book["author"]
            ]

        return result


@app.get("/books/search")
def search_books(
    book_filter: BookFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    """
    도서 검색 엔드포인트.
    BookFilter와 PaginationParams를 동시에 사용합니다.

    처리 순서:
    1. BookFilter로 필터 조건 적용
    2. 필터링된 결과에 PaginationParams 적용
    """
    # 1단계: 필터링
    filtered = book_filter.apply(fake_books)

    # 2단계: 페이지네이션 (필터링된 결과 기준)
    return {
        "books": pagination.apply(filtered),
        "pagination": pagination.get_info(len(filtered)),
    }


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
