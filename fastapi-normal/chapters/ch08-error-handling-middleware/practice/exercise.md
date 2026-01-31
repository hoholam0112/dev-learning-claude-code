# 챕터 08 연습 문제: 에러 처리와 미들웨어

---

## 문제 1: 커스텀 에러 응답 포맷

### 설명
API 전체에서 일관된 에러 응답 형식을 사용하도록 구현하세요. 모든 에러 응답은 동일한 구조를 따라야 합니다.

### 요구사항
1. 모든 에러 응답은 다음 형식을 따르세요:
   ```json
   {
       "success": false,
       "error": {
           "code": "ERROR_CODE",
           "message": "사용자에게 보여줄 메시지",
           "details": {}
       },
       "timestamp": "2024-01-01T00:00:00"
   }
   ```
2. 다음 커스텀 예외와 핸들러를 구현하세요:
   - `ValidationError` -> 422 응답
   - `AuthenticationError` -> 401 응답
   - `PermissionError` -> 403 응답
   - `ResourceNotFoundError` -> 404 응답
3. FastAPI의 기본 422 에러(Pydantic 검증 실패)도 같은 형식으로 변환하세요
4. 테스트용 엔드포인트를 만들어 각 에러를 확인할 수 있도록 하세요

### 예상 입출력

**404 에러:**
```json
{
    "success": false,
    "error": {
        "code": "RESOURCE_NOT_FOUND",
        "message": "요청한 리소스를 찾을 수 없습니다",
        "details": {"resource": "user", "id": 999}
    },
    "timestamp": "2024-01-01T12:00:00"
}
```

<details>
<summary>힌트 보기</summary>

- FastAPI의 기본 422 에러를 가로채려면 `RequestValidationError`를 핸들링하세요:
  ```python
  from fastapi.exceptions import RequestValidationError

  @app.exception_handler(RequestValidationError)
  async def validation_exception_handler(request, exc):
      # exc.errors()로 상세 에러 정보를 가져올 수 있습니다
      ...
  ```
- `datetime.utcnow().isoformat()`으로 타임스탬프를 생성하세요
- 각 에러 클래스에 `code` 속성을 추가하면 핸들러에서 활용하기 좋습니다

</details>

---

## 문제 2: 요청 처리 시간 측정 미들웨어

### 설명
모든 API 요청의 처리 시간을 측정하고, 느린 요청을 감지하는 미들웨어를 구현하세요.

### 요구사항
1. 모든 응답에 `X-Process-Time` 헤더를 추가하세요 (초 단위)
2. 처리 시간이 1초를 초과하면 경고 로그를 출력하세요
3. 처리 시간이 5초를 초과하면 에러 로그를 출력하세요
4. `GET /stats` 엔드포인트에서 다음 통계를 반환하세요:
   - 총 요청 수
   - 평균 처리 시간
   - 최대 처리 시간
   - 느린 요청 수 (1초 초과)
5. 테스트용 느린 엔드포인트(`GET /slow/{seconds}`)를 만드세요

### 예상 입출력

**응답 헤더:**
```
X-Process-Time: 0.0023
```

**통계 조회:**
```json
GET /stats
{
    "total_requests": 150,
    "average_time": 0.045,
    "max_time": 3.21,
    "slow_requests": 5,
    "uptime_seconds": 3600
}
```

<details>
<summary>힌트 보기</summary>

- `time.time()`으로 시작/종료 시간을 측정하세요
- 통계를 저장할 리스트 또는 딕셔너리를 미들웨어 클래스에 두세요
- `__init__`에서 통계 변수를 초기화하고, `dispatch`에서 업데이트하세요
- `statistics.mean()`으로 평균을 계산할 수 있습니다
- 엔드포인트에서 통계에 접근하려면 `app.state`를 활용하세요

</details>

---

## 문제 3: IP 기반 접근 제한 미들웨어

### 설명
허용된 IP 주소 목록을 기반으로 접근을 제한하는 미들웨어를 구현하세요. 또한 간단한 속도 제한(Rate Limiting) 기능도 추가하세요.

### 요구사항
1. 차단된 IP에서의 요청은 `403 Forbidden`으로 응답하세요
2. 특정 경로(`/health`)는 모든 IP에서 접근 가능하도록 예외 처리하세요
3. 같은 IP에서 분당 60회 이상 요청 시 `429 Too Many Requests`로 응답하세요
4. `GET /health` - 서버 상태 확인 (IP 제한 없음)
5. `GET /admin/blocked-ips` - 차단된 IP 목록 조회
6. `POST /admin/block-ip` - IP 차단 추가

### 예상 입출력

**차단된 IP 응답 (403):**
```json
{
    "error": "ACCESS_DENIED",
    "message": "접근이 차단된 IP 주소입니다",
    "client_ip": "192.168.1.100"
}
```

**속도 제한 초과 (429):**
```json
{
    "error": "RATE_LIMIT_EXCEEDED",
    "message": "요청 횟수가 제한을 초과했습니다. 잠시 후 다시 시도해주세요.",
    "retry_after": 45
}
```

**서버 상태:**
```json
GET /health
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00"
}
```

<details>
<summary>힌트 보기</summary>

- `request.client.host`로 클라이언트 IP를 가져올 수 있습니다
- 속도 제한은 딕셔너리에 IP별 요청 기록을 저장하여 구현하세요:
  ```python
  from collections import defaultdict
  request_counts = defaultdict(list)  # IP: [타임스탬프 목록]
  ```
- 1분이 지난 요청 기록은 제거하여 메모리를 관리하세요
- 화이트리스트 경로 목록: `["/health", "/docs", "/openapi.json"]`
- `time.time()`으로 현재 시간과 비교하여 1분 이내 요청만 카운트하세요

</details>
