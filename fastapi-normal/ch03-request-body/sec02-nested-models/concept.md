# sec02: 중첩 모델 (Nested Models)

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: sec01 (Pydantic 기본 모델) 완료
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

이 섹션을 완료하면 다음을 할 수 있습니다:

1. Pydantic 모델 안에 다른 Pydantic 모델을 중첩하여 사용할 수 있다
2. `list[Model]` 타입으로 모델의 리스트를 요청 본문에서 받을 수 있다
3. `dict` 타입과 모델을 조합하여 유연한 데이터 구조를 정의할 수 있다
4. 모델을 재사용하여 코드 중복을 줄일 수 있다

---

## 핵심 개념

### 1. 모델 안의 모델 (중첩 모델)

실제 API에서는 단순한 평면(flat) 구조보다 중첩된 데이터 구조가 훨씬 흔합니다.
예를 들어, 주문서에는 배송 주소가 포함되고, 배송 주소는 여러 필드로 구성됩니다.

```python
from pydantic import BaseModel, Field

class Address(BaseModel):
    """배송 주소 모델"""
    city: str = Field(..., description="도시")
    district: str = Field(..., description="구/군")
    detail: str = Field(..., description="상세 주소")
    zip_code: str = Field(..., min_length=5, max_length=6, description="우편번호")

class Order(BaseModel):
    """주문 모델 - Address를 내부 필드로 사용"""
    order_name: str
    shipping_address: Address  # 중첩 모델!
```

이렇게 정의하면 다음과 같은 JSON 요청 본문을 받을 수 있습니다:

```json
{
    "order_name": "홍길동의 주문",
    "shipping_address": {
        "city": "서울특별시",
        "district": "강남구",
        "detail": "테헤란로 123 4층",
        "zip_code": "06234"
    }
}
```

FastAPI와 Pydantic은 **중첩된 모델도 자동으로 검증**합니다.
`shipping_address` 안의 `zip_code`가 5글자 미만이면 422 에러가 발생합니다.

### 2. 리스트 타입: list[Model]

모델의 리스트를 필드로 사용할 수 있습니다. 주문에 여러 상품이 포함되는 경우가 대표적입니다.

```python
class OrderItem(BaseModel):
    """주문 상품 모델"""
    product_name: str
    quantity: int = Field(..., ge=1, description="수량 (1 이상)")
    unit_price: int = Field(..., gt=0, description="단가")

class Order(BaseModel):
    """주문 모델 - 여러 상품을 포함"""
    customer_name: str
    items: list[OrderItem] = Field(
        ...,
        min_length=1,       # 최소 1개의 상품은 있어야 함
        description="주문 상품 목록"
    )
    memo: str = ""
```

**요청 예시:**
```json
{
    "customer_name": "김철수",
    "items": [
        {"product_name": "노트북", "quantity": 1, "unit_price": 1500000},
        {"product_name": "마우스", "quantity": 2, "unit_price": 35000}
    ],
    "memo": "부재 시 경비실에 맡겨주세요"
}
```

### 3. 딕셔너리 타입: dict[str, T]

키-값 쌍의 데이터를 받을 때 `dict` 타입을 사용합니다.

```python
class ProductUpdate(BaseModel):
    """상품 정보 부분 업데이트 모델"""
    # 어떤 필드든 문자열 키 + 값 형태로 받기
    attributes: dict[str, str] = Field(
        default_factory=dict,
        description="상품 속성 (키-값 쌍)"
    )

    # 값이 특정 타입인 딕셔너리
    scores: dict[str, int] = Field(
        default_factory=dict,
        description="카테고리별 점수"
    )
```

**요청 예시:**
```json
{
    "attributes": {
        "color": "빨강",
        "size": "XL",
        "material": "면 100%"
    },
    "scores": {
        "품질": 9,
        "가격": 7,
        "디자인": 8
    }
}
```

### 4. 모델 재사용

