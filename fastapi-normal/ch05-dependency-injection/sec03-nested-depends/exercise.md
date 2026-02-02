# sec03: 중첩 의존성 - 연습 문제

> `exercise.py` 파일을 열고 TODO 부분을 완성하세요.
> 테스트 실행: `python exercise.py`

---

## 시나리오: 간단한 주문 관리 시스템

주문 관리 시스템에서 사용되는 의존성 체인을 구현합니다.
인증 -> DB 세션 -> 리포지토리 -> 엔드포인트 순서의 의존성 체인을 만들어봅니다.

---

## 문제 1: yield를 사용한 DB 세션 의존성

### 요구사항

`get_db` 의존성 함수를 작성하세요.

- `FakeDB` 인스턴스를 생성합니다.
- `yield`를 사용하여 DB 인스턴스를 제공합니다.
- `finally` 블록에서 `db.close()`를 호출하여 세션을 정리합니다.

### 참고

`FakeDB` 클래스는 이미 제공되어 있습니다:
- `FakeDB.connect()`: 연결 시뮬레이션
- `FakeDB.close()`: 종료 시뮬레이션
- `FakeDB.get_orders()`: 주문 목록 반환
- `FakeDB.get_order(order_id)`: 특정 주문 반환

---

## 문제 2: 중첩 의존성 체인

### 요구사항

다음 의존성 체인을 구성하세요:

```
get_current_user(헤더에서 토큰 추출 및 사용자 조회)
    -> get_order_repository(DB 세션 사용)
        -> 엔드포인트 함수
```

#### `get_current_user` 의존성
- `x_token` 헤더에서 토큰을 받습니다 (`Header()` 사용)
- `fake_users` 딕셔너리에서 토큰에 해당하는 사용자를 찾습니다.
- 사용자가 없으면 `HTTPException(401)` 발생
- 사용자 정보(dict)를 반환합니다.

#### `get_order_repository` 의존성
- `get_db`에 의존합니다. (`db = Depends(get_db)`)
- `OrderRepository(db)` 인스턴스를 반환합니다.

### 엔드포인트

1. `GET /orders`: 현재 사용자의 모든 주문 조회
   - `get_current_user`와 `get_order_repository` 동시 사용
   - 사용자의 `user_id`에 해당하는 주문만 필터링
   - 반환값: `{"user": 사용자 이름, "orders": 주문 목록}`

2. `GET /orders/{order_id}`: 특정 주문 상세 조회
   - `get_current_user`와 `get_order_repository` 동시 사용
   - 주문이 없으면 `HTTPException(404)` 발생
   - 주문의 `user_id`와 현재 사용자의 `user_id`가 다르면 `HTTPException(403)` 발생
   - 반환값: 주문 정보(dict)

---

## 문제 3: 라우터 수준 의존성

### 요구사항

`admin_router`를 생성하고 `require_admin` 의존성을 라우터 수준에서 적용하세요.

- `require_admin` 의존성: `get_current_user`에 의존하며, `role`이 `"admin"`이 아니면 `HTTPException(403)` 발생
- `GET /admin/stats`: 전체 주문 통계를 반환하는 관리자 전용 엔드포인트

---

## 테스트 케이스

```
# 인증된 요청 (일반 사용자)
GET /orders  (x-token: token-user1)  -> user1의 주문만 반환
GET /orders/1 (x-token: token-user1) -> 주문 1 상세 조회

# 인증된 요청 (관리자)
GET /admin/stats (x-token: token-admin) -> 전체 통계 반환

# 인증 실패
GET /orders (x-token: invalid)       -> 401 에러
GET /admin/stats (x-token: token-user1) -> 403 에러 (관리자 아님)
```

---

## 힌트

1. `yield` 의존성에서는 `try`/`finally` 패턴을 사용하세요.
2. `Header()`는 `Query()`와 비슷하게 동작하지만, HTTP 헤더에서 값을 읽습니다.
3. FastAPI에서 헤더 이름은 자동으로 변환됩니다: `x_token` -> `x-token`
4. 라우터 수준 의존성은 `APIRouter(dependencies=[...])` 형태로 설정합니다.
