# sec01: Pydantic 기본 모델

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: Ch02 경로/쿼리 매개변수 완료, Python 타입 어노테이션 기초
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

이 섹션을 완료하면 다음을 할 수 있습니다:

1. Pydantic `BaseModel`을 정의하여 요청 본문의 구조를 선언할 수 있다
2. `Field`를 사용하여 필드별 유효성 검사 규칙을 설정할 수 있다
3. 타입 어노테이션, 기본값, `Optional` 필드를 적절히 활용할 수 있다
4. 유효성 검사 실패 시 FastAPI가 자동으로 반환하는 오류 응답을 이해할 수 있다

---

## 핵심 개념

### 1. BaseModel이란?

`BaseModel`은 Pydantic이 제공하는 기본 클래스로, 이를 상속하면 **데이터 모델**을 정의할 수 있습니다.
FastAPI에서 이 모델을 엔드포인트 함수의 매개변수 타입으로 지정하면,
요청 본문(JSON)이 자동으로 해당 모델의 인스턴스로 변환됩니다.

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False  # 기본값 설정
```

위 코드에서:
- `name: str` - 필수 문자열 필드
- `price: float` - 필수 실수 필드
- `is_offer: bool = False` - 선택 필드 (기본값: False)

### 2. 요청 본문으로 사용하기

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None  # Python 3.10+ 문법
    price: float
    tax: float = 0.0

@app.post("/items")
async def create_item(item: Item):
    """
    FastAPI가 자동으로:
    1. 요청 본문의 JSON을 읽습니다
    2. 각 필드의 타입을 검증합니다
    3. Item 인스턴스를 생성합니다
    4. 검증 실패 시 422 에러를 반환합니다
    """
    item_dict = item.model_dump()  # Pydantic v2 문법
    if item.tax > 0:
        item_dict["price_with_tax"] = item.price + item.tax
    return item_dict
```

**요청 예시:**
```json
{
    "name": "맥북 프로",
    "description": "Apple M3 칩 탑재",
    "price": 2990000,
    "tax": 299000
}
```

### 3. Field를 사용한 유효성 검사

`Field`를 사용하면 각 필드에 대해 세밀한 검증 규칙을 설정할 수 있습니다.

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(
        ...,                    # ... 은 필수 필드를 의미
        min_length=2,           # 최소 길이
        max_length=100,         # 최대 길이
        description="상품명"     # API 문서에 표시되는 설명
    )
    price: int = Field(
        ...,
        gt=0,                   # 0보다 큼 (greater than)
        le=10_000_000,          # 10,000,000 이하 (less than or equal)
        description="상품 가격 (원)"
    )
    discount_rate: float = Field(
        default=0.0,            # 기본값
        ge=0.0,                 # 0 이상 (greater than or equal)
        lt=1.0,                 # 1 미만 (less than)
        description="할인율 (0.0 ~ 0.99)"
    )
    tags: list[str] = Field(
        default=[],
        max_length=10,          # 리스트 최대 길이
        description="상품 태그"
    )
```

**Field의 주요 매개변수:**

| 매개변수 | 적용 대상 | 설명 |
|----------|-----------|------|
| `...` (default) | 모든 타입 | 필수 필드 (기본값 없음) |
| `default` | 모든 타입 | 기본값 지정 |
| `min_length` / `max_length` | str, list | 최소/최대 길이 |
| `gt` / `ge` | 숫자 | 초과 / 이상 |
| `lt` / `le` | 숫자 | 미만 / 이하 |
| `pattern` | str | 정규표현식 패턴 |
| `description` | 모든 타입 | API 문서 설명 |
| `examples` | 모든 타입 | 예시 값 목록 |

### 4. Optional 필드와 기본값

```python
from typing import Optional
from pydantic import BaseModel

class UserProfile(BaseModel):
    # 필수 필드: 기본값 없음
    username: str
    email: str

    # 선택 필드 방법 1: Optional + None 기본값
    nickname: Optional[str] = None

    # 선택 필드 방법 2: Python 3.10+ union 문법
    bio: str | None = None

    # 기본값이 있는 필드: 전송하지 않으면 기본값 사용
    is_active: bool = True
    role: str = "user"
```

> **주의**: `Optional[str]`만 쓰면 기본값이 지정되지 않아 여전히 필수 필드입니다.
> 반드시 `Optional[str] = None`처럼 기본값을 함께 지정해야 선택 필드가 됩니다.

### 5. 타입 변환과 검증

Pydantic은 가능한 경우 타입을 자동으로 변환합니다:

```python
class Example(BaseModel):
    count: int
    rate: float
    active: bool

# 아래 JSON이 전송되면:
# {"count": "42", "rate": "3.14", "active": "true"}
# Pydantic이 자동 변환:
# count=42, rate=3.14, active=True
```

하지만 변환이 불가능한 경우 422 에러를 반환합니다:
```json
// {"count": "abc"} 전송 시 → 422 Unprocessable Entity
{
    "detail": [
        {
            "type": "int_parsing",
            "loc": ["body", "count"],
            "msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "abc"
        }
    ]
}
```

---

## 전체 흐름 다이어그램

```
클라이언트 (POST 요청)
    │
    │  JSON 본문: {"name": "상품A", "price": -100}
    ▼