같은 구조가 여러 곳에서 사용될 때, 모델을 분리하여 재사용합니다.

```python
class Address(BaseModel):
    """재사용 가능한 주소 모델"""
    city: str
    district: str
    detail: str
    zip_code: str

class CustomerCreate(BaseModel):
    """고객 생성 - 주소 재사용"""
    name: str
    home_address: Address
    office_address: Address | None = None  # 선택적 사무실 주소

class StoreCreate(BaseModel):
    """매장 생성 - 같은 주소 모델 재사용"""
    store_name: str
    location: Address
    manager_name: str
```

### 5. 복합 중첩 구조

여러 단계로 중첩된 복잡한 구조도 가능합니다.

```python
class Address(BaseModel):
    city: str
    detail: str
    zip_code: str

class OrderItem(BaseModel):
    product_name: str
    quantity: int = Field(..., ge=1)
    unit_price: int = Field(..., gt=0)

class Payment(BaseModel):
    method: str = Field(..., description="결제 수단 (card, cash, transfer)")
    amount: int = Field(..., gt=0)
    installment_months: int = Field(default=0, ge=0, le=24)

class Order(BaseModel):
    """
    완전한 주문 모델
    - Address, OrderItem, Payment를 모두 포함
    """
    customer_name: str
    shipping_address: Address       # 중첩 모델
    items: list[OrderItem]          # 모델 리스트
    payment: Payment                # 중첩 모델
    tags: list[str] = []            # 기본 타입 리스트
    metadata: dict[str, str] = {}   # 딕셔너리
```

**이 모델이 받는 JSON 구조:**
```json
{
    "customer_name": "홍길동",
    "shipping_address": {
        "city": "서울특별시",
        "detail": "강남구 테헤란로 123",
        "zip_code": "06234"
    },
    "items": [
        {"product_name": "노트북", "quantity": 1, "unit_price": 1500000},
        {"product_name": "충전기", "quantity": 1, "unit_price": 89000}
    ],
    "payment": {
        "method": "card",
        "amount": 1589000,
        "installment_months": 3
    },
    "tags": ["긴급", "선물포장"],
    "metadata": {"coupon_code": "WELCOME10"}
}
```

---

## 전체 흐름 다이어그램

```
클라이언트 요청 (JSON)
    │
    │  {
    │    "customer_name": "홍길동",
    │    "shipping_address": { ... },    ← Address 모델로 검증
    │    "items": [ {...}, {...} ],       ← list[OrderItem]으로 검증
    │    "payment": { ... }              ← Payment 모델로 검증
    │  }
    │
    ▼
┌─────────────────────────────────┐
│     Pydantic 재귀적 검증         │
│                                 │
│  1단계: Order 모델 검증          │
│    ├─ customer_name: str ✓      │
│    ├─ shipping_address → 2단계   │
│    ├─ items → 3단계              │
│    └─ payment → 4단계            │
│                                 │
│  2단계: Address 모델 검증        │
│    ├─ city: str ✓               │
│    ├─ detail: str ✓             │
│    └─ zip_code: str ✓           │
│                                 │
│  3단계: 각 OrderItem 검증        │
│    ├─ [0] product_name ✓        │
│    │      quantity >= 1 ✓       │
│    │      unit_price > 0 ✓      │
│    └─ [1] ... (동일 검증)        │
│                                 │
│  4단계: Payment 모델 검증        │
│    ├─ method: str ✓             │
│    ├─ amount > 0 ✓              │
│    └─ installment_months ✓      │
└─────────────┬───────────────────┘
              │
         모든 검증 통과
              │
              ▼
    핸들러 함수에서 안전하게 사용
```

---

## 실전 코드 예제: 주문서 API

