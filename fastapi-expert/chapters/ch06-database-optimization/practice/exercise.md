# 챕터 06 연습문제: 데이터베이스 최적화 (비동기)

---

## 문제 1: 비동기 리포지토리 패턴 완전 구현

### 설명

`User`와 `Post` 모델에 대한 완전한 리포지토리 패턴을 구현하세요. 제네릭 베이스 리포지토리를 상속받아 도메인 특화 메서드를 추가해야 합니다.

### 요구사항

1. `BaseRepository[T]` 제네릭 클래스에 다음 메서드 구현:
   - `get_by_id(id)` - 단건 조회
   - `get_all(skip, limit)` - 페이징 목록 조회
   - `create(**kwargs)` - 생성
   - `update(id, **kwargs)` - 수정
   - `delete(id)` - 삭제
   - `exists(id)` - 존재 여부 확인

2. `UserRepository(BaseRepository[User])`:
   - `find_by_email(email)` - 이메일로 사용자 조회
   - `get_with_posts(user_id)` - 사용자와 게시글 함께 조회 (N+1 방지)

3. `PostRepository(BaseRepository[Post])`:
   - `get_by_author(user_id, skip, limit)` - 특정 저자의 게시글 조회
   - `search(keyword)` - 제목/내용 검색

4. 모든 리포지토리는 `AsyncSession`을 생성자에서 받아야 합니다

### 예상 입출력

```python
# 사용 예시
async with async_session() as session:
    user_repo = UserRepository(session)

    # 사용자 생성
    user = await user_repo.create(name="홍길동", email="hong@test.com")
    assert user.id is not None

    # 이메일로 조회
    found = await user_repo.find_by_email("hong@test.com")
    assert found.name == "홍길동"

    # 존재 여부
    assert await user_repo.exists(user.id) is True
    assert await user_repo.exists(9999) is False
```

<details>
<summary>힌트</summary>

- `select(User).where(User.email == email)` 패턴을 사용하세요
- `scalar_one_or_none()`은 결과가 0~1개일 때 유용합니다
- `selectinload`를 `options()`에 전달하여 Eager Loading을 적용하세요
- `ilike`를 사용하면 대소문자 무관 검색이 가능합니다

</details>

---

## 문제 2: 커넥션 풀 모니터링 미들웨어 작성

### 설명

모든 요청에 대해 커넥션 풀 상태를 로깅하고, 풀 사용률이 80%를 초과하면 경고 로그를 남기는 미들웨어를 작성하세요.

### 요구사항

1. `PoolMonitorMiddleware` 클래스 작성:
   - 요청 시작 시 풀 상태 기록
   - 요청 완료 후 풀 상태 기록
   - 응답 헤더에 `X-DB-Pool-Usage` 추가 (사용률 %)
   - 풀 사용률 80% 이상 시 WARNING 로그
   - 풀 사용률 95% 이상 시 CRITICAL 로그

2. 풀 사용률 계산: `checked_out / (pool_size + overflow) * 100`

3. `/pool-metrics` 엔드포인트: 현재 풀 상태를 JSON으로 반환

### 예상 입출력

```
# 요청
GET /authors

# 응답 헤더
X-DB-Pool-Usage: 20.0%

# 로그 출력 (사용률 높을 때)
WARNING: DB 커넥션 풀 사용률 85.0% (checked_out=17, total=20)
```

<details>
<summary>힌트</summary>

- `BaseHTTPMiddleware`를 상속받아 `dispatch` 메서드를 구현하세요
- `engine.pool.checkedout()`, `engine.pool.size()` 등으로 풀 상태를 확인합니다
- `response.headers["X-DB-Pool-Usage"]`로 커스텀 헤더를 추가할 수 있습니다
- `logging.getLogger(__name__)`으로 로거를 생성하세요

</details>

---

## 문제 3: 낙관적 잠금(Optimistic Locking) 구현

### 설명

동시에 여러 사용자가 같은 데이터를 수정할 때 충돌을 감지하는 낙관적 잠금 시스템을 구현하세요. `version` 필드를 사용하여 충돌을 감지하고, 재시도 로직도 포함합니다.

