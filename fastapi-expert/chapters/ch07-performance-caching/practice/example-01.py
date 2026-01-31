# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn fakeredis orjson
"""
Redis 기반 캐싱 레이어 구현 예제.
fakeredis를 사용하여 실제 Redis 없이 테스트 가능합니다.

주요 학습 포인트:
- Cache-Aside 패턴 구현
- 캐시 데코레이터 설계
- TTL 기반 + 이벤트 기반 캐시 무효화
- 캐시 히트/미스 통계
- ETag 기반 조건부 응답
"""
import hashlib
import time
from typing import Optional, Callable, Any
from functools import wraps

import orjson
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

# fakeredis: 실제 Redis 없이 테스트 가능한 인메모리 구현
try:
    import fakeredis.aioredis as aioredis

    redis_client = aioredis.FakeRedis(decode_responses=False)
except ImportError:
    # fakeredis가 없으면 간단한 딕셔너리 기반 캐시 사용
    redis_client = None


# ──────────────────────────────────────────────
# 1. 인메모리 캐시 (Redis 대체용)
# ──────────────────────────────────────────────
class InMemoryCache:
    """
    Redis를 사용할 수 없을 때의 폴백 캐시.
    TTL 지원, 프로덕션에서는 반드시 Redis를 사용하세요.
    """

    def __init__(self):
        self._store: dict[str, tuple[bytes, float]] = {}  # key -> (value, expire_at)
        self._stats = {"hits": 0, "misses": 0}

    async def get(self, key: str) -> Optional[bytes]:
        """캐시 조회"""
        if key in self._store:
            value, expire_at = self._store[key]
            if expire_at == 0 or time.time() < expire_at:
                self._stats["hits"] += 1
                return value
            else:
                # 만료된 항목 삭제
                del self._store[key]
        self._stats["misses"] += 1
        return None

    async def set(self, key: str, value: bytes, ex: int = 0) -> None:
        """캐시 저장 (ex: TTL 초)"""
        expire_at = time.time() + ex if ex > 0 else 0
        self._store[key] = (value, expire_at)

    async def delete(self, key: str) -> None:
        """캐시 삭제"""
        self._store.pop(key, None)

    async def flushall(self) -> None:
        """전체 캐시 초기화"""
        self._store.clear()

    async def keys(self, pattern: str = "*") -> list[str]:
        """키 목록 조회 (간단한 패턴 매칭)"""
        if pattern == "*":
            return list(self._store.keys())
        prefix = pattern.rstrip("*")
        return [k for k in self._store.keys() if k.startswith(prefix)]

    def get_stats(self) -> dict:
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
        return {
            **self._stats,
            "total": total,
            "hit_rate": round(hit_rate, 2),
        }


# 캐시 인스턴스 선택
cache = redis_client if redis_client else InMemoryCache()


