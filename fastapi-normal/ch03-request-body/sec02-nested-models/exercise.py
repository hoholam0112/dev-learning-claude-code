"""
sec02 연습 문제: 중첩 모델
실행: uvicorn exercise:app --reload
테스트: python exercise.py
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


# ============================================================
# 문제: 주문 생성 API
# ============================================================

# TODO: Address 모델을 정의하세요
# - city: str (필수, 최소 1자)
# - street: str (필수, 최소 1자)
# - zip_code: str (필수, 정확히 5자: min_length=5, max_length=5)


# TODO: OrderItem 모델을 정의하세요
# - product_name: str (필수, 최소 1자)
# - quantity: int (필수, 1 이상)
# - unit_price: int (필수, 100 이상)


# TODO: OrderCreate 모델을 정의하세요
# - customer_name: str (필수, 최소 2자)
# - address: Address (필수, 중첩 모델)
# - items: list[OrderItem] (필수, 최소 1개)
# - note: Optional[str] (선택, 기본값 None, 최대 300자)


# TODO: POST /orders 엔드포인트를 작성하세요
# OrderCreate 모델을 요청 본문으로 받습니다
# 총액(total_amount)을 계산합니다: 각 상품의 quantity * unit_price의 합
# 반환값: {
#     "message": "주문이 생성되었습니다",
#     "order": {받은 주문 데이터},
#     "total_amount": 계산된 총액
# }


# ============================================================
# 테스트 코드 (수정하지 마세요)
# ============================================================
if __name__ == "__main__":
    client = TestClient(app)

    print("=" * 50)
    print("중첩 모델: 주문 생성 API 테스트")
    print("=" * 50)

    # 테스트 1: 정상 주문 (상품 2개)
    response = client.post("/orders", json={
        "customer_name": "홍길동",
        "address": {
            "city": "서울특별시",
            "street": "강남구 테헤란로 123",
            "zip_code": "06234"
        },
        "items": [
            {"product_name": "노트북", "quantity": 1, "unit_price": 1500000},
            {"product_name": "마우스", "quantity": 2, "unit_price": 35000}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "주문이 생성되었습니다"
    assert data["total_amount"] == 1500000 + (2 * 35000)  # 1,570,000
    assert data["order"]["customer_name"] == "홍길동"
    assert data["order"]["address"]["city"] == "서울특별시"
    assert len(data["order"]["items"]) == 2
    print(f"[PASS] 정상 주문 테스트 통과 (총액: {data['total_amount']:,}원)")

    # 테스트 2: 배송 메모 포함 주문
    response = client.post("/orders", json={
        "customer_name": "김철수",
        "address": {
            "city": "부산광역시",
            "street": "해운대구 마린시티로 45",
            "zip_code": "48099"
        },
        "items": [
            {"product_name": "키보드", "quantity": 1, "unit_price": 150000}
        ],
        "note": "부재 시 경비실에 맡겨주세요"
    })
    assert response.status_code == 200
    assert response.json()["order"]["note"] == "부재 시 경비실에 맡겨주세요"
    print("[PASS] 배송 메모 포함 주문 테스트 통과")

    # 테스트 3: 빈 상품 목록 -> 422
    response = client.post("/orders", json={
        "customer_name": "테스트",
        "address": {
            "city": "서울",
            "street": "테스트로 1",
            "zip_code": "12345"
        },
        "items": []
    })
    assert response.status_code == 422
    print("[PASS] 빈 상품 목록 검증 테스트 통과")

    # 테스트 4: 잘못된 우편번호 (5자리가 아님)
    response = client.post("/orders", json={
        "customer_name": "테스트",
        "address": {
            "city": "서울",
            "street": "테스트로 1",
            "zip_code": "123"
        },
        "items": [
            {"product_name": "테스트 상품", "quantity": 1, "unit_price": 1000}
        ]
    })
    assert response.status_code == 422
    print("[PASS] 우편번호 길이 검증 테스트 통과")

    # 테스트 5: 수량 0인 상품
    response = client.post("/orders", json={
        "customer_name": "테스트",
        "address": {
            "city": "서울",
            "street": "테스트로 1",
            "zip_code": "12345"
        },
        "items": [
            {"product_name": "테스트 상품", "quantity": 0, "unit_price": 1000}
        ]
    })
    assert response.status_code == 422
    print("[PASS] 수량 범위 검증 테스트 통과")

    # 테스트 6: note 기본값 확인
    response = client.post("/orders", json={
        "customer_name": "테스트유저",
        "address": {
            "city": "대전",
            "street": "유성구 대학로 99",
            "zip_code": "34141"
        },
        "items": [
            {"product_name": "볼펜", "quantity": 10, "unit_price": 500}
        ]
    })
    assert response.status_code == 200
    assert response.json()["order"]["note"] is None
    print("[PASS] note 기본값(None) 테스트 통과")

    print()
    print("=" * 50)
    print("모든 테스트를 통과했습니다!")
    print("=" * 50)
