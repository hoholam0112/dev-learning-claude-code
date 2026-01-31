# 챕터 05 연습문제: 고급 보안 패턴

---

## 문제 1: 다중 인증 전략 (JWT + API 키)

### 설명

하나의 엔드포인트에서 JWT 토큰과 API 키를 모두 지원하는 다중 인증 시스템을 구현하세요.

### 요구사항

1. 두 가지 인증 방식을 지원하는 의존성 구현:
   - `Authorization: Bearer <jwt_token>` 헤더
   - `X-API-Key: <api_key>` 헤더
   - 둘 중 하나만 있어도 인증 성공
2. 인증 결과를 통합 `AuthResult` 모델로 반환:
   - `method`: "jwt" 또는 "api_key"
   - `user_id`: 사용자 ID
   - `scopes`: 허용된 스코프 목록
   - `metadata`: 인증 방법별 추가 정보
3. 인증 방법별 차별화된 Rate Limit:
   - JWT: 분당 100회
   - API 키: 키별 설정값
4. 인증 실패 시 적절한 에러 메시지:
   - 토큰/키 없음 → 401
   - 토큰 만료 → 401 + "토큰이 만료되었습니다"
   - 키 비활성화 → 403 + "비활성화된 API 키입니다"
5. 인증 로그 기록 (성공/실패, 방법, IP, 시간)

### 예상 입출력

```bash
# JWT 인증
curl -H "Authorization: Bearer <token>" http://localhost:8000/auth/me
# → {"method": "jwt", "user_id": 1, "scopes": ["read", "write"]}

# API 키 인증
curl -H "X-API-Key: sk_xxx" http://localhost:8000/auth/me
# → {"method": "api_key", "user_id": "key_owner", "scopes": ["read"]}

# 둘 다 없음
curl http://localhost:8000/auth/me
# → 401 {"detail": "인증 정보가 없습니다. JWT 토큰 또는 API 키를 전달하세요."}
```

<details>
<summary>힌트</summary>

- `APIKeyHeader`와 `OAuth2PasswordBearer`를 모두 `auto_error=False`로 설정합니다.
- 의존성 함수에서 두 값을 모두 받아서 어느 것이 있는지 확인합니다.
- `AuthResult` Pydantic 모델로 통합된 인증 결과를 반환합니다.
- 인증 로그는 `logging` 모듈로 기록합니다.
- `request.client.host`로 클라이언트 IP를 확인할 수 있습니다.

</details>

---

## 문제 2: 동적 권한 관리 시스템

### 설명

역할과 권한을 런타임에 동적으로 생성/수정/삭제할 수 있는 RBAC 시스템을 구현하세요.

### 요구사항

1. 역할(Role) CRUD:
   - `POST /roles` - 새 역할 생성
   - `GET /roles` - 역할 목록 조회
   - `PUT /roles/{role_name}` - 역할 수정 (권한 변경)
   - `DELETE /roles/{role_name}` - 역할 삭제
2. 권한(Permission) 관리:
   - 계층 구조 지원: `admin:*`가 `admin:read`, `admin:write`를 포함
   - 와일드카드 매칭: `users:*`는 `users:read`, `users:create` 등 모두 포함
3. 사용자-역할 매핑:
   - 한 사용자가 여러 역할을 가질 수 있음
   - 최종 권한 = 모든 역할의 권한 합집합
4. 권한 검사 엔드포인트:
   - `GET /auth/check?resource=users&action=delete` → 허용/거부 응답
5. 권한 변경 감사 로그

### 예상 입출력

```bash
# 역할 생성
POST /roles
{"name": "content_editor", "permissions": ["articles:read", "articles:write", "comments:*"]}
# → {"id": 1, "name": "content_editor", "permissions": [...]}

# 와일드카드 권한 확인
GET /auth/check?resource=comments&action=delete
# → {"allowed": true, "matched_permission": "comments:*", "role": "content_editor"}

# 사용자에게 역할 부여
POST /users/1/roles
{"role_name": "content_editor"}
# → {"user_id": 1, "roles": ["viewer", "content_editor"]}
```

<details>
<summary>힌트</summary>

- 권한은 "리소스:동작" 형식으로 정의합니다 (예: "users:read").
- 와일드카드 매칭: `fnmatch.fnmatch("users:read", "users:*")` 를 사용합니다.
- 역할과 권한 데이터는 인메모리 딕셔너리로 관리합니다.
- 사용자의 최종 권한은 `set.union()`으로 모든 역할의 권한을 합칩니다.
- 감사 로그는 변경 전/후 상태를 모두 기록합니다.

</details>

---

## 문제 3: IP 기반 Rate Limiter 구현

### 설명

클라이언트 IP 주소를 기반으로 한 다계층 Rate Limiting 시스템을 구현하세요.

### 요구사항

1. 다계층 Rate Limit:
   - 초당: 10회 (버스트 방지)
   - 분당: 100회
   - 시간당: 1000회
   - 모든 계층을 통과해야 요청 허용
2. IP 화이트리스트/블랙리스트:
   - 화이트리스트: Rate Limit 미적용
   - 블랙리스트: 모든 요청 거부 (403)
