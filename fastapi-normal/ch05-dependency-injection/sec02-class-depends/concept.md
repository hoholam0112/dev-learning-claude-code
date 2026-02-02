# sec02: 클래스 의존성 (Class Dependencies)

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: sec01 기본 의존성 완료
> **예상 학습 시간**: 30~40분

---

## 학습 목표

- 클래스를 의존성으로 사용하여 상태가 있는 의존성을 만들 수 있다
- 클래스 기반 의존성과 함수 기반 의존성의 차이를 이해한다
- `__init__` 매개변수가 어떻게 쿼리 매개변수로 매핑되는지 이해한다

---

## 핵심 개념

### 1. 왜 클래스 의존성인가?

sec01에서 배운 함수 의존성은 딕셔너리를 반환했습니다.
딕셔너리는 편리하지만, **타입 힌트**와 **자동완성**이 제대로 동작하지 않는 단점이 있습니다.

```python
# 함수 의존성: 딕셔너리 반환 -> IDE 자동완성 없음
def common_pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/items")
def read_items(params: dict = Depends(common_pagination)):
    # params["skip"] -> IDE가 키를 알 수 없음
    # params["skp"]  -> 오타를 잡을 수 없음!
    ...
```

클래스를 사용하면 이 문제를 해결할 수 있습니다:

```python
# 클래스 의존성: 객체 반환 -> IDE 자동완성 지원
class CommonPagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

@app.get("/items")
def read_items(params: CommonPagination = Depends(CommonPagination)):
    # params.skip -> IDE 자동완성 지원!
    # params.skp  -> IDE가 오타를 잡아줌!
    ...
```

### 2. 클래스 기반 의존성의 원리

FastAPI에서 `Depends()`에 전달하는 것은 **Callable(호출 가능한 객체)**이면 됩니다.
클래스는 인스턴스를 생성할 때 호출되므로(`MyClass()`), 자연스럽게 의존성으로 사용할 수 있습니다.

```python
from fastapi import FastAPI, Depends, Query

app = FastAPI()

class ItemQueryParams:
    """상품 조회용 쿼리 매개변수 클래스"""

    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="건너뛸 항목 수"),
        limit: int = Query(default=10, ge=1, le=100, description="조회할 항목 수"),
        sort_by: str = Query(default="name", description="정렬 기준 필드"),
        order: str = Query(default="asc", regex="^(asc|desc)$", description="정렬 순서"),
    ):
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.order = order
```

> **핵심**: `__init__`의 매개변수가 곧 쿼리 매개변수가 됩니다!

### 3. Depends 축약 문법

클래스 의존성에서는 `Depends()`의 축약 문법을 사용할 수 있습니다:

```python
# 풀 문법: 타입 힌트와 Depends에 같은 클래스를 두 번 작성
@app.get("/items")
def read_items(params: ItemQueryParams = Depends(ItemQueryParams)):
    ...

# 축약 문법: Depends()에 인자 없이 사용 -> 타입 힌트에서 자동 추론
@app.get("/items")
def read_items(params: ItemQueryParams = Depends()):
    ...
```

> `Depends()`에 아무 인자도 전달하지 않으면, FastAPI가 타입 힌트(`ItemQueryParams`)를 보고 자동으로 해당 클래스를 의존성으로 사용합니다.

### 4. 클래스에 메서드 추가하기

클래스 의존성의 장점은 **메서드**를 추가하여 로직을 캡슐화할 수 있다는 것입니다:

```python
class PaginationParams:
    """페이지네이션 매개변수와 유틸리티 메서드를 제공하는 의존성"""

    def __init__(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
    ):
        self.skip = skip
        self.limit = limit

    def apply(self, items: list) -> list:
        """리스트에 페이지네이션을 적용하는 유틸리티 메서드"""
        return items[self.skip : self.skip + self.limit]

    def get_info(self, total: int) -> dict:
        """페이지네이션 정보를 반환하는 유틸리티 메서드"""
        return {
            "total": total,
            "skip": self.skip,
            "limit": self.limit,
            "has_more": self.skip + self.limit < total,
        }


@app.get("/items")
def read_items(pagination: PaginationParams = Depends()):
    items = fake_items
    return {
        "items": pagination.apply(items),       # 메서드 호출!
        "pagination": pagination.get_info(len(items)),  # 메서드 호출!
    }
```

---

## 함수 의존성 vs 클래스 의존성 비교

| 특성 | 함수 의존성 | 클래스 의존성 |
|------|------------|-------------|
| 정의 방식 | `def func():` | `class MyDep:` |
| 반환 타입 | 자유 (보통 dict) | 클래스 인스턴스 |
| IDE 자동완성 | 제한적 (dict) | 완전 지원 (속성) |
| 메서드 추가 | 불가 | 가능 |
| 적합한 경우 | 단순한 값 반환 | 복잡한 로직/상태 |
| 코드 구조 | 간결 | 체계적 |

---

## 실전 예제: 설정 가능한 쿼리 파라미터

```python
class ProductFilter:
    """상품 필터 의존성 클래스"""

    def __init__(
        self,
        category: str | None = Query(default=None, description="카테고리 필터"),
        min_price: int = Query(default=0, ge=0, description="최소 가격"),
        max_price: int = Query(default=1000000, ge=0, description="최대 가격"),
        in_stock: bool = Query(default=True, description="재고 있는 상품만"),
    ):
        self.category = category
        self.min_price = min_price
        self.max_price = max_price
        self.in_stock = in_stock

    def filter(self, products: list[dict]) -> list[dict]:
        """상품 목록에 필터를 적용"""
        result = products

        if self.category:
            result = [p for p in result if p.get("category") == self.category]

        result = [
            p for p in result
            if self.min_price <= p.get("price", 0) <= self.max_price
        ]

        if self.in_stock:
            result = [p for p in result if p.get("stock", 0) > 0]

        return result


@app.get("/products")
def list_products(
    filter_params: ProductFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    filtered = filter_params.filter(all_products)
    return {
        "products": pagination.apply(filtered),
        "pagination": pagination.get_info(len(filtered)),
    }
```

---

## 주의사항

1. **`Depends()` 축약 문법은 클래스에서만 동작합니다**: 함수 의존성에서는 반드시 `Depends(func_name)`으로 함수를 명시해야 합니다.
2. **`__init__`의 첫 번째 매개변수 `self`는 무시됩니다**: FastAPI가 자동으로 처리합니다.
3. **클래스 의존성도 캐싱됩니다**: 같은 요청 내에서 같은 클래스 의존성은 한 번만 인스턴스화됩니다.

---

## 다음 단계

- `exercise.md`를 확인하고 연습 문제를 풀어보세요.
- 다음 섹션: [sec03-nested-depends](../sec03-nested-depends/concept.md) - 중첩 의존성
