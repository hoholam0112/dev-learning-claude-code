# 섹션 03: 커스텀 미들웨어

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 미들웨어 기본, sec02 CORS 설정 완료
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

- `BaseHTTPMiddleware`를 상속하여 클래스 기반 미들웨어를 구현할 수 있다
- 조건부 처리 로직을 가진 미들웨어를 설계할 수 있다
- 실무에서 유용한 미들웨어 패턴(API 키 검증, 요청 ID 추가)을 적용할 수 있다

---

## 클래스 기반 미들웨어

sec01에서는 `@app.middleware("http")` 데코레이터를 사용한 함수형 미들웨어를 학습했습니다.
이번에는 **클래스 기반 미들웨어**를 만들어 봅니다.

### `BaseHTTPMiddleware` 사용하기

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request

class MyCustomMiddleware(BaseHTTPMiddleware):
    """클래스 기반 커스텀 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        # 요청 전처리
        print(f"요청: {request.method} {request.url}")

        # 다음 단계 호출
        response = await call_next(request)

        # 응답 후처리
        response.headers["X-Custom"] = "미들웨어에서 추가"

        return response

app = FastAPI()
app.add_middleware(MyCustomMiddleware)
```

### 함수형 vs 클래스형 비교

| 특성 | 함수형 (`@app.middleware`) | 클래스형 (`BaseHTTPMiddleware`) |
|------|---------------------------|-------------------------------|
| 문법 | 간단한 데코레이터 | 클래스 상속 |
| 재사용성 | 낮음 (앱에 종속) | 높음 (모듈화 가능) |
| 설정 전달 | 클로저로 전달 | 생성자(`__init__`)로 전달 |
| 적합한 상황 | 간단한 미들웨어 | 설정이 필요한 미들웨어 |

---

## 핵심 개념: 설정을 받는 미들웨어

클래스 기반 미들웨어는 **생성자를 통해 설정값을 전달**받을 수 있습니다.

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    """설정 가능한 커스텀 헤더 미들웨어"""

    def __init__(self, app, header_name: str, header_value: str):
        super().__init__(app)
        self.header_name = header_name
        self.header_value = header_value

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers[self.header_name] = self.header_value
        return response


app = FastAPI()

# 미들웨어 추가 시 설정값 전달
app.add_middleware(
    CustomHeaderMiddleware,
    header_name="X-App-Version",
    header_value="2.0.0",
)
```

---

## 코드 예제 1: API 키 검증 미들웨어

특정 경로에 대해 API 키를 검증하는 미들웨어입니다.
인증이 필요한 경로와 공개 경로를 구분하여 처리합니다.

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API 키 검증 미들웨어

    - X-API-Key 헤더에 유효한 API 키가 있는지 확인합니다.
    - 공개 경로(public_paths)는 검증을 건너뜁니다.
    """

    def __init__(self, app, api_key: str, public_paths: list[str] = None):
        super().__init__(app)
        self.api_key = api_key
        self.public_paths = public_paths or ["/", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        # 공개 경로는 검증 없이 통과
        if request.url.path in self.public_paths:
            return await call_next(request)

        # API 키 검증
        provided_key = request.headers.get("X-API-Key")
        if provided_key != self.api_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "유효하지 않은 API 키입니다"},
            )

        # 검증 통과 시 다음 단계 진행
        response = await call_next(request)
        return response


app = FastAPI()

app.add_middleware(
    APIKeyMiddleware,
    api_key="my-secret-key-123",
    public_paths=["/", "/docs", "/openapi.json", "/health"],
)


@app.get("/health")
async def health():
    """공개 엔드포인트 - API 키 불필요"""
    return {"status": "ok"}


@app.get("/api/secret-data")
async def get_secret_data():
    """보호된 엔드포인트 - API 키 필요"""
    return {"secret": "비밀 데이터"}
```

**테스트:**
```bash
# 공개 경로 → 성공
curl http://localhost:8000/health
# → {"status": "ok"}

# 보호된 경로 (키 없음) → 403
curl http://localhost:8000/api/secret-data
# → {"detail": "유효하지 않은 API 키입니다"}

