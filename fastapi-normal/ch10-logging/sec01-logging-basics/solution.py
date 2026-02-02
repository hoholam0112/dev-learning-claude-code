# 모범 답안: 로깅 기본
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

import logging
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()


# --- 로그 캡처를 위한 ListHandler ---
class ListHandler(logging.Handler):
    """테스트용: 로그 레코드를 리스트에 저장하는 핸들러"""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(self.format(record))


# --- 문제 1: 기본 로거 설정 ---

# 로거 생성 및 설정
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# ListHandler 설정
list_handler = ListHandler()
list_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s - %(message)s")
list_handler.setFormatter(formatter)
logger.addHandler(list_handler)

# 액세스 로그 저장용 리스트
access_logs = []


# --- 문제 2: 요청 로깅 미들웨어 ---
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """모든 요청의 메서드, 경로, 상태 코드를 기록하는 미들웨어"""
    response = await call_next(request)

    # /logs 경로는 기록하지 않음
    if request.url.path != "/logs":
        access_logs.append({
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        })

    return response


@app.get("/info")
async def info_endpoint():
    """INFO 레벨 로그를 기록하는 엔드포인트"""
    logger.info("정보 메시지입니다")
    return {"level": "info", "message": "정보 메시지입니다"}


@app.get("/warning")
async def warning_endpoint():
    """WARNING 레벨 로그를 기록하는 엔드포인트"""
    logger.warning("경고 메시지입니다")
    return {"level": "warning", "message": "경고 메시지입니다"}


@app.get("/error")
async def error_endpoint():
    """ERROR 레벨 로그를 기록하는 엔드포인트"""
    logger.error("에러 메시지입니다")
    return {"level": "error", "message": "에러 메시지입니다"}


@app.get("/logs")
async def get_logs():
    """기록된 액세스 로그를 반환하는 엔드포인트"""
    return {"logs": access_logs}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 전 상태 초기화
    list_handler.records.clear()
    access_logs.clear()

    # === 문제 1 테스트: 기본 로거 ===

    # 테스트 1: GET /info - INFO 레벨 로그 확인
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {"level": "info", "message": "정보 메시지입니다"}
    assert any("INFO - 정보 메시지입니다" in r for r in list_handler.records)
    print("✓ GET /info - INFO 레벨 로그 기록 확인")

    # 테스트 2: GET /warning - WARNING 레벨 로그 확인
    response = client.get("/warning")
    assert response.status_code == 200
    assert response.json() == {"level": "warning", "message": "경고 메시지입니다"}
    assert any("WARNING - 경고 메시지입니다" in r for r in list_handler.records)
    print("✓ GET /warning - WARNING 레벨 로그 기록 확인")

    # 테스트 3: GET /error - ERROR 레벨 로그 확인
    response = client.get("/error")
    assert response.status_code == 200
    assert response.json() == {"level": "error", "message": "에러 메시지입니다"}
    assert any("ERROR - 에러 메시지입니다" in r for r in list_handler.records)
    print("✓ GET /error - ERROR 레벨 로그 기록 확인")

    # === 문제 2 테스트: 요청 로깅 미들웨어 ===

    # 테스트 4: 요청이 access_logs에 기록되었는지 확인
    assert len(access_logs) == 3  # /info, /warning, /error
    assert access_logs[0] == {"method": "GET", "path": "/info", "status_code": 200}
    assert access_logs[1] == {"method": "GET", "path": "/warning", "status_code": 200}
    assert access_logs[2] == {"method": "GET", "path": "/error", "status_code": 200}
    print("✓ 요청 로깅 미들웨어 - 요청이 access_logs에 기록됨")

    # 테스트 5: /logs 경로는 access_logs에 기록되지 않음
    logs_before = len(access_logs)
    response = client.get("/logs")
    assert response.status_code == 200
    assert len(access_logs) == logs_before  # /logs 요청은 기록되지 않음
    print("✓ /logs 경로는 access_logs에 기록되지 않음")

    print("\n모든 테스트를 통과했습니다!")