### 요구사항

1. `VersionedModel` 베이스 클래스:
   - `version: int` 필드 포함
   - `updated_at: datetime` 자동 갱신

2. `Account` 모델 (잔액 관리):
   - `id`, `owner`, `balance`, `version` 필드
   - `VersionedModel` 상속

3. `optimistic_update` 함수:
   - version 일치 시에만 UPDATE 실행
   - 충돌 감지 시 `OptimisticLockError` 발생
   - 최대 3회 재시도 (`retry_count` 파라미터)

4. `transfer_funds` 서비스 함수:
   - 계좌 간 이체
   - 출금 계좌와 입금 계좌 모두 낙관적 잠금 적용
   - 잔액 부족 시 에러

### 예상 입출력

```python
# 정상 이체
await transfer_funds(session, from_id=1, to_id=2, amount=10000)
# 결과: 계좌1 잔액 감소, 계좌2 잔액 증가, 양쪽 version 증가

# 동시 수정 충돌
# 트랜잭션 A가 먼저 완료 -> 트랜잭션 B에서 OptimisticLockError
# 자동 재시도로 최신 version 기반 재실행
```

<details>
<summary>힌트</summary>

- `update(Account).where(Account.id == id, Account.version == current_version)` 패턴
- `result.rowcount == 0`이면 다른 트랜잭션이 먼저 수정한 것입니다
- 재시도 시에는 세션을 새로 시작하거나 `session.expire(instance)`로 캐시를 무효화하세요
- `asyncio.sleep(0.1 * retry_number)`로 지수 백오프를 구현할 수 있습니다

</details>

---

## 문제 4: 읽기/쓰기 분리 의존성 구현

### 설명

마스터(쓰기)와 레플리카(읽기) 데이터베이스를 분리하여 사용하는 의존성 시스템을 구현하세요. HTTP 메서드에 따라 자동으로 적절한 세션을 주입합니다.

### 요구사항

1. `DatabaseConfig` 클래스:
   - `write_url`: 마스터 DB URL
   - `read_urls`: 레플리카 DB URL 목록 (복수 개)

2. `DatabaseSessionManager`:
   - `write_engine`: 마스터 엔진
   - `read_engines`: 레플리카 엔진 목록
   - `get_write_session()`: 쓰기 세션 팩토리
   - `get_read_session()`: 읽기 세션 팩토리 (라운드 로빈)

3. FastAPI 의존성:
   - `get_write_db`: 쓰기용 세션 (POST, PUT, DELETE)
   - `get_read_db`: 읽기용 세션 (GET)
   - `get_auto_db`: HTTP 메서드에 따라 자동 선택

4. 라운드 로빈으로 읽기 레플리카 부하 분산

### 예상 입출력

```python
# GET 요청 -> 읽기 레플리카 사용
@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_read_db)):
    ...

# POST 요청 -> 마스터 DB 사용
@app.post("/items")
async def create_item(db: AsyncSession = Depends(get_write_db)):
    ...

# 자동 선택
@app.api_route("/items/{id}", methods=["GET", "PUT"])
async def item_detail(db: AsyncSession = Depends(get_auto_db)):
    ...  # GET이면 읽기 레플리카, PUT이면 마스터
```

<details>
<summary>힌트</summary>

- `itertools.cycle()`을 사용하면 라운드 로빈을 쉽게 구현할 수 있습니다
- `Request` 객체에서 `request.method`로 HTTP 메서드를 확인합니다
- 읽기 세션은 `commit()`이 필요 없으므로 더 가볍게 관리할 수 있습니다
- 테스트 시에는 동일한 SQLite 파일을 사용해도 됩니다 (레플리카 시뮬레이션)

</details>

---

## 제출 기준

- 모든 코드가 비동기로 작성되어야 합니다
- 타입 힌트가 완전해야 합니다
- 에러 처리가 적절해야 합니다
- `# 실행 방법:` 주석이 첫 줄에 포함되어야 합니다
