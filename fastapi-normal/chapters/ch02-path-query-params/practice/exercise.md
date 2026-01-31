# 챕터 02 연습 문제

---

## 문제 1: 사용자 프로필 조회 API (기초)

### 설명
사용자 프로필을 조회하는 API를 만드세요. 경로 파라미터를 활용합니다.

### 요구사항
- `GET /users/{user_id}` — 사용자 ID로 프로필을 조회합니다
- `GET /users/{user_id}/posts` — 특정 사용자의 게시글 목록을 조회합니다
- `user_id`는 1 이상의 정수여야 합니다 (`Path()` 사용)
- 게시글 목록은 `skip`과 `limit` 쿼리 파라미터로 페이지네이션을 지원합니다

### 예상 입출력

```
GET /users/1
→ {"user_id": 1, "name": "사용자_1", "email": "user1@example.com"}

GET /users/1/posts?skip=0&limit=5
→ {
    "user_id": 1,
    "skip": 0,
    "limit": 5,
    "posts": [
        {"id": 1, "title": "첫 번째 글"},
        {"id": 2, "title": "두 번째 글"}
    ]
  }
```

<details>
<summary>힌트 보기</summary>

- `Path(..., ge=1)`을 사용하여 user_id가 1 이상이 되도록 검증하세요
- 게시글 데이터는 임시 리스트로 만들어 두고 `skip`과 `limit`으로 슬라이싱하세요
- `posts[skip : skip + limit]` 형태로 페이지네이션을 구현합니다

</details>

---

## 문제 2: 도서 검색 API (보통)

### 설명
다양한 쿼리 파라미터를 활용하여 도서를 검색하는 API를 만드세요.

### 요구사항
- `GET /books` — 도서 목록 조회
- 쿼리 파라미터:
  - `q` (선택): 검색 키워드, 2~100자
  - `author` (선택): 저자명 필터
  - `min_price` (선택): 최소 가격, 0 이상
  - `max_price` (선택): 최대 가격
  - `page` (선택): 페이지 번호, 기본값 1, 1 이상
  - `page_size` (선택): 페이지 크기, 기본값 10, 1~50
- 모든 쿼리 파라미터에 적절한 `Query()` 검증을 적용하세요

### 임시 데이터

```python
BOOKS = [
    {"id": 1, "title": "파이썬 입문", "author": "김파이", "price": 25000},
    {"id": 2, "title": "FastAPI 마스터", "author": "이패스트", "price": 32000},
    {"id": 3, "title": "데이터 분석", "author": "김파이", "price": 28000},
    {"id": 4, "title": "웹 개발 기초", "author": "박웹", "price": 22000},
    {"id": 5, "title": "머신러닝 입문", "author": "최머신", "price": 35000},
]
```

### 예상 입출력

```
GET /books?q=파이썬&min_price=20000
→ {
    "total": 1,
    "page": 1,
    "page_size": 10,
    "books": [
        {"id": 1, "title": "파이썬 입문", "author": "김파이", "price": 25000}
    ]
  }
```

<details>
<summary>힌트 보기</summary>

- `Query(default=None)`으로 선택적 파라미터를 만드세요
- `Query(default=None, min_length=2, max_length=100)`으로 문자열 길이를 제한하세요
- 필터링 로직: `if q`일 때만 키워드 검색을 적용하고, `if author`일 때만 저자 필터를 적용하세요
- 제목이나 저자에 키워드가 포함되어 있는지는 `in` 연산자로 확인합니다

</details>

---

## 문제 3: Enum 기반 카테고리 필터링 (보통)

### 설명
Enum을 활용하여 제한된 카테고리 값으로 상품을 필터링하는 API를 만드세요.

### 요구사항
- `ProductCategory` Enum 정의: `electronics`, `clothing`, `food`, `books`
- `SortOrder` Enum 정의: `price_asc`, `price_desc`, `name_asc`, `name_desc`
- `GET /shop/products` — 상품 목록 조회
  - `category` (선택): 카테고리 필터 (Enum)
  - `sort` (선택): 정렬 순서 (Enum, 기본값: `name_asc`)
  - `in_stock` (선택): 재고 여부 (bool, 기본값: True)
- `GET /shop/categories` — 사용 가능한 카테고리 목록 반환

### 임시 데이터

```python
SHOP_PRODUCTS = [
    {"id": 1, "name": "노트북", "category": "electronics", "price": 1200000, "in_stock": True},
    {"id": 2, "name": "티셔츠", "category": "clothing", "price": 29000, "in_stock": True},
    {"id": 3, "name": "사과", "category": "food", "price": 5000, "in_stock": False},
    {"id": 4, "name": "파이썬 책", "category": "books", "price": 32000, "in_stock": True},
    {"id": 5, "name": "이어폰", "category": "electronics", "price": 89000, "in_stock": True},
]
```

### 예상 입출력

```
GET /shop/products?category=electronics&sort=price_asc
→ {
    "category": "electronics",
    "sort": "price_asc",
    "count": 2,
    "products": [
        {"id": 5, "name": "이어폰", "category": "electronics", "price": 89000, "in_stock": true},
        {"id": 1, "name": "노트북", "category": "electronics", "price": 1200000, "in_stock": true}
    ]
  }

GET /shop/categories
→ {
    "categories": ["electronics", "clothing", "food", "books"]
  }
```

<details>
<summary>힌트 보기</summary>

- Enum은 반드시 `str`을 상속하세요: `class ProductCategory(str, Enum)`
- 정렬은 `sorted()` 함수와 `key` 파라미터를 활용하세요
- `sorted(products, key=lambda x: x["price"])` — 가격 오름차순
- `sorted(products, key=lambda x: x["price"], reverse=True)` — 가격 내림차순
- 카테고리 목록: `[c.value for c in ProductCategory]`

</details>

---

## 제출 방법

1. `solution.py` 파일에 3개 문제의 답안을 모두 작성하세요
2. `uvicorn solution:app --reload`로 실행하세요
3. `http://localhost:8000/docs`에서 모든 엔드포인트를 테스트하세요
4. 유효하지 않은 값을 넣어 422 에러가 정상적으로 반환되는지 확인하세요
