# 챕터 07 연습 문제: 데이터베이스 연동 (SQLAlchemy)

---

## 문제 1: 메모장 API (기본 CRUD)

### 설명
SQLAlchemy를 사용하여 간단한 메모장 API를 구현하세요.

### 요구사항
1. `Note` 모델: `id`, `title`, `content`, `is_pinned`(고정 여부), `created_at`, `updated_at`
2. 다음 엔드포인트를 구현하세요:
   - `POST /notes` - 메모 생성
   - `GET /notes` - 전체 메모 목록 (고정된 메모가 먼저 표시)
   - `GET /notes/{note_id}` - 메모 상세 조회
   - `PUT /notes/{note_id}` - 메모 수정
   - `DELETE /notes/{note_id}` - 메모 삭제
   - `PATCH /notes/{note_id}/pin` - 메모 고정/해제 토글

### 예상 입출력

**메모 생성:**
```json
POST /notes
{
    "title": "장보기 목록",
    "content": "우유, 빵, 계란"
}
// 응답 (201):
{
    "id": 1,
    "title": "장보기 목록",
    "content": "우유, 빵, 계란",
    "is_pinned": false,
    "created_at": "2024-01-01T00:00:00"
}
```

**고정 토글:**
```json
PATCH /notes/1/pin
// 응답:
{
    "id": 1,
    "title": "장보기 목록",
    "is_pinned": true,
    "message": "메모가 고정되었습니다"
}
```

<details>
<summary>힌트 보기</summary>

- 고정된 메모가 먼저 표시되도록 `order_by(Note.is_pinned.desc(), Note.created_at.desc())`를 사용하세요
- 고정/해제 토글은 `db_note.is_pinned = not db_note.is_pinned`로 구현할 수 있습니다
- `updated_at`은 `onupdate=datetime.utcnow`로 자동 업데이트할 수 있습니다

</details>

---

## 문제 2: 카테고리별 상품 조회 (외래키 관계)

### 설명
카테고리와 상품의 일대다 관계를 구현하고, 카테고리별 상품을 조회하는 API를 만드세요.

### 요구사항
1. `Category` 모델: `id`, `name`, `description`
2. `Product` 모델: `id`, `name`, `price`, `stock`, `category_id`(외래키)
3. 다음 엔드포인트를 구현하세요:
   - `POST /categories` - 카테고리 생성
   - `GET /categories` - 카테고리 목록 (각 카테고리의 상품 수 포함)
   - `POST /categories/{category_id}/products` - 특정 카테고리에 상품 추가
   - `GET /categories/{category_id}/products` - 카테고리별 상품 조회
   - `GET /products` - 전체 상품 조회 (카테고리 정보 포함)

### 예상 입출력

**카테고리 목록:**
```json
GET /categories
[
    {
        "id": 1,
        "name": "전자제품",
        "description": "전자 기기 카테고리",
        "product_count": 3
    },
    {
        "id": 2,
        "name": "도서",
        "description": "책 카테고리",
        "product_count": 5
    }
]
```

**카테고리별 상품:**
```json
GET /categories/1/products
[
    {
        "id": 1,
        "name": "무선 키보드",
        "price": 45000,
        "stock": 100,
        "category": {"id": 1, "name": "전자제품"}
    }
]
```

<details>
<summary>힌트 보기</summary>

- `relationship("Product", back_populates="category")`로 관계를 설정하세요
- 상품 수는 `len(category.products)` 또는 `db.query(func.count(Product.id)).filter(Product.category_id == id).scalar()`로 구할 수 있습니다
- `from sqlalchemy import func`를 가져와 집계 함수를 사용할 수 있습니다

</details>

---

## 문제 3: 페이지네이션이 포함된 목록 조회

### 설명
오프셋 기반 페이지네이션을 구현하여 대량의 데이터를 효율적으로 조회하세요.

### 요구사항
1. 기존 Todo 모델 또는 새로운 모델을 사용하세요
2. `GET /items` 엔드포인트에 다음 쿼리 파라미터를 지원하세요:
   - `page`: 페이지 번호 (기본값: 1, 최소값: 1)
   - `size`: 페이지 크기 (기본값: 10, 최소값: 1, 최대값: 100)
   - `sort_by`: 정렬 기준 필드 (`created_at`, `title`, `price`)
   - `order`: 정렬 방향 (`asc`, `desc`)
3. 응답에 페이지네이션 메타데이터를 포함하세요

### 예상 입출력

```json
GET /items?page=2&size=5&sort_by=price&order=desc

{
    "items": [
        {"id": 6, "title": "상품 F", "price": 15000},
        {"id": 7, "title": "상품 G", "price": 12000},
        ...
    ],
    "pagination": {
        "page": 2,
        "size": 5,
        "total_items": 50,
        "total_pages": 10,
        "has_next": true,
        "has_prev": true
    }
}
```

<details>
<summary>힌트 보기</summary>

- 오프셋 계산: `skip = (page - 1) * size`
- 전체 개수: `db.query(Model).count()`
- 전체 페이지 수: `math.ceil(total / size)`
- 정렬: `getattr(Model, sort_by)` 와 `.asc()` 또는 `.desc()`를 조합하세요
- `from math import ceil`을 사용할 수 있습니다

</details>

---

## 문제 4: 검색 기능 추가 (LIKE 쿼리)

### 설명
제목이나 내용에서 키워드를 검색하는 기능을 구현하세요.

### 요구사항
1. `GET /search` 엔드포인트를 추가하세요
2. 쿼리 파라미터:
   - `q`: 검색 키워드 (필수)
   - `field`: 검색 대상 필드 (`title`, `content`, `all`) - 기본값: `all`
3. 대소문자 구분 없이 검색해야 합니다
4. 검색 결과에 검색어와 결과 수를 포함하세요

### 예상 입출력

```json
GET /search?q=파이썬&field=title

{
    "query": "파이썬",
    "field": "title",
    "count": 3,
    "results": [
        {"id": 1, "title": "파이썬 기초", "content": "..."},
        {"id": 5, "title": "파이썬 고급 문법", "content": "..."},
        {"id": 8, "title": "파이썬 웹 개발", "content": "..."}
    ]
}
```

**검색 결과 없음:**
```json
GET /search?q=존재하지않는키워드

{
    "query": "존재하지않는키워드",
    "field": "all",
    "count": 0,
    "results": []
}
```

<details>
<summary>힌트 보기</summary>

- SQLAlchemy의 LIKE 쿼리: `Model.title.ilike(f"%{keyword}%")`
- `ilike`는 대소문자를 구분하지 않는 LIKE입니다
- 여러 필드를 동시에 검색: `or_(Model.title.ilike(...), Model.content.ilike(...))`
- `from sqlalchemy import or_`를 가져와 OR 조건을 사용하세요
- `Enum`을 사용하면 `field` 파라미터의 유효값을 제한할 수 있습니다

</details>
