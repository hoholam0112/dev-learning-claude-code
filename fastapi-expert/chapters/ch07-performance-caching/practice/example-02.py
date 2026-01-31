# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn orjson
"""
StreamingResponse와 응답 최적화 예제.

주요 학습 포인트:
- StreamingResponse로 대용량 CSV/JSON 스트리밍
- orjson을 사용한 고속 직렬화
- 응답 압축 (GZip 미들웨어)
- 청크 단위 데이터 생성으로 메모리 절약
- 타이밍 미들웨어로 응답 시간 측정
"""
import asyncio
import csv
import io
import time
from datetime import datetime, timezone
from typing import AsyncGenerator

import orjson
from fastapi import FastAPI, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, StreamingResponse, Response
from pydantic import BaseModel

# ──────────────────────────────────────────────
# 1. FastAPI 앱 설정
# ──────────────────────────────────────────────
app = FastAPI(
    title="StreamingResponse와 응답 최적화",
    description="대용량 데이터 스트리밍, 직렬화 최적화, 응답 압축",
    default_response_class=ORJSONResponse,  # orjson 기반 기본 응답
)

# GZip 압축 미들웨어: 500바이트 이상 응답을 자동 압축
app.add_middleware(GZipMiddleware, minimum_size=500)


# ──────────────────────────────────────────────
# 2. 타이밍 미들웨어
# ──────────────────────────────────────────────
@app.middleware("http")
async def add_timing_header(request, call_next):
    """
    모든 응답에 처리 시간 헤더를 추가합니다.
    X-Process-Time: 서버 처리 시간 (ms)
    """
    start = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# ──────────────────────────────────────────────
# 3. 데이터 생성 유틸리티
# ──────────────────────────────────────────────
def generate_sample_data(count: int) -> list[dict]:
    """대용량 샘플 데이터 생성 (메모리 로딩 방식)"""
    return [
        {
            "id": i,
            "name": f"상품_{i:06d}",
            "price": round(1000 + (i * 1.5), 2),
            "category": ["전자기기", "도서", "의류", "식품"][i % 4],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        for i in range(1, count + 1)
    ]


async def generate_sample_data_stream(
    count: int, batch_size: int = 1000
) -> AsyncGenerator[list[dict], None]:
    """대용량 샘플 데이터를 배치 단위로 생성 (스트리밍 방식)"""
    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        batch = [
            {
                "id": i,
                "name": f"상품_{i:06d}",
                "price": round(1000 + (i * 1.5), 2),
                "category": ["전자기기", "도서", "의류", "식품"][i % 4],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            for i in range(batch_start + 1, batch_end + 1)
        ]
        yield batch
        # 다른 코루틴에게 제어권 양보 (이벤트 루프 차단 방지)
        await asyncio.sleep(0)


# ──────────────────────────────────────────────
# 4. CSV 스트리밍
# ──────────────────────────────────────────────
async def csv_stream_generator(count: int) -> AsyncGenerator[str, None]:
    """
    대용량 CSV 데이터를 청크 단위로 생성하는 제너레이터.
    전체 데이터를 메모리에 올리지 않고 스트리밍합니다.
    """
    # 헤더 행
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "상품명", "가격", "카테고리", "생성일시"])
    yield buffer.getvalue()

    # 데이터 행 (배치 단위)
    async for batch in generate_sample_data_stream(count, batch_size=500):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        for item in batch:
            writer.writerow([
                item["id"],
                item["name"],
                item["price"],
                item["category"],
                item["created_at"],
            ])
        yield buffer.getvalue()


async def json_stream_generator(count: int) -> AsyncGenerator[bytes, None]:
    """
    대용량 JSON 배열을 스트리밍하는 제너레이터.
    JSON 배열을 열고, 청크를 보내고, 닫는 방식입니다.

    출력 형식: [{"id":1,...},{"id":2,...},...,{"id":N,...}]
    """
    yield b"["

    first = True
    async for batch in generate_sample_data_stream(count, batch_size=500):
        for item in batch:
            if not first:
                yield b","
            yield orjson.dumps(item)
            first = False

    yield b"]"


# ──────────────────────────────────────────────
# 5. API 엔드포인트
# ──────────────────────────────────────────────
@app.get("/data/normal")
async def get_data_normal(
    count: int = Query(10000, ge=1, le=100000, description="데이터 수"),
):
    """
    일반 응답: 전체 데이터를 메모리에 로드 후 반환.
    count가 크면 메모리 사용량이 비례하여 증가합니다.
    """
    data = generate_sample_data(count)
    return data


@app.get("/data/streaming/csv")
async def get_data_streaming_csv(
    count: int = Query(10000, ge=1, le=1000000, description="데이터 수"),
):
    """
    CSV 스트리밍: 청크 단위로 데이터를 생성하면서 전송.
    100만 건도 메모리 사용량이 일정합니다.
    """
    return StreamingResponse(
        csv_stream_generator(count),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=export_{count}.csv",
        },
    )


@app.get("/data/streaming/json")
async def get_data_streaming_json(
    count: int = Query(10000, ge=1, le=1000000, description="데이터 수"),
):
    """
    JSON 스트리밍: 대용량 JSON 배열을 청크 단위로 전송.
    orjson으로 각 항목을 개별 직렬화합니다.
    """
    return StreamingResponse(
        json_stream_generator(count),
        media_type="application/json",
    )


