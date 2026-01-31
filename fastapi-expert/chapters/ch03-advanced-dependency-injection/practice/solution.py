# 실행 방법: uvicorn solution:app --reload
# 테스트 실행: pytest solution.py -v (pytest, httpx 필요)
# 챕터 03 연습문제 모범 답안
# 필요 패키지: pip install fastapi uvicorn httpx pytest

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# 문제 1: 커넥션 풀 의존성 (yield + 에러 처리)
# ============================================================

@dataclass
class AsyncConnection:
    """비동기 DB 연결 시뮬레이션"""
    connection_id: int
    is_healthy: bool = True
    is_closed: bool = False
    in_transaction: bool = False
    query_count: int = 0

    async def execute(self, query: str) -> dict:
        if self.is_closed:
            raise RuntimeError(f"연결 #{self.connection_id}이 닫혀있습니다")
        if not self.is_healthy:
            raise RuntimeError(f"연결 #{self.connection_id}이 비정상 상태입니다")
        await asyncio.sleep(0.01)
        self.query_count += 1
        return {"ok": True, "query": query, "conn_id": self.connection_id}

    async def begin_transaction(self):
        self.in_transaction = True
        logger.info(f"  [연결 #{self.connection_id}] 트랜잭션 시작")

    async def commit(self):
        self.in_transaction = False
        logger.info(f"  [연결 #{self.connection_id}] 커밋")

    async def rollback(self):
        self.in_transaction = False
        logger.info(f"  [연결 #{self.connection_id}] 롤백")

    async def close(self):
        self.is_closed = True
        logger.info(f"  [연결 #{self.connection_id}] 닫힘")

    async def ping(self) -> bool:
        """연결 상태 확인"""
        return self.is_healthy and not self.is_closed


class AsyncConnectionPool:
    """비동기 커넥션 풀"""

    def __init__(self, max_size: int = 5, acquire_timeout: float = 5.0):
        self.max_size = max_size
        self.acquire_timeout = acquire_timeout
        self._available: asyncio.Queue[AsyncConnection] = asyncio.Queue()
        self._all_connections: list[AsyncConnection] = []
        self._counter = 0
        self._in_use_count = 0
        self._waiting_count = 0
        self._is_closed = False

    async def initialize(self):
        """풀 초기화: 연결 생성"""
        logger.info(f"[풀] 초기화 시작 (최대 {self.max_size}개)")
        for _ in range(self.max_size):
            conn = await self._create_connection()
            await self._available.put(conn)
        logger.info(f"[풀] 초기화 완료 ({self.max_size}개 준비)")

    async def _create_connection(self) -> AsyncConnection:
        """새 연결 생성"""
        self._counter += 1
        conn = AsyncConnection(connection_id=self._counter)
        self._all_connections.append(conn)
        return conn

    async def acquire(self) -> AsyncConnection:
        """풀에서 연결 획득"""
        if self._is_closed:
            raise RuntimeError("풀이 닫혀있습니다")

        self._waiting_count += 1
        try:
            conn = await asyncio.wait_for(
                self._available.get(),
                timeout=self.acquire_timeout,
            )
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"연결 획득 타임아웃 ({self.acquire_timeout}초)"
            )
        finally:
            self._waiting_count -= 1

        self._in_use_count += 1
        logger.info(
            f"[풀] 연결 #{conn.connection_id} 획득 "
            f"(가용: {self._available.qsize()}, 사용 중: {self._in_use_count})"
        )
        return conn

    async def release(self, conn: AsyncConnection):
        """연결을 풀에 반환"""
        self._in_use_count -= 1

        # 비정상 연결이면 교체
        if not await conn.ping():
            logger.info(
                f"[풀] 연결 #{conn.connection_id} 비정상 → 새 연결로 교체"
            )
            await conn.close()
            conn = await self._create_connection()

        # 트랜잭션 정리
        if conn.in_transaction:
            await conn.rollback()

        await self._available.put(conn)
        logger.info(
            f"[풀] 연결 #{conn.connection_id} 반환 "
            f"(가용: {self._available.qsize()})"
        )

    async def health_check(self) -> dict:
        """모든 연결의 상태 확인"""
        results = {}
        for conn in self._all_connections:
            healthy = await conn.ping()
            results[f"connection_{conn.connection_id}"] = {
                "healthy": healthy,
                "closed": conn.is_closed,
                "queries": conn.query_count,
            }
        return results

    @property
    def stats(self) -> dict:
        return {
            "total": len(self._all_connections),
            "available": self._available.qsize(),
            "in_use": self._in_use_count,
            "waiting": self._waiting_count,
            "max_size": self.max_size,
        }

    async def close(self):
        """풀 종료"""
        self._is_closed = True
        for conn in self._all_connections:
            if not conn.is_closed:
                await conn.close()
        logger.info("[풀] 모든 연결 닫힘")


