# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn
"""
이벤트 기반 서비스 간 통신 (간단한 Pub/Sub) 예제.

주요 학습 포인트:
- 인메모리 이벤트 버스 (Pub/Sub) 구현
- 이벤트 기반 느슨한 결합
- 서킷 브레이커 패턴
- 분산 트레이싱 헤더 전파
- 서비스 간 비동기 통신 시뮬레이션
"""
import asyncio
import enum
import logging
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# ──────────────────────────────────────────────
# 1. 이벤트 시스템 (인메모리 Pub/Sub)
# ──────────────────────────────────────────────
@dataclass
class Event:
    """이벤트 데이터 클래스"""
    type: str
    data: dict
    source: str  # 발행 서비스
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


class EventBus:
    """
    인메모리 이벤트 버스 (Pub/Sub).

    프로덕션에서는 Redis Pub/Sub, RabbitMQ, Kafka 등으로 대체합니다.
    이 구현은 동일 프로세스 내에서 서비스 간 통신을 시뮬레이션합니다.
    """

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._event_log: list[Event] = []
        self._max_log_size = 100

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """이벤트 타입에 핸들러 등록"""
        self._handlers[event_type].append(handler)
        logger.info(f"[이벤트 버스] '{event_type}' 구독 등록: {handler.__name__}")

    async def publish(self, event: Event) -> int:
        """
        이벤트 발행: 등록된 모든 핸들러에 비동기 전달.
        반환값: 처리된 핸들러 수
        """
        self._event_log.append(event)
        if len(self._event_log) > self._max_log_size:
            self._event_log.pop(0)

        handlers = self._handlers.get(event.type, [])
        if not handlers:
            logger.warning(f"[이벤트 버스] '{event.type}' 이벤트에 등록된 핸들러 없음")
            return 0

        logger.info(
            f"[이벤트 버스] '{event.type}' 발행 -> {len(handlers)}개 핸들러 "
            f"(trace_id: {event.trace_id})"
        )

        # 모든 핸들러를 비동기로 실행
        results = await asyncio.gather(
            *(handler(event) for handler in handlers),
            return_exceptions=True,
        )

        # 에러 로깅
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"[이벤트 버스] 핸들러 '{handlers[i].__name__}' 실패: {result}"
                )

        return len(handlers)

    def get_log(self, event_type: Optional[str] = None) -> list[dict]:
        """이벤트 로그 조회"""
        events = self._event_log
        if event_type:
            events = [e for e in events if e.type == event_type]
        return [
            {
                "event_id": e.event_id,
                "type": e.type,
                "source": e.source,
                "timestamp": e.timestamp,
                "trace_id": e.trace_id,
                "data": e.data,
            }
            for e in events
        ]


event_bus = EventBus()


# ──────────────────────────────────────────────
# 2. 서킷 브레이커 패턴
# ──────────────────────────────────────────────
class CircuitState(enum.Enum):
    CLOSED = "closed"      # 정상: 요청 통과
    OPEN = "open"          # 차단: 요청 즉시 거부
    HALF_OPEN = "half_open"  # 테스트: 제한된 요청 통과


class CircuitBreaker:
    """
    서킷 브레이커 패턴 구현.

    설정:
    - failure_threshold: 실패 횟수 임계값 (이 수를 초과하면 Open)
    - recovery_timeout: Open -> Half-Open 전환 대기 시간 (초)
    - success_threshold: Half-Open에서 Closed 전환에 필요한 연속 성공 횟수
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 3,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._total_calls = 0
        self._total_failures = 0

    @property
    def state(self) -> CircuitState:
        """현재 상태 (타임아웃 기반 자동 전이 포함)"""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info(f"[서킷 브레이커 {self.name}] OPEN -> HALF_OPEN")
        return self._state

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        서킷 브레이커를 통한 함수 호출.
        Open 상태에서는 즉시 에러를 반환합니다.
        """
        current_state = self.state
        self._total_calls += 1

        if current_state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(
                f"서킷 브레이커 '{self.name}'가 열려있습니다. "
                f"{self.recovery_timeout}초 후 재시도하세요."
            )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """호출 성공 처리"""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info(f"[서킷 브레이커 {self.name}] HALF_OPEN -> CLOSED (복구)")
        else:
            self._failure_count = 0  # 성공 시 실패 카운터 리셋

    def _on_failure(self) -> None:
        """호출 실패 처리"""
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning(f"[서킷 브레이커 {self.name}] HALF_OPEN -> OPEN (테스트 실패)")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                f"[서킷 브레이커 {self.name}] CLOSED -> OPEN "
                f"(실패 {self._failure_count}/{self.failure_threshold})"
            )

    def get_stats(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "failure_rate": (
                round(self._total_failures / self._total_calls * 100, 1)
                if self._total_calls > 0 else 0
            ),
        }


