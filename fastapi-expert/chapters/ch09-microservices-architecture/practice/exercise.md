# 챕터 09 연습문제: 마이크로서비스와 확장 구조

---

## 문제 1: API v1/v2 라우터 분리와 하위 호환성

### 설명

블로그 API의 v1과 v2를 구현하세요. v2는 새로운 기능을 추가하면서 v1과의 하위 호환성을 유지해야 합니다. Deprecated 엔드포인트에 대한 경고 시스템도 포함합니다.

### 요구사항

1. **v1 API** (`/api/v1`):
   - `GET /posts`: 게시글 목록 (id, title, content, author)
   - `GET /posts/{id}`: 게시글 상세
   - `POST /posts`: 게시글 작성 (title, content, author)

2. **v2 API** (`/api/v2`):
   - `GET /posts`: 게시글 목록 + 페이징 + 태그 필터 + 좋아요 수
   - `GET /posts/{id}`: 게시글 상세 + 댓글 수, 태그, 생성일
   - `POST /posts`: 게시글 작성 + 태그 배열 추가
   - `GET /posts/{id}/comments`: 게시글 댓글 목록 (v2 전용)

3. **Deprecation 시스템**:
   - v1 응답 헤더에 `Deprecation: true`, `Sunset: 2025-06-01` 추가
   - v1 호출 시 로그에 경고 기록
   - `GET /api/versions`: 버전 정보와 마이그레이션 가이드

4. 공유 로직은 서비스 계층으로 분리 (중복 코드 최소화)

### 예상 입출력

```json
// v1 응답
GET /api/v1/posts/1
Headers: Deprecation: true, Sunset: 2025-06-01
{
  "id": 1,
  "title": "FastAPI 입문",
  "content": "...",
  "author": "홍길동"
}

// v2 응답 (확장)
GET /api/v2/posts/1
{
  "id": 1,
  "title": "FastAPI 입문",
  "content": "...",
  "author": "홍길동",
  "tags": ["python", "fastapi"],
  "like_count": 42,
  "comment_count": 5,
  "created_at": "2024-01-15T10:00:00Z"
}
```

<details>
<summary>힌트</summary>

- 공유 서비스: `PostService` 클래스에 비즈니스 로직을 집중하세요
- v1, v2 라우터는 같은 서비스를 사용하되 반환 모델만 다릅니다
- Deprecated 헤더: `response.headers["Deprecation"] = "true"`
- 미들웨어에서 `/api/v1` 경로를 감지하여 자동으로 헤더를 추가할 수 있습니다

</details>

---

## 문제 2: 서킷 브레이커 패턴 구현

### 설명

외부 서비스 호출에 대한 서킷 브레이커를 구현하세요. 실패율이 임계값을 초과하면 서킷을 열어 서비스를 보호하고, 자동 복구를 지원합니다.

### 요구사항

1. `CircuitBreaker` 클래스:
   - 상태: `CLOSED` (정상), `OPEN` (차단), `HALF_OPEN` (테스트)
   - 설정: `failure_threshold`, `recovery_timeout`, `success_threshold`
   - `call(func, *args)`: 서킷 브레이커를 통한 함수 호출
   - `get_stats()`: 현재 상태, 실패 수, 성공률 등

2. `circuit_breaker` 데코레이터:
   ```python
   @circuit_breaker(failure_threshold=5, recovery_timeout=30)
   async def call_external_api():
       ...
   ```

3. 폴백 지원:
   - 서킷이 열렸을 때 대체 응답을 반환할 수 있는 `fallback` 매개변수
   - `@circuit_breaker(fallback=default_response)`

4. 모니터링:
   - `GET /circuit-breakers`: 전체 서킷 브레이커 상태
   - `POST /circuit-breakers/{name}/reset`: 수동 리셋

5. 테스트용 엔드포인트:
   - `POST /test/unreliable`: 50% 확률로 실패하는 서비스
   - `POST /test/always-fail`: 항상 실패하는 서비스

### 예상 입출력

