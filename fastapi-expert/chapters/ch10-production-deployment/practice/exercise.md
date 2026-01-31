# 챕터 10 연습문제: 프로덕션 배포와 운영

---

## 문제 1: Dockerfile 최적화 (멀티 스테이지 빌드)

### 설명

FastAPI 앱을 위한 최적화된 Dockerfile을 작성하세요. 멀티 스테이지 빌드를 사용하여 이미지 크기를 최소화하고, 보안 모범 사례를 적용합니다.

### 요구사항

1. **멀티 스테이지 빌드**:
   - 스테이지 1 (builder): 의존성 설치 + wheel 파일 생성
   - 스테이지 2 (runtime): 최소 런타임 이미지

2. **보안**:
   - 비root 사용자로 실행 (`appuser`)
   - 불필요한 쉘 도구 제거
   - `.dockerignore` 파일 작성

3. **최적화**:
   - 레이어 캐싱 활용 (requirements.txt 먼저 복사)
   - `--no-cache-dir` 옵션
   - `python:3.12-slim` 베이스 이미지

4. **설정**:
   - 환경 변수로 설정 주입
   - 헬스 체크 HEALTHCHECK 명령
   - Gunicorn + Uvicorn 워커

5. **docker-compose.yml**:
   - FastAPI 앱 서비스
   - PostgreSQL 서비스
   - Redis 서비스
   - 헬스 체크 설정

### 예상 결과

```bash
# 빌드
docker build -t fastapi-app:latest .

# 이미지 크기 확인
docker images fastapi-app
# REPOSITORY    TAG     IMAGE ID     CREATED     SIZE
# fastapi-app   latest  abc123       1분 전     ~150MB

# 실행
docker-compose up -d

# 헬스 체크
curl http://localhost:8000/health/ready
# {"status": "ready", "checks": {"database": {"healthy": true}, ...}}
```

<details>
<summary>힌트</summary>

- `.dockerignore`에 포함할 것: `__pycache__`, `.git`, `.env`, `*.pyc`, `venv`, `.vscode`
- `HEALTHCHECK` 명령: `HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health/live || exit 1`
- Gunicorn 실행: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`
- `COPY requirements.txt .`와 `RUN pip install`을 먼저 하면 의존성 레이어가 캐싱됩니다

</details>

---

## 문제 2: 구조화된 로깅 시스템 구현

### 설명

JSON 형식의 구조화된 로깅 시스템을 구현하세요. 모든 요청에 대한 접근 로그와 에러 로그를 체계적으로 기록하며, 분산 트레이싱과 연동 가능해야 합니다.

### 요구사항

1. `StructuredLogger` 클래스:
   - JSON 형식 출력
   - 필수 필드: timestamp, level, message, service, request_id
   - 선택 필드: trace_id, user_id, duration_ms, status_code, error
   - 로그 레벨 필터링

2. `AccessLogMiddleware`:
   - 모든 요청/응답을 JSON으로 로깅
   - 필드: method, path, status_code, duration_ms, client_ip, user_agent, request_id
   - 느린 요청 경고 (500ms 이상)
   - 에러 응답 시 에러 로그 추가

3. 컨텍스트 변수:
   - `request_id`: 요청별 고유 ID (X-Request-ID 헤더 또는 자동 생성)
   - `trace_id`: 분산 트레이싱 ID
   - `user_id`: 인증된 사용자 ID

4. 로그 출력 예시:
   ```json
   {"timestamp":"2024-01-15T10:30:00Z","level":"info","message":"request_completed",
    "service":"api","method":"GET","path":"/api/users","status_code":200,
    "duration_ms":45.2,"client_ip":"192.168.1.1","request_id":"req-abc123",
    "trace_id":"trace-xyz"}
   ```

5. 에러 로그:
   ```json
   {"timestamp":"2024-01-15T10:30:01Z","level":"error","message":"unhandled_exception",
    "service":"api","method":"POST","path":"/api/orders","status_code":500,
    "error":"ZeroDivisionError: division by zero","traceback":"...",
    "request_id":"req-def456"}
   ```

### 예상 입출력

```bash
# 정상 요청
curl http://localhost:8000/api/items

