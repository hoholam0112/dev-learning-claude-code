# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn
"""
챕터 10 연습문제 모범 답안.

문제 1: Dockerfile 최적화는 별도 Dockerfile/docker-compose.yml로 제공
문제 2: 구조화된 로깅 시스템
문제 3: Graceful Shutdown 구현

이 파일은 문제 2와 문제 3의 코드를 통합합니다.
"""
import asyncio
import contextvars
import json
import logging
import os
import signal
import sys
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 2: 구조화된 로깅 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 컨텍스트 변수 (비동기 안전)
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)
trace_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default=""
)
user_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "user_id", default=""
)


class StructuredLogger:
    """
    구조화된 JSON 로거.

    모든 로그를 JSON 형식으로 출력하며,
    컨텍스트 변수에서 request_id, trace_id 등을 자동으로 포함합니다.
    """

    def __init__(self, service: str = "api", min_level: int = logging.INFO):
        self.service = service
        self.min_level = min_level

    def _build_entry(self, level: str, message: str, **extra: Any) -> dict:
        """로그 엔트리 구성"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "service": self.service,
        }

        # 컨텍스트 변수 자동 포함
        req_id = request_id_ctx.get("")
        if req_id:
            entry["request_id"] = req_id
        trace_id = trace_id_ctx.get("")
        if trace_id:
            entry["trace_id"] = trace_id
        user_id = user_id_ctx.get("")
        if user_id:
            entry["user_id"] = user_id

        # 추가 필드
        entry.update(extra)

        return entry

    def _emit(self, entry: dict) -> None:
        """로그 출력"""
        print(json.dumps(entry, ensure_ascii=False), flush=True)

    def debug(self, message: str, **extra: Any) -> None:
        if self.min_level <= logging.DEBUG:
            self._emit(self._build_entry("debug", message, **extra))

    def info(self, message: str, **extra: Any) -> None:
        if self.min_level <= logging.INFO:
            self._emit(self._build_entry("info", message, **extra))

    def warning(self, message: str, **extra: Any) -> None:
        if self.min_level <= logging.WARNING:
            self._emit(self._build_entry("warning", message, **extra))

    def error(self, message: str, **extra: Any) -> None:
        if self.min_level <= logging.ERROR:
            self._emit(self._build_entry("error", message, **extra))

    def critical(self, message: str, **extra: Any) -> None:
        self._emit(self._build_entry("critical", message, **extra))


# 로거 인스턴스
logger = StructuredLogger(service="fastapi-app", min_level=logging.INFO)


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    구조화된 접근 로그 미들웨어.

    모든 요청/응답을 JSON으로 로깅합니다.
    - 요청 ID 자동 생성/전파
    - 느린 요청 경고 (500ms 이상)
    - 에러 응답 시 에러 로그
    """

    SLOW_THRESHOLD_MS = 500

    async def dispatch(self, request: Request, call_next):
        # 요청 ID 설정
        req_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:8])
        request_id_ctx.set(req_id)

        # 트레이스 ID 설정
        trace_id = request.headers.get("X-Trace-ID", uuid.uuid4().hex[:16])
        trace_id_ctx.set(trace_id)

        # 클라이언트 정보
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        start = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start) * 1000
            status_code = response.status_code

            # 접근 로그
            log_data = {
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "client_ip": client_ip,
                "user_agent": user_agent[:100],
            }

            if status_code >= 500:
                logger.error("request_failed", **log_data)
            elif status_code >= 400:
                logger.warning("request_client_error", **log_data)
            elif duration_ms > self.SLOW_THRESHOLD_MS:
                logger.warning(
                    "slow_request",
                    threshold_ms=self.SLOW_THRESHOLD_MS,
                    **log_data,
                )
            else:
                logger.info("request_completed", **log_data)

            # 응답 헤더
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Trace-ID"] = trace_id

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "unhandled_exception",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc(),
            )
            raise


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 3: Graceful Shutdown
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class GracefulShutdownManager:
    """
    Graceful Shutdown 관리자.

    SIGTERM/SIGINT 수신 시:
    1. 헬스 체크 실패 시작 (새 트래픽 차단)
    2. 진행 중인 요청 완료 대기
    3. 리소스 정리
    4. 프로세스 종료
    """

    def __init__(self, grace_period_seconds: int = 30):
        self.grace_period = grace_period_seconds
        self.is_shutting_down = False
        self.is_ready = False
        self.active_requests = 0
        self.start_time = time.time()
        self._shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()

    def setup_signals(self) -> None:
        """신호 핸들러 등록"""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._handle_signal)
        logger.info("signal_handlers_registered", signals=["SIGTERM", "SIGINT"])

    def _handle_signal(self, signum: int, frame) -> None:
        """신호 수신 핸들러"""
        sig_name = signal.Signals(signum).name
        logger.info("signal_received", signal=sig_name, action="graceful_shutdown_start")
        self.is_shutting_down = True
        self.is_ready = False

    async def increment_requests(self) -> None:
        """진행 중인 요청 증가"""
        async with self._lock:
            self.active_requests += 1

    async def decrement_requests(self) -> None:
        """진행 중인 요청 감소"""
        async with self._lock:
            self.active_requests -= 1

    async def wait_for_completion(self) -> None:
        """모든 진행 중인 요청 완료 대기"""
        logger.info(
            "waiting_for_requests",
            active_requests=self.active_requests,
            grace_period=self.grace_period,
        )

        wait_start = time.time()
        while self.active_requests > 0:
            elapsed = time.time() - wait_start
            if elapsed >= self.grace_period:
                logger.warning(
                    "grace_period_exceeded",
                    remaining_requests=self.active_requests,
                    elapsed_seconds=round(elapsed, 1),
                )
                break

            logger.info(
                "waiting_for_requests",
                active_requests=self.active_requests,
                remaining_seconds=round(self.grace_period - elapsed, 1),
            )
            await asyncio.sleep(1)

        if self.active_requests == 0:
            logger.info("all_requests_completed")

    async def cleanup_resources(self) -> None:
        """리소스 정리"""
        logger.info("cleaning_up_resources")

        # 데이터베이스 연결 종료
        logger.info("closing_database_connections")
        await asyncio.sleep(0.1)  # 시뮬레이션

        # Redis 연결 종료
        logger.info("closing_redis_connections")
        await asyncio.sleep(0.1)  # 시뮬레이션

        # 기타 정리
        logger.info("resources_cleaned_up")

    @property
    def uptime_seconds(self) -> float:
        return round(time.time() - self.start_time, 1)