class CircuitBreakerOpenError(Exception):
    pass


# 서비스별 서킷 브레이커 인스턴스
payment_breaker = CircuitBreaker("payment", failure_threshold=3, recovery_timeout=10)
inventory_breaker = CircuitBreaker("inventory", failure_threshold=5, recovery_timeout=15)


# ──────────────────────────────────────────────
# 3. 분산 트레이싱 컨텍스트
# ──────────────────────────────────────────────
class TraceContext:
    """
    분산 트레이싱 컨텍스트.
    W3C Trace Context 표준을 간단히 시뮬레이션합니다.
    """

    def __init__(self, trace_id: Optional[str] = None, parent_span_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4()).replace("-", "")[:32]
        self.span_id = str(uuid.uuid4()).replace("-", "")[:16]
        self.parent_span_id = parent_span_id

    def create_child(self) -> "TraceContext":
        """자식 스팬 생성"""
        return TraceContext(
            trace_id=self.trace_id,
            parent_span_id=self.span_id,
        )

    def to_headers(self) -> dict[str, str]:
        """HTTP 헤더로 변환 (W3C traceparent 형식)"""
        return {
            "traceparent": f"00-{self.trace_id}-{self.span_id}-01",
        }

    @classmethod
    def from_headers(cls, headers: dict) -> "TraceContext":
        """HTTP 헤더에서 복원"""
        traceparent = headers.get("traceparent", "")
        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 3:
                return cls(trace_id=parts[1], parent_span_id=parts[2])
        return cls()


# ──────────────────────────────────────────────
# 4. 서비스 시뮬레이션 (이벤트 핸들러)
# ──────────────────────────────────────────────
# 간단한 주문 데이터
orders: dict[int, dict] = {}
order_counter = 0


async def handle_order_created(event: Event) -> None:
    """결제 서비스: 주문 생성 이벤트 처리"""
    order_id = event.data.get("order_id")
    amount = event.data.get("amount", 0)
    logger.info(f"[결제 서비스] 주문 #{order_id} 결제 처리 중... (금액: {amount:,}원)")

    # 결제 처리 시뮬레이션 (일정 확률로 실패)
    await asyncio.sleep(0.1)

    import random
    if random.random() < 0.1:  # 10% 실패율
        raise Exception(f"결제 실패: 주문 #{order_id}")

    # 결제 완료 이벤트 발행
    await event_bus.publish(Event(
        type="payment.completed",
        data={"order_id": order_id, "amount": amount},
        source="payment-service",
        trace_id=event.trace_id,
    ))


async def handle_payment_completed(event: Event) -> None:
    """알림 서비스: 결제 완료 이벤트 처리"""
    order_id = event.data.get("order_id")
    logger.info(f"[알림 서비스] 주문 #{order_id} 결제 완료 알림 발송")

    if order_id in orders:
        orders[order_id]["status"] = "paid"


async def handle_order_for_inventory(event: Event) -> None:
    """재고 서비스: 주문 생성 시 재고 차감"""
    order_id = event.data.get("order_id")
    product = event.data.get("product", "")
    logger.info(f"[재고 서비스] 주문 #{order_id} 재고 예약: {product}")

    await asyncio.sleep(0.05)  # 처리 시뮬레이션


# 이벤트 핸들러 등록
event_bus.subscribe("order.created", handle_order_created)
event_bus.subscribe("order.created", handle_order_for_inventory)
event_bus.subscribe("payment.completed", handle_payment_completed)


# ──────────────────────────────────────────────
# 5. 외부 서비스 호출 시뮬레이션 (서킷 브레이커 적용)
# ──────────────────────────────────────────────
call_count = 0


async def call_payment_service(order_id: int, amount: int) -> dict:
    """결제 서비스 직접 호출 시뮬레이션 (일정 확률로 실패)"""
    global call_count
    call_count += 1

    # 10번 중 3번 실패 시뮬레이션
    import random
    if random.random() < 0.3:
        raise ConnectionError("결제 서비스 연결 실패")

    await asyncio.sleep(0.1)
    return {"status": "success", "transaction_id": f"txn-{order_id}-{call_count}"}


# ──────────────────────────────────────────────
# 6. Pydantic 스키마
# ──────────────────────────────────────────────
class OrderCreate(BaseModel):
    product: str
    amount: int
    customer: str


