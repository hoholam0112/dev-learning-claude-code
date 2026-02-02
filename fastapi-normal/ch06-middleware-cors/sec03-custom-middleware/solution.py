# 모범 답안: 커스텀 미들웨어
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()

# 공개 경로 목록 (API 키 검증을 건너뛰는 경로)
PUBLIC_PATHS = ["/health", "/docs", "/openapi.json"]

# 유효한 API 키
VALID_API_KEY = "test-api-key-2024"


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API 키 검증 미들웨어

    - X-API-Key 헤더에 유효한 API 키가 있는지 확인합니다.
    - PUBLIC_PATHS에 포함된 경로는 검증을 건너뜁니다.
    - 키가 없거나 유효하지 않으면 403 응답을 반환합니다.
    """

    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        # 공개 경로는 검증 없이 통과
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # X-API-Key 헤더 검증
        provided_key = request.headers.get("X-API-Key")
        if provided_key != self.api_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "유효하지 않은 API 키입니다"},
            )

        # 검증 통과 시 다음 단계로 진행
        response = await call_next(request)
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """요청 ID 미들웨어

    - 모든 요청에 고유한 요청 ID를 부여합니다.
    - 클라이언트가 X-Request-ID 헤더를 보내면 그 값을 사용합니다.
    - 헤더가 없으면 UUID v4를 새로 생성합니다.
    - request.state.request_id에 저장하여 핸들러에서 접근 가능하게 합니다.
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


# 미들웨어 등록
# 순서: 나중에 add_middleware한 것이 바깥쪽(먼저 실행)
# 실행 순서: APIKey(검증) → RequestID(ID 부여) → 라우트 핸들러
app.add_middleware(RequestIDMiddleware)
app.add_middleware(APIKeyMiddleware, api_key=VALID_API_KEY)


@app.get("/health")
async def health():
    """공개 엔드포인트 - API 키 불필요"""
    return {"status": "ok"}


@app.get("/api/data")
async def get_data(request: Request):
    """보호된 엔드포인트 - API 키 필요"""
    return {
        "data": "비밀 데이터",
        "request_id": request.state.request_id,
    }


@app.get("/api/users")
async def get_users(request: Request):
    """보호된 엔드포인트 - 사용자 목록"""
    return {
        "users": [{"id": 1, "name": "홍길동"}],
        "request_id": request.state.request_id,
    }


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # === API 키 검증 테스트 ===

    # 테스트 1: 공개 경로는 API 키 없이 접근 가능
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✓ 공개 경로(/health)는 API 키 없이 접근 가능")

    # 테스트 2: 보호된 경로에 API 키 없이 접근 시 403
    response = client.get("/api/data")
    assert response.status_code == 403
    assert "유효하지 않은" in response.json()["detail"]
    print("✓ 보호된 경로에 API 키 없이 접근 시 403 반환")

    # 테스트 3: 잘못된 API 키로 접근 시 403
    response = client.get(
        "/api/data",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 403
    print("✓ 잘못된 API 키로 접근 시 403 반환")

    # 테스트 4: 올바른 API 키로 접근 시 200
    response = client.get(
        "/api/data",
        headers={"X-API-Key": VALID_API_KEY},
    )
    assert response.status_code == 200
    print("✓ 올바른 API 키로 접근 시 200 반환")

    # === 요청 ID 테스트 ===

    # 테스트 5: 서버 생성 요청 ID 확인
    response = client.get(
        "/api/data",
        headers={"X-API-Key": VALID_API_KEY},
    )
    assert "x-request-id" in response.headers
    server_request_id = response.headers["x-request-id"]
    assert len(server_request_id) == 36  # UUID 형식
    print(f"✓ 서버 생성 요청 ID가 응답 헤더에 포함됨: {server_request_id}")

    # 테스트 6: 클라이언트 제공 요청 ID 확인
    custom_request_id = "my-custom-request-123"
    response = client.get(
        "/api/data",
        headers={
            "X-API-Key": VALID_API_KEY,
            "X-Request-ID": custom_request_id,
        },
    )
    assert response.headers["x-request-id"] == custom_request_id
    print(f"✓ 클라이언트 제공 요청 ID가 응답에 그대로 반환됨: {custom_request_id}")

    # 테스트 7: 라우트 핸들러에서 request.state.request_id 접근 확인
    response = client.get(
        "/api/data",
        headers={
            "X-API-Key": VALID_API_KEY,
            "X-Request-ID": "check-state-123",
        },
    )
    body = response.json()
    assert body["request_id"] == "check-state-123"
    print("✓ 라우트 핸들러에서 request.state.request_id 접근 가능")

    print("\n모든 테스트를 통과했습니다!")