# ============================================================
# 문제 2: 공유 리소스 관리
# ============================================================

class CacheClient:
    """캐시 클라이언트 시뮬레이션"""

    def __init__(self):
        self._store: dict[str, Any] = {}
        self._connected = False

    async def connect(self):
        await asyncio.sleep(0.02)
        self._connected = True
        logger.info("[캐시] 연결 완료")

    async def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    async def set(self, key: str, value: Any):
        self._store[key] = value

    async def delete(self, key: str):
        self._store.pop(key, None)

    @property
    def is_healthy(self) -> bool:
        return self._connected

    async def close(self):
        self._connected = False
        self._store.clear()
        logger.info("[캐시] 연결 해제")


class BackgroundScheduler:
    """백그라운드 태스크 스케줄러"""

    def __init__(self, interval: float = 60.0):
        self.interval = interval
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self.execution_count = 0

    async def start(self, cleanup_func=None):
        """스케줄러 시작"""
        self._running = True
        self._cleanup_func = cleanup_func

        async def _run():
            while self._running:
                try:
                    await asyncio.sleep(self.interval)
                    self.execution_count += 1
                    if self._cleanup_func:
                        await self._cleanup_func()
                    logger.info(
                        f"[스케줄러] 정리 작업 실행 #{self.execution_count}"
                    )
                except asyncio.CancelledError:
                    break

        self._task = asyncio.create_task(_run())
        logger.info(f"[스케줄러] 시작 (주기: {self.interval}초)")

    async def stop(self):
        """스케줄러 중지"""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[스케줄러] 중지됨")

    @property
    def is_running(self) -> bool:
        return self._running


@dataclass
class AppSettings:
    """앱 설정"""
    app_name: str = "의존성 주입 예제"
    db_pool_size: int = 3
    cache_enabled: bool = True
    cleanup_interval: float = 60.0
    debug: bool = True


# ============================================================
# 3. lifespan 및 앱 설정
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """앱 생명주기: 리소스 초기화 및 정리"""
    initialized_resources: list[str] = []

    try:
        logger.info("=" * 50)
        logger.info("[lifespan] 앱 시작: 리소스 초기화")

        # 1단계: 설정 로드
        settings = AppSettings()
        app.state.settings = settings
        initialized_resources.append("settings")
        logger.info("[lifespan] 설정 로드 완료")

        # 2단계: DB 풀 초기화 (설정에 의존)
        pool = AsyncConnectionPool(max_size=settings.db_pool_size)
        await pool.initialize()
        app.state.db_pool = pool
        initialized_resources.append("db_pool")

        # 3단계: 캐시 클라이언트 (설정에 의존)
        cache = CacheClient()
        if settings.cache_enabled:
            await cache.connect()
        app.state.cache = cache
        initialized_resources.append("cache")

        # 4단계: 백그라운드 스케줄러 (DB풀 + 캐시에 의존)
        scheduler = BackgroundScheduler(interval=settings.cleanup_interval)

        async def cleanup_task():
            """주기적 정리 작업"""
            health = await pool.health_check()
            logger.info(f"[정리] DB 상태: {health}")

        await scheduler.start(cleanup_func=cleanup_task)
        app.state.scheduler = scheduler
        initialized_resources.append("scheduler")

        logger.info("[lifespan] 모든 리소스 준비 완료!")
        logger.info("=" * 50)

        yield

    except Exception as exc:
        logger.error(f"[lifespan] 초기화 실패: {exc}")
        # 부분 초기화된 리소스 정리 (역순)
        logger.info("[lifespan] 부분 초기화 리소스 정리 시작")
        raise

    finally:
        # 역순 정리
        logger.info("=" * 50)
        logger.info("[lifespan] 앱 종료: 리소스 정리")

        if "scheduler" in initialized_resources:
            await app.state.scheduler.stop()
        if "cache" in initialized_resources:
            await app.state.cache.close()
        if "db_pool" in initialized_resources:
            await app.state.db_pool.close()

        logger.info("[lifespan] 모든 리소스 정리 완료")
        logger.info("=" * 50)


