# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn
"""
챕터 09 연습문제 모범 답안.

문제 1: API v1/v2 라우터 분리와 하위 호환성
문제 2: 서킷 브레이커 패턴 (데코레이터 포함)
문제 3: 분산 트레이싱 헤더 전파
"""
import asyncio
import enum
import logging
import random
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Any, Callable, Optional

from fastapi import FastAPI, APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 공유 데이터 및 서비스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
posts_db: dict[int, dict] = {
    1: {
        "id": 1, "title": "FastAPI 입문", "content": "FastAPI는 Python 웹 프레임워크입니다.",
        "author": "홍길동", "tags": ["python", "fastapi"], "like_count": 42,
        "comment_count": 5, "created_at": "2024-01-15T10:00:00Z",
    },
    2: {
        "id": 2, "title": "비동기 프로그래밍", "content": "asyncio와 await를 이해합시다.",
        "author": "김철수", "tags": ["python", "async"], "like_count": 28,
        "comment_count": 3, "created_at": "2024-02-20T14:00:00Z",
    },
    3: {
        "id": 3, "title": "마이크로서비스 설계", "content": "서비스 분리와 통신 패턴을 다룹니다.",
        "author": "이영희", "tags": ["architecture", "microservices"], "like_count": 55,
        "comment_count": 8, "created_at": "2024-03-10T09:00:00Z",
    },
}

comments_db: dict[int, list[dict]] = {
    1: [
        {"id": 1, "post_id": 1, "author": "김철수", "content": "좋은 글이네요!"},
        {"id": 2, "post_id": 1, "author": "이영희", "content": "감사합니다."},
    ],
    2: [{"id": 3, "post_id": 2, "author": "홍길동", "content": "async 최고!"}],
}
post_counter = 3


class PostService:
    """게시글 서비스 (v1/v2 공유)"""

    @staticmethod
    async def get_all(
        tags: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[dict], int]:
        items = list(posts_db.values())
        if tags:
            items = [
                p for p in items
                if any(t in p.get("tags", []) for t in tags)
            ]
        total = len(items)
        return items[skip:skip + limit], total

    @staticmethod
    async def get_by_id(post_id: int) -> Optional[dict]:
        return posts_db.get(post_id)

    @staticmethod
    async def create(data: dict) -> dict:
        global post_counter
        post_counter += 1
        post = {
            "id": post_counter,
            "title": data["title"],
            "content": data["content"],
            "author": data["author"],
            "tags": data.get("tags", []),
            "like_count": 0,
            "comment_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        posts_db[post_counter] = post
        return post

    @staticmethod
    async def get_comments(post_id: int) -> list[dict]:
        return comments_db.get(post_id, [])


post_service = PostService()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 1: API v1/v2 라우터 분리
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# --- v1 스키마 ---
class PostResponseV1(BaseModel):
    id: int
    title: str
    content: str
    author: str


class PostCreateV1(BaseModel):
    title: str
    content: str
    author: str


# --- v2 스키마 ---
class PostResponseV2(BaseModel):
    id: int
    title: str
    content: str
    author: str
    tags: list[str] = []
    like_count: int = 0
    comment_count: int = 0
    created_at: str


class PostCreateV2(BaseModel):
    title: str
    content: str
    author: str
    tags: list[str] = []


class PaginatedPosts(BaseModel):
    items: list[PostResponseV2]
    total: int
    page: int
    size: int
    has_next: bool


class CommentResponse(BaseModel):
    id: int
    post_id: int
    author: str
    content: str


# --- v1 라우터 ---
v1_router = APIRouter(prefix="/api/v1", tags=["v1 (Deprecated)"])


@v1_router.get("/posts", response_model=list[PostResponseV1])
async def list_posts_v1():
    """[v1] 게시글 목록"""
    items, _ = await post_service.get_all()
    return [PostResponseV1(**{k: v for k, v in p.items() if k in PostResponseV1.model_fields}) for p in items]


@v1_router.get("/posts/{post_id}", response_model=PostResponseV1)
async def get_post_v1(post_id: int):
    """[v1] 게시글 상세"""
    post = await post_service.get_by_id(post_id)
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다")
    return PostResponseV1(**{k: v for k, v in post.items() if k in PostResponseV1.model_fields})


@v1_router.post("/posts", response_model=PostResponseV1, status_code=201)
async def create_post_v1(data: PostCreateV1):
    """[v1] 게시글 작성"""
    post = await post_service.create(data.model_dump())
    return PostResponseV1(**{k: v for k, v in post.items() if k in PostResponseV1.model_fields})


# --- v2 라우터 ---
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])


