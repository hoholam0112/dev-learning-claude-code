# 섹션 03: 매개변수 검증 - 연습 문제

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py` (테스트 자동 실행)
> **서버 실행**: `uvicorn exercise:app --reload`

---

## 문제 1: 검증 규칙이 적용된 상품 조회 API

### 요구 사항

`GET /items/{item_id}` 엔드포인트를 작성하세요.

**매개변수 검증:**
- `item_id` (경로, int): 1 이상 10000 이하 (`Path()` 사용)
  - title: "상품 ID"
- `q` (쿼리, str, 선택적): 2글자 이상 50글자 이하 (`Query()` 사용)
  - title: "검색 키워드"

**반환값:**
- 상품이 존재하면: 해당 상품 정보
- 상품이 없으면: `{"error": "상품을 찾을 수 없습니다"}`
- `q`가 주어지면 결과에 `"q": q` 추가

### 예시

```
GET /items/1
응답: {"name": "노트북", "price": 1500000}

GET /items/0
응답: 422 에러 (item_id는 1 이상)

GET /items/1?q=a
응답: 422 에러 (q는 2글자 이상)

GET /items/1?q=검색어
응답: {"name": "노트북", "price": 1500000, "q": "검색어"}
```

---

## 문제 2: 복합 검증 (여러 조건 동시 적용)

### 요구 사항

`GET /items` 엔드포인트를 작성하세요.

**매개변수 검증:**
- `skip` (쿼리, int, 기본값: 0): 0 이상 (`Query()` 사용)
- `limit` (쿼리, int, 기본값: 10): 1 이상 100 이하 (`Query()` 사용)
- `min_price` (쿼리, int, 선택적): 0 이상 (`Query()` 사용)
- `max_price` (쿼리, int, 선택적): 0 이상 (`Query()` 사용)
- `name` (쿼리, str, 선택적): 1글자 이상 100글자 이하 (`Query()` 사용)

**동작:**
1. `name`이 주어지면 상품 이름에 해당 문자열이 포함된 항목만 필터링
2. `min_price`가 주어지면 해당 가격 이상인 항목만 포함
3. `max_price`가 주어지면 해당 가격 이하인 항목만 포함
4. `skip`과 `limit` 적용
5. 반환: `{"items": [...], "total": 전체개수}`

### 예시

```
GET /items?limit=0
응답: 422 에러 (limit는 1 이상)

GET /items?skip=-1
응답: 422 에러 (skip은 0 이상)

GET /items?min_price=-100
응답: 422 에러 (min_price는 0 이상)

GET /items?name=노트북&min_price=100000
응답: {"items": [가격 100000 이상이고 이름에 "노트북"이 포함된 상품], "total": 1}
```

### 힌트

- `Path()`와 `Query()`를 import해야 합니다: `from fastapi import FastAPI, Path, Query`
- `ge=1` (greater than or equal to 1)은 "1 이상"을 의미합니다.
- `le=100` (less than or equal to 100)은 "100 이하"를 의미합니다.
- 선택적 매개변수는 `Query(default=None, ...)`으로 정의합니다.

---

## 테스트 체크리스트

- [ ] `/items/1` 정상 조회
- [ ] `/items/0` 422 에러 (item_id 범위 위반)
- [ ] `/items/1?q=a` 422 에러 (q 최소 길이 위반)
- [ ] `/items/1?q=검색어` 정상 조회 (q 포함)
- [ ] `/items?limit=0` 422 에러 (limit 범위 위반)
- [ ] `/items?skip=-1` 422 에러 (skip 범위 위반)
- [ ] `/items?name=노트북&min_price=100000` 정상 필터링
