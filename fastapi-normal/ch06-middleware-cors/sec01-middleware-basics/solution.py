# 모범 답안: 미들웨어 기본
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

import time
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()

request_log = []  # 로그 저장용


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """요청 로깅 및 처리 시간 측정 미들웨어

    - 모든 요청의 메서드와 URL을 request_log에 기록합니다.
    - 응답 헤더에 X-Process-Time을 추가합니다.
    """
    # ① 요청 전처리: 시작 시간 기록
    start_time = time.time()

    # ② 요청 정보를 로그에 기록
    request_log.append({
        "method": request.method,
        "url": str(request.url),
    })

    # ③ 다음 미들웨어 또는 라우트 핸들러 호출
    response = await call_next(request)

    # ④ 응답 후처리: 처리 시간 계산 및 헤더 추가
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))

    return response


@app.get("/hello")
async def hello():
    """인사 엔드포인트"""
    return {"message": "안녕하세요"}


@app.get("/items")
async def get_items():
    """상품 목록 엔드포인트"""
    return {"items": ["상품1", "상품2"]}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 1: X-Process-Time 헤더 확인
    response = client.get("/hello")
    assert response.status_code == 200
    assert "x-process-time" in response.headers
    process_time = response.headers["x-process-time"]
    print(f"✓ X-Process-Time 헤더: {process_time}")

    # 테스트 2: 두 번째 요청도 헤더 확인
    response = client.get("/items")
    assert response.status_code == 200
    assert "x-process-time" in response.headers

    # 테스트 3: 요청 로그 확인
    assert len(request_log) == 2
    assert request_log[0]["method"] == "GET"
    assert "/hello" in request_log[0]["url"]
    assert request_log[1]["method"] == "GET"
    assert "/items" in request_log[1]["url"]
    print(f"✓ 요청 로그: {request_log}")

    print("\n모든 테스트를 통과했습니다!")
