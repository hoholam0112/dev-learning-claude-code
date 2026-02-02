# sec01: 기본 의존성 - 연습 문제

> `exercise.py` 파일을 열고 TODO 부분을 완성하세요.
> 테스트 실행: `python exercise.py`

---

## 문제 1: 공통 페이지네이션 의존성 만들기

### 요구사항

`common_pagination` 의존성 함수를 작성하세요.

- **매개변수**:
  - `skip`: `int` 타입, 기본값 `0`, 최솟값 `0`
  - `limit`: `int` 타입, 기본값 `10`, 최솟값 `1`, 최댓값 `100`
- **반환값**: `{"skip": skip, "limit": limit}` 딕셔너리

### 사용처

- `GET /items`: `common_pagination` 의존성을 사용하여 `fake_items`를 슬라이싱
- `GET /items/count`: 같은 의존성을 재사용하여 전체 개수, skip, limit, 슬라이싱 결과 개수를 반환

### 테스트 케이스

```
GET /items              -> 상품 10개 반환 (기본값)
GET /items?skip=5&limit=3 -> 상품_6, 상품_7, 상품_8 반환
GET /items/count?skip=0&limit=5 -> total: 20, count: 5
```

---

## 문제 2: 공통 필터링 의존성 만들기

### 요구사항

`common_filter` 의존성 함수를 작성하세요.

- **매개변수**:
  - `keyword`: `str | None` 타입, 기본값 `None` - 상품 이름에 포함된 키워드로 검색
  - `min_price`: `int` 타입, 기본값 `0` - 최소 가격 필터
  - `max_price`: `int` 타입, 기본값 `100000` - 최대 가격 필터
- **반환값**: `{"keyword": keyword, "min_price": min_price, "max_price": max_price}` 딕셔너리

### 사용처

- `GET /items/search`: `common_filter`와 `common_pagination`을 **동시에** 사용
  - 먼저 필터를 적용한 후 페이지네이션 적용
  - 반환값: `{"results": 필터+페이지네이션 결과, "total_filtered": 필터만 적용한 전체 수}`

### 테스트 케이스

```
GET /items/search?min_price=5000&max_price=15000
  -> 가격이 5000~15000인 상품만 반환

GET /items/search?keyword=1
  -> 이름에 "1"이 포함된 상품만 반환 (상품_1, 상품_10, 상품_11, ...)
```

---

## 힌트

1. `Query()`를 사용하면 기본값과 검증 규칙을 한 번에 설정할 수 있습니다.
2. 의존성 함수의 반환값은 엔드포인트에서 딕셔너리로 받아 사용합니다.
3. 두 개의 의존성을 동시에 사용할 때는 각각 별도의 매개변수로 선언합니다.

```python
@app.get("/example")
def example(
    pagination: dict = Depends(common_pagination),
    filter_params: dict = Depends(common_filter),
):
    ...
```