# ──────────────────────────────────────────────
# 2. 캐싱 레이어 (Cache-Aside 패턴)
# ──────────────────────────────────────────────
class CacheLayer:
    """
    Cache-Aside 패턴을 구현하는 캐싱 레이어.
    Redis(또는 InMemoryCache)를 백엔드로 사용합니다.
    """

    def __init__(self, cache_backend, default_ttl: int = 300):
        self.cache = cache_backend
        self.default_ttl = default_ttl

    def _make_key(self, namespace: str, *args: Any) -> str:
        """캐시 키 생성: namespace:arg1:arg2:..."""
        parts = [namespace] + [str(a) for a in args]
        return ":".join(parts)

    async def get_or_set(
        self,
        key: str,
        fetch_func: Callable,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Cache-Aside 핵심 메서드.
        1. 캐시에서 조회
        2. 없으면 fetch_func 실행 후 캐시에 저장
        """
        # 캐시 조회
        cached = await self.cache.get(key)
        if cached is not None:
            return orjson.loads(cached)

        # 캐시 미스: 원본 데이터 조회
        data = await fetch_func()

        # 캐시에 저장
        serialized = orjson.dumps(data)
        await self.cache.set(key, serialized, ex=ttl or self.default_ttl)

        return data

    async def invalidate(self, key: str) -> None:
        """단일 키 무효화"""
        await self.cache.delete(key)

    async def invalidate_pattern(self, pattern: str) -> None:
        """패턴에 매칭되는 모든 키 무효화"""
        keys = await self.cache.keys(pattern)
        for key in keys:
            if isinstance(key, bytes):
                key = key.decode()
            await self.cache.delete(key)

    async def flush_all(self) -> None:
        """전체 캐시 초기화"""
        await self.cache.flushall()


cache_layer = CacheLayer(cache, default_ttl=60)


# ──────────────────────────────────────────────
# 3. 캐시 데코레이터
# ──────────────────────────────────────────────
def cached(namespace: str, ttl: int = 300):
    """
    캐시 데코레이터.
    함수의 인자를 기반으로 캐시 키를 자동 생성합니다.

    사용법:
        @cached("items", ttl=60)
        async def get_items(page: int, size: int):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성: namespace:arg1:arg2:kwarg1=val1
            key_parts = [namespace]
            key_parts.extend(str(a) for a in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            return await cache_layer.get_or_set(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl,
            )
        # 원본 함수 참조 보존 (캐시 무효화 시 필요)
        wrapper._cache_namespace = namespace  # type: ignore
        return wrapper
    return decorator


# ──────────────────────────────────────────────
# 4. 시뮬레이션용 데이터 저장소
# ──────────────────────────────────────────────
class DataStore:
    """데이터베이스를 시뮬레이션하는 인메모리 저장소"""

    def __init__(self):
        self.items: dict[int, dict] = {
            1: {"id": 1, "name": "노트북", "price": 1500000, "category": "전자기기"},
            2: {"id": 2, "name": "키보드", "price": 150000, "category": "전자기기"},
            3: {"id": 3, "name": "마우스", "price": 80000, "category": "전자기기"},
            4: {"id": 4, "name": "파이썬 교재", "price": 35000, "category": "도서"},
            5: {"id": 5, "name": "FastAPI 가이드", "price": 42000, "category": "도서"},
        }
        self._next_id = 6
        self.query_count = 0

    async def get_all(self, category: Optional[str] = None) -> list[dict]:
        """전체 목록 조회 (DB 쿼리 시뮬레이션)"""
        self.query_count += 1
        import asyncio
        await asyncio.sleep(0.05)  # DB 쿼리 지연 시뮬레이션 (50ms)

        items = list(self.items.values())
        if category:
            items = [i for i in items if i["category"] == category]
        return items

    async def get_by_id(self, item_id: int) -> Optional[dict]:
        """단건 조회"""
        self.query_count += 1
        import asyncio
        await asyncio.sleep(0.02)  # 20ms 지연
        return self.items.get(item_id)

    async def create(self, data: dict) -> dict:
        """새 항목 생성"""
        data["id"] = self._next_id
        self.items[self._next_id] = data
        self._next_id += 1
        return data

    async def update(self, item_id: int, data: dict) -> Optional[dict]:
        """항목 수정"""
        if item_id in self.items:
            self.items[item_id].update(data)
            return self.items[item_id]
        return None

    async def delete(self, item_id: int) -> bool:
        """항목 삭제"""
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False


store = DataStore()


# ──────────────────────────────────────────────
# 5. Pydantic 스키마
# ──────────────────────────────────────────────
class ItemCreate(BaseModel):
    name: str
    price: float
    category: str = "기타"


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str


# ──────────────────────────────────────────────
# 6. FastAPI 앱
# ──────────────────────────────────────────────
app = FastAPI(
    title="Redis 캐싱 레이어 예제",
    description="Cache-Aside 패턴, ETag, 캐시 무효화",
    default_response_class=ORJSONResponse,
)


@app.get("/items", response_model=list[ItemResponse])
async def list_items(category: Optional[str] = None):
    """
    상품 목록 조회 (캐시 적용).
    첫 요청은 DB에서 조회 (50ms), 이후 요청은 캐시에서 반환 (~0ms).
    """
    cache_key = f"items:list:{category or 'all'}"

    async def fetch():
        return await store.get_all(category)

    return await cache_layer.get_or_set(cache_key, fetch, ttl=60)


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, request: Request):
    """
    상품 상세 조회 (캐시 + ETag 적용).
    ETag가 일치하면 304 Not Modified를 반환합니다.
    """
    cache_key = f"items:{item_id}"

    async def fetch():
        item = await store.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")
        return item

    data = await cache_layer.get_or_set(cache_key, fetch, ttl=120)

    if data is None:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    # ETag 생성: 데이터 해시
    etag = hashlib.md5(orjson.dumps(data)).hexdigest()

    # 조건부 요청: If-None-Match 헤더 확인
    client_etag = request.headers.get("if-none-match")
    if client_etag and client_etag == etag:
        return Response(status_code=304)  # 변경 없음 -> 본문 없이 반환

    return ORJSONResponse(
        content=data,
        headers={
            "ETag": etag,
            "Cache-Control": "private, max-age=60",
        },
    )


@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(data: ItemCreate):
    """
    상품 생성 (캐시 무효화 포함).
    새 항목 생성 시 목록 캐시를 무효화합니다.
    """
    item = await store.create(data.model_dump())

    # 관련 캐시 무효화 (이벤트 기반)
    await cache_layer.invalidate_pattern("items:list:*")

    return item


@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, data: ItemCreate):
    """
    상품 수정 (캐시 무효화 포함).
    수정된 항목의 캐시와 목록 캐시를 모두 무효화합니다.
    """
    item = await store.update(item_id, data.model_dump())
    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    # 관련 캐시 무효화
    await cache_layer.invalidate(f"items:{item_id}")      # 단건 캐시
    await cache_layer.invalidate_pattern("items:list:*")   # 목록 캐시

    return item


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """상품 삭제 (캐시 무효화 포함)"""
    success = await store.delete(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다")

    # 관련 캐시 무효화
    await cache_layer.invalidate(f"items:{item_id}")
    await cache_layer.invalidate_pattern("items:list:*")


# ──────────────────────────────────────────────
# 7. 캐시 관리 엔드포인트
# ──────────────────────────────────────────────
@app.get("/cache/stats")
async def get_cache_stats():
    """
    캐시 성능 통계.
    히트율, 미스율, DB 쿼리 수를 확인할 수 있습니다.
    """
    if isinstance(cache, InMemoryCache):
        cache_stats = cache.get_stats()
    else:
        cache_stats = {"message": "Redis 사용 중 (별도 모니터링 필요)"}

    return {
        "cache": cache_stats,
        "db_query_count": store.query_count,
    }


@app.delete("/cache/flush", status_code=204)
async def flush_cache():
    """전체 캐시 초기화"""
    await cache_layer.flush_all()


@app.get("/benchmark")
async def benchmark():
    """
    캐시 성능 벤치마크.
    캐시 유무에 따른 응답 시간 차이를 측정합니다.
    """
    # 캐시 비우기
    await cache_layer.flush_all()
    initial_queries = store.query_count

    # 1. 캐시 미스 (DB 조회)
    start = time.perf_counter()
    for _ in range(10):
        await list_items(category=None)
    cold_time = (time.perf_counter() - start) * 1000

    cold_queries = store.query_count - initial_queries

    # 2. 캐시 히트
    start = time.perf_counter()
    for _ in range(10):
        await list_items(category=None)
    warm_time = (time.perf_counter() - start) * 1000

    warm_queries = store.query_count - initial_queries - cold_queries

    return {
        "cold_cache": {
            "total_ms": round(cold_time, 2),
            "avg_ms": round(cold_time / 10, 2),
            "db_queries": cold_queries,
        },
        "warm_cache": {
            "total_ms": round(warm_time, 2),
            "avg_ms": round(warm_time / 10, 2),
            "db_queries": warm_queries,
        },
        "speedup": f"{cold_time / warm_time:.1f}x" if warm_time > 0 else "N/A",
    }
