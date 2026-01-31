# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn pyjwt
"""
챕터 08 연습문제 모범 답안.

문제 1: 방(Room) 기반 채팅 시스템
문제 2: JWT 인증이 포함된 WebSocket 연결
문제 3: 실시간 대시보드 데이터 스트리밍 (SSE)
"""
import asyncio
import json
import logging
import random
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# JWT 라이브러리 (없으면 간단한 대체 구현 사용)
try:
    import jwt as pyjwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

JWT_SECRET = "super-secret-key-for-demo-only"
JWT_ALGORITHM = "HS256"

app = FastAPI(title="챕터 08 모범 답안")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 1: 방(Room) 기반 채팅 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class RoomInfo:
    """방 정보"""
    def __init__(self, name: str, max_users: int = 50):
        self.name = name
        self.max_users = max_users
        self.created_at = datetime.now(timezone.utc)
        self.message_count = 0
        self.history: deque[dict] = deque(maxlen=50)


class RoomManager:
    """
    방(Room) 기반 채팅 관리자.

    기능:
    - 방 생성/삭제
    - 입장/퇴장 (인원 제한)
    - 방별 브로드캐스트
    - 메시지 히스토리
    - 귓속말
    """

    def __init__(self):
        self.rooms: dict[str, RoomInfo] = {}
        self.room_members: dict[str, dict[WebSocket, str]] = defaultdict(dict)  # {room: {ws: username}}
        self.user_connections: dict[str, WebSocket] = {}  # {username: ws}
        self.ws_username: dict[WebSocket, str] = {}  # {ws: username}

        # 기본 방 생성
        self.create_room("general", max_users=100)
        self.create_room("tech", max_users=30)
        self.create_room("random", max_users=30)

    def create_room(self, name: str, max_users: int = 50) -> RoomInfo:
        """방 생성"""
        if name not in self.rooms:
            self.rooms[name] = RoomInfo(name, max_users)
        return self.rooms[name]

    async def connect(self, websocket: WebSocket, username: str) -> None:
        """사용자 연결"""
        await websocket.accept()
        self.user_connections[username] = websocket
        self.ws_username[websocket] = username

    async def disconnect(self, websocket: WebSocket) -> None:
        """사용자 연결 해제 (모든 방에서 퇴장)"""
        username = self.ws_username.pop(websocket, None)
        if username:
            self.user_connections.pop(username, None)

        # 모든 방에서 퇴장
        for room_name in list(self.room_members.keys()):
            if websocket in self.room_members[room_name]:
                del self.room_members[room_name][websocket]
                await self.send_to_room(
                    room_name,
                    {
                        "type": "system",
                        "message": f"{username}님이 퇴장했습니다.",
                        "room": room_name,
                        "online_users": list(self.room_members[room_name].values()),
                    },
                )

    async def join_room(self, websocket: WebSocket, room_name: str) -> bool:
        """방 입장 (인원 초과 시 거부)"""
        username = self.ws_username.get(websocket, "익명")

        if room_name not in self.rooms:
            await self._send(websocket, {
                "type": "error",
                "message": f"방 '{room_name}'이 존재하지 않습니다.",
            })
            return False

        room = self.rooms[room_name]
        if len(self.room_members[room_name]) >= room.max_users:
            await self._send(websocket, {
                "type": "error",
                "message": f"방 '{room_name}'이 가득 찼습니다 (최대 {room.max_users}명).",
            })
            return False

        self.room_members[room_name][websocket] = username

        # 입장 확인 + 히스토리 전송
        await self._send(websocket, {
            "type": "room_joined",
            "room": room_name,
            "history": list(room.history),
            "online_users": list(self.room_members[room_name].values()),
        })

        # 다른 사용자에게 알림
        await self.send_to_room(
            room_name,
            {
                "type": "system",
                "message": f"{username}님이 입장했습니다.",
                "room": room_name,
                "online_users": list(self.room_members[room_name].values()),
            },
            exclude=websocket,
        )
        return True

    async def leave_room(self, websocket: WebSocket, room_name: str) -> None:
        """방 퇴장"""
        username = self.room_members.get(room_name, {}).pop(websocket, None)
        if username:
            await self.send_to_room(
                room_name,
                {
                    "type": "system",
                    "message": f"{username}님이 나갔습니다.",
                    "room": room_name,
                    "online_users": list(self.room_members[room_name].values()),
                },
            )

    async def send_to_room(
        self,
        room_name: str,
        message: dict,
        exclude: Optional[WebSocket] = None,
    ) -> None:
        """방 내 브로드캐스트"""
        disconnected = []
        for ws in list(self.room_members.get(room_name, {}).keys()):
            if ws == exclude:
                continue
            try:
                await self._send(ws, message)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            await self.disconnect(ws)

    async def send_chat(
        self, websocket: WebSocket, room_name: str, content: str
    ) -> None:
        """채팅 메시지 전송"""
        username = self.ws_username.get(websocket, "익명")
        message = {
            "type": "chat",
            "room": room_name,
            "username": username,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 히스토리 저장
        if room_name in self.rooms:
            self.rooms[room_name].history.append(message)
            self.rooms[room_name].message_count += 1

        # 브로드캐스트 (보낸 사람에게도 전송)
        await self.send_to_room(room_name, message)

    async def send_whisper(
        self, from_ws: WebSocket, to_username: str, content: str
    ) -> None:
        """귓속말"""
        from_username = self.ws_username.get(from_ws, "익명")
        to_ws = self.user_connections.get(to_username)

        if not to_ws:
            await self._send(from_ws, {
                "type": "error",
                "message": f"'{to_username}' 사용자를 찾을 수 없습니다.",
            })
            return

        whisper_msg = {
            "type": "whisper",
            "from": from_username,
            "to": to_username,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self._send(to_ws, whisper_msg)
        await self._send(from_ws, {**whisper_msg, "type": "whisper_sent"})

    async def _send(self, ws: WebSocket, data: dict) -> None:
        """개별 메시지 전송"""
        await ws.send_text(json.dumps(data, ensure_ascii=False))

    def get_room_list(self) -> list[dict]:
        """전체 방 목록"""
        return [
            {
                "name": room.name,
                "max_users": room.max_users,
                "online_count": len(self.room_members.get(room.name, {})),
                "message_count": room.message_count,
            }
            for room in self.rooms.values()
        ]


room_manager = RoomManager()


@app.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    username: str = Query(...),
):
    """방 기반 채팅 WebSocket"""
    await room_manager.connect(websocket, username)

    try:
        # 기본 방 입장
        await room_manager.join_room(websocket, "general")

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                room = data.get("room", "general")
                content = data.get("content", "")
                await room_manager.send_chat(websocket, room, content)

            elif msg_type == "join":
                room = data.get("room", "general")
                await room_manager.join_room(websocket, room)

            elif msg_type == "leave":
                room = data.get("room", "general")
                await room_manager.leave_room(websocket, room)

            elif msg_type == "room_list":
                await room_manager._send(websocket, {
                    "type": "room_list",
                    "rooms": room_manager.get_room_list(),
                })

            elif msg_type == "whisper":
                to = data.get("to", "")
                content = data.get("content", "")
                await room_manager.send_whisper(websocket, to, content)

    except WebSocketDisconnect:
        pass
    except json.JSONDecodeError:
        pass
    finally:
        await room_manager.disconnect(websocket)


@app.get("/rooms")
async def list_rooms():
    """방 목록 REST API"""
    return room_manager.get_room_list()


class RoomCreate(BaseModel):
    name: str
    max_users: int = 50


@app.post("/rooms", status_code=201)
async def create_room(data: RoomCreate):
    """방 생성 REST API"""
    if data.name in room_manager.rooms:
        raise HTTPException(409, "이미 존재하는 방입니다")
    room = room_manager.create_room(data.name, data.max_users)
    return {"name": room.name, "max_users": room.max_users}


@app.get("/rooms/{name}/history")
async def get_room_history(name: str):
    """방 메시지 히스토리"""
    if name not in room_manager.rooms:
        raise HTTPException(404, "방을 찾을 수 없습니다")
    return list(room_manager.rooms[name].history)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 2: JWT 인증이 포함된 WebSocket 연결
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 간단한 사용자 저장소
fake_users = {
    "admin": {"password": "secret", "role": "admin"},
    "user1": {"password": "password", "role": "user"},
}

# 티켓 저장소
ticket_store: dict[str, dict] = {}

security = HTTPBearer()


def create_jwt_token(username: str, role: str) -> str:
    """JWT 토큰 생성"""
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    if HAS_JWT:
        return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    else:
        # JWT 없을 때 간단한 대체
        import base64
        data = json.dumps({"sub": username, "role": role, "exp": time.time() + 3600})
        return base64.urlsafe_b64encode(data.encode()).decode()


def verify_jwt_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증"""
    try:
        if HAS_JWT:
            payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        else:
            import base64
            data = json.loads(base64.urlsafe_b64decode(token.encode()))
            if data.get("exp", 0) < time.time():
                return None
            return data
    except Exception:
        return None


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/auth/login")
async def login(data: LoginRequest):
    """사용자 로그인 -> JWT 토큰 발급"""
    user = fake_users.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(401, "잘못된 인증 정보입니다")

    token = create_jwt_token(data.username, user["role"])
    return {"access_token": token, "token_type": "bearer"}


@app.post("/auth/ws-ticket")
async def create_ws_ticket(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """JWT로 1회용 WebSocket 티켓 발급"""
    payload = verify_jwt_token(credentials.credentials)
    if not payload:
        raise HTTPException(401, "유효하지 않은 토큰입니다")

    ticket = secrets.token_urlsafe(32)
    ticket_store[ticket] = {
        "username": payload["sub"],
        "role": payload.get("role", "user"),
        "created_at": time.time(),
    }

    return {"ticket": ticket, "expires_in": 30}


@app.websocket("/ws/auth")
async def authenticated_websocket(
    websocket: WebSocket,
    ticket: str = Query(...),
):
    """티켓 기반 인증 WebSocket 연결"""
    # 티켓 검증
    user_info = ticket_store.pop(ticket, None)  # 1회용: 사용 후 삭제

    if not user_info:
        await websocket.close(code=4001, reason="유효하지 않은 티켓입니다")
        return

    # 만료 확인 (30초)
    if time.time() - user_info["created_at"] > 30:
        await websocket.close(code=4001, reason="만료된 티켓입니다")
        return

    # 인증 성공
    await websocket.accept()
    username = user_info["username"]

    await websocket.send_text(json.dumps({
        "type": "authenticated",
        "username": username,
        "role": user_info["role"],
        "message": f"{username}님, 인증된 연결이 수립되었습니다.",
    }))

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            await websocket.send_text(json.dumps({
                "type": "echo",
                "from": username,
                "content": msg.get("content", ""),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }))
    except WebSocketDisconnect:
        logger.info(f"인증 사용자 '{username}' 연결 종료")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 3: 실시간 대시보드 데이터 스트리밍 (SSE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class DashboardMetrics:
    """대시보드 메트릭 관리자"""

    def __init__(self):
        self.subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self.event_counter = 0
        self.event_history: deque[dict] = deque(maxlen=200)
        self.client_count = 0

        # 현재 메트릭 값 (이전 값 기반 변화)
        self._cpu = 50.0
        self._memory = 60.0
        self._disk = 45.0
        self._requests = 0
        self._active_users = 200

    def subscribe(self, channel: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self.subscribers[channel].append(queue)
        self.client_count += 1
        return queue

    def unsubscribe(self, channel: str, queue: asyncio.Queue) -> None:
        self.subscribers[channel] = [
            q for q in self.subscribers[channel] if q is not queue
        ]
        self.client_count = max(0, self.client_count - 1)

    async def publish(self, channel: str, event_type: str, data: dict) -> None:
        self.event_counter += 1
        event = {
            "id": self.event_counter,
            "type": event_type,
            "channel": channel,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.event_history.append(event)

        # 해당 채널 + "all" 구독자에게 전달
        for ch in [channel, "all"]:
            dead_queues = []
            for queue in self.subscribers.get(ch, []):
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    dead_queues.append(queue)
            for dq in dead_queues:
                self.subscribers[ch] = [
                    q for q in self.subscribers[ch] if q is not dq
                ]

    def get_history(self, channel: Optional[str], last_id: int) -> list[dict]:
        events = list(self.event_history)
        if channel and channel != "all":
            events = [e for e in events if e["channel"] == channel]
        if last_id > 0:
            events = [e for e in events if e["id"] > last_id]
        return events

    async def generate_system_metrics(self) -> None:
        """시스템 메트릭 생성 (1초 간격)"""
        while True:
            # 이전 값 기반으로 부드럽게 변화
            self._cpu = max(5, min(95, self._cpu + random.uniform(-5, 5)))
            self._memory = max(20, min(95, self._memory + random.uniform(-2, 2)))
            self._disk = max(30, min(95, self._disk + random.uniform(-0.5, 0.5)))

            await self.publish("system", "system_metrics", {
                "cpu": round(self._cpu, 1),
                "memory": round(self._memory, 1),
                "disk": round(self._disk, 1),
            })
            await asyncio.sleep(1)

    async def generate_api_metrics(self) -> None:
        """API 메트릭 생성 (5초 간격)"""
        while True:
            self._requests += random.randint(50, 200)
            await self.publish("api", "api_metrics", {
                "requests": self._requests,
                "avg_response_ms": round(random.uniform(10, 100), 1),
                "error_rate": round(random.uniform(0, 3), 2),
                "active_connections": random.randint(50, 500),
            })
            await asyncio.sleep(5)

    async def generate_business_metrics(self) -> None:
        """비즈니스 메트릭 생성 (10초 간격)"""
        while True:
            self._active_users = max(
                50, min(1000, self._active_users + random.randint(-20, 20))
            )
            await self.publish("business", "business_metrics", {
                "active_users": self._active_users,
                "revenue": random.randint(500000, 5000000),
                "orders": random.randint(10, 100),
                "conversion_rate": round(random.uniform(1, 8), 2),
            })
            await asyncio.sleep(10)


dashboard = DashboardMetrics()


@app.on_event("startup")
async def startup_dashboard():
    """대시보드 메트릭 생성 태스크 시작"""
    asyncio.create_task(dashboard.generate_system_metrics())
    asyncio.create_task(dashboard.generate_api_metrics())
    asyncio.create_task(dashboard.generate_business_metrics())


async def dashboard_sse_stream(
    channel: str, last_event_id: int
) -> AsyncGenerator[str, None]:
    """대시보드 SSE 스트림"""
    yield f"retry: 3000\n\n"

    # 놓친 이벤트 복구
    if last_event_id > 0:
        missed = dashboard.get_history(channel, last_event_id)
        for event in missed:
            yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\nid: {event['id']}\n\n"

    queue = dashboard.subscribe(channel)
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\nid: {event['id']}\n\n"
            except asyncio.TimeoutError:
                yield f": heartbeat {datetime.now(timezone.utc).isoformat()}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        dashboard.unsubscribe(channel, queue)


@app.get("/sse/{channel}")
async def subscribe_sse(
    channel: str,
    request: Request,
    last_event_id: int = Query(0, alias="lastEventId"),
):
    """SSE 채널 구독"""
    valid_channels = {"system", "api", "business", "all"}
    if channel not in valid_channels:
        raise HTTPException(400, f"유효하지 않은 채널: {channel}. 사용 가능: {valid_channels}")

    header_last_id = request.headers.get("last-event-id")
    if header_last_id:
        last_event_id = int(header_last_id)

    return StreamingResponse(
        dashboard_sse_stream(channel, last_event_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """대시보드 통계"""
    return {
        "connected_clients": dashboard.client_count,
        "total_events": dashboard.event_counter,
        "channels": {
            ch: len(subs) for ch, subs in dashboard.subscribers.items()
        },
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HTML 테스트 페이지
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.get("/")
async def index():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>챕터 08 모범 답안 - 실시간 시스템</title>
    <style>
        body { font-family: sans-serif; background: #111; color: #ddd; padding: 20px; max-width: 900px; margin: auto; }
        h1 { color: #4fc3f7; }
        h2 { color: #81c784; margin-top: 30px; }
        a { color: #ff8a65; }
        .card { background: #1e1e2e; padding: 15px; border-radius: 8px; margin: 10px 0; }
        code { background: #2a2a3e; padding: 2px 6px; border-radius: 3px; }
        .gauge { height: 20px; background: #333; border-radius: 10px; overflow: hidden; margin: 5px 0; }
        .gauge-fill { height: 100%; border-radius: 10px; transition: width 0.5s; }
        .metric-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; }
    </style>
</head>
<body>
    <h1>챕터 08: WebSocket과 실시간 통신</h1>

    <h2>실시간 시스템 메트릭 (SSE)</h2>
    <div class="card">
        <div class="metric-row">
            <span>CPU</span><span id="cpu">-</span>
        </div>
        <div class="gauge"><div class="gauge-fill" id="cpu-bar" style="width:0%;background:#4fc3f7;"></div></div>
        <div class="metric-row">
            <span>메모리</span><span id="mem">-</span>
        </div>
        <div class="gauge"><div class="gauge-fill" id="mem-bar" style="width:0%;background:#81c784;"></div></div>
        <div class="metric-row">
            <span>디스크</span><span id="disk">-</span>
        </div>
        <div class="gauge"><div class="gauge-fill" id="disk-bar" style="width:0%;background:#ff8a65;"></div></div>
    </div>

    <h2>테스트 링크</h2>
    <div class="card">
        <p><strong>채팅:</strong> 새 탭에서 열어 테스트하세요</p>
        <ul>
            <li>WebSocket 채팅: <code>ws://localhost:8000/ws/chat?username=테스트</code></li>
            <li>방 목록: <a href="/rooms">/rooms</a></li>
        </ul>
        <p><strong>인증:</strong></p>
        <ul>
            <li>로그인: <code>POST /auth/login {"username":"admin","password":"secret"}</code></li>
            <li>티켓 발급: <code>POST /auth/ws-ticket (Bearer 토큰 필요)</code></li>
        </ul>
        <p><strong>SSE:</strong></p>
        <ul>
            <li>시스템 메트릭: <a href="/sse/system">/sse/system</a></li>
            <li>API 메트릭: <a href="/sse/api">/sse/api</a></li>
            <li>비즈니스 메트릭: <a href="/sse/business">/sse/business</a></li>
            <li>전체: <a href="/sse/all">/sse/all</a></li>
            <li>대시보드 통계: <a href="/dashboard/stats">/dashboard/stats</a></li>
        </ul>
    </div>

<script>
const src = new EventSource('/sse/system');
src.addEventListener('system_metrics', (e) => {
    const d = JSON.parse(e.data);
    document.getElementById('cpu').textContent = d.cpu + '%';
    document.getElementById('mem').textContent = d.memory + '%';
    document.getElementById('disk').textContent = d.disk + '%';
    document.getElementById('cpu-bar').style.width = d.cpu + '%';
    document.getElementById('mem-bar').style.width = d.memory + '%';
    document.getElementById('disk-bar').style.width = d.disk + '%';
});
</script>
</body>
</html>
    """)
