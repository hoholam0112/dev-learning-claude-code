# 챕터 06: 데이터베이스 최적화 (비동기)

> **난이도**: ⭐⭐⭐⭐ (4/5)
> **예상 학습 시간**: 4~5시간
> **사전 요구사항**: SQLAlchemy 기본, 비동기 프로그래밍, FastAPI 의존성 주입

---

## 학습 목표

이 챕터를 완료하면 다음을 할 수 있습니다:

1. SQLAlchemy 2.0 비동기 엔진의 내부 동작 원리를 이해한다
2. 커넥션 풀을 프로덕션 환경에 맞게 최적화한다
3. N+1 문제를 식별하고 체계적으로 해결한다
4. 트랜잭션 관리 전략(중첩, 세이브포인트)을 실무에 적용한다
5. 리포지토리 패턴으로 데이터 접근 계층을 설계한다
6. Alembic으로 마이그레이션을 자동화한다
7. 읽기/쓰기 분리 전략을 구현한다

---

## 1. SQLAlchemy 2.0 비동기 엔진

### 1.1 AsyncEngine 내부 구조

SQLAlchemy 2.0의 비동기 지원은 **greenlet** 기반으로 동작합니다. `AsyncEngine`은 동기 `Engine`을 래핑하여 비동기 인터페이스를 제공합니다.

```mermaid
graph TB
    subgraph "비동기 레이어"
        AE[AsyncEngine]
        AS[AsyncSession]
        AC[AsyncConnection]
    end

    subgraph "동기 코어 (greenlet)"
        SE[Engine]
        SS[Session]
        SC[Connection]
    end

    subgraph "DBAPI"
        AD[aiosqlite / asyncpg]
        Pool[Connection Pool]
    end

    AE -->|래핑| SE
    AS -->|래핑| SS
    AC -->|래핑| SC
    SE --> Pool
    Pool --> AD
```

**핵심 원리**: `AsyncEngine`은 내부적으로 `greenlet`을 사용하여 동기 SQLAlchemy 코어를 비동기 컨텍스트에서 실행합니다. 이는 SQLAlchemy의 모든 기존 기능을 비동기에서 재사용할 수 있게 합니다.

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 비동기 엔진 생성 - 내부적으로 동기 Engine + greenlet 브릿지
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True,  # SQL 로깅 (개발 시)
)

# async_sessionmaker는 Session 팩토리의 비동기 버전
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 커밋 후 속성 만료 방지 (중요!)
)
```

### 1.2 expire_on_commit=False의 중요성

```python
# expire_on_commit=True (기본값) 일 때 문제:
async with async_session() as session:
    user = User(name="홍길동")
    session.add(user)
    await session.commit()
    # 아래 줄에서 MissingGreenlet 에러 발생!
    # 커밋 후 속성에 접근하면 Lazy Loading 시도 -> 비동기에서 실패
    print(user.name)  # ❌ 에러

# expire_on_commit=False로 설정하면:
async with async_session() as session:
    user = User(name="홍길동")
    session.add(user)
    await session.commit()
    print(user.name)  # ✅ 정상 동작 (캐시된 값 사용)
```

---

## 2. 커넥션 풀 설정과 최적화

### 2.1 커넥션 풀 동작 원리

```mermaid
sequenceDiagram
    participant App as 애플리케이션
    participant Pool as 커넥션 풀
    participant DB as 데이터베이스

    Note over Pool: pool_size=5, max_overflow=10

    App->>Pool: 연결 요청 #1~5
    Pool->>DB: 새 연결 생성 (풀 범위 내)
    DB-->>Pool: 연결 반환
    Pool-->>App: 연결 제공

    App->>Pool: 연결 요청 #6~15
    Pool->>DB: 오버플로우 연결 생성
    DB-->>Pool: 연결 반환
    Pool-->>App: 연결 제공

    App->>Pool: 연결 요청 #16 (pool_timeout 대기)
    Note over Pool: 30초 대기 후 TimeoutError

    App->>Pool: 연결 반환
    Pool->>Pool: pool_size 이내면 풀에 보관
    Pool->>DB: 오버플로우 연결이면 종료
