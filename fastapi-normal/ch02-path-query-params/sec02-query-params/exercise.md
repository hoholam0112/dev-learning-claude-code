# 섹션 02: 쿼리 매개변수 - 연습 문제

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py` (테스트 자동 실행)
> **서버 실행**: `uvicorn exercise:app --reload`

---

## 문제 1: 상품 목록 검색 API

### 요구 사항

`GET /items` 엔드포인트를 작성하세요.

**매개변수:**
- `skip` (int, 기본값: 0): 건너뛸 항목 수
- `limit` (int, 기본값: 10): 반환할 최대 항목 수
- `q` (str, 선택적, 기본값: None): 검색 키워드

**동작:**
1. `q`가 주어지면, 상품 이름에 `q`가 포함된 항목만 필터링합니다.
2. 필터링된 결과에 `skip`과 `limit`을 적용합니다.
3. 반환 형식: `{"items": [...], "total": 전체개수}`

### 예시

```
GET /items
응답: {"items": [...전체 상품...], "total": 5}

GET /items?skip=1&limit=2
응답: {"items": [2번째, 3번째 상품], "total": 5}

GET /items?q=노트북
응답: {"items": [이름에 "노트북"이 포함된 상품], "total": 1}
```

---

## 문제 2: 필수/선택 쿼리 매개변수 혼합 사용

### 요구 사항

`GET /items/search` 엔드포인트를 작성하세요.

**매개변수:**
- `q` (str, **필수**): 검색 키워드
- `min_price` (int, 선택적, 기본값: None): 최소 가격
- `max_price` (int, 선택적, 기본값: None): 최대 가격

**동작:**
1. `q`로 상품 이름을 필터링합니다.
2. `min_price`가 주어지면 해당 가격 이상인 상품만 포함합니다.
3. `max_price`가 주어지면 해당 가격 이하인 상품만 포함합니다.
4. 반환 형식: `{"query": q, "results": [...]}`

### 예시

```
GET /items/search?q=노트
응답: {"query": "노트", "results": [이름에 "노트"가 포함된 상품들]}

GET /items/search
응답: 422 에러 (q는 필수)

GET /items/search?q=&min_price=10000&max_price=100000
응답: {"query": "", "results": [가격 범위에 맞는 상품들]}
```

### 힌트

- 기본값이 없는 매개변수는 자동으로 필수가 됩니다.
- `None`을 기본값으로 지정하면 선택적 매개변수가 됩니다.
- `if min_price is not None:`으로 값이 전달되었는지 확인합니다.

---

## 테스트 체크리스트

- [ ] `/items` 기본 조회 시 전체 상품 반환
- [ ] `/items?skip=1&limit=2` 페이지네이션 동작 확인
- [ ] `/items?q=노트북` 키워드 검색 동작 확인
- [ ] `/items/search?q=노트북` 필수 매개변수 정상 동작
- [ ] `/items/search` 요청 시 422 에러 반환
- [ ] `/items/search?q=&min_price=10000&max_price=100000` 가격 필터 동작
