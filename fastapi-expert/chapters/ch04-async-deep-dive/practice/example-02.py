# 실행 방법: uvicorn example-02:app --reload
# CPU 바운드 작업을 블로킹 없이 처리하는 예제
# 필요 패키지: pip install fastapi uvicorn

import asyncio
import hashlib
import math
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from typing import AsyncGenerator

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

app = FastAPI(title="비동기 프로그래밍 심화 - CPU 바운드 & 스트리밍")

# 스레드풀과 프로세스풀 설정
thread_pool = ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="io-worker",
)
process_pool = ProcessPoolExecutor(
    max_workers=2,  # CPU 코어 수에 맞게 설정
)


# ============================================================
# 1. CPU 바운드 작업 예시
# ============================================================

def calculate_primes(limit: int) -> list[int]:
    """
    소수 계산 (CPU 바운드 작업).
    이 함수는 동기 함수이므로 이벤트 루프에서 직접 호출하면 안 된다.
    """
    primes = []
    for num in range(2, limit):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes


def hash_password(password: str, iterations: int = 100000) -> str:
    """
    비밀번호 해싱 (CPU 바운드 작업).
    PBKDF2는 의도적으로 느리게 설계되어 CPU를 많이 사용한다.
    """
    salt = b"fixed-salt-for-demo"
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hashed.hex()


def fibonacci(n: int) -> int:
    """재귀적 피보나치 (CPU 바운드, 의도적으로 비효율적)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# ============================================================
# 2. 블로킹 vs 논블로킹 비교
# ============================================================

@app.get("/blocking-bad")
async def blocking_bad_example():
    """
    나쁜 예: async def 내에서 CPU 바운드 작업을 직접 호출.
    이 요청이 처리되는 동안 다른 모든 요청이 멈춘다!
    """
    start = time.perf_counter()

    # 경고: 이벤트 루프를 블로킹함!
    primes = calculate_primes(50000)

    elapsed = time.perf_counter() - start
    return {
        "방식": "블로킹 (나쁜 예)",
        "소수_개수": len(primes),
        "소요시간": f"{elapsed:.3f}초",
        "경고": "이 요청 처리 중 다른 모든 요청이 멈춥니다!",
    }


@app.get("/thread-pool")
async def thread_pool_example():
    """
    스레드풀에서 CPU 바운드 작업 실행.
    이벤트 루프를 블로킹하지 않는다.
    """
    start = time.perf_counter()

    loop = asyncio.get_event_loop()
    primes = await loop.run_in_executor(
        thread_pool,
        calculate_primes,
        50000,
    )

    elapsed = time.perf_counter() - start
    return {
        "방식": "스레드풀 (run_in_executor)",
        "소수_개수": len(primes),
        "소요시간": f"{elapsed:.3f}초",
        "설명": "스레드풀에서 실행되어 이벤트 루프를 블로킹하지 않습니다",
    }


@app.get("/process-pool")
async def process_pool_example():
    """
    프로세스풀에서 CPU 바운드 작업 실행.
    GIL을 우회하여 진정한 병렬 처리가 가능하다.
    """
    start = time.perf_counter()

    loop = asyncio.get_event_loop()
    primes = await loop.run_in_executor(
        process_pool,
        calculate_primes,
        50000,
    )

    elapsed = time.perf_counter() - start
    return {
        "방식": "프로세스풀 (ProcessPoolExecutor)",
        "소수_개수": len(primes),
        "소요시간": f"{elapsed:.3f}초",
        "설명": "별도 프로세스에서 실행되어 GIL 우회 가능",
    }


@app.get("/sync-route")
def sync_route_example():
    """
    def (동기) 라우트: FastAPI가 자동으로 스레드풀에서 실행한다.
    async def가 아니므로 블로킹 함수를 직접 호출해도 된다.
    """
    start = time.perf_counter()

    # def 라우트에서는 블로킹 호출이 안전하다
    # FastAPI가 자동으로 스레드풀에 위임하기 때문
    primes = calculate_primes(50000)

    elapsed = time.perf_counter() - start
    return {
        "방식": "def 라우트 (자동 스레드풀)",
        "소수_개수": len(primes),
        "소요시간": f"{elapsed:.3f}초",
        "설명": "def 라우트는 FastAPI가 자동으로 스레드풀에서 실행합니다",
    }


# ============================================================
# 3. 여러 CPU 작업의 병렬 실행
# ============================================================

@app.get("/parallel-hashing")
async def parallel_hashing():
    """
    여러 비밀번호를 병렬로 해싱하는 예제.
    프로세스풀을 사용하여 진정한 병렬 처리를 수행한다.
    """
    passwords = [f"password_{i}" for i in range(4)]
    start = time.perf_counter()

    loop = asyncio.get_event_loop()

    # 순차 실행
    seq_start = time.perf_counter()
    sequential_results = []
    for pw in passwords:
        result = await loop.run_in_executor(thread_pool, hash_password, pw)
        sequential_results.append(result)
    seq_time = time.perf_counter() - seq_start

    # 병렬 실행
    par_start = time.perf_counter()
    parallel_results = await asyncio.gather(*[
        loop.run_in_executor(process_pool, hash_password, pw)
        for pw in passwords
    ])
    par_time = time.perf_counter() - par_start

    return {
        "비밀번호_수": len(passwords),
        "순차_실행": {
            "소요시간": f"{seq_time:.3f}초",
            "결과": sequential_results[:2],  # 처음 2개만 표시
        },
        "병렬_실행": {
            "소요시간": f"{par_time:.3f}초",
            "결과": list(parallel_results[:2]),
        },
        "속도_향상": f"{seq_time / par_time:.2f}배" if par_time > 0 else "N/A",
    }


# ============================================================
# 4. 동기 라이브러리를 비동기로 래핑하는 유틸리티
# ============================================================

async def run_sync(func, *args, executor=None, **kwargs):
    """
    동기 함수를 비동기로 실행하는 범용 헬퍼 함수.
    키워드 인자도 지원한다.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        partial(func, *args, **kwargs),
    )