# 보호된 경로 (키 있음) → 성공
curl -H "X-API-Key: my-secret-key-123" http://localhost:8000/api/secret-data
# → {"secret": "비밀 데이터"}
```

---

## 코드 예제 2: 요청 ID 추가 미들웨어

모든 요청에 고유한 요청 ID를 부여하여 로그 추적을 용이하게 합니다.
마이크로서비스 환경에서 **분산 추적(Distributed Tracing)**에 활용됩니다.

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """요청 ID 미들웨어

    - 모든 요청에 고유 ID를 부여합니다.
    - 클라이언트가 X-Request-ID를 보내면 그 값을 사용합니다.
    - 없으면 서버에서 UUID를 생성합니다.
    - 응답 헤더에도 같은 요청 ID를 포함합니다.
    """

    async def dispatch(self, request: Request, call_next):
        # 클라이언트가 보낸 요청 ID가 있으면 사용, 없으면 새로 생성
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # request.state에 요청 ID 저장 (라우트 핸들러에서 접근 가능)
        request.state.request_id = request_id

        # 다음 단계 호출
        response = await call_next(request)

        # 응답 헤더에 요청 ID 추가
        response.headers["X-Request-ID"] = request_id

        return response


app = FastAPI()
app.add_middleware(RequestIDMiddleware)


@app.get("/api/data")
async def get_data(request: Request):
    """라우트 핸들러에서 요청 ID에 접근하는 예제"""
    request_id = request.state.request_id
    return {
        "data": "샘플 데이터",
        "request_id": request_id,
    }
```

> **`request.state` 활용**: 미들웨어에서 `request.state`에 데이터를 저장하면,
> 라우트 핸들러나 의존성 함수에서 해당 데이터에 접근할 수 있습니다.

---

## 조건부 처리 패턴

### 경로 기반 조건 분기

```python
class ConditionalMiddleware(BaseHTTPMiddleware):
    """특정 경로에만 적용되는 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        # /api/로 시작하는 경로에만 적용
        if request.url.path.startswith("/api/"):
            # API 전용 로직 수행
            response = await call_next(request)
            response.headers["X-API-Version"] = "v1"
            return response

        # 그 외 경로는 그대로 통과
        return await call_next(request)
```

### 메서드 기반 조건 분기

```python
class WriteProtectionMiddleware(BaseHTTPMiddleware):
    """쓰기 작업에 대한 추가 검증 미들웨어"""

    WRITE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    async def dispatch(self, request: Request, call_next):
        if request.method in self.WRITE_METHODS:
            # 쓰기 작업 시 추가 검증
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "쓰기 작업에는 인증이 필요합니다"},
                )

        return await call_next(request)
```

---

## 미들웨어 조합 패턴

여러 미들웨어를 조합할 때는 **등록 순서**에 주의해야 합니다.

```python
app = FastAPI()

# 미들웨어는 add_middleware()의 역순으로 실행됩니다.
# 아래 순서대로 등록하면:
#   요청 → RequestID → APIKey → 라우트 → APIKey → RequestID → 응답

app.add_middleware(RequestIDMiddleware)          # ② 두 번째로 실행
app.add_middleware(APIKeyMiddleware, api_key="secret")  # ① 먼저 실행

# add_middleware로 추가하면 나중에 추가한 것이 바깥쪽(먼저 실행)
# 따라서 APIKey 검증 후 통과하면 RequestID가 부여됩니다.
```

---

## 핵심 정리

1. `BaseHTTPMiddleware`를 상속하여 **클래스 기반 미들웨어**를 만들 수 있다
2. 생성자(`__init__`)를 통해 **설정값을 주입**받을 수 있다
3. `request.state`를 사용하여 **미들웨어와 핸들러 간 데이터를 공유**할 수 있다
4. 경로(`request.url.path`)나 메서드(`request.method`)로 **조건부 처리**가 가능하다
5. `JSONResponse`를 직접 반환하여 `call_next` 없이 **요청을 차단**할 수 있다
6. 미들웨어 등록 순서가 **실행 순서에 영향**을 미친다

---

## 다음 단계

이 챕터의 모든 섹션을 완료했습니다!
[Ch07: 데이터베이스 연동](../../ch07-database/README.md)에서 SQLAlchemy를 사용한 데이터베이스 연동을 학습합니다.