app = FastAPI(
    title="챕터 03 연습문제 모범 답안",
    lifespan=lifespan,
)


# ============================================================
# 4. 의존성 함수 정의
# ============================================================

def get_settings(request: Request) -> AppSettings:
    """설정 의존성"""
    return request.app.state.settings


async def get_connection(request: Request) -> AsyncGenerator:
    """
    문제 1 답안: 커넥션 풀에서 연결을 안전하게 획득/반환하는 yield 의존성.
    """
    pool: AsyncConnectionPool = request.app.state.db_pool
    conn = await pool.acquire()

    try:
        yield conn
    except Exception as exc:
        # 예외 발생 시 롤백 후 로깅
        logger.error(f"[의존성] 예외 발생: {exc}")
        if conn.in_transaction:
            await conn.rollback()
        raise
    finally:
        # 항상 연결 반환 (비정상이면 교체됨)
        await pool.release(conn)


async def get_cache_client(request: Request) -> CacheClient:
    """캐시 클라이언트 의존성"""
    return request.app.state.cache


# ============================================================
# 문제 3: 의존성 오버라이드를 위한 프로덕션 의존성
# ============================================================

class UserModel(BaseModel):
    id: int
    name: str
    email: str


class EmailRecord(BaseModel):
    to: str
    subject: str
    body: str


# 프로덕션 DB (시뮬레이션)
class InMemoryDB:
    """인메모리 데이터베이스"""

    def __init__(self):
        self.users: dict[int, dict] = {}
        self._next_id = 1

    def create_user(self, name: str, email: str) -> dict:
        user = {"id": self._next_id, "name": name, "email": email}
        self.users[self._next_id] = user
        self._next_id += 1
        return user

    def get_user(self, user_id: int) -> Optional[dict]:
        return self.users.get(user_id)

    def list_users(self) -> list[dict]:
        return list(self.users.values())

    def clear(self):
        self.users.clear()
        self._next_id = 1


# 전역 DB 인스턴스
production_db = InMemoryDB()


async def get_db() -> InMemoryDB:
    """프로덕션 DB 의존성"""
    return production_db


async def get_current_user(request: Request) -> UserModel:
    """프로덕션 인증 의존성 (헤더 기반 시뮬레이션)"""
    user_id_str = request.headers.get("X-User-Id")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    user_data = production_db.get_user(int(user_id_str))
    if not user_data:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return UserModel(**user_data)


class EmailService:
    """이메일 서비스"""

    def __init__(self):
        self.sent_emails: list[dict] = []

    async def send(self, to: str, subject: str, body: str):
        """실제 이메일 전송 시뮬레이션"""
        self.sent_emails.append({
            "to": to, "subject": subject, "body": body,
            "timestamp": time.time(),
        })
        logger.info(f"[이메일] 전송: {to} - {subject}")


email_service = EmailService()


async def get_email_service() -> EmailService:
    """이메일 서비스 의존성"""
    return email_service


# ============================================================
# 5. 엔드포인트 정의
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "챕터 03 연습문제 모범 답안",
        "문제1": "/pool/* (커넥션 풀)",
        "문제2": "/health (리소스 상태)",
        "문제3": "/api/* (CRUD + 테스트용)",
    }


# --- 문제 1 엔드포인트 ---

@app.get("/pool/stats")
async def pool_stats(request: Request):
    """커넥션 풀 상태 조회"""
    pool: AsyncConnectionPool = request.app.state.db_pool
    return {
        "stats": pool.stats,
        "health": await pool.health_check(),
    }


@app.get("/success")
async def success_query(
    conn: AsyncConnection = Depends(get_connection),
):
    """정상 쿼리 실행"""
    result = await conn.execute("SELECT 1")
    return {
        "result": result,
        "connection_id": conn.connection_id,
    }


@app.get("/error")
async def error_query(
    conn: AsyncConnection = Depends(get_connection),
):
    """에러 발생 쿼리 (롤백 테스트)"""
    await conn.begin_transaction()
    await conn.execute("INSERT INTO test VALUES (1)")
    # 의도적 에러 → 롤백 후 연결 반환
    raise HTTPException(
        status_code=500,
        detail="의도적 에러: 트랜잭션이 자동 롤백됩니다",
    )


