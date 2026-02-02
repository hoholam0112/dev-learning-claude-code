"""
sec02 모범 답안: 중첩 모델
실행: uvicorn solution:app --reload
테스트: python solution.py
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()


# ============================================================
# 모델 정의
# ============================================================

class Address(BaseModel):
    """
    배송 주소 모델

    주문의 하위 모델로 사용됩니다.
    zip_code는 정확히 5자리여야 합니다.
    """
    city: str = Field(
        ...,
        min_length=1,
        description="도시"
    )
    street: str = Field(
        ...,
        min_length=1,
        description="도로명 주소"
    )
    zip_code: str = Field(
        ...,
        min_length=5,       # 최소 5자
        max_length=5,       # 최대 5자 → 정확히 5자
        description="우편번호 (5자리)"
    )


class OrderItem(BaseModel):
    """
    주문 상품 모델

    각 주문에 포함되는 개별 상품 정보입니다.
    수량은 1 이상, 단가는 100원 이상이어야 합니다.
    """
    product_name: str = Field(
        ...,
        min_length=1,
        description="상품명"
    )
    quantity: int = Field(
        ...,
        ge=1,               # 수량은 1 이상
        description="수량"
    )
    unit_price: int = Field(
        ...,
        ge=100,             # 최소 금액 100원
        description="단가 (원)"
    )


class OrderCreate(BaseModel):
    """
    주문 생성 요청 모델

    중첩 모델의 핵심 예제입니다:
    - address: Address 모델을 필드로 사용 (중첩 모델)
    - items: OrderItem 모델의 리스트를 필드로 사용 (모델 리스트)
    """
    customer_name: str = Field(
        ...,
        min_length=2,
        description="주문자 이름"
    )
    address: Address = Field(
        ...,
        description="배송지 주소"
    )
    items: list[OrderItem] = Field(
        ...,
        min_length=1,       # 최소 1개의 상품이 필요
        description="주문 상품 목록"
    )
    note: Optional[str] = Field(
        default=None,
        max_length=300,
        description="배송 메모 (선택사항)"
    )


# ============================================================
# 엔드포인트
# ============================================================

@app.post("/orders")
async def create_order(order: OrderCreate):
    """
    주문을 생성합니다.

    중첩된 모든 모델 (Address, OrderItem)이 자동으로 검증됩니다.
    총액은 각 상품의 (수량 x 단가)를 합산하여 계산합니다.
    """
    # 총액 계산: 각 상품의 quantity * unit_price를 합산
    total_amount = sum(
        item.quantity * item.unit_price
        for item in order.items
    )

    return {
        "message": "주문이 생성되었습니다",
        "order": order.model_dump(),
        "total_amount": total_amount
    }


# ============================================================
# 테스트 코드
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
    assert data["total_amount"] == 1500000 + (2 * 35000)
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