```

### 2.2 풀 설정 파라미터 상세

| 파라미터 | 기본값 | 설명 | 프로덕션 권장값 |
|----------|--------|------|-----------------|
| `pool_size` | 5 | 풀에 유지할 영구 연결 수 | CPU 코어 수 * 2 |
| `max_overflow` | 10 | 풀 초과 시 추가 가능한 연결 수 | pool_size와 동일 |
| `pool_timeout` | 30 | 연결 대기 최대 시간 (초) | 10~30 |
| `pool_recycle` | -1 | 연결 재활용 주기 (초) | 1800 (30분) |
| `pool_pre_ping` | False | 연결 사용 전 유효성 검사 | True |

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # 동시 연결 10개 유지
    max_overflow=10,        # 최대 20개까지 허용
    pool_timeout=10,        # 10초 대기 후 에러
    pool_recycle=1800,      # 30분마다 연결 재생성 (MySQL wait_timeout 대응)
    pool_pre_ping=True,     # 끊어진 연결 자동 감지/복구
    echo=False,             # 프로덕션에서는 반드시 False
)
```

### 2.3 풀 크기 결정 공식

```
최적 pool_size = (CPU 코어 수 * 2) + 동시 I/O 대기 수
```

**주의사항**:
- PostgreSQL `max_connections` (기본 100) 을 초과하지 않아야 합니다
- Gunicorn 워커 수 * pool_size < DB max_connections
- 예: 4 워커 * pool_size=10 = 40 연결 필요

---

## 3. N+1 문제 분석과 해결

### 3.1 N+1 문제란?

```mermaid
graph LR
    subgraph "N+1 문제 (비효율)"
        Q1["쿼리 1: SELECT * FROM authors"]
        Q2["쿼리 2: SELECT * FROM books WHERE author_id=1"]
        Q3["쿼리 3: SELECT * FROM books WHERE author_id=2"]
        QN["쿼리 N: SELECT * FROM books WHERE author_id=N"]
        Q1 --> Q2
        Q1 --> Q3
        Q1 --> QN
    end
```

```mermaid
graph LR
    subgraph "selectinload (효율적)"
        SQ1["쿼리 1: SELECT * FROM authors"]
        SQ2["쿼리 2: SELECT * FROM books WHERE author_id IN (1,2,...N)"]
        SQ1 --> SQ2
    end
```

### 3.2 로딩 전략 비교

| 전략 | SQL 쿼리 수 | 메모리 사용 | 적합한 경우 |
|------|------------|------------|------------|
| `lazy` (기본) | 1 + N | 낮음 | 관계 데이터를 거의 안 쓸 때 |
| `selectinload` | 2 | 중간 | 대부분의 경우 (권장) |
| `joinedload` | 1 (JOIN) | 높음 | 1:1 관계, 적은 데이터 |
| `subqueryload` | 2 | 중간 | 복잡한 필터링이 필요할 때 |
| `raiseload` | 에러 발생 | - | N+1 방지를 강제할 때 |

```python
from sqlalchemy.orm import selectinload, joinedload, raiseload

# selectinload: 별도 IN 쿼리로 관계 로딩 (가장 범용적)
stmt = select(Author).options(selectinload(Author.books))

# joinedload: JOIN으로 한 번에 로딩 (1:1 관계에 적합)
stmt = select(Author).options(joinedload(Author.profile))

# 중첩 로딩: 다단계 관계
stmt = select(Author).options(
    selectinload(Author.books).selectinload(Book.reviews)
)

# raiseload: 명시적 로딩 없이 접근 시 에러 (N+1 방지 강제)
stmt = select(Author).options(raiseload(Author.books))
```

### 3.3 N+1 문제 감지 방법

```python
import logging

# SQL 쿼리 로깅으로 N+1 감지
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# 또는 이벤트 리스너로 쿼리 수 카운트
from sqlalchemy import event

query_count = 0

@event.listens_for(engine.sync_engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1
```

---

## 4. 트랜잭션 관리 전략

### 4.1 기본 트랜잭션 패턴

```python
# 패턴 1: 의존성에서 트랜잭션 관리 (권장)
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# 패턴 2: 명시적 트랜잭션 블록
async def transfer_funds(session: AsyncSession, from_id: int, to_id: int, amount: float):
    async with session.begin():  # 자동 커밋/롤백
        from_account = await session.get(Account, from_id)
        to_account = await session.get(Account, to_id)
        from_account.balance -= amount
        to_account.balance += amount
```

### 4.2 중첩 트랜잭션과 세이브포인트

