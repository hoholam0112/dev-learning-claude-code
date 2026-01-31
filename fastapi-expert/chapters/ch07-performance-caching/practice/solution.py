# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn orjson
"""
챕터 07 연습문제 모범 답안.

문제 1: 캐시 무효화 전략 (TTL + 이벤트 기반 + 태그)
문제 2: API 응답 시간 프로파일링과 최적화
문제 3: 대용량 CSV 스트리밍 다운로드
"""
import asyncio
import csv
import io
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Optional

import orjson
from fastapi import FastAPI, Query, Request
from fastapi.responses import ORJSONResponse, StreamingResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 1: 캐시 무효화 전략 (TTL + 이벤트 기반 + 태그)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class CacheEntry:
    """캐시 항목: 값, 만료 시간, 태그 정보를 포함"""

    __slots__ = ("value", "expire_at", "tags")

    def __init__(self, value: Any, ttl: int, tags: set[str]):
        self.value = value
        self.expire_at = time.monotonic() + ttl if ttl > 0 else 0
        self.tags = tags

    @property
    def is_expired(self) -> bool:
        return self.expire_at > 0 and time.monotonic() > self.expire_at


class CacheManager:
    """
    태그 기반 캐시 무효화를 지원하는 캐시 매니저.

    특징:
    - TTL 기반 자동 만료
    - 태그 기반 일괄 무효화
    - 히트/미스/무효화 통계
    """

    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._store: dict[str, CacheEntry] = {}
        self._tag_to_keys: dict[str, set[str]] = defaultdict(set)

        # 통계
        self._hits = 0
        self._misses = 0
        self._invalidations = 0
        self._hit_times: deque[float] = deque(maxlen=1000)
        self._miss_times: deque[float] = deque(maxlen=1000)

    async def get(self, key: str) -> Optional[Any]:
        """캐시 조회 (TTL 만료 검사 포함)"""
        start = time.perf_counter()
        entry = self._store.get(key)

        if entry is None or entry.is_expired:
            if entry and entry.is_expired:
                await self._remove_entry(key)
            self._misses += 1
            elapsed = (time.perf_counter() - start) * 1000
            self._miss_times.append(elapsed)
            return None

        self._hits += 1
        elapsed = (time.perf_counter() - start) * 1000
        self._hit_times.append(elapsed)
        return entry.value

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None, tags: Optional[list[str]] = None
    ) -> None:
        """캐시 저장 (TTL + 태그 지원)"""
        tag_set = set(tags) if tags else set()
        entry = CacheEntry(value, ttl or self.default_ttl, tag_set)
        self._store[key] = entry

        # 태그 매핑 등록
        for tag in tag_set:
            self._tag_to_keys[tag].add(key)

    async def tag(self, key: str, *tags: str) -> None:
        """기존 키에 태그 추가"""
        entry = self._store.get(key)
        if entry:
            for t in tags:
                entry.tags.add(t)
                self._tag_to_keys[t].add(key)

    async def invalidate(self, key: str) -> None:
        """단일 키 무효화"""
        await self._remove_entry(key)
        self._invalidations += 1

    async def invalidate_by_tag(self, tag: str) -> int:
        """태그 기반 일괄 무효화. 삭제된 키 수를 반환합니다."""
        keys = self._tag_to_keys.pop(tag, set()).copy()
        count = 0
        for key in keys:
            if key in self._store:
                await self._remove_entry(key)
                count += 1
        self._invalidations += count
        return count

    async def _remove_entry(self, key: str) -> None:
        """캐시 항목 제거 (태그 매핑 정리 포함)"""
        entry = self._store.pop(key, None)
        if entry:
            for tag in entry.tags:
                self._tag_to_keys.get(tag, set()).discard(key)

    def get_stats(self) -> dict:
        """캐시 성능 통계"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        avg_hit_time = sum(self._hit_times) / len(self._hit_times) if self._hit_times else 0
        avg_miss_time = sum(self._miss_times) / len(self._miss_times) if self._miss_times else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": round(hit_rate, 2),
            "invalidations": self._invalidations,
            "cached_keys": len(self._store),
            "avg_hit_time_ms": round(avg_hit_time, 4),
            "avg_miss_time_ms": round(avg_miss_time, 4),
        }


# 캐시 이벤트 시스템
class CacheEventSystem:
    """
    데이터 변경 이벤트에 따라 캐시를 자동 무효화하는 시스템.
    리소스 타입별로 무효화 규칙을 등록합니다.
    """

    def __init__(self, cache: CacheManager):
        self.cache = cache

    async def on_create(self, resource_type: str) -> None:
        """생성 이벤트 -> 목록 캐시 무효화"""
        count = await self.cache.invalidate_by_tag(f"{resource_type}:list")
        logger.info(f"[캐시 이벤트] {resource_type} 생성 -> {count}개 목록 캐시 무효화")

    async def on_update(self, resource_type: str, resource_id: int) -> None:
        """수정 이벤트 -> 단건 + 목록 캐시 무효화"""
        await self.cache.invalidate(f"{resource_type}:{resource_id}")
        count = await self.cache.invalidate_by_tag(f"{resource_type}:list")
        logger.info(
            f"[캐시 이벤트] {resource_type}:{resource_id} 수정 -> "
            f"단건 + {count}개 목록 캐시 무효화"
        )

    async def on_delete(self, resource_type: str, resource_id: int) -> None:
        """삭제 이벤트 -> 단건 + 목록 캐시 무효화"""
        await self.cache.invalidate(f"{resource_type}:{resource_id}")
        count = await self.cache.invalidate_by_tag(f"{resource_type}:list")
        logger.info(
            f"[캐시 이벤트] {resource_type}:{resource_id} 삭제 -> "
            f"단건 + {count}개 목록 캐시 무효화"
        )


cache_manager = CacheManager(default_ttl=60)
cache_events = CacheEventSystem(cache_manager)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 2: API 응답 시간 프로파일링
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class EndpointStats:
    """엔드포인트별 성능 통계를 누적하는 클래스"""

    def __init__(self, maxlen: int = 1000):
        self.times: deque[float] = deque(maxlen=maxlen)
        self.count: int = 0

    def record(self, time_ms: float) -> None:
        self.times.append(time_ms)
        self.count += 1

    def get_stats(self) -> dict:
        if not self.times:
            return {}

        sorted_times = sorted(self.times)
        n = len(sorted_times)

        return {
            "count": self.count,
            "avg_ms": round(sum(sorted_times) / n, 2),
            "min_ms": round(sorted_times[0], 2),
            "max_ms": round(sorted_times[-1], 2),
            "p50_ms": round(sorted_times[int(n * 0.50)], 2),
            "p95_ms": round(sorted_times[int(n * 0.95)], 2),
            "p99_ms": round(sorted_times[min(int(n * 0.99), n - 1)], 2),
        }


class ProfilingMiddleware(BaseHTTPMiddleware):
    """
    API 응답 시간 프로파일링 미들웨어.
    모든 요청의 응답 시간을 엔드포인트별로 기록하고,
    느린 요청을 감지하여 경고 로그를 남깁니다.
    """

    SLOW_THRESHOLD_MS = 200  # 느린 요청 임계값

    def __init__(self, app):
        super().__init__(app)
        self.endpoint_stats: dict[str, EndpointStats] = defaultdict(EndpointStats)
        self.start_time = time.time()
        self.total_requests = 0

    async def dispatch(self, request: Request, call_next):
        endpoint_key = f"{request.method} {request.url.path}"

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # 통계 기록
        self.endpoint_stats[endpoint_key].record(elapsed_ms)
        self.total_requests += 1

        # 느린 요청 감지
        if elapsed_ms > self.SLOW_THRESHOLD_MS:
            logger.warning(
                f"[느린 요청] {endpoint_key}: {elapsed_ms:.1f}ms "
                f"(임계값: {self.SLOW_THRESHOLD_MS}ms)"
            )

        # 응답 헤더에 처리 시간 추가
        response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"

        return response

    def get_metrics(self) -> dict:
        """전체 성능 통계 반환"""
        endpoints = {}
        for key, stats in self.endpoint_stats.items():
            endpoint_data = stats.get_stats()
            if endpoint_data:
                endpoints[key] = endpoint_data

        # 가장 느린 Top 5
        top_5 = sorted(
            [
                {"endpoint": k, "avg_ms": v.get("avg_ms", 0)}
                for k, v in endpoints.items()
            ],
            key=lambda x: x["avg_ms"],
            reverse=True,
        )[:5]

        # RPS 계산
        elapsed = time.time() - self.start_time
        rps = self.total_requests / elapsed if elapsed > 0 else 0

        return {
            "endpoints": endpoints,
            "top_5_slowest": top_5,
            "total_requests": self.total_requests,
            "rps": round(rps, 2),
            "uptime_seconds": round(elapsed, 1),
        }


# 미들웨어 인스턴스 (메트릭 접근을 위해 참조 보관)
profiling_middleware = ProfilingMiddleware


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 3: 대용량 CSV 스트리밍 다운로드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class StreamingCSVExporter:
    """
    대용량 데이터를 CSV로 스트리밍 내보내기하는 클래스.

    특징:
    - 배치 단위 DB 조회로 메모리 절약
    - UTF-8 BOM 포함 (Excel 호환)
    - 진행 상태 로깅 (10% 단위)
    - CSV/TSV/사용자 정의 구분자 지원
    """

    def __init__(
        self,
        total_count: int,
        batch_size: int = 1000,
        delimiter: str = ",",
    ):
        self.total_count = total_count
        self.batch_size = batch_size
        self.delimiter = delimiter
        self._last_logged_percent = 0

    def _log_progress(self, current: int) -> None:
        """10% 단위로 진행 상태 로깅"""
        if self.total_count == 0:
            return
        percent = int(current / self.total_count * 100)
        if percent >= self._last_logged_percent + 10:
            self._last_logged_percent = percent - (percent % 10)
            logger.info(
                f"진행: {self._last_logged_percent}% "
                f"({current:,}/{self.total_count:,})"
            )

    async def export(
        self,
        headers: list[str],
        data_fetcher: Callable[[int, int], Any],
    ) -> AsyncGenerator[str, None]:
        """
        CSV 스트리밍 제너레이터.

        Args:
            headers: CSV 헤더 목록
            data_fetcher: 배치 데이터 조회 함수 (offset, limit) -> list[dict]
        """
        start_time = time.perf_counter()
        logger.info(f"CSV 내보내기 시작: 총 {self.total_count:,}건")

        # UTF-8 BOM + 헤더 행
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=self.delimiter)
        bom = "\ufeff"  # UTF-8 BOM
        writer.writerow(headers)
        yield bom + buffer.getvalue()

        # 데이터 행 (배치 단위)
        processed = 0
        offset = 0

        while offset < self.total_count:
            # 배치 데이터 조회
            batch = await data_fetcher(offset, self.batch_size)
            if not batch:
                break

            buffer = io.StringIO()
            writer = csv.writer(buffer, delimiter=self.delimiter)

            for row in batch:
                if isinstance(row, dict):
                    writer.writerow(row.values())
                else:
                    writer.writerow(row)
                processed += 1

            yield buffer.getvalue()

            # 진행 로깅
            self._log_progress(processed)

            offset += self.batch_size

            # 이벤트 루프 양보 (차단 방지)
            await asyncio.sleep(0)

        elapsed = time.perf_counter() - start_time
        logger.info(
            f"CSV 내보내기 완료: {processed:,}건, "
            f"소요 시간 {elapsed:.1f}초"
        )


# 주문 데이터 시뮬레이션
async def fetch_orders(offset: int, limit: int) -> list[dict]:
    """주문 데이터를 배치로 조회 (DB 시뮬레이션)"""
    import random

    result = []
    for i in range(offset, min(offset + limit, 100000)):
        result.append({
            "order_id": i + 1,
            "customer": f"고객_{(i % 500) + 1:04d}",
            "product": f"상품_{(i % 200) + 1:03d}",
            "quantity": random.randint(1, 10),
            "price": round(random.uniform(1000, 500000), 0),
            "order_date": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
            "status": ["주문완료", "배송중", "배송완료", "취소"][i % 4],
        })

    # DB 조회 지연 시뮬레이션
    await asyncio.sleep(0.01)
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic 스키마
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ItemCreate(BaseModel):
    name: str
    price: float
    category: str = "기타"


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str


# 시뮬레이션 데이터
items_db: dict[int, dict] = {
    i: {
        "id": i,
        "name": f"상품_{i}",
        "price": i * 1000.0,
        "category": ["전자기기", "도서", "의류"][i % 3],
    }
    for i in range(1, 21)
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI 앱
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app = FastAPI(
    title="챕터 07 모범 답안",
    default_response_class=ORJSONResponse,
)

# 프로파일링 미들웨어 등록 (인스턴스 참조 보관)
_profiling_instance = None


@app.middleware("http")
async def profiling(request: Request, call_next):
    global _profiling_instance
    if _profiling_instance is None:
        _profiling_instance = ProfilingMiddleware(None)
        _profiling_instance.start_time = time.time()
        _profiling_instance.total_requests = 0
        _profiling_instance.endpoint_stats = defaultdict(EndpointStats)

    endpoint_key = f"{request.method} {request.url.path}"
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    _profiling_instance.endpoint_stats[endpoint_key].record(elapsed_ms)
    _profiling_instance.total_requests += 1

    if elapsed_ms > 200:
        logger.warning(f"[느린 요청] {endpoint_key}: {elapsed_ms:.1f}ms")

    response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"
    return response


# ── 캐시가 적용된 아이템 API ──
@app.get("/items", response_model=list[ItemResponse])
async def list_items(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
):
    """상품 목록 (캐시 적용)"""
    cache_key = f"items:list:{category or 'all'}:page={page}"

    cached = await cache_manager.get(cache_key)
    if cached:
        return cached

    # DB 조회 시뮬레이션
    await asyncio.sleep(0.05)
    items = list(items_db.values())
    if category:
        items = [i for i in items if i["category"] == category]

    # 캐시 저장 (태그 포함)
    await cache_manager.set(
        cache_key, items, ttl=60, tags=["items", "items:list"]
    )
    return items


@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(data: ItemCreate):
    """상품 생성 (캐시 이벤트 무효화)"""
    new_id = max(items_db.keys()) + 1
    item = {"id": new_id, **data.model_dump()}
    items_db[new_id] = item

    # 이벤트 기반 캐시 무효화
    await cache_events.on_create("items")
    return item


@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, data: ItemCreate):
    """상품 수정 (캐시 이벤트 무효화)"""
    if item_id not in items_db:
        from fastapi import HTTPException
        raise HTTPException(404, "상품을 찾을 수 없습니다")

    items_db[item_id].update(data.model_dump())
    await cache_events.on_update("items", item_id)
    return items_db[item_id]


# ── 느린 엔드포인트 (프로파일링 테스트) ──
@app.get("/slow/db-query")
async def slow_db_query():
    """느린 DB 쿼리 시뮬레이션 (200ms)"""
    await asyncio.sleep(0.2)
    return {"message": "느린 DB 쿼리 완료", "delay_ms": 200}


@app.get("/slow/serialization")
async def slow_serialization():
    """대용량 직렬화 시뮬레이션 (100ms)"""
    import json
    data = [{"id": i, "value": f"data_{i}" * 100} for i in range(5000)]
    json.dumps(data)  # 느린 직렬화
    return {"message": "대용량 직렬화 완료", "delay_ms": "~100"}


@app.get("/slow/external-api")
async def slow_external_api():
    """외부 API 호출 시뮬레이션 (500ms)"""
    await asyncio.sleep(0.5)
    return {"message": "외부 API 호출 완료", "delay_ms": 500}


# ── 메트릭 ──
@app.get("/metrics")
async def get_metrics():
    """API 성능 메트릭"""
    if _profiling_instance:
        return _profiling_instance.get_metrics()
    return {"message": "아직 요청이 없습니다"}


@app.get("/cache/stats")
async def get_cache_stats():
    """캐시 성능 통계"""
    return cache_manager.get_stats()


# ── CSV 스트리밍 내보내기 ──
@app.get("/export/orders/count")
async def get_order_count(year: int = Query(2024)):
    """내보내기 전 총 건수 확인"""
    total = 100000  # 시뮬레이션: 10만 건
    estimated_size_mb = total * 150 / 1024 / 1024  # 행당 약 150바이트
    return {
        "count": total,
        "estimated_size_mb": round(estimated_size_mb, 1),
        "year": year,
    }


@app.get("/export/orders")
async def export_orders(
    year: int = Query(2024),
    format: str = Query("csv", regex="^(csv|tsv)$"),
):
    """
    주문 데이터 CSV/TSV 스트리밍 다운로드.
    배치 단위로 조회하여 메모리 사용량을 일정하게 유지합니다.
    """
    total_count = 100000  # 시뮬레이션
    delimiter = "\t" if format == "tsv" else ","
    extension = format

    exporter = StreamingCSVExporter(
        total_count=total_count,
        batch_size=1000,
        delimiter=delimiter,
    )

    headers = ["주문번호", "고객명", "상품명", "수량", "금액", "주문일", "상태"]

    return StreamingResponse(
        exporter.export(headers, fetch_orders),
        media_type=f"text/{extension}; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=orders_{year}.{extension}",
        },
    )
