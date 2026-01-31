# 챕터 08 연습문제: WebSocket과 실시간 통신

---

## 문제 1: 방(Room) 기반 채팅 시스템

### 설명

여러 방(Room)을 지원하는 채팅 시스템을 구현하세요. 사용자는 동시에 여러 방에 참여할 수 있으며, 각 방은 독립적으로 메시지를 주고받습니다.

### 요구사항

1. `RoomManager` 클래스:
   - `create_room(name, max_users)`: 방 생성 (최대 인원 제한)
   - `join_room(websocket, room_name)`: 방 입장 (인원 초과 시 거부)
   - `leave_room(websocket, room_name)`: 방 퇴장
   - `send_to_room(room_name, message, exclude)`: 방 내 브로드캐스트
   - `get_room_info(room_name)`: 방 정보 (접속자, 메시지 수 등)

2. 메시지 타입:
   - `chat`: 일반 채팅 메시지
   - `join`: 방 입장
   - `leave`: 방 퇴장
   - `room_list`: 전체 방 목록 요청
   - `whisper`: 특정 사용자에게 귓속말

3. 메시지 히스토리:
   - 각 방의 최근 50개 메시지를 보관
   - 새로 입장한 사용자에게 히스토리 전송

4. REST API:
   - `GET /rooms`: 방 목록
   - `POST /rooms`: 방 생성
   - `GET /rooms/{name}/history`: 방 메시지 히스토리

### 예상 입출력

```json
// WebSocket 연결: ws://localhost:8000/ws?username=홍길동

// 클라이언트 -> 서버: 방 입장
{"type": "join", "room": "tech"}

// 서버 -> 클라이언트: 입장 확인 + 히스토리
{
  "type": "room_joined",
  "room": "tech",
  "history": [...],
  "online_users": ["김철수", "이영희"]
}

// 클라이언트 -> 서버: 메시지 전송
{"type": "chat", "room": "tech", "content": "안녕하세요!"}

// 서버 -> 방 전체: 메시지 브로드캐스트
{
  "type": "chat",
  "room": "tech",
  "username": "홍길동",
  "content": "안녕하세요!",
  "timestamp": "2024-01-15T10:30:00Z"
}

// 클라이언트 -> 서버: 귓속말
{"type": "whisper", "to": "김철수", "content": "비밀 메시지"}
```

<details>
<summary>힌트</summary>

- `defaultdict(set)`으로 방별 연결을 관리하세요
- `defaultdict(deque)`로 방별 메시지 히스토리를 관리하세요 (maxlen=50)
- 귓속말은 사용자명 -> WebSocket 매핑이 필요합니다
- 인원 초과 시 `await websocket.send_json({"type": "error", "message": "방이 가득 찼습니다"})`

</details>

---

## 문제 2: JWT 인증이 포함된 WebSocket 연결

### 설명

JWT 토큰 기반 인증을 지원하는 WebSocket 시스템을 구현하세요. HTTP 티켓 방식으로 안전하게 인증합니다.

### 요구사항

1. 인증 흐름:
   - `POST /auth/login`: 사용자 로그인 -> JWT 토큰 발급
   - `POST /auth/ws-ticket`: JWT로 1회용 WebSocket 티켓 발급
   - `ws://host/ws?ticket=xxx`: 티켓으로 WebSocket 연결

2. 티켓 규칙:
   - 발급 후 30초 이내 사용
   - 1회 사용 후 폐기
   - 티켓에 사용자 정보 포함

3. 인증된 사용자만 메시지 전송 가능
4. 미인증 연결 시 4001 코드로 종료
5. 토큰 만료 시 연결 종료 (4002 코드)

### 예상 입출력

