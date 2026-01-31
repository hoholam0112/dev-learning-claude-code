# 실행 방법: uvicorn example-01:app --reload
# 외부 API 동시 호출 (asyncio.gather + httpx) 예제
# 필요 패키지: pip install fastapi uvicorn httpx

import asyncio
import time
from typing import Optional

import httpx
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="비동기 프로그래밍 심화 - 외부 API 동시 호출")


# ============================================================
# 1. 외부 API 호출 시뮬레이션
# ============================================================

async def simulate_api_call(
    service_name: str,
    delay: float = 1.0,
    should_fail: bool = False,
) -> dict:
    """
    외부 API 호출을 시뮬레이션한다.
    실제로는 httpx.AsyncClient를 사용하여 HTTP 요청을 보낸다.
    """
    start = time.perf_counter()

    # 네트워크 지연 시뮬레이션
    await asyncio.sleep(delay)

    if should_fail:
        raise httpx.HTTPError(f"{service_name} 호출 실패")

    elapsed = time.perf_counter() - start
    return {
        "service": service_name,
        "data": f"{service_name}의 응답 데이터",
        "response_time": f"{elapsed:.3f}초",
    }


# ============================================================
# 2. 순차 실행 vs 동시 실행 비교
# ============================================================

@app.get("/sequential")
async def sequential_calls():
    """
    순차 실행: 각 API를 하나씩 호출한다.
    총 소요 시간 = 각 호출 시간의 합 (약 3초)
    """
    start = time.perf_counter()

    # 하나씩 순차적으로 호출
    result1 = await simulate_api_call("사용자 서비스", delay=1.0)
    result2 = await simulate_api_call("주문 서비스", delay=1.0)
    result3 = await simulate_api_call("결제 서비스", delay=1.0)

    total_time = time.perf_counter() - start
    return {
        "방식": "순차 실행",
        "결과": [result1, result2, result3],
        "총_소요시간": f"{total_time:.3f}초",
        "설명": "3개 API를 순차적으로 호출하여 약 3초 소요",
    }


@app.get("/concurrent")
async def concurrent_calls():
    """
    동시 실행: asyncio.gather로 모든 API를 동시에 호출한다.
    총 소요 시간 = 가장 느린 호출 시간 (약 1초)
    """
    start = time.perf_counter()

    # 모든 호출을 동시에 실행
    result1, result2, result3 = await asyncio.gather(
        simulate_api_call("사용자 서비스", delay=1.0),
        simulate_api_call("주문 서비스", delay=0.8),
        simulate_api_call("결제 서비스", delay=1.0),
    )

    total_time = time.perf_counter() - start
    return {
        "방식": "동시 실행 (asyncio.gather)",
        "결과": [result1, result2, result3],
        "총_소요시간": f"{total_time:.3f}초",
        "설명": "3개 API를 동시에 호출하여 약 1초 소요 (가장 느린 것 기준)",
    }


# ============================================================
# 3. 에러 처리가 포함된 동시 호출
# ============================================================

@app.get("/concurrent-with-errors")
async def concurrent_with_errors(
    fail_payment: bool = Query(False, description="결제 서비스 실패 시뮬레이션"),
):
    """
    return_exceptions=True로 에러를 결과에 포함시킨다.
    일부 서비스가 실패해도 나머지 결과를 사용할 수 있다.
    """
    start = time.perf_counter()

    results = await asyncio.gather(
        simulate_api_call("사용자 서비스", delay=0.5),
        simulate_api_call("주문 서비스", delay=0.8),
        simulate_api_call("결제 서비스", delay=0.3, should_fail=fail_payment),
        return_exceptions=True,  # 예외도 결과 리스트에 포함
    )

    total_time = time.perf_counter() - start

    # 성공/실패 분류
    successes = []
    failures = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failures.append({
                "index": i,
                "error": str(result),
                "type": type(result).__name__,
            })
        else:
            successes.append(result)

    return {
        "방식": "동시 실행 (에러 처리 포함)",
        "성공": successes,
        "실패": failures,
        "총_소요시간": f"{total_time:.3f}초",
        "설명": "fail_payment=true로 결제 서비스 실패를 테스트하세요",
    }


# ============================================================
# 4. create_task를 사용한 세밀한 제어
# ============================================================

@app.get("/create-task-demo")
async def create_task_demo():
    """
    create_task로 태스크를 개별 관리하는 예제.
    타임아웃과 취소를 세밀하게 제어할 수 있다.
    """
    start = time.perf_counter()

    # 태스크 생성 (즉시 스케줄링됨)
    task_fast = asyncio.create_task(
        simulate_api_call("빠른 서비스", delay=0.3)
    )
    task_slow = asyncio.create_task(
        simulate_api_call("느린 서비스", delay=2.0)
    )
    task_medium = asyncio.create_task(
        simulate_api_call("중간 서비스", delay=0.8)
    )

    # 빠른 태스크 먼저 완료 기다림
    fast_result = await task_fast
    fast_time = time.perf_counter() - start

    # 느린 태스크에 타임아웃 적용
    try:
        slow_result = await asyncio.wait_for(task_slow, timeout=1.0)
    except asyncio.TimeoutError:
        task_slow.cancel()
        slow_result = {"error": "타임아웃으로 취소됨"}

    # 중간 태스크 기다림
    medium_result = await task_medium
    total_time = time.perf_counter() - start

    return {
        "방식": "create_task (개별 제어)",
        "빠른_서비스": {
            "결과": fast_result,
            "소요시간": f"{fast_time:.3f}초",
        },
        "느린_서비스": {
            "결과": slow_result,
            "설명": "1초 타임아웃으로 취소됨",
        },
        "중간_서비스": {
            "결과": medium_result,
        },
        "총_소요시간": f"{total_time:.3f}초",
    }


