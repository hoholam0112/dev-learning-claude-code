# 실행 방법: uvicorn example-01:app --reload
# yield 의존성과 lifespan 이벤트 활용 예제
# 필요 패키지: pip install fastapi uvicorn

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Request

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# 1. 시뮬레이션용 리소스 클래스
# ============================================================

@dataclass
class DatabaseConnection:
    """데이터베이스 연결 시뮬레이션"""
    connection_id: int
    is_closed: bool = False
    in_transaction: bool = False
    _data: dict = field(default_factory=dict)

    async def execute(self, query: str, params: dict = None) -> dict:
        """쿼리 실행 시뮬레이션"""
        if self.is_closed:
            raise RuntimeError("이미 닫힌 연결입니다")
        logger.info(f"  [DB #{self.connection_id}] 쿼리 실행: {query}")
        await asyncio.sleep(0.01)  # 네트워크 지연 시뮬레이션
        return {"result": "ok", "query": query}

    async def begin(self):
        """트랜잭션 시작"""
        self.in_transaction = True
        logger.info(f"  [DB #{self.connection_id}] 트랜잭션 시작")

    async def commit(self):
        """트랜잭션 커밋"""
        self.in_transaction = False
        logger.info(f"  [DB #{self.connection_id}] 커밋")

    async def rollback(self):
        """트랜잭션 롤백"""
        self.in_transaction = False
        logger.info(f"  [DB #{self.connection_id}] 롤백")

    async def close(self):
        """연결 닫기"""
        if self.in_transaction:
            await self.rollback()
        self.is_closed = True
        logger.info(f"  [DB #{self.connection_id}] 연결 닫힘")


class ConnectionPool:
    """커넥션 풀 시뮬레이션"""

    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self._connections: list[DatabaseConnection] = []
        self._available: asyncio.Queue = asyncio.Queue()
        self._counter = 0
        self._is_closed = False

    async def initialize(self):
        """풀 초기화: 미리 연결을 생성"""
        logger.info(f"[풀] 커넥션 풀 초기화 (최대 {self.max_size}개)")
        for _ in range(self.max_size):
            conn = await self._create_connection()
            await self._available.put(conn)
        logger.info(f"[풀] {self.max_size}개 연결 준비 완료")

    async def _create_connection(self) -> DatabaseConnection:
        """새 연결 생성"""
        self._counter += 1
        conn = DatabaseConnection(connection_id=self._counter)
        self._connections.append(conn)
        return conn

    async def acquire(self) -> DatabaseConnection:
        """풀에서 연결 획득"""
        if self._is_closed:
            raise RuntimeError("풀이 닫혀있습니다")
        conn = await asyncio.wait_for(self._available.get(), timeout=5.0)
        logger.info(f"[풀] 연결 #{conn.connection_id} 획득 "
                     f"(남은 연결: {self._available.qsize()})")
        return conn

    async def release(self, conn: DatabaseConnection):
        """연결을 풀에 반환"""
        if not conn.is_closed:
            if conn.in_transaction:
                await conn.rollback()
            await self._available.put(conn)
            logger.info(f"[풀] 연결 #{conn.connection_id} 반환 "
                         f"(남은 연결: {self._available.qsize()})")

    async def close(self):
        """풀의 모든 연결 닫기"""
        self._is_closed = True
        for conn in self._connections:
            if not conn.is_closed:
                await conn.close()
        logger.info("[풀] 모든 연결 닫힘")

    @property
    def stats(self) -> dict:
        return {
            "총_연결_수": len(self._connections),
            "사용_가능": self._available.qsize(),
            "사용_중": len(self._connections) - self._available.qsize(),
            "최대_크기": self.max_size,
        }


class CacheClient:
    """캐시 클라이언트 시뮬레이션"""

    def __init__(self):
        self._store: dict = {}
        self._connected = False

    async def connect(self):
        """캐시 서버 연결"""
        await asyncio.sleep(0.05)  # 연결 지연 시뮬레이션
        self._connected = True
        logger.info("[캐시] 연결 완료")

    async def get(self, key: str):
        """캐시 조회"""
        return self._store.get(key)

    async def set(self, key: str, value, ttl: int = 300):
        """캐시 저장"""
        self._store[key] = value

    async def close(self):
        """연결 해제"""
        self._connected = False
        logger.info("[캐시] 연결 해제")