3. 토큰 버킷 알고리즘 구현:
   - 버스트 용량(burst) 설정 가능
   - 지속 속도(sustained rate) 설정 가능
4. Rate Limit 응답 헤더 포함:
   - `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
   - `Retry-After` (429 응답 시)
5. 관리자 API:
   - IP별 Rate Limit 현황 조회
   - IP 화이트리스트/블랙리스트 관리
   - Rate Limit 초기화

### 예상 입출력

```bash
# 정상 요청
curl http://localhost:8000/api/data
# 응답 헤더: X-RateLimit-Remaining: 99

# Rate Limit 초과 시
curl http://localhost:8000/api/data
# → 429 {"detail": "요청 한도 초과", "retry_after": 5}
# 응답 헤더: Retry-After: 5

# 관리자: Rate Limit 현황
GET /admin/rate-limits
# → {"127.0.0.1": {"second": {"used": 5, "limit": 10}, ...}}

# 관리자: IP 블랙리스트 추가
POST /admin/blacklist
{"ip": "10.0.0.1"}
```

<details>
<summary>힌트</summary>

- `request.client.host`로 클라이언트 IP를 확인합니다.
- 프록시 뒤에 있는 경우 `X-Forwarded-For` 헤더를 확인해야 합니다.
- 토큰 버킷은 `last_refill_time`과 `tokens` 두 값으로 관리합니다.
- 다계층 제한은 각 계층을 순서대로 확인하고, 하나라도 초과하면 거부합니다.
- 미들웨어로 구현하면 모든 엔드포인트에 자동 적용됩니다.
- IP별 상태는 `defaultdict`로 관리합니다.

</details>

---

## 문제 4: 보안 감사 로그 미들웨어

### 설명

모든 요청의 보안 관련 정보를 기록하는 감사 로그 미들웨어를 구현하세요.

### 요구사항

1. 감사 로그 항목:
   - 타임스탬프 (ISO 8601)
   - 클라이언트 IP
   - HTTP 메서드 + 경로
   - 인증 정보 (사용자/API 키, 마스킹)
   - 요청 본문 (민감 정보 마스킹)
   - 응답 상태 코드
   - 처리 시간
   - 보안 이벤트 분류 (정상, 인증실패, 권한부족, Rate초과)
2. 민감 정보 마스킹:
   - 비밀번호 필드: `"password": "***"`
   - 토큰: 처음 4자만 표시 `"Bearer eyJh..."`  → `"Bearer eyJh****"`
   - API 키: 접두사만 표시 `"sk_abc..."`
3. 보안 이벤트 감지 및 알림:
   - 같은 IP에서 5분 내 5회 이상 인증 실패 → 경고 로그
   - 비정상적인 경로 접근 시도 (../,  etc.) → 경고 로그
4. 감사 로그 조회 API:
   - `GET /audit/logs` - 최근 로그 조회 (페이지네이션)
   - `GET /audit/logs?event_type=auth_failure` - 필터링
   - `GET /audit/alerts` - 보안 경고 목록
5. 구조화된 로그 형식 (JSON)

### 예상 입출력

```bash
# 감사 로그 예시
{
  "timestamp": "2024-01-01T12:00:00Z",
  "client_ip": "192.168.1.1",
  "method": "POST",
  "path": "/api/users",
  "auth": {"type": "jwt", "user": "admin", "token_prefix": "eyJh"},
  "request_body": {"name": "홍길동", "password": "***"},
  "status_code": 201,
  "duration_ms": 45,
  "event_type": "normal"
}

# 보안 경고
GET /audit/alerts
[
  {
    "type": "brute_force_attempt",
    "ip": "10.0.0.1",
    "failures": 7,
    "window": "5분",
    "first_attempt": "2024-01-01T11:55:00Z"
  }
]
```

<details>
<summary>힌트</summary>

- `BaseHTTPMiddleware`로 모든 요청을 가로챕니다.
- 요청 본문은 `await request.body()`로 읽되, 다시 사용할 수 있도록 주의합니다.
- 민감 필드 마스킹: `"password"`, `"secret"`, `"token"`, `"api_key"` 등의 키를 재귀적으로 검색합니다.
- 로그 저장소는 `collections.deque(maxlen=1000)`으로 메모리 제한합니다.
- 인증 실패 추적은 `defaultdict(list)`로 IP별 실패 기록을 관리합니다.
- 비정상 경로 감지: `..`, `%2e%2e`, `<script>` 등의 패턴을 확인합니다.

</details>

---

## 제출 가이드

- `solution.py` 파일에 네 문제의 답안을 모두 작성하세요
- `uvicorn solution:app --reload`로 실행 가능해야 합니다
- 보안 기능은 `curl`로 테스트하세요:
  - 인증: `curl -H "Authorization: Bearer <token>" ...`
  - API 키: `curl -H "X-API-Key: <key>" ...`
  - Rate Limit: `for i in $(seq 1 20); do curl ...; done`
- 감사 로그는 콘솔과 API에서 모두 확인 가능해야 합니다
