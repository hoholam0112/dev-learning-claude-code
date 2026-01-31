# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn pydantic-settings
"""
프로덕션 설정과 헬스 체크 구현 예제.

주요 학습 포인트:
- pydantic-settings로 환경 변수 체계적 관리
- 계층별 헬스 체크 (liveness, readiness, startup)
- 구조화된 로깅 (JSON 형식)
- Graceful Shutdown 구현
- CORS, 보안 헤더 설정
"""
import asyncio
import logging
import os
import signal
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# pydantic-settings 사용 시도 (없으면 기본 Pydantic 사용)
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # pydantic-settings가 없으면 기본 BaseModel로 대체
    from pydantic import BaseModel as BaseSettings


# ──────────────────────────────────────────────
# 1. 환경 설정 (pydantic-settings)
# ──────────────────────────────────────────────
class Settings(BaseSettings):
    """
    앱 설정: 환경 변수에서 자동 로딩.

    환경 변수 형식: APP_변수명
    예: APP_DEBUG=true, APP_DATABASE_URL=postgresql://...
    """
    # 앱 기본
    app_name: str = "FastAPI 프로덕션 앱"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # 서버
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # 데이터베이스
    database_url: str = "sqlite:///./app.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300

    # 보안
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 30
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"

    # 로깅
    log_level: str = "INFO"
    log_format: str = "json"  # json 또는 text

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤 (매번 파싱하지 않음)"""
    return Settings()


# ──────────────────────────────────────────────
# 2. 구조화된 로깅
# ──────────────────────────────────────────────
class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포매터"""

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
        }

        # 추가 필드
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
            log_entry["exception_type"] = type(record.exc_info[1]).__name__

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(settings: Settings) -> logging.Logger:
    """로깅 설정"""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 핸들러 설정
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if settings.log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )

    root_logger.handlers = [handler]

    return logging.getLogger("app")


# ──────────────────────────────────────────────
# 3. Graceful Shutdown
# ──────────────────────────────────────────────
class AppState:
    """앱 상태 관리"""

    def __init__(self):
        self.is_ready = False
        self.is_shutting_down = False
        self.start_time = time.time()
        self.request_count = 0
        self.active_requests = 0

    @property
    def uptime_seconds(self) -> float:
        return round(time.time() - self.start_time, 1)


app_state = AppState()


def setup_graceful_shutdown(logger: logging.Logger) -> None:
    """SIGTERM/SIGINT 핸들러 등록"""

    def handle_signal(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.info(f"신호 수신: {sig_name}, Graceful Shutdown 시작...")
        app_state.is_shutting_down = True

    # Docker/K8s에서 SIGTERM 수신 시 Graceful Shutdown
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)


# ──────────────────────────────────────────────
# 4. 헬스 체크
# ──────────────────────────────────────────────
class HealthCheck(BaseModel):
    status: str
    version: str
    environment: str
    uptime_seconds: float
    checks: Optional[dict] = None
    timestamp: str


async def check_database(settings: Settings) -> dict:
    """데이터베이스 연결 확인"""
    try:
        # 실제로는 DB 연결 테스트
        # await db.execute(text("SELECT 1"))
        return {"healthy": True, "latency_ms": 2.5}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def check_redis(settings: Settings) -> dict:
    """Redis 연결 확인"""
    try:
        # 실제로는 Redis ping
        # await redis.ping()
        return {"healthy": True, "latency_ms": 1.0}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


def check_disk_space() -> dict:
    """디스크 공간 확인"""
    import shutil
    total, used, free = shutil.disk_usage("/")
    usage_percent = used / total * 100
    return {
        "healthy": usage_percent < 90,
        "usage_percent": round(usage_percent, 1),
        "free_gb": round(free / (1024 ** 3), 1),
    }


def check_memory() -> dict:
    """메모리 사용량 확인"""
    try:
        import resource
        mem_usage_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        return {"healthy": True, "usage_mb": round(mem_usage_mb, 1)}
    except Exception:
        return {"healthy": True, "usage_mb": 0}


