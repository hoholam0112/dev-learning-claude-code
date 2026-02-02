# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

app = FastAPI()

# TODO: CORSMiddleware를 추가하세요
# - 허용 출처: "http://localhost:3000", "http://localhost:5173"
# - 허용 메서드: "GET", "POST", "PUT", "DELETE"
# - 허용 헤더: "*" (모두 허용)
# - 자격 증명 포함 허용: True
#
# 힌트:
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[...],
#     allow_credentials=...,
#     allow_methods=[...],
#     allow_headers=[...],
# )


@app.get("/api/users")
async def get_users():
    """사용자 목록 조회"""
    return [
        {"id": 1, "name": "홍길동"},
        {"id": 2, "name": "김철수"},
    ]


@app.post("/api/users")
async def create_user():
    """사용자 생성"""
    return {"id": 3, "name": "이영희"}


@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 1: localhost:3000에서의 요청 허용 확인
    response = client.get(
        "/api/users",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000", (
        "access-control-allow-origin 헤더가 'http://localhost:3000'이어야 합니다. "
        "CORSMiddleware를 추가하세요."
    )
    print("✓ CORS 기본 설정 확인 - localhost:3000 허용됨")

    # 테스트 2: localhost:5173에서의 요청 허용 확인
    response = client.get(
        "/api/users",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173", (
        "access-control-allow-origin 헤더가 'http://localhost:5173'이어야 합니다."
    )
    print("✓ CORS 추가 출처 확인 - localhost:5173 허용됨")

    # 테스트 3: 허용되지 않은 출처 차단 확인
    response = client.get(
        "/api/users",
        headers={"Origin": "http://evil-site.com"},
    )
    assert response.status_code == 200  # 응답은 200이지만
    cors_header = response.headers.get("access-control-allow-origin")
    assert cors_header is None, (
        f"허용되지 않은 출처에 CORS 헤더가 있으면 안 됩니다. 현재: {cors_header}"
    )
    print("✓ 허용되지 않은 출처 차단 확인")

    # 테스트 4: Preflight (OPTIONS) 요청 확인
    response = client.options(
        "/api/users",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-methods" in response.headers, (
        "Preflight 응답에 access-control-allow-methods 헤더가 없습니다."
    )
    allowed_methods = response.headers["access-control-allow-methods"]
    assert "POST" in allowed_methods, (
        f"허용 메서드에 POST가 포함되어야 합니다. 현재: {allowed_methods}"
    )
    print("✓ Preflight 요청 응답 확인")

    print("\n모든 테스트를 통과했습니다!")
