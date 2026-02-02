# 모범 답안: CORS 설정
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

app = FastAPI()

# 허용할 출처 목록
allowed_origins = [
    "http://localhost:3000",   # React 개발 서버
    "http://localhost:5173",   # Vite 개발 서버
]

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,          # 허용할 출처
    allow_credentials=True,                  # 쿠키 포함 허용
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 허용할 HTTP 메서드
    allow_headers=["*"],                     # 모든 요청 헤더 허용
)


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
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    print("✓ CORS 기본 설정 확인 - localhost:3000 허용됨")

    # 테스트 2: localhost:5173에서의 요청 허용 확인
    response = client.get(
        "/api/users",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    print("✓ CORS 추가 출처 확인 - localhost:5173 허용됨")

    # 테스트 3: 허용되지 않은 출처 차단 확인
    response = client.get(
        "/api/users",
        headers={"Origin": "http://evil-site.com"},
    )
    assert response.status_code == 200
    cors_header = response.headers.get("access-control-allow-origin")
    assert cors_header is None
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
    assert "access-control-allow-methods" in response.headers
    allowed_methods = response.headers["access-control-allow-methods"]
    assert "POST" in allowed_methods
    print("✓ Preflight 요청 응답 확인")

    print("\n모든 테스트를 통과했습니다!")