@app.get("/async-wrapper-demo")
async def async_wrapper_demo():
    """run_sync 헬퍼를 사용한 예제"""
    start = time.perf_counter()

    # 동기 함수를 비동기로 래핑하여 동시 실행
    result_primes, result_hash = await asyncio.gather(
        run_sync(calculate_primes, 30000, executor=process_pool),
        run_sync(hash_password, "test_password", iterations=50000),
    )

    elapsed = time.perf_counter() - start
    return {
        "소수_개수": len(result_primes),
        "해시_결과": result_hash[:32] + "...",
        "소요시간": f"{elapsed:.3f}초",
        "설명": "run_sync 헬퍼로 동기 함수를 간편하게 비동기 실행",
    }


# ============================================================
# 5. 스트리밍 응답 (async generator)
# ============================================================

async def generate_fibonacci_stream(count: int) -> AsyncGenerator[str, None]:
    """피보나치 수열을 스트리밍으로 생성"""
    a, b = 0, 1
    for i in range(count):
        yield f"data: {{\"index\": {i}, \"value\": {a}}}\n\n"
        a, b = b, a + b
        await asyncio.sleep(0.1)  # 스트리밍 효과를 위한 지연


async def generate_progress_stream(
    total_steps: int = 10,
) -> AsyncGenerator[str, None]:
    """진행 상황을 스트리밍으로 전송"""
    for step in range(1, total_steps + 1):
        progress = (step / total_steps) * 100
        yield (
            f"data: {{\"step\": {step}, \"total\": {total_steps}, "
            f"\"progress\": {progress:.1f}}}\n\n"
        )
        # 각 단계에서 비동기 작업 시뮬레이션
        await asyncio.sleep(0.5)

    yield 'data: {"status": "완료"}\n\n'