@v2_router.get("/posts", response_model=PaginatedPosts)
async def list_posts_v2(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    tags: Optional[str] = Query(None, description="쉼표 구분 태그 필터"),
):
    """[v2] 게시글 목록 (페이징 + 태그 필터)"""
    tag_list = tags.split(",") if tags else None
    skip = (page - 1) * size
    items, total = await post_service.get_all(tags=tag_list, skip=skip, limit=size)

    return PaginatedPosts(
        items=[PostResponseV2(**p) for p in items],
        total=total,
        page=page,
        size=size,
        has_next=(skip + size) < total,
    )


@v2_router.get("/posts/{post_id}", response_model=PostResponseV2)
async def get_post_v2(post_id: int):
    """[v2] 게시글 상세"""
    post = await post_service.get_by_id(post_id)
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다")
    return PostResponseV2(**post)


@v2_router.post("/posts", response_model=PostResponseV2, status_code=201)
async def create_post_v2(data: PostCreateV2):
    """[v2] 게시글 작성 (태그 포함)"""
    post = await post_service.create(data.model_dump())
    return PostResponseV2(**post)


@v2_router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments_v2(post_id: int):
    """[v2] 게시글 댓글 목록"""
    post = await post_service.get_by_id(post_id)
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다")
    comments = await post_service.get_comments(post_id)
    return comments


