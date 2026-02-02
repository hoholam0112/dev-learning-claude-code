"""
sec01 연습 문제: Pydantic 기본 모델
실행: uvicorn exercise:app --reload
테스트: python exercise.py
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


# ============================================================
# 문제 1: 사용자 등록 API
# ============================================================

# TODO: User 모델을 정의하세요
# - name: str (필수, 최소 2자, 최대 50자)
# - email: str (필수)
# - age: int (필수, 0 이상 150 이하)
# - nickname: Optional[str] (선택, 기본값 None)


# TODO: POST /users 엔드포인트를 작성하세요
# User 모델을 요청 본문으로 받습니다
# 반환값: {"message": "사용자가 등록되었습니다", "user": {받은 사용자 데이터}}


# ============================================================
# 문제 2: 상품 리뷰 API (심화)
# ============================================================

# TODO: ProductReview 모델을 정의하세요
# - product_id: int (필수, 1 이상)
# - rating: int (필수, 1 이상 5 이하)
# - title: str (필수, 최소 5자, 최대 100자)
# - content: str (선택, 기본값 "", 최대 1000자)
# - reviewer_name: str (필수, 최소 2자, 최대 30자)


# TODO: POST /reviews 엔드포인트를 작성하세요
# ProductReview 모델을 요청 본문으로 받습니다
# 반환값: {"message": "리뷰가 등록되었습니다", "review": {받은 리뷰 데이터}}


# ============================================================
# 테스트 코드 (수정하지 마세요)
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