@app.get("/data/orjson-vs-json")
async def compare_serialization(
    count: int = Query(1000, ge=100, le=50000, description="데이터 수"),
):
    """
    orjson vs 표준 json 직렬화 성능 비교.
    같은 데이터를 두 방식으로 직렬화하고 시간을 비교합니다.
    """
    import json

    data = generate_sample_data(count)

    # 표준 json 직렬화
    start = time.perf_counter()
    json_result = json.dumps(data, ensure_ascii=False)
    json_time = (time.perf_counter() - start) * 1000

    # orjson 직렬화
    start = time.perf_counter()
    orjson_result = orjson.dumps(data)
    orjson_time = (time.perf_counter() - start) * 1000

    return {
        "data_count": count,
        "standard_json": {
            "time_ms": round(json_time, 2),
            "size_bytes": len(json_result.encode()),
        },
        "orjson": {
            "time_ms": round(orjson_time, 2),
            "size_bytes": len(orjson_result),
        },
        "speedup": f"{json_time / orjson_time:.1f}x" if orjson_time > 0 else "N/A",
    }


# ──────────────────────────────────────────────
# 6. SSE (Server-Sent Events) 스트리밍
# ──────────────────────────────────────────────
async def sse_event_generator(duration: int = 10) -> AsyncGenerator[str, None]:
    """
    SSE 이벤트 생성기.
    실시간 데이터 피드를 시뮬레이션합니다.

    SSE 형식:
    event: message
    data: {"key": "value"}

    """
    import random

    start_time = time.time()
    event_id = 0

    while time.time() - start_time < duration:
        event_id += 1
        data = {
            "id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_usage": round(random.uniform(10, 90), 1),
            "memory_usage": round(random.uniform(30, 80), 1),
            "request_count": random.randint(100, 1000),
        }
        # SSE 형식으로 이벤트 전송
        yield f"event: metrics\ndata: {orjson.dumps(data).decode()}\nid: {event_id}\n\n"
        await asyncio.sleep(1)  # 1초마다 이벤트 전송

    # 종료 이벤트
    yield f"event: close\ndata: {{\"message\": \"스트림 종료\"}}\n\n"


@app.get("/stream/sse")
async def stream_sse(
    duration: int = Query(10, ge=1, le=60, description="스트리밍 지속 시간 (초)"),
):
    """
    SSE (Server-Sent Events) 스트리밍.
    실시간 서버 메트릭을 1초 간격으로 전송합니다.

    테스트:
    curl -N http://localhost:8000/stream/sse?duration=5
    """
    return StreamingResponse(
        sse_event_generator(duration),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 버퍼링 비활성화
        },
    )


# ──────────────────────────────────────────────
# 7. 메모리 사용량 비교 엔드포인트
# ──────────────────────────────────────────────
@app.get("/memory-comparison")
async def memory_comparison():
    """
    일반 응답 vs 스트리밍 응답의 메모리 사용 패턴 설명.
    실제 메모리 측정은 프로파일러로 해야 정확합니다.
    """
    return {
        "description": "일반 응답 vs 스트리밍 응답 메모리 비교",
        "normal_response": {
            "pattern": "전체 데이터를 메모리에 로드 -> 직렬화 -> 전송",
            "memory": "O(N) - 데이터 크기에 비례",
            "example": "10만 건 * 200바이트 = ~20MB 메모리 필요",
            "endpoint": "/data/normal?count=100000",
        },
        "streaming_response": {
            "pattern": "배치 단위로 생성 -> 직렬화 -> 전송 -> 버퍼 해제",
            "memory": "O(batch_size) - 배치 크기만큼만 사용",
            "example": "배치 500건 * 200바이트 = ~100KB 메모리 사용",
            "endpoint": "/data/streaming/csv?count=100000",
        },
        "recommendation": "10000건 이상일 때 StreamingResponse 권장",
    }


@app.get("/tips")
async def performance_tips():
    """성능 최적화 팁 요약"""
    return {
        "serialization": [
            "orjson은 표준 json 대비 3~10배 빠릅니다",
            "default_response_class=ORJSONResponse로 전역 설정하세요",
            "msgspec은 orjson보다 더 빠르지만 Pydantic 호환이 제한적입니다",
        ],
        "streaming": [
            "대용량 데이터는 반드시 StreamingResponse를 사용하세요",
            "CSV 내보내기는 배치 단위(500~1000행)로 생성하세요",
            "JSON 스트리밍은 배열을 열고/닫는 패턴을 사용하세요",
        ],
        "compression": [
            "GZipMiddleware로 자동 압축 (minimum_size=500)",
            "JSON 데이터는 압축 시 70~90% 크기 감소",
            "정적 파일은 Nginx에서 압축하는 것이 더 효율적입니다",
        ],
        "general": [
            "응답에 X-Process-Time 헤더를 추가하여 지연 추적",
            "큰 페이로드는 페이징으로 분할하세요",
            "response_model_exclude로 불필요한 필드를 제외하세요",
        ],
    }