shutdown_manager = GracefulShutdownManager(grace_period_seconds=30)


class ShutdownMiddleware(BaseHTTPMiddleware):
    """
    Graceful Shutdown 미들웨어.
    종료 중이면 새 요청을 503으로 거부합니다.
    """

    async def dispatch(self, request: Request, call_next):
        # 헬스 체크는 항상 통과
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # 종료 중이면 새 요청 거부
        if shutdown_manager.is_shutting_down:
            logger.info(
                "request_rejected_during_shutdown",
                method=request.method,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "서비스 종료 중입니다",
                    "retry_after": 30,
                },
                headers={
                    "Connection": "close",
                    "Retry-After": "30",
                },
            )

        # 요청 카운터 관리
        await shutdown_manager.increment_requests()
        try:
            response = await call_next(request)
            return response
        finally:
            await shutdown_manager.decrement_requests()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI 앱
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기"""
    # 시작
    shutdown_manager.setup_signals()
    shutdown_manager.is_ready = True
    logger.info("app_started", version="1.0.0")

    yield

    # 종료
    logger.info("app_shutdown_initiated")
    shutdown_manager.is_shutting_down = True
    shutdown_manager.is_ready = False

    await shutdown_manager.wait_for_completion()
    await shutdown_manager.cleanup_resources()

    logger.info("app_shutdown_completed", uptime_seconds=shutdown_manager.uptime_seconds)


app = FastAPI(
    title="챕터 10 모범 답안",
    description="구조화된 로깅, Graceful Shutdown",
    lifespan=lifespan,
)

# 미들웨어 등록 (순서 중요)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(ShutdownMiddleware)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 헬스 체크
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.get("/health/live")
async def liveness():
    """Liveness: 프로세스 생존 확인"""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    """Readiness: 서비스 준비 상태"""
    if not shutdown_manager.is_ready or shutdown_manager.is_shutting_down:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "is_shutting_down": shutdown_manager.is_shutting_down,
            },
        )
    return {
        "status": "ready",
        "uptime_seconds": shutdown_manager.uptime_seconds,
        "active_requests": shutdown_manager.active_requests,
    }


@app.get("/health/startup")
async def startup():
    """Startup: 초기화 완료 확인"""
    if shutdown_manager.is_ready:
        return {"status": "started"}
    return JSONResponse(status_code=503, content={"status": "starting"})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 샘플 API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.get("/api/items")
async def list_items():
    """상품 목록"""
    await asyncio.sleep(0.02)
    return [
        {"id": 1, "name": "노트북", "price": 1500000},
        {"id": 2, "name": "키보드", "price": 150000},
    ]


@app.get("/api/slow")
async def slow_endpoint():
    """느린 엔드포인트 (로깅 테스트)"""
    await asyncio.sleep(1.5)
    return {"message": "느린 응답 완료"}


@app.get("/api/error")
async def error_endpoint():
    """에러 엔드포인트 (로깅 테스트)"""
    raise HTTPException(500, "의도적 서버 에러")


@app.get("/api/long-task")
async def long_task():
    """
    긴 작업 (Graceful Shutdown 테스트).
    5초 동안 실행됩니다.
    """
    logger.info("long_task_started", estimated_seconds=5)

    for i in range(5):
        await asyncio.sleep(1)
        logger.debug("long_task_progress", progress=f"{(i+1)*20}%")

    logger.info("long_task_completed")
    return {"message": "긴 작업 완료", "duration_seconds": 5}


@app.post("/admin/shutdown")
async def manual_shutdown():
    """
    수동 Graceful Shutdown 트리거.
    테스트 목적으로 SIGTERM 없이 종료 프로세스를 시작합니다.
    """
    if shutdown_manager.is_shutting_down:
        return JSONResponse(
            status_code=409,
            content={"detail": "이미 종료 중입니다"},
        )

    logger.info("manual_shutdown_triggered")
    shutdown_manager.is_shutting_down = True
    shutdown_manager.is_ready = False

    return {
        "message": "Graceful Shutdown 시작됨",
        "active_requests": shutdown_manager.active_requests,
        "grace_period_seconds": shutdown_manager.grace_period,
    }


@app.get("/")
async def root():
    return {
        "title": "챕터 10 모범 답안",
        "endpoints": {
            "헬스 체크": "/health/ready",
            "상품 목록": "/api/items",
            "느린 응답 (로깅 테스트)": "/api/slow",
            "에러 (로깅 테스트)": "/api/error",
            "긴 작업 (Shutdown 테스트)": "/api/long-task",
            "수동 종료": "POST /admin/shutdown",
        },
        "logging": "모든 요청이 JSON 형식으로 로깅됩니다",
        "graceful_shutdown": "SIGTERM 또는 POST /admin/shutdown으로 안전 종료",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 참고: Dockerfile (문제 1 답안)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOCKERFILE_CONTENT = """