@app.get("/timeout-test")
async def timeout_test(request: Request):
    """
    타임아웃 테스트.
    모든 연결을 점유한 상태에서 추가 요청 시 타임아웃 발생.
    """
    pool: AsyncConnectionPool = request.app.state.db_pool

    # 모든 연결 점유
    connections = []
    try:
        for _ in range(pool.max_size):
            conn = await pool.acquire()
            connections.append(conn)

        # 추가 연결 시도 (타임아웃 발생 예상)
        try:
            extra_conn = await asyncio.wait_for(
                pool.acquire(), timeout=1.0,
            )
            await pool.release(extra_conn)
            return {"message": "타임아웃이 발생하지 않음 (예상치 못한 결과)"}
        except (asyncio.TimeoutError, TimeoutError):
            return {
                "message": "타임아웃 발생 (예상대로)",
                "풀_상태": pool.stats,
            }
    finally:
        # 점유한 연결 모두 반환
        for conn in connections:
            await pool.release(conn)


# --- 문제 2 엔드포인트 ---

@app.get("/health")
async def health_check(request: Request):
    """
    헬스체크: 모든 리소스의 상태를 확인한다.
    하나라도 비정상이면 503 응답.
    """
    pool: AsyncConnectionPool = request.app.state.db_pool
    cache: CacheClient = request.app.state.cache
    scheduler: BackgroundScheduler = request.app.state.scheduler

    resources = {
        "db_pool": {
            "status": "ok" if not pool._is_closed else "error",
            "stats": pool.stats,
        },
        "cache": {
            "status": "ok" if cache.is_healthy else "error",
        },
        "scheduler": {
            "status": "running" if scheduler.is_running else "stopped",
            "executions": scheduler.execution_count,
        },
    }

    all_healthy = all(
        r.get("status") in ("ok", "running")
        for r in resources.values()
    )

    if not all_healthy:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "resources": resources},
        )

    return {"status": "healthy", "resources": resources}


# --- 문제 3 엔드포인트 ---

class CreateUserRequest(BaseModel):
    name: str
    email: str


@app.post("/api/users")
async def create_user(
    data: CreateUserRequest,
    db: InMemoryDB = Depends(get_db),
    mailer: EmailService = Depends(get_email_service),
):
    """사용자 생성 + 환영 이메일 전송"""
    user = db.create_user(data.name, data.email)
    await mailer.send(
        to=data.email,
        subject="환영합니다!",
        body=f"{data.name}님, 가입을 환영합니다.",
    )
    return {"user": user, "email_sent": True}