# ============================================================
# 5. httpx를 사용한 실제 HTTP 동시 호출
# ============================================================

@app.get("/real-http-calls")
async def real_http_calls():
    """
    httpx.AsyncClient를 사용한 실제 HTTP 동시 호출.
    여러 공개 API를 동시에 호출한다.
    """
    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 여러 공개 API에 동시 요청
        tasks = [
            client.get("https://httpbin.org/delay/1"),
            client.get("https://httpbin.org/get"),
            client.get("https://httpbin.org/headers"),
        ]

        try:
            responses = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )
        except Exception as exc:
            return {"error": f"HTTP 호출 실패: {str(exc)}"}

    total_time = time.perf_counter() - start

    results = []
    for i, resp in enumerate(responses):
        if isinstance(resp, Exception):
            results.append({
                "index": i,
                "error": str(resp),
            })
        else:
            results.append({
                "index": i,
                "status": resp.status_code,
                "url": str(resp.url),
            })

    return {
        "방식": "httpx.AsyncClient 동시 호출",
        "결과": results,
        "총_소요시간": f"{total_time:.3f}초",
        "설명": (
            "3개의 HTTP 요청이 동시에 실행되어 "
            "가장 느린 것의 시간만큼만 소요됩니다"
        ),
    }


# ============================================================
# 6. 세마포어로 동시 호출 수 제한
# ============================================================

# 동시에 최대 2개의 API 호출만 허용
api_semaphore = asyncio.Semaphore(2)


async def rate_limited_api_call(
    service_name: str, delay: float = 0.5
) -> dict:
    """세마포어로 동시 실행 수가 제한된 API 호출"""
    async with api_semaphore:
        # 이 블록 내에서는 최대 2개의 코루틴만 동시 실행
        start = time.perf_counter()
        await asyncio.sleep(delay)
        elapsed = time.perf_counter() - start
        return {
            "service": service_name,
            "response_time": f"{elapsed:.3f}초",
        }


@app.get("/rate-limited")
async def rate_limited_calls():
    """
    세마포어로 동시 호출 수를 제한하는 예제.
    5개의 API를 호출하지만 동시에 최대 2개만 실행된다.
    """
    start = time.perf_counter()

    results = await asyncio.gather(
        rate_limited_api_call("서비스-A", 0.5),
        rate_limited_api_call("서비스-B", 0.5),
        rate_limited_api_call("서비스-C", 0.5),
        rate_limited_api_call("서비스-D", 0.5),
        rate_limited_api_call("서비스-E", 0.5),
    )

    total_time = time.perf_counter() - start
    return {
        "방식": "세마포어 제한 (최대 2개 동시 실행)",
        "결과": list(results),
        "총_소요시간": f"{total_time:.3f}초",
        "설명": (
            "5개 호출 각각 0.5초인데, 동시에 2개만 실행되므로 "
            "총 약 1.5초 소요 (5/2 올림 = 3 배치 * 0.5초)"
        ),
    }


@app.get("/comparison")
async def comparison():
    """순차/동시/세마포어 방식을 한 눈에 비교"""
    return {
        "비교": {
            "/sequential": {
                "설명": "3개 API 순차 호출",
                "예상_시간": "~3초 (1+1+1)",
            },
            "/concurrent": {
                "설명": "3개 API 동시 호출 (gather)",
                "예상_시간": "~1초 (max(1,0.8,1))",
            },
            "/concurrent-with-errors": {
                "설명": "동시 호출 + 에러 처리",
                "예상_시간": "~0.8초",
            },
            "/create-task-demo": {
                "설명": "개별 태스크 + 타임아웃",
                "예상_시간": "~1초 (타임아웃)",
            },
            "/rate-limited": {
                "설명": "5개 호출, 동시 최대 2개",
                "예상_시간": "~1.5초",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("외부 API 동시 호출 서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print("\n비교 테스트:")
    print("  순차 실행:    curl http://localhost:8000/sequential")
    print("  동시 실행:    curl http://localhost:8000/concurrent")
    print("  에러 처리:    curl 'http://localhost:8000/concurrent-with-errors?fail_payment=true'")
    print("  태스크 제어:  curl http://localhost:8000/create-task-demo")
    print("  세마포어:     curl http://localhost:8000/rate-limited")
    uvicorn.run(app, host="0.0.0.0", port=8000)
