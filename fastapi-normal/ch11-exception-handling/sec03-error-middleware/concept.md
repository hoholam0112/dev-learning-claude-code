# sec03: 에러 미들웨어 (Error Middleware)

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 예외 계층 구조, sec02 전역 에러 핸들러 완료
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

- 에러 캐칭 미들웨어의 개념과 역할을 이해할 수 있다
- `trace_id`를 생성하고 요청 전체에 전파할 수 있다
- 에러 로깅 미들웨어를 구현할 수 있다
- 미들웨어 → 전역 핸들러 → 엔드포인트의 다중 방어선 아키텍처를 설명할 수 있다

---

## 핵심 개념

### 1. 에러 캐칭 미들웨어

sec02에서 배운 `exception_handler`는 FastAPI 레벨에서 예외를 처리합니다.
**미들웨어**는 그보다 더 바깥쪽에서 동작하여, 예외 핸들러가 처리하지 못한 에러도 잡을 수 있습니다.

```python
from starlette.middleware.base import BaseHTTPMiddleware

class ErrorCatchMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # 모든 미처리 예외를 안전하게 처리
            return JSONResponse(
                status_code=500,
                content={"error": "서버 오류가 발생했습니다"},
            )
```

### 2. trace_id 생성과 전파

마이크로서비스 환경에서 하나의 요청이 여러 서비스를 거칠 때,
**trace_id**를 사용하면 요청의 전체 경로를 추적할 수 있습니다.

```python
import uuid

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 1. trace_id 생성 (또는 클라이언트 제공값 사용)
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))

        # 2. request.state에 저장 (핸들러/핸들러에서 사용 가능)
        request.state.trace_id = trace_id

        # 3. 요청 처리
        response = await call_next(request)

        # 4. 응답 헤더에 추가
        response.headers["X-Trace-ID"] = trace_id

        return response
```

**trace_id 전파 흐름:**

```
클라이언트 → [미들웨어: trace_id 생성]
                    ↓
            [request.state.trace_id에 저장]
                    ↓
            [전역 핸들러: 에러 응답에 trace_id 포함]
                    ↓
            [엔드포인트: request.state.trace_id 접근 가능]
                    ↓
            [응답 헤더: X-Trace-ID에 포함]
```

### 3. 에러 로깅 미들웨어

에러가 발생했을 때 자동으로 로그를 기록하는 미들웨어입니다.
프로덕션에서는 `logging` 모듈을 사용하지만, 테스트에서는 리스트에 기록합니다.

**중요한 동작 원리:**
`@app.middleware("http")` 미들웨어에서 `call_next()`를 호출하면, 전역 핸들러가 처리한 에러는
JSON 응답으로 변환되어 정상적으로 반환됩니다. 하지만 일부 예외(예: `RuntimeError`)는
미들웨어까지 전파될 수 있습니다. 따라서 미들웨어에서는 **두 가지 케이스** 모두 처리해야 합니다.

```python
error_log = []  # 테스트용 에러 로그

@app.middleware("http")
async def error_logging_middleware(request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        # 미들웨어까지 전파된 예외 → 직접 500 응답 생성
        response = JSONResponse(
            status_code=500,
            content={"error_code": "INTERNAL_ERROR", "message": "내부 서버 오류"},
        )

    # 에러 응답(4xx, 5xx)인 경우 로깅
    if response.status_code >= 400:
        error_log.append({
            "trace_id": getattr(request.state, "trace_id", "unknown"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        })

    return response
```

> **두 가지 에러 감지 방식**: 전역 핸들러가 처리한 에러는 `response.status_code >= 400`으로 감지하고,
> 전역 핸들러를 우회하여 전파된 예외는 `try-except`로 잡아서 직접 응답을 생성합니다.

### 4. 다중 방어선 아키텍처

예외 처리는 **여러 레이어**에서 이루어집니다.
각 레이어는 독립적으로 동작하며, 이전 레이어가 놓친 에러를 다음 레이어가 처리합니다.

```
요청 →  ┌─────────────────────────────┐
        │  미들웨어 (3번째 방어선)       │  ← trace_id 부여, 에러 로깅
        │  ┌───────────────────────┐   │
        │  │  전역 핸들러 (2번째 방어선) │  ← AppException, ValidationError, catch-all
        │  │  ┌─────────────────┐  │   │
        │  │  │  엔드포인트       │  │   │  ← 비즈니스 로직, 도메인 예외 발생
        │  │  │  (1번째 방어선)   │  │   │
        │  │  └─────────────────┘  │   │
        │  └───────────────────────┘   │
        └─────────────────────────────┘
응답 ←
```

| 레이어 | 역할 | 처리하는 에러 |
|--------|------|-------------|
| 엔드포인트 | 비즈니스 로직 | 도메인 예외 발생 (`raise NotFoundException(...)`) |
| 전역 핸들러 | 예외 → JSON 변환 | `AppException`, `RequestValidationError`, `Exception` |
| 미들웨어 | 로깅, 추적 | 모든 에러 로깅, `trace_id` 전파 |

### 5. 미들웨어 vs exception_handler 차이

| 특성 | 미들웨어 | exception_handler |
|------|---------|-------------------|
| 실행 위치 | ASGI 레벨 (더 바깥쪽) | FastAPI 레벨 |
| 처리 범위 | 모든 요청/응답 | 특정 예외 타입만 |
| 요청/응답 접근 | 둘 다 가능 | 요청만 접근 가능 |
| 주요 용도 | 로깅, 추적, 모니터링 | 예외 → JSON 변환 |
| 에러 처리 방식 | try-except로 직접 | 데코레이터로 등록 |

---

## 주의사항

1. **미들웨어 등록 순서**: `@app.middleware("http")`와 `add_middleware()`는 모두 나중에 등록한 것이 바깥쪽(먼저 실행)입니다. error_logging을 먼저 등록(안쪽)하고, trace_id를 나중에 등록(바깥쪽)하면 trace_id가 먼저 설정된 후 로깅에서 사용할 수 있습니다.
2. **`request.state` 안전하게 접근**: `getattr(request.state, "trace_id", "unknown")`을 사용하면 trace_id가 아직 설정되지 않은 경우에도 안전합니다.
3. **예외 전파 주의**: 일부 예외는 전역 핸들러를 거치지 않고 미들웨어까지 전파됩니다. 미들웨어에서 `try-except`로 잡아서 직접 응답을 생성해야 합니다.

---

## 핵심 정리

1. **에러 캐칭 미들웨어**는 전역 핸들러보다 바깥쪽에서 동작한다
2. **trace_id**를 미들웨어에서 생성하여 `request.state`와 응답 헤더에 전파한다
3. **에러 로깅 미들웨어**는 응답 상태 코드와 예외를 모두 확인하여 에러를 감지한다
4. **다중 방어선**: 미들웨어 → 전역 핸들러 → 엔드포인트 순으로 에러를 처리한다
5. 미들웨어는 **모든 요청/응답**을 처리하고, `exception_handler`는 **특정 예외**만 처리한다

---

## 다음 단계

이 챕터의 모든 섹션을 완료했습니다!
다음 챕터에서 더 고급 주제를 학습할 수 있습니다.