# --- Deprecation 미들웨어 ---
class DeprecationMiddleware(BaseHTTPMiddleware):
    """v1 API 호출 시 Deprecation 헤더를 자동 추가하는 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("/api/v1"):
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = "2025-06-01"
            response.headers["Link"] = '</api/v2>; rel="successor-version"'
            logger.warning(f"[Deprecated] v1 API 호출: {request.method} {request.url.path}")

        return response


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 2: 서킷 브레이커 패턴 (데코레이터 포함)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    pass


class CircuitBreaker:
    """서킷 브레이커 구현 (스레드 안전)"""

    # 전역 레지스트리
    _registry: dict[str, "CircuitBreaker"] = {}

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 3,
        fallback: Optional[Callable] = None,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.fallback = fallback

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._total_calls = 0
        self._total_failures = 0
        self._lock = asyncio.Lock()

        CircuitBreaker._registry[name] = self

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
        return self._state

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        async with self._lock:
            current_state = self.state
            self._total_calls += 1

        if current_state == CircuitState.OPEN:
            if self.fallback:
                return await self.fallback() if asyncio.iscoroutinefunction(self.fallback) else self.fallback()
            raise CircuitBreakerOpenError(f"서킷 브레이커 '{self.name}' 열림")

        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self._on_success()
            return result
        except Exception as e:
            async with self._lock:
                self._on_failure()
            if self.fallback:
                return await self.fallback() if asyncio.iscoroutinefunction(self.fallback) else self.fallback()
            raise

    def _on_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info(f"[서킷 {self.name}] HALF_OPEN -> CLOSED")
        else:
            self._failure_count = 0

    def _on_failure(self) -> None:
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(f"[서킷 {self.name}] -> OPEN ({self._failure_count} 실패)")

    def reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0

    def get_stats(self) -> dict:
        state = self.state
        result = {
            "name": self.name,
            "state": state.value,
            "failure_count": self._failure_count,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "failure_rate": (
                round(self._total_failures / self._total_calls * 100, 1)
                if self._total_calls > 0 else 0
            ),
        }
        if state == CircuitState.OPEN:
            remaining = self.recovery_timeout - (time.time() - self._last_failure_time)
            result["opens_in"] = f"{max(0, remaining):.0f}초 후 HALF_OPEN 전환"
        return result


def circuit_breaker(
    name: Optional[str] = None,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    fallback: Optional[Callable] = None,
):
    """서킷 브레이커 데코레이터"""
    def decorator(func: Callable):
        cb_name = name or func.__name__
        cb = CircuitBreaker(
            name=cb_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            fallback=fallback,
        )

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)

        wrapper._circuit_breaker = cb  # type: ignore
        return wrapper
    return decorator


# 서킷 브레이커 적용 예시
async def unreliable_fallback():
    return {"status": "fallback", "message": "서비스 불안정, 캐시된 데이터 반환"}


@circuit_breaker(name="unreliable_service", failure_threshold=3, recovery_timeout=10)
async def call_unreliable_service():
    """50% 확률로 실패하는 서비스"""
    if random.random() < 0.5:
        raise ConnectionError("서비스 연결 실패")
    await asyncio.sleep(0.05)
    return {"status": "success", "data": "결과 데이터"}


@circuit_breaker(
    name="always_fail_service",
    failure_threshold=3,
    recovery_timeout=15,
    fallback=unreliable_fallback,
)
async def call_always_fail_service():
    """항상 실패하는 서비스 (폴백 테스트)"""
    raise ConnectionError("서비스 다운")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 3: 분산 트레이싱
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class SpanRecord:
    """스팬 기록"""

    def __init__(
        self,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str],
        service: str,
        operation: str,
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.service = service
        self.operation = operation
        self.start_time = time.perf_counter()
        self.end_time: Optional[float] = None
        self.status_code: Optional[int] = None
        self.attributes: dict = {}

    def finish(self, status_code: int = 200) -> None:
        self.end_time = time.perf_counter()
        self.status_code = status_code

    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return round((self.end_time - self.start_time) * 1000, 2)
        return 0

    def to_dict(self) -> dict:
        return {
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "service": self.service,
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "status_code": self.status_code,
        }


class SpanCollector:
    """스팬 수집기: 메모리에 스팬을 저장하고 트리 구조로 반환"""

    def __init__(self, max_traces: int = 100):
        self.traces: dict[str, list[SpanRecord]] = defaultdict(list)
        self.max_traces = max_traces

    def record(self, span: SpanRecord) -> None:
        self.traces[span.trace_id].append(span)
        # 오래된 트레이스 정리
        if len(self.traces) > self.max_traces:
            oldest = next(iter(self.traces))
            del self.traces[oldest]

    def get_trace(self, trace_id: str) -> Optional[dict]:
        spans = self.traces.get(trace_id)
        if not spans:
            return None

        # 전체 소요 시간 계산
        all_durations = [s.duration_ms for s in spans if s.duration_ms > 0]
        total_duration = max(all_durations) if all_durations else 0

        # 트리 구조 변환
        span_dicts = [s.to_dict() for s in spans]
        tree = self._build_tree(span_dicts)

        return {
            "trace_id": trace_id,
            "duration_ms": total_duration,
            "span_count": len(spans),
            "spans": tree,
        }

    def _build_tree(self, spans: list[dict], parent_id: Optional[str] = None) -> list[dict]:
        """스팬 리스트를 트리 구조로 변환"""
        result = []
        for span in spans:
            if span["parent_span_id"] == parent_id:
                children = self._build_tree(spans, span["span_id"])
                if children:
                    span["children"] = children
                result.append(span)
        return result

    def list_traces(self) -> list[dict]:
        """전체 트레이스 목록"""
        result = []
        for trace_id, spans in self.traces.items():
            all_durations = [s.duration_ms for s in spans if s.duration_ms > 0]
            result.append({
                "trace_id": trace_id,
                "span_count": len(spans),
                "duration_ms": max(all_durations) if all_durations else 0,
                "services": list(set(s.service for s in spans)),
            })
        return result


class TraceContext:
    """분산 트레이싱 컨텍스트"""

    def __init__(
        self,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ):
        self.trace_id = trace_id or uuid.uuid4().hex[:32]
        self.span_id = span_id or uuid.uuid4().hex[:16]
        self.parent_span_id = parent_span_id

    def create_child(self) -> "TraceContext":
        return TraceContext(
            trace_id=self.trace_id,
            parent_span_id=self.span_id,
        )

    def to_headers(self) -> dict[str, str]:
        return {"traceparent": f"00-{self.trace_id}-{self.span_id}-01"}

    @classmethod
    def from_headers(cls, headers: dict) -> "TraceContext":
        traceparent = headers.get("traceparent", "")
        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 3:
                return cls(trace_id=parts[1], parent_span_id=parts[2])
        return cls()


span_collector = SpanCollector()


class TracingMiddleware(BaseHTTPMiddleware):
    """분산 트레이싱 미들웨어"""

    def __init__(self, app, service_name: str = "api-gateway"):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        trace = TraceContext.from_headers(dict(request.headers))
        request.state.trace = trace

        span = SpanRecord(
            trace_id=trace.trace_id,
            span_id=trace.span_id,
            parent_span_id=trace.parent_span_id,
            service=self.service_name,
            operation=f"{request.method} {request.url.path}",
        )

        response = await call_next(request)

        span.finish(status_code=response.status_code)
        span_collector.record(span)

        response.headers["X-Trace-Id"] = trace.trace_id
        response.headers["X-Span-Id"] = trace.span_id

        return response


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI 앱 조립
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[시작] 챕터 09 모범 답안 앱 준비 완료")
    yield


app = FastAPI(
    title="챕터 09 모범 답안",
    description="API 버전 관리, 서킷 브레이커, 분산 트레이싱",
    lifespan=lifespan,
)

# 미들웨어 등록 (순서 중요: 마지막에 추가한 것이 먼저 실행)
app.add_middleware(DeprecationMiddleware)
app.add_middleware(TracingMiddleware, service_name="api-gateway")

# v1/v2 라우터 등록
app.include_router(v1_router)
app.include_router(v2_router)


# --- 서킷 브레이커 엔드포인트 ---
@app.get("/circuit-breakers")
async def get_all_circuit_breakers():
    """전체 서킷 브레이커 상태"""
    return {
        name: cb.get_stats()
        for name, cb in CircuitBreaker._registry.items()
    }


@app.post("/circuit-breakers/{name}/reset")
async def reset_cb(name: str):
    """서킷 브레이커 수동 리셋"""
    cb = CircuitBreaker._registry.get(name)
    if not cb:
        raise HTTPException(404, f"서킷 브레이커 '{name}' 없음")
    cb.reset()
    return {"message": f"리셋 완료", "stats": cb.get_stats()}


@app.post("/test/unreliable")
async def test_unreliable():
    """불안정한 서비스 테스트 (서킷 브레이커 적용)"""
    try:
        result = await call_unreliable_service()
        return result
    except CircuitBreakerOpenError as e:
        raise HTTPException(503, str(e))
    except ConnectionError as e:
        raise HTTPException(502, str(e))


@app.post("/test/always-fail")
async def test_always_fail():
    """항상 실패하는 서비스 테스트 (폴백 적용)"""
    result = await call_always_fail_service()
    return result


# --- 트레이싱 엔드포인트 ---
@app.get("/traces")
async def list_traces():
    """전체 트레이스 목록"""
    return span_collector.list_traces()


@app.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """특정 트레이스의 스팬 트리"""
    trace = span_collector.get_trace(trace_id)
    if not trace:
        raise HTTPException(404, "트레이스를 찾을 수 없습니다")
    return trace


# --- 버전 정보 ---
@app.get("/api/versions")
async def api_versions():
    return {
        "current": "v2",
        "supported": ["v1", "v2"],
        "deprecated": ["v1"],
        "sunset": {"v1": "2025-06-01"},
        "migration_guide": {
            "v1_to_v2": [
                "목록 응답에 페이징 래퍼 추가",
                "게시글에 tags, like_count, comment_count, created_at 추가",
                "댓글 조회 엔드포인트 추가 (GET /api/v2/posts/{id}/comments)",
            ],
        },
    }


@app.get("/")
async def root():
    return {
        "title": "챕터 09 모범 답안",
        "endpoints": {
            "v1 API (Deprecated)": "/api/v1/posts",
            "v2 API": "/api/v2/posts",
            "서킷 브레이커": "/circuit-breakers",
            "트레이싱": "/traces",
            "버전 정보": "/api/versions",
        },
    }
