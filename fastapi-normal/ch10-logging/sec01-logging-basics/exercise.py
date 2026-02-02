# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

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


# TODO 1: 기본 로거를 설정하세요
# - "app" 이름의 로거를 생성 (logging.getLogger("app"))
# - 로거 레벨을 DEBUG로 설정
# - ListHandler 인스턴스를 생성하고 DEBUG 레벨로 설정
# - Formatter를 "%(levelname)s - %(message)s" 포맷으로 생성
# - 핸들러에 포매터를 연결하고, 로거에 핸들러를 추가
#
# 힌트:
# logger = logging.getLogger("app")
# logger.setLevel(logging.DEBUG)
# list_handler = ListHandler()
# ...


# 액세스 로그 저장용 리스트
access_logs = []


# TODO 2: 요청 로깅 미들웨어를 작성하세요
# - 모든 요청의 메서드, 경로, 상태 코드를 access_logs에 딕셔너리로 기록
#   예: {"method": "GET", "path": "/info", "status_code": 200}
# - /logs 경로에 대한 요청은 기록하지 않음
#
# 힌트:
# @app.middleware("http")
# async def request_logging_middleware(request: Request, call_next):
#     response = await call_next(request)
#     if request.url.path != "/logs":
#         access_logs.append({...})
#     return response


# TODO 3: 아래 3개의 엔드포인트를 구현하세요
# GET /info - logger.info("정보 메시지입니다") 호출 후
#             {"level": "info", "message": "정보 메시지입니다"} 반환
# GET /warning - logger.warning("경고 메시지입니다") 호출 후
#                {"level": "warning", "message": "경고 메시지입니다"} 반환
# GET /error - logger.error("에러 메시지입니다") 호출 후
#              {"level": "error", "message": "에러 메시지입니다"} 반환


@app.get("/logs")
async def get_logs():
    """기록된 액세스 로그를 반환하는 엔드포인트"""
    return {"logs": access_logs}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 전 상태 초기화 (list_handler가 정의되어 있어야 합니다)
    list_handler.records.clear()
    access_logs.clear()

    # === 문제 1 테스트: 기본 로거 ===

    # 테스트 1: GET /info - INFO 레벨 로그 확인
    response = client.get("/info")
    assert response.status_code == 200, (
        f"GET /info의 상태 코드가 200이어야 합니다. 현재: {response.status_code}"
    )
    assert response.json() == {"level": "info", "message": "정보 메시지입니다"}, (
        f"응답 본문이 올바르지 않습니다. 현재: {response.json()}"
    )
    assert any("INFO - 정보 메시지입니다" in r for r in list_handler.records), (
        f"INFO 레벨 로그가 기록되지 않았습니다. 현재 records: {list_handler.records}"
    )
    print("✓ GET /info - INFO 레벨 로그 기록 확인")

    # 테스트 2: GET /warning - WARNING 레벨 로그 확인
    response = client.get("/warning")
    assert response.status_code == 200, (
        f"GET /warning의 상태 코드가 200이어야 합니다. 현재: {response.status_code}"
    )
    assert response.json() == {"level": "warning", "message": "경고 메시지입니다"}, (
        f"응답 본문이 올바르지 않습니다. 현재: {response.json()}"
    )
    assert any("WARNING - 경고 메시지입니다" in r for r in list_handler.records), (
        f"WARNING 레벨 로그가 기록되지 않았습니다. 현재 records: {list_handler.records}"
    )
    print("✓ GET /warning - WARNING 레벨 로그 기록 확인")

    # 테스트 3: GET /error - ERROR 레벨 로그 확인
    response = client.get("/error")
    assert response.status_code == 200, (
        f"GET /error의 상태 코드가 200이어야 합니다. 현재: {response.status_code}"
    )
    assert response.json() == {"level": "error", "message": "에러 메시지입니다"}, (
        f"응답 본문이 올바르지 않습니다. 현재: {response.json()}"
    )
    assert any("ERROR - 에러 메시지입니다" in r for r in list_handler.records), (
        f"ERROR 레벨 로그가 기록되지 않았습니다. 현재 records: {list_handler.records}"
    )
    print("✓ GET /error - ERROR 레벨 로그 기록 확인")

    # === 문제 2 테스트: 요청 로깅 미들웨어 ===

    # 테스트 4: 요청이 access_logs에 기록되었는지 확인
    assert len(access_logs) == 3, (
        f"access_logs에 3개의 기록이 있어야 합니다. 현재: {len(access_logs)}개"
    )
    assert access_logs[0] == {"method": "GET", "path": "/info", "status_code": 200}, (
        f"첫 번째 로그가 올바르지 않습니다. 현재: {access_logs[0]}"
    )
    assert access_logs[1] == {"method": "GET", "path": "/warning", "status_code": 200}, (
        f"두 번째 로그가 올바르지 않습니다. 현재: {access_logs[1]}"
    )
    assert access_logs[2] == {"method": "GET", "path": "/error", "status_code": 200}, (
        f"세 번째 로그가 올바르지 않습니다. 현재: {access_logs[2]}"
    )
    print("✓ 요청 로깅 미들웨어 - 요청이 access_logs에 기록됨")

    # 테스트 5: /logs 경로는 access_logs에 기록되지 않음
    logs_before = len(access_logs)
    response = client.get("/logs")
    assert response.status_code == 200
    assert len(access_logs) == logs_before, (
        f"/logs 경로는 access_logs에 기록되면 안 됩니다. "
        f"이전: {logs_before}개, 현재: {len(access_logs)}개"
    )
    print("✓ /logs 경로는 access_logs에 기록되지 않음")

    print("\n모든 테스트를 통과했습니다!")