┌─────────────────────────┐
│    FastAPI 수신 계층     │
│  (JSON 파싱)            │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Pydantic 검증 계층     │
│                         │
│  1. 타입 확인            │  ← name: str ✓, price: int ✓
│  2. 필수 필드 확인       │  ← name ✓, price ✓
│  3. Field 규칙 확인      │  ← price > 0 ? ✗ (실패!)
│                         │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
  성공      실패
    │         │
    ▼         ▼
┌────────┐ ┌──────────────────┐
│ 핸들러  │ │  422 에러 응답     │
│ 함수    │ │  (상세 오류 정보)  │
│ 실행    │ │  자동 반환         │
└────────┘ └──────────────────┘
```

---

## 실전 코드 예제: 상품 생성 API

```python
"""
상품 생성 API - Pydantic 모델 활용 예제
실행: uvicorn example_product:app --reload
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="상품 관리 API", version="1.0.0")

# --- 모델 정의 ---

class ProductCreate(BaseModel):
    """상품 생성 요청 모델"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["맥북 프로 16인치"],
        description="상품명"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="상품 설명"
    )
    price: int = Field(
        ...,
        gt=0,
        le=100_000_000,
        examples=[2990000],
        description="상품 가격 (원, 1 이상)"
    )
    category: str = Field(
        default="기타",
        min_length=1,
        max_length=50,
        description="상품 카테고리"
    )
    in_stock: bool = Field(
        default=True,
        description="재고 여부"
    )

# --- 간단한 인메모리 저장소 ---
products_db: list[dict] = []
next_id: int = 1

# --- 엔드포인트 ---

@app.post("/products")
async def create_product(product: ProductCreate):
    """
    새 상품을 등록합니다.
    Pydantic이 요청 본문을 자동으로 검증합니다.
    """
    global next_id

    # product는 이미 검증된 ProductCreate 인스턴스
    product_dict = product.model_dump()
    product_dict["id"] = next_id
    next_id += 1

    products_db.append(product_dict)

    return {
        "message": "상품이 등록되었습니다",
        "product": product_dict
    }

@app.get("/products")
async def list_products():
    """등록된 모든 상품을 조회합니다."""
    return {"products": products_db, "total": len(products_db)}
```

**테스트 방법:**

```bash
# 정상 요청
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "맥북 프로", "price": 2990000, "category": "노트북"}'

# 유효성 검사 실패 (가격이 0)
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "테스트", "price": 0}'

# 유효성 검사 실패 (이름 누락)
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"price": 1000}'
```

---

## 주의 사항

### 1. dict vs BaseModel

```python
# 나쁜 예: dict를 직접 사용
@app.post("/items-bad")
async def create_item_bad(item: dict):
    # 타입 검증 없음, 어떤 데이터든 통과
    # IDE 자동완성 불가
    # API 문서에 스키마 표시 안 됨
    name = item.get("name", "")  # KeyError 위험
    return item

# 좋은 예: BaseModel 사용
@app.post("/items-good")
async def create_item_good(item: Item):
    # 자동 타입 검증
    # IDE 자동완성 지원 (item.name, item.price)
    # API 문서에 스키마 자동 표시
    return item
```

### 2. Mutable Default 주의

```python
# 위험: 리스트나 딕셔너리를 직접 기본값으로 사용
class BadModel(BaseModel):
    tags: list[str] = []  # Pydantic에서는 안전하지만...

# 더 명확한 방법: Field의 default_factory 사용
class GoodModel(BaseModel):
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
```

> **참고**: Pydantic v2에서는 `list[str] = []`와 같은 mutable default도
> 내부적으로 안전하게 처리됩니다. 하지만 `default_factory`를 사용하면
> 의도가 더 명확하게 드러나므로 권장됩니다.

### 3. 모델 재사용과 분리

하나의 엔티티에 대해 용도별로 모델을 분리하는 것이 좋습니다:

```python
class ProductBase(BaseModel):
    """공통 필드를 가진 기본 모델"""
    name: str
    price: int

class ProductCreate(ProductBase):
    """생성 시 사용 (id 없음)"""
    description: Optional[str] = None

class ProductResponse(ProductBase):
    """응답 시 사용 (id 포함)"""
    id: int
    created_at: str
```

---

## 요약

| 개념 | 설명 |
|------|------|
| `BaseModel` | Pydantic의 기본 클래스. 상속하여 데이터 모델을 정의 |
| `Field(...)` | 필드별 유효성 검사 규칙 설정 (길이, 범위 등) |
| 타입 어노테이션 | `str`, `int`, `float`, `bool`, `list[str]` 등 |
| `Optional[T]` | `T` 또는 `None`이 될 수 있는 타입 |
| 기본값 | `= None`, `= 0`, `= "default"` 등으로 선택 필드 생성 |
| 422 응답 | 유효성 검사 실패 시 FastAPI가 자동으로 반환하는 에러 |

---

## 다음 단계

[sec02: 중첩 모델](../sec02-nested-models/concept.md)에서 모델 안에 모델을 포함하는 방법을 학습합니다.