```bash
# 1단계: 로그인
POST /auth/login
{"username": "admin", "password": "secret"}
-> {"access_token": "eyJ...", "token_type": "bearer"}

# 2단계: 티켓 발급
POST /auth/ws-ticket
Authorization: Bearer eyJ...
-> {"ticket": "abc123...", "expires_in": 30}

# 3단계: WebSocket 연결
ws://localhost:8000/ws?ticket=abc123...
-> 연결 성공 (인증된 사용자)

# 만료된 티켓으로 연결 시
ws://localhost:8000/ws?ticket=expired...
-> 연결 거부 (4001: 유효하지 않은 티켓)
```

<details>
<summary>힌트</summary>

- `python-jose` 또는 `PyJWT` 패키지로 JWT를 생성/검증하세요
- 간단한 JWT: `jwt.encode({"sub": username, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET, algorithm="HS256")`
- 티켓 저장소: `dict[str, dict]`로 관리, 타임스탬프 포함
- WebSocket 종료 코드: `await websocket.close(code=4001, reason="유효하지 않은 티켓")`
- `secrets.token_urlsafe(32)`로 안전한 티켓 생성

</details>

---

## 문제 3: 실시간 대시보드 데이터 스트리밍 (SSE)

### 설명

SSE를 사용하여 서버 상태를 실시간으로 모니터링하는 대시보드를 구현하세요. 여러 종류의 메트릭을 다른 간격으로 전송합니다.

### 요구사항

1. 메트릭 스트림 (`/sse/dashboard`):
   - 시스템 메트릭 (1초 간격): CPU, 메모리, 디스크
   - API 메트릭 (5초 간격): 요청 수, 평균 응답 시간, 에러율
   - 비즈니스 메트릭 (10초 간격): 활성 사용자, 매출, 주문 수

2. 채널별 구독 (`/sse/{channel}`):
   - `system`: 시스템 메트릭만
   - `api`: API 메트릭만
   - `business`: 비즈니스 메트릭만
   - `all`: 전체

3. 이벤트 히스토리:
   - `Last-Event-ID` 헤더 기반 놓친 이벤트 복구
   - 최근 200개 이벤트 보관

4. 클라이언트 관리:
   - 연결된 클라이언트 수 추적
   - 비활성 클라이언트 자동 정리 (60초 타임아웃)

5. HTML 대시보드:
   - 실시간 차트 또는 게이지 표시
   - 연결 상태 표시 (연결됨/재연결 중)
   - 메트릭 값 자동 업데이트

### 예상 입출력

```bash
# SSE 스트림 연결
curl -N http://localhost:8000/sse/all

# 수신 데이터
event: system_metrics
data: {"cpu": 45.2, "memory": 67.8, "disk": 52.1}
id: 1

event: api_metrics
data: {"requests": 1250, "avg_response_ms": 23.4, "error_rate": 0.2}
id: 2

event: business_metrics
data: {"active_users": 342, "revenue": 1250000, "orders": 89}
id: 3

: heartbeat 2024-01-15T10:30:00Z

# 재연결 시 (Last-Event-ID: 2)
# id=3부터 전송 시작
```

<details>
<summary>힌트</summary>

- `asyncio.create_task()`로 각 메트릭 생성 태스크를 별도 실행하세요
- SSE 코멘트(`:`)로 하트비트를 보내면 연결 유지에 도움이 됩니다
- `EventSource` 객체는 자동 재연결을 지원합니다 (`retry:` 필드로 간격 설정)
- 메트릭 생성 시 `random` 모듈로 시뮬레이션하되, 이전 값과 크게 차이나지 않게 하세요
- HTML 차트: CSS progress bar나 `<meter>` 태그로 간단히 구현 가능

</details>

---

## 제출 기준

- WebSocket 연결 및 해제가 안정적으로 처리되어야 합니다
- 에러 발생 시 연결이 정상적으로 정리되어야 합니다
- HTML 클라이언트가 포함되어 브라우저에서 테스트 가능해야 합니다
- `# 실행 방법:` 주석이 첫 줄에 포함되어야 합니다
