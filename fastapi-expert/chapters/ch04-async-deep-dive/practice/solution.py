# 실행 방법: uvicorn solution:app --reload
# 챕터 04 연습문제 모범 답안
# 필요 패키지: pip install fastapi uvicorn

import asyncio
import hashlib
import json
import math
import random
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import asynccontextmanager
from functools import partial
from typing import Any, AsyncGenerator, Optional

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse


# ============================================================
# 문제 2: AsyncExecutor 클래스
# ============================================================

class AsyncExecutor:
    """
    동기 함수를 비동기로 실행하는 실행기.
    I/O 바운드용 스레드풀과 CPU 바운드용 프로세스풀을 관리한다.
    """

    def __init__(
        self,
        io_workers: int = 4,
        cpu_workers: int = 2,
    ):
        self.thread_pool = ThreadPoolExecutor(
            max_workers=io_workers,
            thread_name_prefix="io",
        )
        self.process_pool = ProcessPoolExecutor(
            max_workers=cpu_workers,
        )

    async def run_io(self, func, *args, **kwargs):
        """스레드풀에서 I/O 바운드 함수 실행"""
        loop = asyncio.get_event_loop()
        if kwargs:
            func = partial(func, *args, **kwargs)
            return await loop.run_in_executor(self.thread_pool, func)
        return await loop.run_in_executor(self.thread_pool, func, *args)

    async def run_cpu(self, func, *args, **kwargs):
        """프로세스풀에서 CPU 바운드 함수 실행"""
        loop = asyncio.get_event_loop()
        if kwargs:
            func = partial(func, *args, **kwargs)
            return await loop.run_in_executor(self.process_pool, func)
        return await loop.run_in_executor(self.process_pool, func, *args)

    def shutdown(self):
        """풀 종료"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


# ============================================================
# 문제 3: AsyncRateLimiter 클래스
# ============================================================

class AsyncRateLimiter:
    """
    세마포어 + 토큰 버킷 기반 비동기 Rate Limiter.
    동시 요청 수와 초당 요청 수를 동시에 제한한다.
    """

    def __init__(self, max_concurrent: int = 3, max_per_second: float = 5.0):
        self.max_concurrent = max_concurrent
        self.max_per_second = max_per_second

        # 동시성 제한: 세마포어
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # 속도 제한: 토큰 버킷
        self._tokens = asyncio.Queue(maxsize=int(max_per_second))
        self._refill_task: Optional[asyncio.Task] = None

        # 상태 추적
        self._current_concurrent = 0
        self._waiting_count = 0
        self._request_times: list[float] = []

    async def start(self):
        """Rate Limiter 시작 (토큰 리필 태스크 시작)"""
        # 초기 토큰 충전
        for _ in range(int(self.max_per_second)):
            try:
                self._tokens.put_nowait(True)
            except asyncio.QueueFull:
                break

        # 토큰 리필 태스크 시작
        self._refill_task = asyncio.create_task(self._refill_tokens())

    async def stop(self):
        """Rate Limiter 종료"""
        if self._refill_task:
            self._refill_task.cancel()
            try:
                await self._refill_task
            except asyncio.CancelledError:
                pass

    async def _refill_tokens(self):
        """주기적으로 토큰을 리필"""
        interval = 1.0 / self.max_per_second
        while True:
            await asyncio.sleep(interval)
            try:
                self._tokens.put_nowait(True)
            except asyncio.QueueFull:
                pass  # 버킷이 가득 찬 경우 무시

    async def acquire(self):
        """토큰 획득 + 세마포어 획득"""
        self._waiting_count += 1

        # 1. 토큰 버킷에서 토큰 획득 (속도 제한)
        await self._tokens.get()

        # 2. 세마포어 획득 (동시성 제한)
        await self._semaphore.acquire()

        self._waiting_count -= 1
        self._current_concurrent += 1
        self._request_times.append(time.monotonic())

        # 오래된 요청 시간 정리 (1초 이내만 유지)
        now = time.monotonic()
        self._request_times = [
            t for t in self._request_times if now - t < 1.0
        ]

    def release(self):
        """세마포어 해제"""
        self._current_concurrent -= 1
        self._semaphore.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    @property
    def status(self) -> dict:
        now = time.monotonic()
        recent = [t for t in self._request_times if now - t < 1.0]
        return {
            "concurrent": {
                "current": self._current_concurrent,
                "max": self.max_concurrent,
            },
            "rate": {
                "current_rps": len(recent),
                "max_rps": self.max_per_second,
            },
            "waiting": self._waiting_count,
            "tokens_available": self._tokens.qsize(),
        }


# ============================================================
# lifespan 및 앱 설정
# ============================================================

executor: Optional[AsyncExecutor] = None
rate_limiter: Optional[AsyncRateLimiter] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global executor, rate_limiter

    # 문제 2: AsyncExecutor 초기화
    executor = AsyncExecutor(io_workers=4, cpu_workers=2)
    app.state.executor = executor

    # 문제 3: Rate Limiter 초기화
    rate_limiter = AsyncRateLimiter(max_concurrent=3, max_per_second=5.0)
    await rate_limiter.start()
    app.state.rate_limiter = rate_limiter

    yield

    # 정리
    await rate_limiter.stop()
    executor.shutdown()


app = FastAPI(
    title="챕터 04 연습문제 모범 답안",
    lifespan=lifespan,
)


# ============================================================
# 문제 1: 여러 외부 서비스 동시 호출 최적화
# ============================================================

async def call_user_service(delay: float = 0.5) -> dict:
    """사용자 서비스 호출 시뮬레이션"""
    await asyncio.sleep(delay)
    return {"user_id": 1, "name": "홍길동", "address": "서울"}


async def call_inventory_service(delay: float = 0.3) -> dict:
    """재고 서비스 호출 시뮬레이션"""
    await asyncio.sleep(delay)
    return {"product_id": 100, "stock": 50, "available": True}


async def call_pricing_service(delay: float = 0.4) -> dict:
    """가격 서비스 호출 시뮬레이션"""
    await asyncio.sleep(delay)
    return {"original_price": 50000, "discount": 10, "final_price": 45000}


async def call_shipping_service(
    user_data: dict, inventory_data: dict, delay: float = 0.6
) -> dict:
    """배송 서비스 호출 (사용자 + 재고 정보 필요)"""
    await asyncio.sleep(delay)
    return {
        "address": user_data["address"],
        "weight": "1.5kg",
        "shipping_fee": 3000,
        "estimated_days": 2,
    }


async def call_payment_service(
    total_amount: float, delay: float = 0.8
) -> dict:
    """결제 서비스 호출 (최종 금액 필요)"""
    await asyncio.sleep(delay)
    return {
        "payment_id": "pay_abc123",
        "amount": total_amount,
        "status": "approved",
    }


@app.post("/orders/process")
async def process_order():
    """
    문제 1 답안: 의존 관계를 고려한 최적화된 외부 서비스 호출.

    의존 관계:
    - 1단계: 사용자 + 재고 + 가격 (독립, 동시 실행)
    - 2단계: 배송 (1단계의 사용자/재고 결과 필요)
    - 3단계: 결제 (2단계까지의 모든 결과 필요)
    """
    total_start = time.perf_counter()

    # --- 1단계: 독립적인 서비스 동시 호출 ---
    stage1_start = time.perf_counter()
    user_data, inventory_data, pricing_data = await asyncio.gather(
        call_user_service(),
        call_inventory_service(),
        call_pricing_service(),
    )
    stage1_time = time.perf_counter() - stage1_start

    # --- 2단계: 배송 서비스 (1단계 결과에 의존) ---
    stage2_start = time.perf_counter()
    shipping_data = await call_shipping_service(user_data, inventory_data)
    stage2_time = time.perf_counter() - stage2_start

    # --- 3단계: 결제 서비스 (모든 결과에 의존) ---
    total_amount = pricing_data["final_price"] + shipping_data["shipping_fee"]
    stage3_start = time.perf_counter()
    payment_data = await call_payment_service(total_amount)
    stage3_time = time.perf_counter() - stage3_start

    total_time = time.perf_counter() - total_start

    return {
        "순차_실행_예상시간": "2.6초 (0.5+0.3+0.4+0.6+0.8)",
        "최적화_실행_시간": f"{total_time:.3f}초",
        "절약_시간": f"{2.6 - total_time:.3f}초",
        "단계별_결과": {
            "1단계_동시": {
                "사용자": user_data,
                "재고": inventory_data,
                "가격": pricing_data,
                "소요시간": f"{stage1_time:.3f}초",
            },
            "2단계_배송": {
                "배송": shipping_data,
                "소요시간": f"{stage2_time:.3f}초",
            },
            "3단계_결제": {
                "결제": payment_data,
                "소요시간": f"{stage3_time:.3f}초",
            },
        },
    }


# ============================================================
# 문제 2: 동기 라이브러리를 비동기로 래핑
# ============================================================

def sync_hash_password(password: str, iterations: int = 100000) -> str:
    """동기 비밀번호 해싱 (CPU 바운드)"""
    salt = b"secure-salt-value"
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, iterations
    )
    return hashed.hex()


def sync_parse_json(data_str: str) -> list:
    """동기 JSON 파싱"""
    return json.loads(data_str)


def sync_regex_search(pattern: str, texts: list[str]) -> list[dict]:
    """동기 정규식 대량 매칭"""
    import re
    results = []
    compiled = re.compile(pattern, re.IGNORECASE)
    for i, text in enumerate(texts):
        matches = compiled.findall(text)
        if matches:
            results.append({"index": i, "matches": matches})
    return results


@app.post("/auth/hash")
async def hash_password_endpoint(data: dict):
    """비밀번호를 비동기적으로 해싱"""
    password = data.get("password", "")
    start = time.perf_counter()

    hashed = await executor.run_cpu(sync_hash_password, password)

    elapsed = time.perf_counter() - start
    return {
        "hash": hashed,
        "method": "pbkdf2_sha256",
        "소요시간": f"{elapsed:.3f}초",
        "async": True,
    }


@app.post("/parse/json")
async def parse_json_endpoint():
    """대량 JSON 데이터를 비동기적으로 파싱"""
    # 테스트 데이터 생성
    large_data = json.dumps([
        {"id": i, "name": f"항목_{i}", "value": random.random()}
        for i in range(10000)
    ])

    start = time.perf_counter()
    parsed = await executor.run_io(sync_parse_json, large_data)
    elapsed = time.perf_counter() - start

    return {
        "parsed_items": len(parsed),
        "parse_time": f"{elapsed:.4f}초",
        "첫번째_항목": parsed[0] if parsed else None,
        "async": True,
    }


@app.get("/regex/search")
async def regex_search_endpoint(
    pattern: str = Query("python", description="검색 패턴"),
):
    """정규식 대량 매칭을 비동기적으로 실행"""
    # 테스트 데이터 생성
    texts = [
        f"이것은 {random.choice(['Python', 'Java', 'Go', 'Rust'])} "
        f"프로그래밍 예제 #{i}입니다."
        for i in range(5000)
    ]

    start = time.perf_counter()
    results = await executor.run_cpu(sync_regex_search, pattern, texts)
    elapsed = time.perf_counter() - start

    return {
        "pattern": pattern,
        "total_texts": len(texts),
        "matches_found": len(results),
        "search_time": f"{elapsed:.4f}초",
        "first_results": results[:5],
        "async": True,
    }


# ============================================================
# 문제 3: 세마포어로 동시 요청 제한
# ============================================================

async def simulated_external_api(request_id: int) -> dict:
    """외부 API 호출 시뮬레이션"""
    start = time.perf_counter()
    await asyncio.sleep(0.3)  # API 응답 시간
    elapsed = time.perf_counter() - start
    return {
        "request_id": request_id,
        "response_time": f"{elapsed:.3f}초",
        "timestamp": time.time(),
    }


@app.get("/rate-limit-test")
async def rate_limit_test(
    requests_count: int = Query(10, ge=1, le=50, alias="requests"),
):
    """
    문제 3 답안: Rate Limiter를 통한 동시 요청 제한 테스트.
    여러 요청을 동시에 보내면서 Rate Limiter가 동작하는 것을 확인한다.
    """
    start = time.perf_counter()

    async def rate_limited_call(request_id: int) -> dict:
        """Rate Limiter를 거쳐 API를 호출"""
        wait_start = time.perf_counter()
        async with rate_limiter:
            wait_time = time.perf_counter() - wait_start
            result = await simulated_external_api(request_id)
            result["wait_time"] = f"{wait_time:.3f}초"
            return result

    # 모든 요청을 동시에 실행 (Rate Limiter가 제한)
    results = await asyncio.gather(*[
        rate_limited_call(i) for i in range(requests_count)
    ])

    total_time = time.perf_counter() - start

    return {
        "total_requests": requests_count,
        "max_concurrent": rate_limiter.max_concurrent,
        "max_per_second": rate_limiter.max_per_second,
        "total_time": f"{total_time:.3f}초",
        "results": sorted(results, key=lambda x: x["request_id"]),
        "limiter_status": rate_limiter.status,
    }


@app.get("/rate-limiter/status")
async def rate_limiter_status():
    """Rate Limiter 현재 상태 조회"""
    return rate_limiter.status


# ============================================================
# 문제 4: async generator를 사용한 스트리밍 응답
# ============================================================

async def search_stream(
    keyword: str, data_size: int
) -> AsyncGenerator[str, None]:
    """대량 데이터에서 키워드를 검색하면서 결과를 스트리밍"""
    start = time.perf_counter()
    matches = 0
    batch_size = 1000

    # 시작 이벤트
    yield f'data: {{"type": "start", "keyword": "{keyword}", "total": {data_size}}}\n\n'

    for batch_start in range(0, data_size, batch_size):
        batch_end = min(batch_start + batch_size, data_size)
        batch_matches = 0

        # 배치 처리 (CPU 바운드를 시뮬레이션)
        for i in range(batch_start, batch_end):
            # 랜덤하게 매칭 시뮬레이션
            if random.random() < 0.005:  # 0.5% 확률로 매칭
                matches += 1
                batch_matches += 1
                # 매칭된 항목 전송
                yield (
                    f'data: {{"type": "match", "item": '
                    f'{{"id": {i}, "content": "...{keyword}..."}}}}\n\n'
                )

        # 진행 상황 전송
        progress = (batch_end / data_size) * 100
        yield (
            f'data: {{"type": "progress", "processed": {batch_end}, '
            f'"total": {data_size}, "progress": {progress:.1f}, '
            f'"matches": {matches}}}\n\n'
        )

        # 이벤트 루프에 양보
        await asyncio.sleep(0.05)

    # 완료 이벤트
    elapsed = time.perf_counter() - start
    yield (
        f'data: {{"type": "complete", "total_matches": {matches}, '
        f'"total_time": "{elapsed:.3f}초"}}\n\n'
    )


async def transform_stream(
    batch_size: int, total: int = 1000
) -> AsyncGenerator[str, None]:
    """데이터를 변환하면서 진행 상황을 스트리밍"""
    start = time.perf_counter()
    processed = 0

    yield f'data: {{"type": "start", "total": {total}, "batch_size": {batch_size}}}\n\n'

    batch_num = 0
    while processed < total:
        batch_num += 1
        current_batch = min(batch_size, total - processed)

        # 변환 작업 시뮬레이션
        await asyncio.sleep(0.1)

        processed += current_batch
        progress = (processed / total) * 100

        yield (
            f'data: {{"type": "batch", "batch_num": {batch_num}, '
            f'"items_processed": {processed}, "progress": {progress:.1f}}}\n\n'
        )

    elapsed = time.perf_counter() - start
    yield (
        f'data: {{"type": "complete", "total_processed": {processed}, '
        f'"total_time": "{elapsed:.3f}초"}}\n\n'
    )


async def aggregate_stream() -> AsyncGenerator[str, None]:
    """집계 작업을 단계별로 스트리밍"""
    stages = [
        ("데이터 수집", 0.5),
        ("필터링", 0.3),
        ("그룹화", 0.4),
        ("집계 계산", 0.6),
        ("결과 포맷팅", 0.2),
    ]

    start = time.perf_counter()
    yield f'data: {{"type": "start", "stages": {len(stages)}}}\n\n'

    results = {}
    for i, (stage_name, duration) in enumerate(stages, 1):
        stage_start = time.perf_counter()

        yield (
            f'data: {{"type": "stage_start", "stage": {i}, '
            f'"name": "{stage_name}"}}\n\n'
        )

        await asyncio.sleep(duration)

        stage_elapsed = time.perf_counter() - stage_start
        result_value = random.randint(100, 10000)
        results[stage_name] = result_value

        yield (
            f'data: {{"type": "stage_complete", "stage": {i}, '
            f'"name": "{stage_name}", '
            f'"duration": "{stage_elapsed:.3f}초", '
            f'"result": {result_value}}}\n\n'
        )

    total_elapsed = time.perf_counter() - start
    results_json = json.dumps(results, ensure_ascii=False)
    yield (
        f'data: {{"type": "complete", '
        f'"total_time": "{total_elapsed:.3f}초", '
        f'"results": {results_json}}}\n\n'
    )


@app.get("/stream/search")
async def stream_search(
    keyword: str = Query("python", description="검색 키워드"),
    data_size: int = Query(10000, ge=100, le=100000),
):
    """
    문제 4 답안: 대량 데이터 검색 결과를 실시간 스트리밍.

    테스트: curl -N 'http://localhost:8000/stream/search?keyword=python&data_size=10000'
    """
    return StreamingResponse(
        search_stream(keyword, data_size),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/stream/transform")
async def stream_transform(
    batch_size: int = Query(100, ge=10, le=1000),
    total: int = Query(1000, ge=100, le=100000),
):
    """
    데이터 변환 진행 상황을 스트리밍.

    테스트: curl -N 'http://localhost:8000/stream/transform?batch_size=100'
    """
    return StreamingResponse(
        transform_stream(batch_size, total),
        media_type="text/event-stream",
    )


@app.get("/stream/aggregate")
async def stream_aggregate():
    """
    집계 작업을 단계별로 스트리밍.

    테스트: curl -N http://localhost:8000/stream/aggregate
    """
    return StreamingResponse(
        aggregate_stream(),
        media_type="text/event-stream",
    )


@app.get("/")
async def root():
    return {
        "message": "챕터 04 연습문제 모범 답안",
        "문제1": "POST /orders/process (외부 서비스 동시 호출)",
        "문제2": {
            "POST /auth/hash": "비밀번호 해싱",
            "POST /parse/json": "JSON 파싱",
            "GET /regex/search?pattern=python": "정규식 검색",
        },
        "문제3": {
            "GET /rate-limit-test?requests=10": "Rate Limit 테스트",
            "GET /rate-limiter/status": "Rate Limiter 상태",
        },
        "문제4": {
            "GET /stream/search": "스트리밍 검색 (curl -N 사용)",
            "GET /stream/transform": "스트리밍 변환",
            "GET /stream/aggregate": "스트리밍 집계",
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("챕터 04 연습문제 모범 답안 서버")
    print("=" * 60)
    print("\n문제 1: POST http://localhost:8000/orders/process")
    print("문제 2: POST http://localhost:8000/auth/hash")
    print("문제 3: GET  http://localhost:8000/rate-limit-test?requests=10")
    print("문제 4: curl -N http://localhost:8000/stream/search")
    print("\nAPI 문서: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