```json
GET /circuit-breakers
{
  "external_api": {
    "state": "closed",
    "failure_count": 2,
    "success_count": 48,
    "total_calls": 50,
    "failure_rate": 4.0,
    "last_failure": "2024-01-15T10:30:00Z"
  },
  "payment_service": {
    "state": "open",
    "failure_count": 6,
    "total_calls": 20,
    "failure_rate": 30.0,
    "opens_in": "25초 후 HALF_OPEN 전환"
  }
}
```

<details>
<summary>힌트</summary>

- `time.time()`으로 타임아웃을 관리하세요
- `@property`로 상태를 조회할 때 자동으로 OPEN -> HALF_OPEN 전이를 검사하세요
- 데코레이터는 `functools.wraps`를 사용하여 원본 함수 정보를 보존하세요
- 전역 레지스트리: `dict[str, CircuitBreaker]`로 모든 서킷 브레이커를 관리하세요
- `asyncio.Lock`을 사용하면 동시 접근 시 경쟁 조건을 방지할 수 있습니다

</details>

---

## 문제 3: 분산 트레이싱 헤더 전파

### 설명

여러 서비스 간 요청을 추적할 수 있는 분산 트레이싱 시스템을 구현하세요. W3C Trace Context 표준을 따르며, 전체 요청 흐름을 시각화할 수 있어야 합니다.

### 요구사항

1. `TraceContext` 클래스:
   - `trace_id`: 전체 요청 흐름의 고유 ID (32자 hex)
   - `span_id`: 현재 작업 단위의 고유 ID (16자 hex)
   - `parent_span_id`: 부모 스팬의 ID
   - `to_headers()`: W3C traceparent 헤더 형식으로 변환
   - `from_headers()`: 헤더에서 복원

2. `TracingMiddleware`:
   - 수신 요청에서 traceparent 헤더 추출 (없으면 새 trace 생성)
   - 응답 헤더에 trace_id, span_id 추가
   - 스팬 정보를 로그에 기록 (시작/종료 시간, 상태 코드)

3. `SpanCollector`:
   - 수집된 스팬 저장 (메모리)
   - `GET /traces`: 전체 트레이스 목록
   - `GET /traces/{trace_id}`: 특정 트레이스의 모든 스팬 (트리 구조)

4. 서비스 간 호출 시 trace context 전파:
   - `httpx`로 다른 서비스 호출 시 traceparent 헤더 자동 추가
   - 수신 서비스에서 부모 스팬과 연결

### 예상 입출력

```json
GET /traces/abc123...
{
  "trace_id": "abc123...",
  "duration_ms": 150,
  "spans": [
    {
      "span_id": "span1",
      "parent_span_id": null,
      "service": "api-gateway",
      "operation": "GET /orders/1",
      "duration_ms": 150,
      "status_code": 200,
      "children": [
        {
          "span_id": "span2",
          "parent_span_id": "span1",
          "service": "order-service",
          "operation": "get_order",
          "duration_ms": 80,
          "children": [
            {
              "span_id": "span3",
              "parent_span_id": "span2",
              "service": "order-service",
              "operation": "db_query",
              "duration_ms": 15
            }
          ]
        }
      ]
    }
  ]
}
```

<details>
<summary>힌트</summary>

- W3C traceparent 형식: `00-{trace_id}-{span_id}-01`
- `uuid.uuid4().hex[:32]`로 trace_id 생성
- 스팬을 트리 구조로 변환: `parent_span_id`로 부모-자식 관계를 매핑하세요
- 재귀 함수로 트리를 구성: `build_tree(spans, parent_id=None)`
- `request.state`에 trace context를 저장하면 라우터에서 접근 가능합니다
- `contextvar`를 사용하면 비동기 컨텍스트에서도 안전하게 trace 정보를 전파할 수 있습니다

</details>

---

## 제출 기준

- API 버전 간 하위 호환성이 유지되어야 합니다
- 서킷 브레이커의 상태 전이가 정확해야 합니다
- 트레이싱 컨텍스트가 서비스 간 정확히 전파되어야 합니다
- 모든 코드가 비동기로 작성되어야 합니다
- `# 실행 방법:` 주석이 첫 줄에 포함되어야 합니다