# === 멀티 스테이지 Dockerfile ===

# 스테이지 1: 빌더
FROM python:3.12-slim AS builder

WORKDIR /build

# 의존성 먼저 복사 (레이어 캐싱)
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# 스테이지 2: 런타임
FROM python:3.12-slim

# 비root 사용자 생성
RUN adduser --disabled-password --no-create-home appuser

# 작업 디렉토리
WORKDIR /app

# 의존성 복사
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages/

# 앱 코드 복사
COPY ./app /app

# 비root 사용자로 전환
USER appuser

# 포트 노출
EXPOSE 8000

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')" || exit 1

# 실행
CMD ["python", "-m", "gunicorn", "main:app", \\
     "-w", "4", \\
     "-k", "uvicorn.workers.UvicornWorker", \\
     "--bind", "0.0.0.0:8000", \\
     "--graceful-timeout", "30", \\
     "--timeout", "120"]
"""

DOCKER_COMPOSE_CONTENT = """
# === docker-compose.yml ===
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENVIRONMENT=production
      - APP_DEBUG=false
      - APP_DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/appdb
      - APP_REDIS_URL=redis://redis:6379/0
      - APP_SECRET_KEY=${SECRET_KEY:-change-me}
      - APP_LOG_FORMAT=json
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
"""

DOCKERIGNORE_CONTENT = """
# === .dockerignore ===
__pycache__
*.pyc
*.pyo
.git
.gitignore
.env
.env.*
*.md
.vscode
.idea
venv
.venv
*.sqlite
*.db
tests
.pytest_cache
.mypy_cache
.coverage
htmlcov
"""
