# 챕터 05 연습 문제

---

## 문제 1: 페이지네이션 의존성 (기초)

### 설명
클래스 기반 페이지네이션 의존성을 구현하고, 여러 엔드포인트에서 재사용하세요.

### 요구사항
- `Pagination` 클래스 의존성:
  - `page` (int): 페이지 번호, 기본값 1, 1 이상
  - `page_size` (int): 페이지 크기, 기본값 10, 1~50
  - `skip` 속성: 자동 계산 `(page - 1) * page_size`
- 다음 엔드포인트에서 `Pagination` 의존성을 재사용:
  - `GET /products` — 상품 목록 (페이지네이션)
  - `GET /reviews` — 리뷰 목록 (페이지네이션)
- 각 응답에 페이지 정보(total, page, page_size, total_pages)를 포함하세요

### 임시 데이터
```python
PRODUCTS = [
    {"id": i, "name": f"상품_{i}", "price": i * 10000}
    for i in range(1, 21)  # 20개 상품
]

REVIEWS = [
    {"id": i, "product_id": (i % 5) + 1, "content": f"리뷰_{i}", "rating": (i % 5) + 1}
    for i in range(1, 31)  # 30개 리뷰
]
```

### 예상 입출력

```
GET /products?page=2&page_size=5
→ {
    "total": 20,
    "page": 2,
    "page_size": 5,
    "total_pages": 4,
    "items": [
        {"id": 6, "name": "상품_6", "price": 60000},
        ...
    ]
  }
```

<details>
<summary>힌트 보기</summary>

- `Pagination` 클래스의 `__init__`에서 Query 파라미터를 받으세요
- `Depends()`에 인자를 생략하면 타입 힌트를 의존성으로 사용합니다: `pagination: Pagination = Depends()`
- `total_pages = math.ceil(total / pagination.page_size)`
- 슬라이싱: `items[pagination.skip : pagination.skip + pagination.page_size]`

</details>

---

## 문제 2: 인증 상태 확인 의존성 (보통)

### 설명
간단한 토큰 기반 인증 의존성을 구현하세요. `Authorization` 헤더에서 토큰을 추출하고 검증합니다.

### 요구사항
- `verify_token` 함수 의존성:
  - `Authorization` 헤더에서 토큰을 추출합니다 (Header 사용)
  - 토큰이 없거나 "Bearer "로 시작하지 않으면 401 에러
  - 유효하지 않은 토큰이면 401 에러
- `get_current_user` 함수 의존성:
  - `verify_token`에 의존합니다 (하위 의존성)
  - 토큰으로 사용자 정보를 조회하여 반환합니다
- 엔드포인트:
  - `GET /public/info` — 인증 불필요
  - `GET /protected/profile` — 인증 필요 (get_current_user 사용)
  - `GET /protected/settings` — 인증 필요

### 유효한 토큰 매핑
```python
VALID_TOKENS = {
    "token-abc-123": {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    "token-def-456": {"id": 2, "name": "김철수", "email": "kim@example.com"},
}
```

### 예상 입출력

```
GET /protected/profile
Headers: Authorization: Bearer token-abc-123
→ {"user": {"id": 1, "name": "홍길동", "email": "hong@example.com"}}

GET /protected/profile
Headers: Authorization: Bearer invalid-token
→ 401 {"detail": "유효하지 않은 토큰입니다"}

GET /protected/profile
(Authorization 헤더 없음)
→ 401 {"detail": "인증이 필요합니다"}
```

<details>
<summary>힌트 보기</summary>

- `from fastapi import Header`를 사용하세요
- `authorization: str = Header(default=None)`으로 헤더를 받습니다
- FastAPI에서는 헤더 이름의 하이픈(-)이 언더스코어(_)로 자동 변환됩니다
- `token = authorization.replace("Bearer ", "")`으로 토큰을 추출하세요
- `HTTPException(status_code=401)`로 인증 실패를 처리하세요

</details>

---

## 문제 3: 중첩 의존성 체인 (보통)

### 설명
데이터베이스 연결, 사용자 인증, 권한 확인이 순차적으로 이루어지는 3단계 의존성 체인을 구현하세요.

### 요구사항
- 1단계 `get_database` 의존성:
  - 데이터베이스 연결 객체(딕셔너리)를 반환합니다
  - 연결 상태와 타임스탬프를 포함합니다
- 2단계 `get_authenticated_user` 의존성:
  - `get_database`에 의존합니다
  - 쿼리 파라미터 `username`과 `password`를 받아 사용자를 검증합니다
  - DB에서 사용자를 조회하고 비밀번호를 확인합니다
- 3단계 `require_role` 함수 (의존성 팩토리):
  - `get_authenticated_user`에 의존합니다
  - 특정 역할을 가진 사용자만 허용합니다
  - `require_role("admin")`, `require_role("editor")` 형태로 사용
- 엔드포인트:
  - `GET /dashboard` — 모든 인증된 사용자 접근 가능
  - `GET /admin/panel` — admin 역할만 접근 가능
  - `GET /editor/posts` — editor 역할만 접근 가능

### 사용자 데이터
```python
USERS_DB = {
    "admin": {"id": 1, "name": "관리자", "password": "admin123", "role": "admin"},
    "editor1": {"id": 2, "name": "편집자", "password": "edit123", "role": "editor"},
    "user1": {"id": 3, "name": "일반사용자", "password": "user123", "role": "user"},
}
```

### 예상 입출력

```
GET /dashboard?username=admin&password=admin123
→ {"message": "환영합니다, 관리자님!", "role": "admin", "db_status": "connected"}

GET /admin/panel?username=editor1&password=edit123
→ 403 {"detail": "admin 역할이 필요합니다"}

GET /admin/panel?username=admin&password=wrong
→ 401 {"detail": "비밀번호가 일치하지 않습니다"}
```

<details>
<summary>힌트 보기</summary>

- 의존성 팩토리: 함수를 반환하는 함수입니다
```python
def require_role(required_role: str):
    def role_checker(user: dict = Depends(get_authenticated_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail=f"{required_role} 역할이 필요합니다")
        return user
    return role_checker
```
- 사용법: `Depends(require_role("admin"))`
- `get_database`는 간단한 딕셔너리를 반환하면 됩니다

</details>

---

## 제출 방법

1. `solution.py` 파일에 3개 문제의 답안을 모두 작성하세요
2. `uvicorn solution:app --reload`로 실행하세요
3. `http://localhost:8000/docs`에서 의존성이 자동으로 파라미터에 반영되는지 확인하세요
4. 의존성 체인의 각 단계에서 에러가 올바르게 반환되는지 테스트하세요
5. 동일한 의존성이 여러 엔드포인트에서 재사용되는지 확인하세요
