# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

import time
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()

request_log = []  # 로그 저장용


# TODO: 요청 로깅 미들웨어를 작성하세요
# - 요청 메서드와 URL을 request_log 리스트에 딕셔너리로 기록
#   예: {"method": "GET", "url": "http://testserver/hello"}
# - 응답 헤더에 X-Process-Time 추가 (처리 시간, 초 단위 문자열)
#
# 힌트:
# @app.middleware("http")
# async def logging_middleware(request: Request, call_next):
#     ...


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
    assert "x-process-time" in response.headers, (
        "X-Process-Time 헤더가 응답에 없습니다. 미들웨어를 작성하세요."
    )
    process_time = response.headers["x-process-time"]
    print(f"✓ X-Process-Time 헤더: {process_time}")

    # 테스트 2: 두 번째 요청도 헤더 확인
    response = client.get("/items")
    assert response.status_code == 200
    assert "x-process-time" in response.headers, (
        "X-Process-Time 헤더가 /items 응답에 없습니다."
    )

    # 테스트 3: 요청 로그 확인
    assert len(request_log) == 2, (
        f"request_log에 2개의 기록이 있어야 합니다. 현재: {len(request_log)}개"
    )
    assert request_log[0]["method"] == "GET", (
        f"첫 번째 로그의 method가 'GET'이어야 합니다. 현재: {request_log[0].get('method')}"
    )
    assert "/hello" in request_log[0]["url"], (
        f"첫 번째 로그의 url에 '/hello'가 포함되어야 합니다. 현재: {request_log[0].get('url')}"
    )
    assert request_log[1]["method"] == "GET"
    assert "/items" in request_log[1]["url"]
    print(f"✓ 요청 로그: {request_log}")

    print("\n모든 테스트를 통과했습니다!")