@app.get("/api/users/{user_id}")
async def get_user_by_id(
    user_id: int,
    db: InMemoryDB = Depends(get_db),
):
    """사용자 조회"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@app.get("/api/users")
async def list_users(
    db: InMemoryDB = Depends(get_db),
):
    """사용자 목록 조회"""
    return {"users": db.list_users()}


@app.get("/api/me")
async def get_me(
    current_user: UserModel = Depends(get_current_user),
):
    """현재 사용자 정보 (인증 필요)"""
    return current_user.model_dump()


# ============================================================
# 문제 3: 테스트 코드 (pytest로 실행)
# ============================================================
# 아래 테스트는 pytest로 실행할 수 있습니다:
#   pytest solution.py -v
# httpx가 필요합니다: pip install httpx

def get_test_fixtures():
    """
    테스트 픽스처를 반환하는 함수.
    pytest가 설치되지 않은 환경에서도 앱이 동작하도록 분리.
    """
    try:
        import pytest
        from fastapi.testclient import TestClient

        # 테스트용 DB
        test_db = InMemoryDB()

        async def get_test_db():
            return test_db

        # 테스트용 사용자
        mock_user = UserModel(id=99, name="테스트사용자", email="test@test.com")

        async def get_mock_user():
            return mock_user

        # 테스트용 이메일 서비스
        test_email_service = EmailService()

        async def get_mock_email():
            return test_email_service

        @pytest.fixture(autouse=True)
        def reset_state():
            """각 테스트 전에 상태 초기화"""
            test_db.clear()
            test_email_service.sent_emails.clear()
            yield
            # 정리
            app.dependency_overrides.clear()

        @pytest.fixture
        def client():
            """테스트 클라이언트 픽스처"""
            app.dependency_overrides[get_db] = get_test_db
            app.dependency_overrides[get_email_service] = get_mock_email
            with TestClient(app) as c:
                yield c
            app.dependency_overrides.clear()

        @pytest.fixture
        def auth_client():
            """인증된 테스트 클라이언트"""
            app.dependency_overrides[get_db] = get_test_db
            app.dependency_overrides[get_current_user] = get_mock_user
            app.dependency_overrides[get_email_service] = get_mock_email
            with TestClient(app) as c:
                yield c
            app.dependency_overrides.clear()

        return {
            "test_db": test_db,
            "test_email_service": test_email_service,
            "mock_user": mock_user,
            "reset_state": reset_state,
            "client": client,
            "auth_client": auth_client,
        }
    except ImportError:
        return None


# 테스트 함수들
fixtures = get_test_fixtures()

if fixtures:
    import pytest
    from fastapi.testclient import TestClient

    _test_db = fixtures["test_db"]
    _test_email = fixtures["test_email_service"]
    _mock_user = fixtures["mock_user"]
    reset_state = fixtures["reset_state"]
    client = fixtures["client"]
    auth_client = fixtures["auth_client"]

    def test_create_user(client: TestClient, reset_state):
        """사용자 생성 테스트"""
        response = client.post("/api/users", json={
            "name": "홍길동",
            "email": "hong@example.com",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "홍길동"
        assert data["email_sent"] is True

    def test_get_user(client: TestClient, reset_state):
        """사용자 조회 테스트"""
        # 먼저 생성
        client.post("/api/users", json={
            "name": "김영희", "email": "kim@example.com",
        })
        # 조회
        response = client.get("/api/users/1")
        assert response.status_code == 200
        assert response.json()["name"] == "김영희"

    def test_get_nonexistent_user(client: TestClient, reset_state):
        """존재하지 않는 사용자 조회 테스트"""
        response = client.get("/api/users/999")
        assert response.status_code == 404

    def test_protected_endpoint_with_auth(
        auth_client: TestClient, reset_state
    ):
        """인증된 요청 테스트"""
        response = auth_client.get("/api/me")
        assert response.status_code == 200
        assert response.json()["name"] == "테스트사용자"

    def test_protected_endpoint_without_auth(reset_state):
        """인증 없는 요청 테스트"""
        # 오버라이드 없이 원래 의존성 사용
        app.dependency_overrides[get_db] = fixtures["client"].__wrapped__ if hasattr(fixtures["client"], '__wrapped__') else lambda: _test_db
        with TestClient(app) as c:
            response = c.get("/api/me")
            assert response.status_code == 401
        app.dependency_overrides.clear()

    def test_email_sent_on_registration(
        client: TestClient, reset_state
    ):
        """회원가입 시 이메일 전송 확인"""
        client.post("/api/users", json={
            "name": "테스트", "email": "test@example.com",
        })
        assert len(_test_email.sent_emails) == 1
        assert _test_email.sent_emails[0]["to"] == "test@example.com"
        assert "환영" in _test_email.sent_emails[0]["subject"]

    def test_data_isolation(client: TestClient, reset_state):
        """테스트 간 데이터 격리 확인"""
        # 이 테스트에서 생성한 데이터는 다른 테스트에 영향을 주지 않음
        response = client.get("/api/users")
        assert response.json()["users"] == []  # 비어있어야 함

        client.post("/api/users", json={
            "name": "격리테스트", "email": "isolation@test.com",
        })
        response = client.get("/api/users")
        assert len(response.json()["users"]) == 1


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("챕터 03 연습문제 모범 답안 서버")
    print("=" * 60)
    print("\n문제 1 (커넥션 풀):")
    print("  GET  http://localhost:8000/pool/stats")
    print("  GET  http://localhost:8000/success")
    print("  GET  http://localhost:8000/error")
    print("  GET  http://localhost:8000/timeout-test")
    print("\n문제 2 (리소스 관리):")
    print("  GET  http://localhost:8000/health")
    print("\n문제 3 (CRUD + 테스트):")
    print("  POST http://localhost:8000/api/users")
    print("  GET  http://localhost:8000/api/users")
    print("  GET  http://localhost:8000/api/users/1")
    print("  GET  http://localhost:8000/api/me (X-User-Id 헤더 필요)")
    print("\n테스트 실행: pytest solution.py -v")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