async def generate_prime_stream(limit: int) -> AsyncGenerator[str, None]:
    """
    소수를 찾을 때마다 스트리밍으로 전송.
    CPU 바운드 작업을 청크로 나누어 이벤트 루프를 블로킹하지 않는다.
    """
    count = 0
    for num in range(2, limit):
        is_prime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
            yield f"data: {{\"prime\": {num}, \"count\": {count}}}\n\n"

        # 매 100번째 숫자마다 이벤트 루프에 양보
        if num % 100 == 0:
            await asyncio.sleep(0)  # 양보 포인트


@app.get("/stream/fibonacci")
async def stream_fibonacci(
    count: int = Query(20, ge=1, le=100, description="피보나치 수열 개수"),
):
    """
    피보나치 수열을 Server-Sent Events로 스트리밍.

    테스트: curl -N http://localhost:8000/stream/fibonacci?count=20
    """
    return StreamingResponse(
        generate_fibonacci_stream(count),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/stream/progress")
async def stream_progress(
    steps: int = Query(10, ge=1, le=50, description="총 단계 수"),
):
    """
    작업 진행 상황을 실시간으로 스트리밍.

    테스트: curl -N http://localhost:8000/stream/progress?steps=10
    """
    return StreamingResponse(
        generate_progress_stream(steps),
        media_type="text/event-stream",
    )


@app.get("/stream/primes")
async def stream_primes(
    limit: int = Query(1000, ge=10, le=100000, description="소수 탐색 상한"),
):
    """
    소수를 찾을 때마다 스트리밍으로 전송.
    CPU 바운드 작업을 청크로 나누어 이벤트 루프를 블로킹하지 않는다.

    테스트: curl -N http://localhost:8000/stream/primes?limit=1000
    """
    return StreamingResponse(
        generate_prime_stream(limit),
        media_type="text/event-stream",
    )


# ============================================================
# 6. async def vs def 비교 데모
# ============================================================

@app.get("/async-vs-sync-comparison")
async def async_vs_sync_comparison():
    """
    async def와 def 라우트의 내부 처리 차이를 설명하는 데모.
    """
    return {
        "async_def_라우트": {
            "실행_위치": "이벤트 루프 (메인 스레드)",
            "블로킹_코드": "금지! (이벤트 루프가 멈춤)",
            "비동기_I/O": "await로 직접 사용 가능",
            "적합한_작업": "I/O 바운드 (DB, HTTP, 파일)",
            "예시": "async def endpoint(): return await db.query()",
        },
        "def_라우트": {
            "실행_위치": "스레드풀 (별도 스레드)",
            "블로킹_코드": "허용 (자동 스레드풀 위임)",
            "비동기_I/O": "사용 불가 (await 불가능)",
            "적합한_작업": "동기 라이브러리 사용, 경량 CPU 작업",
            "예시": "def endpoint(): return requests.get(url).json()",
        },
        "run_in_executor": {
            "용도": "async def에서 블로킹 함수를 실행할 때",
            "스레드풀": "I/O 바운드 블로킹 (파일 I/O, 동기 DB 등)",
            "프로세스풀": "CPU 바운드 (해싱, 계산, 이미지 처리)",
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("CPU 바운드 & 스트리밍 서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print("\nCPU 바운드 비교:")
    print("  블로킹:       curl http://localhost:8000/blocking-bad")
    print("  스레드풀:     curl http://localhost:8000/thread-pool")
    print("  프로세스풀:   curl http://localhost:8000/process-pool")
    print("  def 라우트:   curl http://localhost:8000/sync-route")
    print("\n스트리밍:")
    print("  피보나치:     curl -N http://localhost:8000/stream/fibonacci")
    print("  진행 상황:    curl -N http://localhost:8000/stream/progress")
    print("  소수:         curl -N http://localhost:8000/stream/primes")
    uvicorn.run(app, host="0.0.0.0", port=8000)
