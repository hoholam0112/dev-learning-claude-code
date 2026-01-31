# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn
"""
Prometheus 메트릭 익스포터 예제.

주요 학습 포인트:
- Prometheus 메트릭 타입 (Counter, Gauge, Histogram)
- 커스텀 메트릭 수집 미들웨어
- /metrics 엔드포인트 (Prometheus scrape 형식)
- RED 방법론 (Rate, Errors, Duration) 적용
- 비즈니스 메트릭 추가
"""
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ──────────────────────────────────────────────
# 1. Prometheus 메트릭 구현 (라이브러리 없이)
# ──────────────────────────────────────────────
class Counter:
    """
    Prometheus Counter: 단조 증가하는 값.
    사용 예: 총 요청 수, 총 에러 수
    """

    def __init__(self, name: str, description: str, labels: Optional[list[str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values: dict[tuple, float] = defaultdict(float)

    def inc(self, value: float = 1, **label_values) -> None:
        """카운터 증가"""
        key = tuple(label_values.get(l, "") for l in self.labels)
        self._values[key] += value

    def collect(self) -> str:
        """Prometheus 형식으로 출력"""
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} counter",
        ]
        for key, value in self._values.items():
            labels_str = self._format_labels(key)
            lines.append(f"{self.name}{labels_str} {value}")
        return "\n".join(lines)

    def _format_labels(self, key: tuple) -> str:
        if not self.labels:
            return ""
        pairs = [f'{l}="{v}"' for l, v in zip(self.labels, key)]
        return "{" + ",".join(pairs) + "}"


class Gauge:
    """
    Prometheus Gauge: 증가/감소하는 값.
    사용 예: 현재 연결 수, 메모리 사용량
    """

    def __init__(self, name: str, description: str, labels: Optional[list[str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values: dict[tuple, float] = defaultdict(float)

    def set(self, value: float, **label_values) -> None:
        """값 설정"""
        key = tuple(label_values.get(l, "") for l in self.labels)
        self._values[key] = value

    def inc(self, value: float = 1, **label_values) -> None:
        """값 증가"""
        key = tuple(label_values.get(l, "") for l in self.labels)
        self._values[key] += value

    def dec(self, value: float = 1, **label_values) -> None:
        """값 감소"""
        key = tuple(label_values.get(l, "") for l in self.labels)
        self._values[key] -= value

    def collect(self) -> str:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} gauge",
        ]
        for key, value in self._values.items():
            labels_str = self._format_labels(key)
            lines.append(f"{self.name}{labels_str} {value}")
        return "\n".join(lines)

    def _format_labels(self, key: tuple) -> str:
        if not self.labels:
            return ""
        pairs = [f'{l}="{v}"' for l, v in zip(self.labels, key)]
        return "{" + ",".join(pairs) + "}"


class Histogram:
    """
    Prometheus Histogram: 값의 분포를 측정.
    사용 예: 응답 시간 분포
    """

    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

    def __init__(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
        buckets: Optional[tuple] = None,
    ):
        self.name = name
        self.description = description
        self.labels = labels or []
        self.buckets = buckets or self.DEFAULT_BUCKETS
        self._counts: dict[tuple, dict[float, int]] = defaultdict(
            lambda: {b: 0 for b in self.buckets}
        )
        self._sums: dict[tuple, float] = defaultdict(float)
        self._totals: dict[tuple, int] = defaultdict(int)

    def observe(self, value: float, **label_values) -> None:
        """관측값 기록"""
        key = tuple(label_values.get(l, "") for l in self.labels)
        self._sums[key] += value
        self._totals[key] += 1
        for bucket in self.buckets:
            if value <= bucket:
                self._counts[key][bucket] += 1

    def collect(self) -> str:
        lines = [
            f"# HELP {self.name} {self.description}",
            f"# TYPE {self.name} histogram",
        ]
        for key in set(list(self._counts.keys()) + list(self._sums.keys())):
            labels_str = self._format_labels(key)
            for bucket in self.buckets:
                count = self._counts.get(key, {}).get(bucket, 0)
                lines.append(f'{self.name}_bucket{{le="{bucket}"{labels_str}}} {count}')
            lines.append(f'{self.name}_bucket{{le="+Inf"{labels_str}}} {self._totals.get(key, 0)}')
            lines.append(f"{self.name}_sum{{{labels_str.strip('{}')}}} {self._sums.get(key, 0):.6f}")
            lines.append(f"{self.name}_count{{{labels_str.strip('{}')}}} {self._totals.get(key, 0)}")
        return "\n".join(lines)

    def _format_labels(self, key: tuple) -> str:
        if not self.labels:
            return ""
        pairs = [f',{l}="{v}"' for l, v in zip(self.labels, key)]
        return "".join(pairs)


# ──────────────────────────────────────────────
# 2. 메트릭 인스턴스 정의
# ──────────────────────────────────────────────

# RED 메트릭
http_requests_total = Counter(
    "http_requests_total",
    "HTTP 요청 총 수",
    labels=["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP 요청 처리 시간 (초)",
    labels=["method", "path"],
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "현재 처리 중인 HTTP 요청 수",
    labels=["method"],
)

# 비즈니스 메트릭
orders_total = Counter(
    "orders_total",
    "생성된 주문 총 수",
    labels=["status"],
)

active_users = Gauge(
    "active_users",
    "현재 활성 사용자 수",
)

# 시스템 메트릭
app_info_gauge = Gauge(
    "app_info",
    "앱 정보",
    labels=["version", "environment"],
)
app_info_gauge.set(1, version="1.0.0", environment="development")

app_uptime_seconds = Gauge(
    "app_uptime_seconds",
    "앱 가동 시간 (초)",
)

start_time = time.time()


# ──────────────────────────────────────────────
# 3. 메트릭 수집 미들웨어
# ──────────────────────────────────────────────
class MetricsMiddleware(BaseHTTPMiddleware):
    """
    모든 HTTP 요청에 대해 Prometheus 메트릭을 자동 수집하는 미들웨어.
    - 요청 수 (Counter)
    - 응답 시간 (Histogram)
    - 진행 중인 요청 (Gauge)
    """

    # 메트릭에서 제외할 경로
    EXCLUDE_PATHS = {"/metrics", "/health/live", "/health/ready", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # 제외 경로
        if path in self.EXCLUDE_PATHS:
            return await call_next(request)

        # 진행 중인 요청 추적
        http_requests_in_progress.inc(method=method)

        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception as e:
            status = "500"
            raise
        finally:
            duration = time.perf_counter() - start

            # 메트릭 기록
            http_requests_total.inc(method=method, path=path, status=status)
            http_request_duration_seconds.observe(duration, method=method, path=path)
            http_requests_in_progress.dec(method=method)

        return response


# ──────────────────────────────────────────────
# 4. FastAPI 앱
# ──────────────────────────────────────────────
app = FastAPI(title="Prometheus 메트릭 익스포터")
app.add_middleware(MetricsMiddleware)


@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus 메트릭 엔드포인트.
    Prometheus가 이 엔드포인트를 주기적으로 스크래핑합니다.

    설정 예시 (prometheus.yml):
    scrape_configs:
      - job_name: 'fastapi'
        scrape_interval: 15s
        static_configs:
          - targets: ['localhost:8000']
    """
    # 시스템 메트릭 갱신
    app_uptime_seconds.set(time.time() - start_time)

    # 모든 메트릭 수집
    metrics = [
        http_requests_total.collect(),
        http_request_duration_seconds.collect(),
        http_requests_in_progress.collect(),
        orders_total.collect(),
        active_users.collect(),
        app_info_gauge.collect(),
        app_uptime_seconds.collect(),
    ]

    return PlainTextResponse(
        content="\n\n".join(m for m in metrics if m) + "\n",
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


# ──────────────────────────────────────────────
# 5. 샘플 API (메트릭 테스트용)
# ──────────────────────────────────────────────
import asyncio
import random

# 시뮬레이션 데이터
items = [
    {"id": i, "name": f"상품_{i}", "price": random.randint(1000, 100000)}
    for i in range(1, 11)
]


@app.get("/api/items")
async def list_items():
    """상품 목록 (정상 응답)"""
    await asyncio.sleep(random.uniform(0.01, 0.05))  # 응답 시간 변동
    return items


@app.get("/api/items/{item_id}")
async def get_item(item_id: int):
    """상품 상세"""
    await asyncio.sleep(random.uniform(0.01, 0.03))
    if item_id > 10:
        raise HTTPException(404, "상품을 찾을 수 없습니다")
    return items[item_id - 1]


@app.post("/api/orders")
async def create_order(item_id: int, quantity: int = 1):
    """주문 생성 (비즈니스 메트릭 포함)"""
    await asyncio.sleep(random.uniform(0.05, 0.2))  # 주문 처리 시뮬레이션

    # 10% 확률로 실패
    if random.random() < 0.1:
        orders_total.inc(status="failed")
        raise HTTPException(400, "주문 처리 실패")

    orders_total.inc(status="success")

    return {
        "order_id": random.randint(1000, 9999),
        "item_id": item_id,
        "quantity": quantity,
        "status": "confirmed",
    }


@app.get("/api/slow")
async def slow_endpoint():
    """의도적으로 느린 엔드포인트 (메트릭 테스트)"""
    delay = random.uniform(0.5, 2.0)
    await asyncio.sleep(delay)
    return {"message": "느린 응답", "delay_seconds": round(delay, 2)}


@app.get("/api/error")
async def error_endpoint():
    """의도적으로 에러 발생 (메트릭 테스트)"""
    raise HTTPException(500, "의도적 서버 에러")


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready", "uptime": time.time() - start_time}


@app.get("/")
async def root():
    return {
        "message": "Prometheus 메트릭 익스포터 예제",
        "endpoints": {
            "메트릭": "/metrics (Prometheus 스크래핑용)",
            "상품 목록": "/api/items",
            "주문 생성": "POST /api/orders?item_id=1&quantity=2",
            "느린 응답": "/api/slow",
            "에러 테스트": "/api/error",
            "헬스 체크": "/health/ready",
        },
        "tip": "여러 번 요청한 후 /metrics를 확인하세요",
    }