# ============================================================
# 2. lifespan 이벤트로 앱 수준 리소스 관리
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    애플리케이션 생명주기 관리.
    서버 시작 시 리소스를 초기화하고, 종료 시 정리한다.
    """
    logger.info("=" * 50)
    logger.info("앱 시작: 리소스 초기화 중...")

    # 1. 커넥션 풀 생성 및 초기화
    pool = ConnectionPool(max_size=3)
    await pool.initialize()
    app.state.db_pool = pool

    # 2. 캐시 클라이언트 연결
    cache = CacheClient()
    await cache.connect()
    app.state.cache = cache

    # 3. 앱 설정 로딩
    app.state.config = {
        "app_name": "의존성 주입 예제",
        "version": "1.0.0",
        "started_at": time.time(),
    }

    logger.info("앱 시작 완료!")
    logger.info("=" * 50)

    yield  # 앱이 실행되는 동안 대기

    logger.info("=" * 50)
    logger.info("앱 종료: 리소스 정리 중...")

    # 역순으로 정리 (LIFO)
    await cache.close()
    await pool.close()

    logger.info("앱 종료 완료!")
    logger.info("=" * 50)


app = FastAPI(
    title="yield 의존성과 lifespan 이벤트",
    lifespan=lifespan,
)


# ============================================================
# 3. yield 의존성 정의
# ============================================================

async def get_db_connection(request: Request) -> AsyncGenerator:
    """
    커넥션 풀에서 DB 연결을 획득하는 yield 의존성.
    요청 처리 후 반드시 연결을 풀에 반환한다.
    """
    pool: ConnectionPool = request.app.state.db_pool
    conn = await pool.acquire()

    try:
        yield conn
    except Exception as exc:
        # 엔드포인트에서 예외 발생 시 롤백
        logger.error(f"[의존성] 예외 발생, 롤백: {exc}")
        if conn.in_transaction:
            await conn.rollback()
        raise
    finally:
        # 항상 연결을 풀에 반환
        await pool.release(conn)


async def get_db_transaction(
    conn: DatabaseConnection = Depends(get_db_connection),
) -> AsyncGenerator:
    """
    트랜잭션을 자동으로 관리하는 yield 의존성.
    get_db_connection 위에 구축된 계층적 의존성이다.
    """
    await conn.begin()
    try:
        yield conn
        # 정상 완료 시 커밋
        await conn.commit()
    except Exception:
        # 예외 발생 시 롤백
        await conn.rollback()
        raise


async def get_cache(request: Request) -> CacheClient:
    """캐시 클라이언트 의존성 (lifespan에서 초기화한 것을 반환)"""
    return request.app.state.cache


# ============================================================
# 4. 엔드포인트 정의
# ============================================================

@app.get("/")
async def root():
    """기본 엔드포인트"""
    return {
        "message": "yield 의존성과 lifespan 이벤트 예제",
        "엔드포인트": {
            "/pool-stats": "커넥션 풀 상태",
            "/query": "단순 쿼리 (커넥션 자동 반환)",
            "/transaction": "트랜잭션 (자동 커밋/롤백)",
            "/transaction-error": "트랜잭션 에러 (자동 롤백 테스트)",
            "/cached-query": "캐시 + DB 조합",
        },
    }


@app.get("/pool-stats")
async def pool_stats(request: Request):
    """커넥션 풀 상태 확인"""
    pool: ConnectionPool = request.app.state.db_pool
    config = request.app.state.config
    uptime = time.time() - config["started_at"]

    return {
        "풀_상태": pool.stats,
        "앱_정보": config,
        "가동_시간": f"{uptime:.1f}초",
    }


@app.get("/query")
async def simple_query(
    q: str = "SELECT * FROM users",
    conn: DatabaseConnection = Depends(get_db_connection),
):
    """
    단순 쿼리 실행.
    요청 완료 후 커넥션이 자동으로 풀에 반환된다.
    """
    result = await conn.execute(q)
    return {
        "connection_id": conn.connection_id,
        "result": result,
        "설명": "이 응답 후 연결은 자동으로 풀에 반환됩니다",
    }


@app.post("/transaction")
async def with_transaction(
    conn: DatabaseConnection = Depends(get_db_transaction),
):
    """
    트랜잭션 내에서 여러 쿼리 실행.
    모두 성공하면 자동 커밋, 하나라도 실패하면 자동 롤백된다.
    """
    await conn.execute("INSERT INTO users (name) VALUES ('홍길동')")
    await conn.execute("INSERT INTO logs (action) VALUES ('user_created')")
    return {
        "connection_id": conn.connection_id,
        "result": "두 쿼리가 하나의 트랜잭션으로 커밋되었습니다",
    }


@app.post("/transaction-error")
async def transaction_with_error(
    conn: DatabaseConnection = Depends(get_db_transaction),
):
    """
    의도적으로 에러를 발생시켜 자동 롤백을 테스트한다.
    """
    await conn.execute("INSERT INTO users (name) VALUES ('테스트')")
    # 의도적 에러 발생 → 트랜잭션이 자동 롤백됨
    raise HTTPException(status_code=400, detail="의도적 에러: 트랜잭션 롤백됨")


@app.get("/cached-query")
async def cached_query(
    key: str = "user:1",
    conn: DatabaseConnection = Depends(get_db_connection),
    cache: CacheClient = Depends(get_cache),
):
    """
    캐시를 먼저 확인하고, 없으면 DB에서 조회 후 캐싱.
    두 개의 의존성(conn, cache)을 조합하여 사용한다.
    """
    # 캐시 확인
    cached = await cache.get(key)
    if cached:
        return {
            "source": "cache",
            "data": cached,
            "설명": "캐시에서 조회됨",
        }

    # DB 조회
    result = await conn.execute(f"SELECT * FROM users WHERE id = '{key}'")

    # 캐시 저장
    await cache.set(key, result, ttl=60)

    return {
        "source": "database",
        "data": result,
        "connection_id": conn.connection_id,
        "설명": "DB에서 조회 후 캐시에 저장됨",
    }


@app.get("/dependency-caching-demo")
async def dependency_caching_demo(
    conn1: DatabaseConnection = Depends(get_db_connection),
    conn2: DatabaseConnection = Depends(get_db_connection),
):
    """
    의존성 캐싱 데모.
    같은 요청 내에서 동일한 의존성이 두 번 사용되면 캐싱된다.
    """
    return {
        "conn1_id": conn1.connection_id,
        "conn2_id": conn2.connection_id,
        "같은_객체인가": conn1 is conn2,
        "설명": (
            "FastAPI는 같은 요청 내에서 동일한 의존성 함수를 "
            "한 번만 실행하고 결과를 캐싱합니다 (use_cache=True가 기본)"
        ),
    }


if __name__ == "__main__":
    import uvicorn

    print("yield 의존성과 lifespan 이벤트 서버를 시작합니다...")
    print("서버 시작 시 리소스 초기화 로그를 확인하세요!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