class OrderResponse(BaseModel):
    id: int
    product: str
    amount: int
    customer: str
    status: str
    created_at: str


# ──────────────────────────────────────────────
# 7. 트레이싱 미들웨어
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[시작] 이벤트 기반 마이크로서비스 준비 완료")
    yield
    logger.info("[종료] 앱 정리 완료")


app = FastAPI(
    title="이벤트 기반 서비스 통신",
    description="Pub/Sub, 서킷 브레이커, 분산 트레이싱",
    lifespan=lifespan,
)


@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    """
    분산 트레이싱 미들웨어.
    요청 헤더에서 trace context를 추출하거나 새로 생성하고,
    응답 헤더에 추가합니다.
    """
    trace = TraceContext.from_headers(dict(request.headers))
    request.state.trace = trace

    response = await call_next(request)

    response.headers["X-Trace-Id"] = trace.trace_id
    response.headers["X-Span-Id"] = trace.span_id

    return response


# ──────────────────────────────────────────────
# 8. API 엔드포인트
# ──────────────────────────────────────────────
@app.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(data: OrderCreate, request: Request):
    """
    주문 생성 (이벤트 기반).

    동작:
    1. 주문 레코드 생성
    2. 'order.created' 이벤트 발행
    3. 결제 서비스와 재고 서비스가 이벤트를 수신하여 처리
    """
    global order_counter
    order_counter += 1

    trace: TraceContext = request.state.trace

    order = {
        "id": order_counter,
        "product": data.product,
        "amount": data.amount,
        "customer": data.customer,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    orders[order_counter] = order

    # 이벤트 발행 (비동기 처리)
    event = Event(
        type="order.created",
        data={
            "order_id": order_counter,
            "product": data.product,
            "amount": data.amount,
            "customer": data.customer,
        },
        source="order-service",
        trace_id=trace.trace_id,
        span_id=trace.span_id,
    )
    delivered = await event_bus.publish(event)

    logger.info(
        f"주문 #{order_counter} 생성 완료 "
        f"(이벤트 {delivered}개 핸들러에 전달, trace: {trace.trace_id[:8]}...)"
    )

    return OrderResponse(**order)


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    """주문 조회"""
    order = orders.get(order_id)
    if not order:
        raise HTTPException(404, "주문을 찾을 수 없습니다")
    return OrderResponse(**order)


@app.post("/orders/{order_id}/pay")
async def pay_order(order_id: int, request: Request):
    """
    결제 처리 (서킷 브레이커 적용).
    결제 서비스가 불안정할 때 서킷 브레이커가 보호합니다.
    """
    order = orders.get(order_id)
    if not order:
        raise HTTPException(404, "주문을 찾을 수 없습니다")

    try:
        result = await payment_breaker.call(
            call_payment_service, order_id, order["amount"]
        )
        order["status"] = "paid"
        return {
            "order_id": order_id,
            "payment": result,
            "circuit_breaker": payment_breaker.get_stats(),
        }
    except CircuitBreakerOpenError as e:
        raise HTTPException(503, str(e))
    except ConnectionError as e:
        raise HTTPException(502, f"결제 서비스 오류: {e}")


@app.get("/events")
async def get_event_log(event_type: Optional[str] = None):
    """이벤트 로그 조회"""
    return event_bus.get_log(event_type)


@app.get("/circuit-breakers")
async def get_circuit_breaker_stats():
    """서킷 브레이커 상태 조회"""
    return {
        "payment": payment_breaker.get_stats(),
        "inventory": inventory_breaker.get_stats(),
    }


@app.post("/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(name: str):
    """서킷 브레이커 수동 리셋"""
    breakers = {"payment": payment_breaker, "inventory": inventory_breaker}
    breaker = breakers.get(name)
    if not breaker:
        raise HTTPException(404, f"서킷 브레이커 '{name}'을 찾을 수 없습니다")

    breaker._state = CircuitState.CLOSED
    breaker._failure_count = 0
    return {"message": f"서킷 브레이커 '{name}' 리셋 완료", "stats": breaker.get_stats()}


@app.get("/health")
async def health():
    """헬스 체크 (서킷 브레이커 상태 포함)"""
    payment_healthy = payment_breaker.state != CircuitState.OPEN
    inventory_healthy = inventory_breaker.state != CircuitState.OPEN

    all_healthy = payment_healthy and inventory_healthy
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": {
            "payment": "healthy" if payment_healthy else "unhealthy",
            "inventory": "healthy" if inventory_healthy else "unhealthy",
        },
    }
