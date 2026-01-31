# 실행 방법: uvicorn example-02:app --reload
# 파라미터 유효성 검증 예제 - Path()와 Query() 활용

from typing import Optional

from fastapi import FastAPI, Path, Query

app = FastAPI(title="파라미터 검증 API", description="Path/Query 유효성 검증 예제")


@app.get("/users/{user_id}", tags=["사용자"])
def get_user(
    user_id: int = Path(
        ...,
        title="사용자 ID",
        description="조회할 사용자의 고유 번호 (1 이상)",
        ge=1,
        le=100000,
        examples=[1, 42, 1000],
    ),
):
    """사용자를 조회합니다.

    user_id는 1 이상 100,000 이하의 정수만 허용됩니다.
    범위를 벗어나면 422 에러가 반환됩니다.
    """
    return {"user_id": user_id, "name": f"사용자_{user_id}"}


@app.get("/search", tags=["검색"])
def search(
    keyword: str = Query(
        ...,
        min_length=2,
        max_length=50,
        title="검색 키워드",
        description="2~50자 사이의 검색어를 입력하세요",
    ),
    page: int = Query(
        default=1,
        ge=1,
        le=1000,
        title="페이지 번호",
        description="조회할 페이지 번호 (1~1000)",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        title="페이지 크기",
        description="한 페이지에 표시할 항목 수 (1~100)",
    ),
):
    """검색을 수행합니다.

    - keyword: 필수, 2~50자
    - page: 선택적, 기본값 1
    - page_size: 선택적, 기본값 20
    """
    return {
        "keyword": keyword,
        "page": page,
        "page_size": page_size,
        "message": f"'{keyword}' 검색 결과 (페이지 {page})",
    }


@app.get("/products/{product_id}/reviews", tags=["리뷰"])
def get_product_reviews(
    product_id: int = Path(
        ...,
        title="상품 ID",
        ge=1,
    ),
    rating: Optional[int] = Query(
        default=None,
        ge=1,
        le=5,
        title="별점 필터",
        description="1~5 사이의 별점으로 필터링",
    ),
    sort_by: str = Query(
        default="newest",
        pattern="^(newest|oldest|highest|lowest)$",
        title="정렬 기준",
        description="newest(최신순), oldest(오래된순), highest(높은평점), lowest(낮은평점)",
    ),
):
    """상품 리뷰를 조회합니다.

    경로 파라미터와 쿼리 파라미터를 조합하여 사용하는 예제입니다.
    sort_by는 정규식 패턴으로 허용 값을 제한합니다.
    """
    return {
        "product_id": product_id,
        "rating_filter": rating,
        "sort_by": sort_by,
        "reviews": [
            {"user": "사용자A", "rating": 5, "comment": "훌륭합니다!"},
            {"user": "사용자B", "rating": 4, "comment": "만족합니다."},
        ],
    }


@app.get("/validate/email", tags=["검증"])
def validate_email(
    email: str = Query(
        ...,
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        title="이메일 주소",
        description="유효한 이메일 형식을 입력하세요",
        examples=["user@example.com", "test@gmail.com"],
    ),
):
    """이메일 형식을 검증합니다.

    정규식 패턴을 사용하여 이메일 형식을 검증하는 예제입니다.
    """
    return {"email": email, "valid": True}
