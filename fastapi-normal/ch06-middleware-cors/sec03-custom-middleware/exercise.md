# 연습 문제: 커스텀 미들웨어

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: API 키 검증 미들웨어

`BaseHTTPMiddleware`를 상속하여 API 키 검증 미들웨어를 구현하세요.

### 요구 사항

- `X-API-Key` 헤더의 값이 지정된 API 키와 일치하는지 검증
- 공개 경로(`/health`, `/docs`, `/openapi.json`)는 검증 없이 통과
- API 키가 없거나 틀리면 403 상태 코드와 에러 메시지 반환
- API 키는 생성자를 통해 전달받음

### 힌트

```python
class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request, call_next):
        # 공개 경로 확인 → 검증 → call_next 또는 에러 반환
        ...
```

---

## 문제 2: 요청 ID 미들웨어

모든 요청에 고유한 요청 ID를 부여하는 미들웨어를 구현하세요.

### 요구 사항

- 클라이언트가 `X-Request-ID` 헤더를 보내면 그 값을 사용
- 헤더가 없으면 `uuid.uuid4()`로 새 ID 생성
- `request.state.request_id`에 요청 ID 저장
- 응답 헤더 `X-Request-ID`에도 같은 값 포함

### 힌트

```python
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # request.state에 저장 → call_next → 응답 헤더에 추가
        ...
```

---

## 테스트 기대 결과

```
✓ 공개 경로(/health)는 API 키 없이 접근 가능
✓ 보호된 경로에 API 키 없이 접근 시 403 반환
✓ 잘못된 API 키로 접근 시 403 반환
✓ 올바른 API 키로 접근 시 200 반환
✓ 서버 생성 요청 ID가 응답 헤더에 포함됨
✓ 클라이언트 제공 요청 ID가 응답에 그대로 반환됨
✓ 라우트 핸들러에서 request.state.request_id 접근 가능

모든 테스트를 통과했습니다!
```