# ──────────────────────────────────────────────
# 5. 앱 생성
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기 관리"""
    settings = get_settings()
    app_logger = setup_logging(settings)

    app_logger.info(
        f"앱 시작: {settings.app_name} v{settings.app_version} "
        f"(환경: {settings.environment})"
    )

    # 시작 처리
    setup_graceful_shutdown(app_logger)
    # DB 연결, Redis 연결 등 초기화...

    app_state.is_ready = True
    app_logger.info("앱 준비 완료")

    yield

    # 종료 처리
    app_logger.info("앱 종료 시작...")
    app_state.is_shutting_down = True

    # 진행 중인 요청 완료 대기 (최대 30초)
    wait_start = time.time()
    while app_state.active_requests > 0 and time.time() - wait_start < 30:
        app_logger.info(f"진행 중인 요청 {app_state.active_requests}개 완료 대기...")
        await asyncio.sleep(1)

    # DB 연결, Redis 연결 정리...
    app_logger.info("앱 종료 완료")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,       # 프로덕션에서는 Swagger 비활성화
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# 6. 미들웨어
# ──────────────────────────────────────────────
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """요청 처리 미들웨어: 로깅, 카운팅, 보안 헤더"""
    import uuid

    # 요청 ID 생성
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

    # Graceful Shutdown 중이면 503 반환
    if app_state.is_shutting_down:
        return JSONResponse(
            status_code=503,
            content={"detail": "서비스 종료 중입니다"},
            headers={"Connection": "close", "Retry-After": "30"},
        )

    # 요청 카운팅
    app_state.request_count += 1
    app_state.active_requests += 1

    start = time.perf_counter()

    try:
        response = await call_next(request)
    finally:
        app_state.active_requests -= 1

    duration_ms = (time.perf_counter() - start) * 1000

    # 보안 헤더 추가
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # 요청 로깅
    logger = logging.getLogger("app.access")
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} "
        f"({duration_ms:.1f}ms) [req:{request_id}]"
    )

    return response


# ──────────────────────────────────────────────
# 7. 헬스 체크 엔드포인트
# ──────────────────────────────────────────────
@app.get("/health/live")
async def liveness():
    """
    Liveness Probe: 프로세스 생존 확인.
    이 엔드포인트가 실패하면 컨테이너를 재시작합니다.
    """
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness(settings: Settings = Depends(get_settings)):
    """
    Readiness Probe: 서비스 준비 상태 확인.
    이 엔드포인트가 실패하면 트래픽을 보내지 않습니다.
    """
    if not app_state.is_ready or app_state.is_shutting_down:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "서비스 준비 안 됨 또는 종료 중"},
        )

    checks = {
        "database": await check_database(settings),
        "redis": await check_redis(settings),
        "disk_space": check_disk_space(),
        "memory": check_memory(),
    }

    all_healthy = all(v.get("healthy", False) for v in checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content=HealthCheck(
            status="ready" if all_healthy else "not_ready",
            version=settings.app_version,
            environment=settings.environment,
            uptime_seconds=app_state.uptime_seconds,
            checks=checks,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ).model_dump(),
    )


@app.get("/health/startup")
async def startup_check():
    """
    Startup Probe: 초기화 완료 확인.
    앱이 시작되는 동안 다른 프로브를 지연시킵니다.
    """
    if app_state.is_ready:
        return {"status": "started"}
    return JSONResponse(status_code=503, content={"status": "starting"})


@app.get("/info")
async def app_info(settings: Settings = Depends(get_settings)):
    """앱 정보"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "uptime_seconds": app_state.uptime_seconds,
        "request_count": app_state.request_count,
        "active_requests": app_state.active_requests,
        "python_version": sys.version,
    }


@app.get("/config")
async def show_config(settings: Settings = Depends(get_settings)):
    """
    설정 확인 (개발 환경만).
    프로덕션에서는 비활성화됩니다.
    """
    if not settings.debug:
        return JSONResponse(
            status_code=403,
            content={"detail": "프로덕션 환경에서는 접근할 수 없습니다"},
        )

    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "database_url": settings.database_url[:20] + "...",  # URL 일부만 노출
        "redis_url": settings.redis_url[:20] + "...",
        "log_level": settings.log_level,
        "workers": settings.workers,
    }


# ──────────────────────────────────────────────
# 8. 샘플 API (테스트용)
# ──────────────────────────────────────────────
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "프로덕션 FastAPI 앱",
        "docs": "/docs" if settings.debug else "비활성화 (프로덕션)",
        "health": "/health/ready",
    }


@app.get("/api/items")
async def list_items():
    """샘플 API 엔드포인트"""
    return [
        {"id": 1, "name": "아이템 1", "price": 10000},
        {"id": 2, "name": "아이템 2", "price": 20000},
    ]
