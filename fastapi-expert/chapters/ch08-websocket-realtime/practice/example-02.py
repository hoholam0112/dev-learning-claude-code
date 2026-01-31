# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn
# 테스트: 브라우저에서 http://localhost:8000 접속
"""
SSE(Server-Sent Events)로 실시간 알림 시스템 구현.

주요 학습 포인트:
- SSE 프로토콜 구현 (text/event-stream)
- 여러 이벤트 타입 지원 (notification, alert, metrics)
- 알림 채널별 구독
- 클라이언트 자동 재연결 (EventSource 내장)
- SSE vs WebSocket 비교 체험
"""
import asyncio
import json
import random
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(title="SSE 실시간 알림 시스템")


# ──────────────────────────────────────────────
# 1. 알림 관리자
# ──────────────────────────────────────────────
class NotificationManager:
    """
    SSE 기반 알림 관리자.
    채널별로 구독자를 관리하고, 이벤트를 전달합니다.

    SSE 형식:
    event: <이벤트 타입>
    data: <JSON 데이터>
    id: <이벤트 ID>
    retry: <재연결 대기 시간 ms>
    """

    def __init__(self):
        # 채널별 이벤트 큐: {channel: [asyncio.Queue, ...]}
        self.subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self.event_counter = 0
        self.event_history: list[dict] = []  # 최근 이벤트 보관 (재연결 시 복구용)
        self.max_history = 100

    def subscribe(self, channel: str) -> asyncio.Queue:
        """채널 구독: 이벤트를 받을 큐를 반환"""
        queue: asyncio.Queue = asyncio.Queue(maxsize=50)
        self.subscribers[channel].append(queue)
        return queue

    def unsubscribe(self, channel: str, queue: asyncio.Queue) -> None:
        """채널 구독 해제"""
        if channel in self.subscribers:
            self.subscribers[channel] = [
                q for q in self.subscribers[channel] if q is not queue
            ]

    async def publish(
        self,
        channel: str,
        event_type: str,
        data: dict,
    ) -> int:
        """
        이벤트 발행: 해당 채널의 모든 구독자에게 전달.
        큐가 가득 찬 구독자는 건너뛰기 (느린 클라이언트 보호).
        """
        self.event_counter += 1
        event = {
            "id": self.event_counter,
            "type": event_type,
            "channel": channel,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 이벤트 히스토리 보관
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # 구독자에게 전달
        delivered = 0
        dead_queues = []

        for queue in self.subscribers.get(channel, []):
            try:
                queue.put_nowait(event)
                delivered += 1
            except asyncio.QueueFull:
                # 큐가 가득 찬 경우 건너뛰기
                dead_queues.append(queue)

        # 응답 없는 구독자 정리
        for dq in dead_queues:
            self.subscribers[channel] = [
                q for q in self.subscribers[channel] if q is not dq
            ]

        return delivered

    def get_history(
        self, channel: Optional[str] = None, last_id: int = 0
    ) -> list[dict]:
        """
        이벤트 히스토리 조회 (재연결 시 놓친 이벤트 복구용).
        Last-Event-ID 이후의 이벤트만 반환합니다.
        """
        events = self.event_history
        if channel:
            events = [e for e in events if e["channel"] == channel]
        if last_id > 0:
            events = [e for e in events if e["id"] > last_id]
        return events

    def get_stats(self) -> dict:
        """알림 시스템 통계"""
        return {
            "total_events": self.event_counter,
            "channels": {
                ch: len(subs) for ch, subs in self.subscribers.items()
            },
            "history_size": len(self.event_history),
        }


notification_manager = NotificationManager()


# ──────────────────────────────────────────────
# 2. SSE 이벤트 생성기
# ──────────────────────────────────────────────
async def sse_event_stream(
    channel: str,
    last_event_id: int = 0,
) -> AsyncGenerator[str, None]:
    """
    SSE 이벤트 스트림 생성기.

    SSE 프로토콜 형식:
    - event: <타입> (선택적)
    - data: <내용> (필수)
    - id: <이벤트 ID> (선택적, 재연결 시 복구용)
    - retry: <ms> (선택적, 재연결 대기 시간)
    - 빈 줄로 이벤트 구분
    """
    # 재연결 대기 시간 설정 (3초)
    yield f"retry: 3000\n\n"

    # 놓친 이벤트 복구 (Last-Event-ID 기반)
    if last_event_id > 0:
        missed = notification_manager.get_history(channel, last_event_id)
        for event in missed:
            yield _format_sse_event(event)

    # 구독 시작
    queue = notification_manager.subscribe(channel)
    try:
        while True:
            try:
                # 30초 타임아웃으로 이벤트 대기
                event = await asyncio.wait_for(queue.get(), timeout=30)
                yield _format_sse_event(event)
            except asyncio.TimeoutError:
                # 하트비트: 연결 유지를 위한 빈 코멘트
                yield f": heartbeat {datetime.now(timezone.utc).isoformat()}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        notification_manager.unsubscribe(channel, queue)


def _format_sse_event(event: dict) -> str:
    """이벤트를 SSE 형식으로 포맷팅"""
    lines = []
    if "type" in event:
        lines.append(f"event: {event['type']}")
    lines.append(f"data: {json.dumps(event['data'], ensure_ascii=False)}")
    if "id" in event:
        lines.append(f"id: {event['id']}")
    lines.append("")  # 이벤트 구분 빈 줄
    lines.append("")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 3. 시뮬레이션 이벤트 생성 태스크
# ──────────────────────────────────────────────
async def simulate_events():
    """백그라운드 태스크: 다양한 이벤트를 주기적으로 생성"""
    while True:
        # 시스템 메트릭 이벤트
        await notification_manager.publish(
            "metrics",
            "system_metrics",
            {
                "cpu": round(random.uniform(10, 95), 1),
                "memory": round(random.uniform(30, 85), 1),
                "disk": round(random.uniform(40, 90), 1),
                "network_in": random.randint(100, 10000),
                "network_out": random.randint(50, 5000),
            },
        )

        # 랜덤 알림 이벤트 (30% 확률)
        if random.random() < 0.3:
            alerts = [
                {"level": "info", "message": "배포가 완료되었습니다"},
                {"level": "warning", "message": "CPU 사용률이 80%를 초과했습니다"},
                {"level": "error", "message": "데이터베이스 연결 실패"},
                {"level": "info", "message": "새 사용자가 가입했습니다"},
                {"level": "warning", "message": "디스크 용량이 90%를 초과했습니다"},
            ]
            alert = random.choice(alerts)
            await notification_manager.publish("alerts", "alert", alert)

        # 주문 이벤트 (20% 확률)
        if random.random() < 0.2:
            await notification_manager.publish(
                "orders",
                "new_order",
                {
                    "order_id": random.randint(10000, 99999),
                    "customer": f"고객_{random.randint(1, 100)}",
                    "amount": random.randint(10000, 500000),
                },
            )

        await asyncio.sleep(2)  # 2초 간격


# 앱 시작 시 시뮬레이션 태스크 실행
@app.on_event("startup")
async def startup():
    asyncio.create_task(simulate_events())


# ──────────────────────────────────────────────
# 4. API 엔드포인트
# ──────────────────────────────────────────────
@app.get("/sse/{channel}")
async def subscribe_channel(
    channel: str,
    request: Request,
    last_event_id: int = Query(0, alias="lastEventId"),
):
    """
    SSE 채널 구독.

    사용 가능한 채널:
    - metrics: 시스템 메트릭 (2초 간격)
    - alerts: 시스템 알림 (랜덤)
    - orders: 주문 이벤트 (랜덤)

    테스트:
    curl -N http://localhost:8000/sse/metrics
    """
    # Last-Event-ID 헤더 확인 (브라우저 재연결 시)
    header_last_id = request.headers.get("last-event-id")
    if header_last_id:
        last_event_id = int(header_last_id)

    return StreamingResponse(
        sse_event_stream(channel, last_event_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 버퍼링 비활성화
        },
    )


@app.post("/notifications/publish")
async def publish_notification(
    channel: str = Query(...),
    event_type: str = Query("notification"),
    message: str = Query(...),
):
    """수동으로 알림 발행"""
    delivered = await notification_manager.publish(
        channel,
        event_type,
        {"message": message, "source": "manual"},
    )
    return {"delivered_to": delivered, "channel": channel}


@app.get("/notifications/stats")
async def get_notification_stats():
    """알림 시스템 통계"""
    return notification_manager.get_stats()


@app.get("/notifications/history")
async def get_notification_history(
    channel: Optional[str] = None,
    last_id: int = Query(0),
):
    """이벤트 히스토리 조회"""
    return notification_manager.get_history(channel, last_id)


# ──────────────────────────────────────────────
# 5. HTML 테스트 클라이언트
# ──────────────────────────────────────────────
@app.get("/")
async def get_dashboard():
    """실시간 대시보드 HTML 클라이언트"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>SSE 실시간 대시보드</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f23; color: #ccc; padding: 20px; }
        h1 { color: #00d4aa; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 1200px; }
        .panel { background: #1a1a3e; border-radius: 8px; padding: 20px; }
        .panel h2 { color: #4fc3f7; margin-bottom: 15px; font-size: 1.1em; }
        .metric { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2a2a4e; }
        .metric-value { font-weight: bold; font-size: 1.2em; }
        .alert-item { padding: 10px; margin: 5px 0; border-radius: 4px; font-size: 0.9em; }
        .alert-info { background: #1a3a5c; border-left: 3px solid #4fc3f7; }
        .alert-warning { background: #3a3a1c; border-left: 3px solid #ffd54f; }
        .alert-error { background: #3a1a1c; border-left: 3px solid #ef5350; }
        .order-item { padding: 8px; margin: 4px 0; background: #1a2a3e; border-radius: 4px; }
        .status { padding: 5px 10px; border-radius: 12px; font-size: 0.8em; display: inline-block; }
        .status.connected { background: #1b5e20; color: #a5d6a7; }
        .status.disconnected { background: #b71c1c; color: #ef9a9a; }
        #alerts-list, #orders-list { max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>SSE 실시간 대시보드
        <span class="status disconnected" id="status">연결 중...</span>
    </h1>

    <div class="grid">
        <div class="panel">
            <h2>시스템 메트릭</h2>
            <div class="metric">
                <span>CPU</span>
                <span class="metric-value" id="cpu">-</span>
            </div>
            <div class="metric">
                <span>메모리</span>
                <span class="metric-value" id="memory">-</span>
            </div>
            <div class="metric">
                <span>디스크</span>
                <span class="metric-value" id="disk">-</span>
            </div>
            <div class="metric">
                <span>네트워크 In</span>
                <span class="metric-value" id="net-in">-</span>
            </div>
            <div class="metric">
                <span>네트워크 Out</span>
                <span class="metric-value" id="net-out">-</span>
            </div>
        </div>

        <div class="panel">
            <h2>알림</h2>
            <div id="alerts-list"></div>
        </div>

        <div class="panel" style="grid-column: span 2;">
            <h2>최근 주문</h2>
            <div id="orders-list"></div>
        </div>
    </div>

<script>
// 메트릭 SSE 연결
const metricsSource = new EventSource('/sse/metrics');
metricsSource.addEventListener('system_metrics', (e) => {
    const data = JSON.parse(e.data);
    document.getElementById('cpu').textContent = data.cpu + '%';
    document.getElementById('memory').textContent = data.memory + '%';
    document.getElementById('disk').textContent = data.disk + '%';
    document.getElementById('net-in').textContent = data.network_in + ' KB/s';
    document.getElementById('net-out').textContent = data.network_out + ' KB/s';
});

metricsSource.onopen = () => {
    const s = document.getElementById('status');
    s.textContent = '연결됨';
    s.className = 'status connected';
};
metricsSource.onerror = () => {
    const s = document.getElementById('status');
    s.textContent = '재연결 중...';
    s.className = 'status disconnected';
};

// 알림 SSE 연결
const alertsSource = new EventSource('/sse/alerts');
alertsSource.addEventListener('alert', (e) => {
    const data = JSON.parse(e.data);
    const list = document.getElementById('alerts-list');
    const div = document.createElement('div');
    div.className = 'alert-item alert-' + data.level;
    div.textContent = `[${data.level.toUpperCase()}] ${data.message}`;
    list.insertBefore(div, list.firstChild);
    if (list.children.length > 20) list.removeChild(list.lastChild);
});

// 주문 SSE 연결
const ordersSource = new EventSource('/sse/orders');
ordersSource.addEventListener('new_order', (e) => {
    const data = JSON.parse(e.data);
    const list = document.getElementById('orders-list');
    const div = document.createElement('div');
    div.className = 'order-item';
    div.textContent = `주문 #${data.order_id} - ${data.customer} - ${data.amount.toLocaleString()}원`;
    list.insertBefore(div, list.firstChild);
    if (list.children.length > 15) list.removeChild(list.lastChild);
});
</script>
</body>
</html>
    """)