```python
"""
주문서 API - 중첩 모델 활용 예제
실행: uvicorn example_order:app --reload
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="주문 관리 API", version="1.0.0")


# --- 모델 정의 ---

class Address(BaseModel):
    """배송 주소"""
    city: str = Field(..., min_length=1, description="도시")
    district: str = Field(..., min_length=1, description="구/군")
    detail: str = Field(..., min_length=1, description="상세 주소")
    zip_code: str = Field(..., min_length=5, max_length=6, description="우편번호")


class OrderItem(BaseModel):
    """주문 상품"""
    product_name: str = Field(..., min_length=1, description="상품명")
    quantity: int = Field(..., ge=1, le=100, description="수량")
    unit_price: int = Field(..., gt=0, description="단가 (원)")


class OrderCreate(BaseModel):
    """주문 생성 요청"""
    customer_name: str = Field(..., min_length=2, description="주문자 이름")
    shipping_address: Address = Field(..., description="배송지")
    items: list[OrderItem] = Field(..., min_length=1, description="주문 상품 목록")
    memo: Optional[str] = Field(default=None, max_length=200, description="배송 메모")


# --- 인메모리 저장소 ---
orders_db: list[dict] = []
next_order_id: int = 1


# --- 엔드포인트 ---

@app.post("/orders")
async def create_order(order: OrderCreate):
    """
    새 주문을 생성합니다.
    중첩된 모든 모델(Address, OrderItem)이 자동으로 검증됩니다.
    """
    global next_order_id

    # 총액 계산
    total_amount = sum(
        item.quantity * item.unit_price for item in order.items
    )

    order_dict = order.model_dump()
    order_dict["id"] = next_order_id
    order_dict["total_amount"] = total_amount
    order_dict["item_count"] = len(order.items)
    next_order_id += 1

    orders_db.append(order_dict)

    return {
        "message": "주문이 생성되었습니다",
        "order": order_dict
    }


@app.get("/orders")
async def list_orders():
    """모든 주문을 조회합니다."""
    return {"orders": orders_db, "total": len(orders_db)}
```

---

## 주의 사항

### 1. 중첩 모델의 검증 오류 위치

중첩 모델에서 검증 오류가 발생하면, 오류 위치(`loc`)에 중첩 경로가 포함됩니다:

```json
{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "shipping_address", "zip_code"],
            "msg": "String should have at least 5 characters",
            "input": "123"
        }
    ]
}
```

`loc` 배열의 `["body", "shipping_address", "zip_code"]`를 통해
정확히 어느 위치에서 오류가 발생했는지 알 수 있습니다.

### 2. 빈 리스트 주의

```python
class Order(BaseModel):
    # 주의: 이렇게 하면 빈 리스트도 허용됩니다
    items: list[OrderItem] = []

    # 최소 1개를 보장하려면 min_length를 사용하세요
    items: list[OrderItem] = Field(..., min_length=1)
```

### 3. 순환 참조 주의

모델이 서로를 참조하는 순환 구조는 피해야 합니다:

```python
# 주의: 순환 참조 (피해야 함)
class Parent(BaseModel):
    children: list["Child"]    # Child가 아직 정의되지 않음

class Child(BaseModel):
    parent: Parent             # 순환 참조!
```

순환 참조가 필요한 경우 `Optional`과 `model_rebuild()`를 활용할 수 있지만,
일반적으로 설계를 변경하여 피하는 것이 좋습니다.

---

## 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| 중첩 모델 | 모델 안에 다른 모델을 필드로 사용 | `address: Address` |
| 모델 리스트 | 모델의 리스트를 필드로 사용 | `items: list[OrderItem]` |
| 딕셔너리 | 키-값 쌍을 필드로 사용 | `metadata: dict[str, str]` |
| 모델 재사용 | 같은 모델을 여러 곳에서 활용 | `Address`를 여러 모델에서 사용 |
| 재귀적 검증 | 중첩된 모든 단계에서 자동 검증 | 깊은 구조도 한 번에 검증 |

---

## 다음 단계

[sec03: 폼 데이터와 파일 업로드](../sec03-form-and-file/concept.md)에서 JSON이 아닌 폼 데이터와 파일을 처리하는 방법을 학습합니다.
