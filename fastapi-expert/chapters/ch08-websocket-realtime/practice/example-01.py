# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn
# 테스트: 브라우저에서 http://localhost:8000 접속
"""
실시간 채팅 서버 (ConnectionManager 패턴).

주요 학습 포인트:
- ConnectionManager 패턴으로 WebSocket 연결 관리
- 방(Room) 기반 브로드캐스트 시스템
- 하트비트(Heartbeat)로 끊어진 연결 감지
- HTML 클라이언트 내장 (테스트용)
"""
import asyncio
import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse

app = FastAPI(title="실시간 채팅 서버")


# ──────────────────────────────────────────────
# 1. ConnectionManager (방 기반)
# ──────────────────────────────────────────────
class ConnectionManager:
    """
    방(Room) 기반 WebSocket 연결 관리자.

    기능:
    - 사용자 연결/해제 관리
    - 방 입장/퇴장
    - 방 단위 브로드캐스트
    - 전체 브로드캐스트
    - 연결 통계
    """

    def __init__(self):
        # 방별 연결 관리: {room_name: {websocket: user_info}}
        self.rooms: dict[str, dict[WebSocket, dict]] = defaultdict(dict)
        # 사용자별 연결 관리: {websocket: {rooms, username, connected_at}}
        self.connections: dict[WebSocket, dict] = {}

    async def connect(
        self, websocket: WebSocket, username: str, room: str = "general"
    ) -> None:
        """사용자 연결 및 방 입장"""
        await websocket.accept()

        user_info = {
            "username": username,
            "rooms": {room},
            "connected_at": time.time(),
        }
        self.connections[websocket] = user_info
        self.rooms[room][websocket] = user_info

        # 입장 알림
        await self.broadcast_to_room(
            room,
            {
                "type": "system",
                "message": f"{username}님이 입장했습니다.",
                "room": room,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "online_count": len(self.rooms[room]),
            },
            exclude=websocket,
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        """사용자 연결 해제 및 모든 방에서 퇴장"""
        user_info = self.connections.pop(websocket, None)
        if not user_info:
            return

        username = user_info["username"]

        # 모든 방에서 퇴장
        for room in user_info["rooms"]:
            self.rooms[room].pop(websocket, None)

            # 퇴장 알림
            await self.broadcast_to_room(
                room,
                {
                    "type": "system",
                    "message": f"{username}님이 퇴장했습니다.",
                    "room": room,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "online_count": len(self.rooms[room]),
                },
            )

            # 빈 방 정리
            if not self.rooms[room]:
                del self.rooms[room]

    async def join_room(self, websocket: WebSocket, room: str) -> None:
        """방 입장"""
        user_info = self.connections.get(websocket)
        if not user_info:
            return

        user_info["rooms"].add(room)
        self.rooms[room][websocket] = user_info

        await self.broadcast_to_room(
            room,
            {
                "type": "system",
                "message": f"{user_info['username']}님이 {room} 방에 입장했습니다.",
                "room": room,
                "online_count": len(self.rooms[room]),
            },
            exclude=websocket,
        )

    async def leave_room(self, websocket: WebSocket, room: str) -> None:
        """방 퇴장"""
        user_info = self.connections.get(websocket)
        if not user_info:
            return

        user_info["rooms"].discard(room)
        self.rooms[room].pop(websocket, None)

        await self.broadcast_to_room(
            room,
            {
                "type": "system",
                "message": f"{user_info['username']}님이 {room} 방을 나갔습니다.",
                "room": room,
                "online_count": len(self.rooms[room]),
            },
        )

    async def broadcast_to_room(
        self,
        room: str,
        message: dict,
        exclude: Optional[WebSocket] = None,
    ) -> None:
        """방 내 모든 사용자에게 메시지 전송 (안전한 브로드캐스트)"""
        disconnected = []
        message_text = json.dumps(message, ensure_ascii=False)

        for ws in list(self.rooms.get(room, {}).keys()):
            if ws == exclude:
                continue
            try:
                await ws.send_text(message_text)
            except Exception:
                disconnected.append(ws)

        # 끊어진 연결 정리
        for ws in disconnected:
            await self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, message: dict) -> None:
        """특정 사용자에게 개인 메시지 전송"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception:
            await self.disconnect(websocket)

    def get_stats(self) -> dict:
        """연결 통계"""
        return {
            "total_connections": len(self.connections),
            "rooms": {
                room: {
                    "user_count": len(members),
                    "users": [
                        info["username"] for info in members.values()
                    ],
                }
                for room, members in self.rooms.items()
            },
        }


manager = ConnectionManager()


# ──────────────────────────────────────────────
# 2. WebSocket 엔드포인트
# ──────────────────────────────────────────────
@app.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    username: str = Query(...),
    room: str = Query("general"),
):
    """
    채팅 WebSocket 엔드포인트.

    메시지 형식:
    - 일반 메시지: {"type": "message", "content": "안녕하세요"}
    - 방 입장: {"type": "join", "room": "tech"}
    - 방 퇴장: {"type": "leave", "room": "tech"}
    - 하트비트: {"type": "pong"}

    연결: ws://localhost:8000/ws/chat?username=홍길동&room=general
    """
    await manager.connect(websocket, username, room)

    # 하트비트 태스크 시작
    heartbeat_task = asyncio.create_task(
        _heartbeat_loop(websocket, interval=30)
    )

    try:
        # 입장 환영 메시지
        await manager.send_personal(websocket, {
            "type": "welcome",
            "message": f"{room} 방에 오신 것을 환영합니다!",
            "room": room,
            "online_count": len(manager.rooms[room]),
        })

        # 메시지 수신 루프
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # 단순 텍스트 메시지
                data = {"type": "message", "content": raw}

            msg_type = data.get("type", "message")

            if msg_type == "message":
                # 일반 채팅 메시지
                content = data.get("content", "")
                target_room = data.get("room", room)

                await manager.broadcast_to_room(
                    target_room,
                    {
                        "type": "message",
                        "username": username,
                        "content": content,
                        "room": target_room,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    exclude=websocket,  # 보낸 사람 제외
                )

                # 보낸 사람에게 확인
                await manager.send_personal(websocket, {
                    "type": "message_sent",
                    "content": content,
                    "room": target_room,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            elif msg_type == "join":
                # 방 입장
                new_room = data.get("room", "general")
                await manager.join_room(websocket, new_room)
                await manager.send_personal(websocket, {
                    "type": "joined",
                    "room": new_room,
                    "online_count": len(manager.rooms[new_room]),
                })

            elif msg_type == "leave":
                # 방 퇴장
                leave_room = data.get("room", room)
                await manager.leave_room(websocket, leave_room)

            elif msg_type == "pong":
                # 하트비트 응답 (로깅만)
                pass

    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()
        await manager.disconnect(websocket)


async def _heartbeat_loop(websocket: WebSocket, interval: int = 30) -> None:
    """
    하트비트 태스크: 주기적으로 ping을 전송하여 연결 상태를 확인합니다.
    클라이언트가 pong을 보내지 않아도 send 실패로 감지 가능합니다.
    """
    try:
        while True:
            await asyncio.sleep(interval)
            try:
                await websocket.send_text(
                    json.dumps({"type": "ping", "timestamp": time.time()})
                )
            except Exception:
                break
    except asyncio.CancelledError:
        pass


# ──────────────────────────────────────────────
# 3. REST API (채팅 관리)
# ──────────────────────────────────────────────
@app.get("/chat/stats")
async def get_chat_stats():
    """채팅 서버 통계"""
    return manager.get_stats()


@app.get("/chat/rooms")
async def list_rooms():
    """활성 방 목록"""
    return {
        room: len(members) for room, members in manager.rooms.items()
    }


# ──────────────────────────────────────────────
# 4. HTML 테스트 클라이언트
# ──────────────────────────────────────────────
@app.get("/")
async def get_chat_client():
    """내장 HTML 채팅 클라이언트"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>실시간 채팅</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }
        .container { max-width: 800px; margin: 20px auto; padding: 0 20px; }
        h1 { color: #e94560; margin-bottom: 20px; }
        .setup { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .setup input, .setup button { padding: 10px 15px; border: none; border-radius: 4px; margin: 5px; }
        .setup input { background: #0f3460; color: #eee; }
        .setup button { background: #e94560; color: white; cursor: pointer; }
        .setup button:hover { background: #c73e54; }
        #chat-box { background: #16213e; height: 400px; overflow-y: auto; padding: 15px;
                    border-radius: 8px; margin-bottom: 10px; }
        .msg { margin: 8px 0; padding: 8px 12px; border-radius: 6px; }
        .msg.system { color: #a0a0a0; font-style: italic; font-size: 0.9em; }
        .msg.received { background: #0f3460; }
        .msg.sent { background: #533483; text-align: right; }
        .msg .user { color: #e94560; font-weight: bold; font-size: 0.85em; }
        .msg .time { color: #888; font-size: 0.75em; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px; background: #16213e; color: #eee;
                           border: 1px solid #0f3460; border-radius: 4px; }
        .input-area button { padding: 12px 24px; background: #e94560; color: white;
                            border: none; border-radius: 4px; cursor: pointer; }
        .status { padding: 8px; font-size: 0.85em; color: #a0a0a0; }
    </style>
</head>
<body>
<div class="container">
    <h1>WebSocket 실시간 채팅</h1>

    <div class="setup" id="setup">
        <input type="text" id="username" placeholder="사용자 이름" value="사용자">
        <input type="text" id="room" placeholder="방 이름" value="general">
        <button onclick="connect()">연결</button>
    </div>

    <div id="chat-area" style="display:none;">
        <div class="status" id="status">연결 안 됨</div>
        <div id="chat-box"></div>
        <div class="input-area">
            <input type="text" id="message" placeholder="메시지 입력..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()">전송</button>
        </div>
    </div>
</div>

<script>
let ws = null;
let username = '';

function connect() {
    username = document.getElementById('username').value || '익명';
    const room = document.getElementById('room').value || 'general';

    ws = new WebSocket(`ws://${location.host}/ws/chat?username=${encodeURIComponent(username)}&room=${encodeURIComponent(room)}`);

    ws.onopen = () => {
        document.getElementById('setup').style.display = 'none';
        document.getElementById('chat-area').style.display = 'block';
        document.getElementById('status').textContent = `연결됨 - ${username} @ ${room}`;
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'ping') {
            ws.send(JSON.stringify({type: 'pong'}));
            return;
        }
        addMessage(data);
    };

    ws.onclose = () => {
        document.getElementById('status').textContent = '연결 종료됨';
        addMessage({type: 'system', message: '연결이 종료되었습니다.'});
    };
}

function sendMessage() {
    const input = document.getElementById('message');
    const content = input.value.trim();
    if (!content || !ws) return;

    ws.send(JSON.stringify({type: 'message', content: content}));
    input.value = '';
}

function addMessage(data) {
    const box = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = 'msg';

    if (data.type === 'system') {
        div.className += ' system';
        div.textContent = data.message;
    } else if (data.type === 'message') {
        div.className += ' received';
        div.innerHTML = `<div class="user">${data.username}</div>${data.content}<div class="time">${new Date(data.timestamp).toLocaleTimeString()}</div>`;
    } else if (data.type === 'message_sent') {
        div.className += ' sent';
        div.innerHTML = `${data.content}<div class="time">${new Date(data.timestamp).toLocaleTimeString()}</div>`;
    } else if (data.type === 'welcome' || data.type === 'joined') {
        div.className += ' system';
        div.textContent = data.message || `방에 입장했습니다 (접속자: ${data.online_count}명)`;
    }

    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}
</script>
</body>
</html>
    """)
