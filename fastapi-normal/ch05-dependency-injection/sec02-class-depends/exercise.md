# sec02: 클래스 의존성 - 연습 문제

> `exercise.py` 파일을 열고 TODO 부분을 완성하세요.
> 테스트 실행: `python exercise.py`

---

## 문제 1: PaginationParams 클래스 의존성

### 요구사항

`PaginationParams` 클래스를 의존성으로 작성하세요.

- **`__init__` 매개변수**:
  - `skip`: `int` 타입, 기본값 `0`, 최솟값 `0`
  - `limit`: `int` 타입, 기본값 `10`, 최솟값 `1`, 최댓값 `100`
- **속성**: `self.skip`, `self.limit`
- **메서드**:
  - `apply(items: list) -> list`: 리스트에 페이지네이션을 적용하여 반환
  - `get_info(total: int) -> dict`: 페이지네이션 정보를 딕셔너리로 반환
    - 반환값: `{"total": total, "skip": skip, "limit": limit, "has_more": bool}`
    - `has_more`: `skip + limit < total`이면 `True`

### 사용처

- `GET /books`: `PaginationParams`를 사용하여 도서 목록 조회

---

## 문제 2: BookFilter 클래스 의존성

### 요구사항

`BookFilter` 클래스를 의존성으로 작성하세요.

- **`__init__` 매개변수**:
  - `genre`: `str | None` 타입, 기본값 `None` - 장르 필터
  - `min_price`: `int` 타입, 기본값 `0` - 최소 가격
  - `max_price`: `int` 타입, 기본값 `100000` - 최대 가격
  - `author`: `str | None` 타입, 기본값 `None` - 저자 이름 검색
- **속성**: `self.genre`, `self.min_price`, `self.max_price`, `self.author`
- **메서드**:
  - `apply(books: list[dict]) -> list[dict]`: 도서 목록에 필터를 적용하여 반환
    - `genre`가 None이 아니면: `book["genre"] == genre`인 항목만
    - `min_price <= book["price"] <= max_price` 조건
    - `author`가 None이 아니면: `author`가 `book["author"]`에 포함된 항목만

### 사용처

- `GET /books/search`: `BookFilter`와 `PaginationParams`를 동시에 사용

---

## 테스트 케이스

```
GET /books                            -> 도서 10개 반환 (기본 페이지네이션)
GET /books?skip=0&limit=5             -> 도서 5개 반환, has_more: true
GET /books/search?genre=소설           -> 장르가 "소설"인 도서만 반환
GET /books/search?author=작가&limit=3  -> 저자 이름에 "작가"가 포함된 도서 3개 반환
```

---

## 힌트

1. 클래스의 `__init__` 메서드에 `Query()`를 사용하여 검증 규칙을 추가하세요.
2. `Depends()` 축약 문법을 사용하면 코드가 더 깔끔해집니다: `params: PaginationParams = Depends()`
3. `apply` 메서드에서는 리스트 컴프리헨션을 활용하세요.
