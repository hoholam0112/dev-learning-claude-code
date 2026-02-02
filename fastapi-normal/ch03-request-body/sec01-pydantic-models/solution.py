"""
sec01 모범 답안: Pydantic 기본 모델
실행: uvicorn solution:app --reload
테스트: python solution.py
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


# ============================================================
# 문제 1: 사용자 등록 API
# ============================================================

class User(BaseModel):
    """
    사용자 등록 요청 모델

    각 필드에 Field를 사용하여 유효성 검사 규칙을 설정합니다.
    - min_length / max_length: 문자열의 최소/최대 길이
    - ge (greater than or equal): 이상
    - le (less than or equal): 이하
    """
    name: str = Field(
        ...,                    # ... 은 필수 필드를 의미합니다
        min_length=2,           # 최소 2글자
        max_length=50,          # 최대 50글자
        description="사용자 이름"
    )
    email: str = Field(
        ...,
        description="이메일 주소"
    )
    age: int = Field(
        ...,
        ge=0,                   # 0 이상
        le=150,                 # 150 이하
        description="나이"
    )
    nickname: Optional[str] = Field(
        default=None,           # 기본값 None (선택 필드)
        description="닉네임 (선택사항)"
    )


@app.post("/users")
async def register_user(user: User):
    """
    사용자를 등록합니다.

    FastAPI가 요청 본문을 자동으로 User 모델로 변환하고 검증합니다.
    검증에 실패하면 422 Unprocessable Entity 에러가 자동으로 반환됩니다.
    """
    # model_dump()로 Pydantic 모델을 딕셔너리로 변환합니다
    # (Pydantic v1에서는 .dict() 메서드를 사용했습니다)
    return {
        "message": "사용자가 등록되었습니다",
        "user": user.model_dump()
    }


# ============================================================
# 문제 2: 상품 리뷰 API (심화)
# ============================================================

class ProductReview(BaseModel):
    """
    상품 리뷰 요청 모델

    다양한 Field 검증 규칙을 조합하여 사용합니다.
    """
    product_id: int = Field(
        ...,
        ge=1,                   # 상품 ID는 1 이상
        description="리뷰 대상 상품 ID"
    )
    rating: int = Field(
        ...,
        ge=1,                   # 최소 1점
        le=5,                   # 최대 5점
        description="별점 (1~5)"
    )
    title: str = Field(
        ...,
        min_length=5,           # 제목은 최소 5글자
        max_length=100,         # 최대 100글자
        description="리뷰 제목"
    )
    content: str = Field(
        default="",             # 기본값은 빈 문자열
        max_length=1000,        # 최대 1000글자
        description="리뷰 내용 (선택사항)"
    )
    reviewer_name: str = Field(
        ...,
        min_length=2,           # 이름은 최소 2글자
        max_length=30,          # 최대 30글자
        description="작성자 이름"
    )


@app.post("/reviews")
async def create_review(review: ProductReview):
    """
    상품 리뷰를 등록합니다.

    rating, title 등 모든 필드가 Field에 정의된 규칙에 따라 자동 검증됩니다.
    """
    return {
        "message": "리뷰가 등록되었습니다",
        "review": review.model_dump()
    }


# ============================================================
# 테스트 코드
# ============================================================
if __name__ == "__main__":
    client = TestClient(app)

    print("=" * 50)
    print("문제 1: 사용자 등록 API 테스트")
    print("=" * 50)

    # 테스트 1-1: 정상 요청
    response = client.post("/users", json={
        "name": "홍길동",
        "email": "hong@example.com",
        "age": 25
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "사용자가 등록되었습니다"
    assert data["user"]["name"] == "홍길동"
    assert data["user"]["nickname"] is None
    print("[PASS] 정상 사용자 등록 테스트 통과")

    # 테스트 1-2: 닉네임 포함 요청
    response = client.post("/users", json={
        "name": "김철수",
        "email": "kim@example.com",
        "age": 30,
        "nickname": "철수짱"
    })
    assert response.status_code == 200
    assert response.json()["user"]["nickname"] == "철수짱"
    print("[PASS] 닉네임 포함 등록 테스트 통과")

    # 테스트 1-3: 유효성 검사 실패 (이름 너무 짧음)
    response = client.post("/users", json={
        "name": "A",
        "email": "test@test.com",
        "age": 25
    })
    assert response.status_code == 422
    print("[PASS] 이름 길이 검증 테스트 통과")

    # 테스트 1-4: 유효성 검사 실패 (나이 범위 초과)
    response = client.post("/users", json={
        "name": "테스트",
        "email": "test@test.com",
        "age": 200
    })
    assert response.status_code == 422
    print("[PASS] 나이 범위 검증 테스트 통과")

    # 테스트 1-5: 유효성 검사 실패 (필수 필드 누락)
    response = client.post("/users", json={
        "name": "테스트"
    })
    assert response.status_code == 422
    print("[PASS] 필수 필드 누락 검증 테스트 통과")

    print()
    print("=" * 50)
    print("문제 2: 상품 리뷰 API 테스트")
    print("=" * 50)

    # 테스트 2-1: 정상 리뷰 등록
    response = client.post("/reviews", json={
        "product_id": 1,
        "rating": 5,
        "title": "정말 좋은 상품입니다",
        "content": "배송도 빠르고 품질도 좋아요.",
        "reviewer_name": "홍길동"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "리뷰가 등록되었습니다"
    assert data["review"]["rating"] == 5
    print("[PASS] 정상 리뷰 등록 테스트 통과")

    # 테스트 2-2: content 생략 (기본값 사용)
    response = client.post("/reviews", json={
        "product_id": 2,
        "rating": 3,
        "title": "보통입니다 그냥 그래요",
        "reviewer_name": "김철수"
    })
    assert response.status_code == 200
    assert response.json()["review"]["content"] == ""
    print("[PASS] content 기본값 테스트 통과")

    # 테스트 2-3: 유효성 검사 실패 (별점 범위 초과)
    response = client.post("/reviews", json={
        "product_id": 1,
        "rating": 6,
        "title": "별점 테스트 리뷰입니다",
        "reviewer_name": "테스터"
    })
    assert response.status_code == 422
    print("[PASS] 별점 범위 검증 테스트 통과")

    # 테스트 2-4: 유효성 검사 실패 (제목 너무 짧음)
    response = client.post("/reviews", json={
        "product_id": 1,
        "rating": 4,
        "title": "짧음",
        "reviewer_name": "테스터"
    })
    assert response.status_code == 422
    print("[PASS] 제목 길이 검증 테스트 통과")

    print()
    print("=" * 50)
    print("모든 테스트를 통과했습니다!")
    print("=" * 50)