# 서버 로그 출력
{"timestamp":"...","level":"info","message":"request_completed","method":"GET",
 "path":"/api/items","status_code":200,"duration_ms":12.3,"request_id":"abc"}

# 느린 요청
curl http://localhost:8000/api/slow

# 서버 로그 출력
{"timestamp":"...","level":"warning","message":"slow_request","method":"GET",
 "path":"/api/slow","duration_ms":1523.4,"threshold_ms":500,"request_id":"def"}
```

<details>
<summary>힌트</summary>

- `logging.Formatter`를 상속받아 `format()` 메서드에서 JSON을 생성하세요
- `contextvars.ContextVar`를 사용하면 비동기 환경에서 안전하게 컨텍스트를 전파할 수 있습니다
- `uuid.uuid4().hex[:8]`로 짧은 request_id를 생성하세요
- `traceback.format_exception()`으로 스택 트레이스를 문자열로 변환할 수 있습니다
- `time.perf_counter()`가 `time.time()`보다 정밀합니다

</details>

---

## 문제 3: Graceful Shutdown 구현

### 설명

SIGTERM 신호를 받았을 때 진행 중인 요청을 안전하게 완료한 후 종료하는 시스템을 구현하세요. 쿠버네티스 환경에서의 무중단 배포를 지원합니다.

### 요구사항

1. `GracefulShutdownManager`:
   - SIGTERM/SIGINT 신호 핸들링
   - 진행 중인 요청 추적 (active_requests 카운터)
   - 최대 대기 시간 설정 (grace_period_seconds)
   - 종료 상태에서 새 요청 거부 (503 + Retry-After)

2. `ShutdownMiddleware`:
   - 종료 중이면 503 반환
   - 진행 중인 요청 카운터 관리
   - 응답 헤더에 `Connection: close` 추가 (종료 중)

3. 종료 순서:
   ```
   1. SIGTERM 수신
   2. 헬스 체크 실패 시작 (새 트래픽 차단)
   3. 진행 중인 요청 완료 대기 (최대 grace_period)
   4. 데이터베이스 연결 정리
   5. 캐시 연결 정리
   6. 프로세스 종료
   ```

4. 테스트 엔드포인트:
   - `GET /api/long-task`: 5초 걸리는 작업 (Graceful Shutdown 테스트)
   - `POST /admin/shutdown`: 수동 Graceful Shutdown 트리거

### 예상 입출력

```bash
# 긴 작업 실행 중
curl http://localhost:8000/api/long-task &

# SIGTERM 전송 (다른 터미널)
kill -SIGTERM <PID>

# 로그 출력
INFO: SIGTERM 수신, Graceful Shutdown 시작
INFO: 진행 중인 요청 1개 완료 대기... (최대 30초)
INFO: 새 요청 거부 중 (503 Service Unavailable)
INFO: 모든 요청 완료, 연결 정리 중...
INFO: 데이터베이스 연결 종료
INFO: Redis 연결 종료
INFO: 프로세스 종료

# 종료 중 새 요청
curl http://localhost:8000/api/items
# HTTP 503 {"detail": "서비스 종료 중입니다", "retry_after": 30}
```

<details>
<summary>힌트</summary>

- `signal.signal(signal.SIGTERM, handler)`로 SIGTERM을 처리하세요
- `asyncio.Event`를 사용하면 종료 신호를 비동기적으로 전파할 수 있습니다
- 진행 중인 요청 카운터: `asyncio.Lock`으로 보호하면 안전합니다
- Gunicorn의 `graceful_timeout` 설정도 함께 고려하세요
- 쿠버네티스의 `terminationGracePeriodSeconds`와 앱의 grace_period를 맞추세요
- 헬스 체크가 먼저 실패해야 로드 밸런서가 트래픽을 중단합니다

</details>

---

## 제출 기준

- Dockerfile이 빌드되어야 하고 이미지 크기가 200MB 이하여야 합니다
- 로그가 JSON 형식으로 출력되어야 합니다
- Graceful Shutdown이 진행 중인 요청을 보호해야 합니다
- `# 실행 방법:` 주석이 첫 줄에 포함되어야 합니다
