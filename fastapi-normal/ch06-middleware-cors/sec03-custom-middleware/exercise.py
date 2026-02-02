# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

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


# TODO 1: APIKeyMiddleware 클래스를 구현하세요
# - BaseHTTPMiddleware를 상속
# - __init__에서 api_key를 매개변수로 받아 저장
# - dispatch 메서드에서:
#   - PUBLIC_PATHS에 포함된 경로는 검증 없이 통과
#   - X-API-Key 헤더가 없거나 api_key와 다르면 403 반환
#     (JSONResponse(status_code=403, content={"detail": "유효하지 않은 API 키입니다"}))
#   - 검증 통과 시 call_next(request) 호출


# TODO 2: RequestIDMiddleware 클래스를 구현하세요
# - BaseHTTPMiddleware를 상속
# - dispatch 메서드에서:
#   - X-Request-ID 헤더가 있으면 그 값을 사용, 없으면 uuid.uuid4()로 생성
#   - request.state.request_id에 요청 ID 저장
#   - call_next(request) 호출 후 응답 헤더에 X-Request-ID 추가


# TODO 3: 미들웨어를 앱에 등록하세요
# - RequestIDMiddleware를 먼저 등록 (안쪽)
# - APIKeyMiddleware를 나중에 등록 (바깥쪽, 먼저 실행됨)
#   api_key 매개변수에 VALID_API_KEY 전달
#
# 힌트:
# app.add_middleware(RequestIDMiddleware)
# app.add_middleware(APIKeyMiddleware, api_key=VALID_API_KEY)


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
    assert response.status_code == 403, (
        f"API 키 없이 접근 시 403이어야 합니다. 현재: {response.status_code}"
    )
    assert "유효하지 않은" in response.json()["detail"]
    print("✓ 보호된 경로에 API 키 없이 접근 시 403 반환")

    # 테스트 3: 잘못된 API 키로 접근 시 403
    response = client.get(
        "/api/data",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 403, (
        f"잘못된 API 키로 접근 시 403이어야 합니다. 현재: {response.status_code}"
    )
    print("✓ 잘못된 API 키로 접근 시 403 반환")

    # 테스트 4: 올바른 API 키로 접근 시 200
    response = client.get(
        "/api/data",
        headers={"X-API-Key": VALID_API_KEY},
    )
    assert response.status_code == 200, (
        f"올바른 API 키로 접근 시 200이어야 합니다. 현재: {response.status_code}"
    )
    print("✓ 올바른 API 키로 접근 시 200 반환")

    # === 요청 ID 테스트 ===

    # 테스트 5: 서버 생성 요청 ID 확인
    response = client.get(
        "/api/data",
        headers={"X-API-Key": VALID_API_KEY},
    )
    assert "x-request-id" in response.headers, (
        "응답 헤더에 X-Request-ID가 없습니다. RequestIDMiddleware를 구현하세요."
    )
    server_request_id = response.headers["x-request-id"]
    # UUID 형식인지 확인 (8-4-4-4-12)
    assert len(server_request_id) == 36, (
        f"요청 ID가 UUID 형식이어야 합니다. 현재: {server_request_id}"
    )
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
    assert response.headers["x-request-id"] == custom_request_id, (
        f"클라이언트가 보낸 요청 ID가 그대로 반환되어야 합니다. "
        f"기대: {custom_request_id}, 현재: {response.headers.get('x-request-id')}"
    )
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
    assert body["request_id"] == "check-state-123", (
        f"라우트 핸들러에서 request.state.request_id에 접근할 수 있어야 합니다. "
        f"현재: {body.get('request_id')}"
    )
    print("✓ 라우트 핸들러에서 request.state.request_id 접근 가능")

    print("\n모든 테스트를 통과했습니다!")