```python
async def complex_operation(session: AsyncSession):
    """중첩 트랜잭션: 부분 롤백이 필요한 경우"""
    # 외부 트랜잭션 시작
    async with session.begin():
        await session.execute(...)  # 작업 A

        # 중첩 트랜잭션 (SAVEPOINT)
        try:
            async with session.begin_nested():
                await session.execute(...)  # 작업 B (실패할 수 있음)
        except Exception:
            # 작업 B만 롤백, 작업 A는 유지
            pass

        await session.execute(...)  # 작업 C
    # 작업 A + C 커밋 (작업 B가 실패해도)
```

### 4.3 트랜잭션 격리 수준

```python
from sqlalchemy import text

# 격리 수준 설정
engine = create_async_engine(
    DATABASE_URL,
    execution_options={"isolation_level": "REPEATABLE READ"}
)

# 또는 세션별 설정
async with async_session() as session:
    await session.connection(
        execution_options={"isolation_level": "SERIALIZABLE"}
    )
```

---

## 5. 리포지토리 패턴

### 5.1 패턴 구조

```mermaid
graph TB
    Router[라우터/엔드포인트] --> Service[서비스 계층]
    Service --> Repo[리포지토리]
    Repo --> Session[AsyncSession]
    Session --> DB[(데이터베이스)]

    style Router fill:#e1f5fe
    style Service fill:#f3e5f5
    style Repo fill:#e8f5e9
    style Session fill:#fff3e0
```

### 5.2 제네릭 리포지토리

```python
from typing import TypeVar, Generic, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """제네릭 리포지토리 베이스 클래스"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.flush()
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False
```

---

## 6. Alembic 마이그레이션 자동화

### 6.1 비동기 Alembic 설정

```bash
# 초기화
alembic init -t async alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "add users table"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

### 6.2 env.py 비동기 설정

```python
# alembic/env.py
from sqlalchemy.ext.asyncio import async_engine_from_config

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()
```

---

## 7. 읽기/쓰기 분리 전략

### 7.1 아키텍처

```mermaid
graph LR
    App[FastAPI 앱] --> Router{라우터}
    Router -->|읽기 요청| ReadDB[(읽기 복제본)]
    Router -->|쓰기 요청| WriteDB[(마스터 DB)]
    WriteDB -->|복제| ReadDB
```

### 7.2 구현 예시

```python
# 읽기/쓰기 엔진 분리
write_engine = create_async_engine("postgresql+asyncpg://master:5432/db")
read_engine = create_async_engine("postgresql+asyncpg://replica:5432/db")

write_session = async_sessionmaker(write_engine, expire_on_commit=False)
read_session = async_sessionmaker(read_engine, expire_on_commit=False)

# 의존성으로 분리
async def get_write_db():
    async with write_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_read_db():
    async with read_session() as session:
        yield session  # 읽기 전용, 커밋 불필요
```

---

## 주의사항

1. **비동기에서 Lazy Loading 금지**: 비동기 세션에서는 반드시 Eager Loading 전략을 사용해야 합니다
2. **커넥션 풀 누수 방지**: 세션을 반드시 `async with`로 관리하세요
3. **pool_pre_ping 활성화**: 프로덕션에서는 끊어진 연결 자동 감지를 위해 반드시 활성화하세요
4. **expire_on_commit=False**: 비동기 세션에서는 거의 필수입니다
5. **트랜잭션 범위 최소화**: 긴 트랜잭션은 데드락과 성능 저하의 원인입니다

---

## 정리

| 개념 | 핵심 포인트 |
|------|------------|
| AsyncEngine | greenlet 기반 동기 코어 래핑, expire_on_commit=False 필수 |
| 커넥션 풀 | pool_size는 코어*2, pool_pre_ping=True, 총 연결 수 관리 |
| N+1 문제 | selectinload 기본, joinedload는 1:1, raiseload로 강제 방지 |
| 트랜잭션 | begin_nested()로 세이브포인트, 격리 수준 적절히 설정 |
| 리포지토리 패턴 | 제네릭 베이스 + 도메인별 확장, 서비스 계층과 분리 |
| 읽기/쓰기 분리 | 별도 엔진/세션, 의존성으로 주입 |

---

## 다음 단계

- **챕터 07**: Redis 캐싱 레이어를 추가하여 데이터베이스 부하를 더욱 줄이는 방법을 학습합니다
- 실제 프로젝트에서 슬로우 쿼리 로그를 분석하고 최적화하는 연습을 해보세요
- PostgreSQL의 `EXPLAIN ANALYZE`를 사용한 쿼리 실행 계획 분석을 병행하면 좋습니다
