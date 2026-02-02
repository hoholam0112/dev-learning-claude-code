# 모범 답안: 구조화된 로깅
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

import json
import logging
import uuid
from datetime import datetime, timezone
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


# --- 문제 1: JSON 포맷 로거 ---

class JSONFormatter(logging.Formatter):
    """로그를 JSON 형식으로 포맷하는 커스텀 포매터

    - timestamp: ISO 형식의 UTC 시간
    - level: 로그 레벨 (INFO, WARNING, ERROR 등)
    - message: 로그 메시지
    - extra_data가 있으면 JSON에 병합
    """

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # extra_data 속성이 있으면 병합
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)


# 로거 설정
logger = logging.getLogger("structured_app")
logger.setLevel(logging.DEBUG)

# ListHandler에 JSONFormatter 적용
list_handler = ListHandler()
list_handler.setLevel(logging.DEBUG)
list_handler.setFormatter(JSONFormatter())
logger.addHandler(list_handler)


# --- 문제 2: request_id 미들웨어 ---
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """모든 요청에 고유 request_id를 부여하는 미들웨어"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/items")
async def get_items(request: Request):
    """아이템 목록 조회 - extra_data 포함 로깅"""
    logger.info(
        "아이템 목록 조회",
        extra={"extra_data": {"action": "list_items", "count": 3}},
    )
    return {"items": ["아이템1", "아이템2", "아이템3"]}


@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    """사용자 조회 - request_id 포함 로깅"""
    request_id = request.state.request_id
    logger.info(
        "사용자 조회",
        extra={"extra_data": {
            "request_id": request_id,
            "user_id": user_id,
            "action": "get_user",
        }},
    )
    return {
        "user_id": user_id,
        "name": "홍길동",
        "request_id": request_id,
    }


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 전 상태 초기화
    list_handler.records.clear()

    # === 문제 1 테스트: JSON 포맷 로거 ===

    # 테스트 1: GET /items 요청 후 JSON 로그 확인
    response = client.get("/items")
    assert response.status_code == 200

    # 로그가 기록되었는지 확인
    assert len(list_handler.records) >= 1
    log_entry = json.loads(list_handler.records[0])

    # 테스트 2: timestamp 필드 확인
    assert "timestamp" in log_entry
    print(f"✓ JSON 포맷 로그에 timestamp 필드 존재: {log_entry['timestamp']}")

    # 테스트 3: level 필드 확인
    assert "level" in log_entry
    assert log_entry["level"] == "INFO"
    print(f"✓ JSON 포맷 로그에 level 필드 존재: {log_entry['level']}")

    # 테스트 4: message 필드 확인
    assert "message" in log_entry
    assert log_entry["message"] == "아이템 목록 조회"
    print(f"✓ JSON 포맷 로그에 message 필드 존재: {log_entry['message']}")

    # 테스트 5: extra_data 필드 병합 확인
    assert "action" in log_entry
    assert log_entry["action"] == "list_items"
    assert "count" in log_entry
    assert log_entry["count"] == 3
    print(f"✓ JSON 포맷 로그에 extra_data 필드가 병합됨: action={log_entry['action']}, count={log_entry['count']}")

    # === 문제 2 테스트: request_id 기반 요청 추적 ===

    list_handler.records.clear()

    # 테스트 6: GET /users/42 요청
    response = client.get("/users/42")
    assert response.status_code == 200

    # 응답 헤더에 X-Request-ID 확인
    assert "x-request-id" in response.headers
    header_request_id = response.headers["x-request-id"]
    print(f"✓ 응답 헤더에 X-Request-ID 포함: {header_request_id}")

    # 테스트 7: 로그에 request_id 확인
    assert len(list_handler.records) >= 1
    log_entry = json.loads(list_handler.records[0])
    assert "request_id" in log_entry
    print(f"✓ 로그에 request_id 필드 존재: {log_entry['request_id']}")

    # 테스트 8: 응답 본문에 request_id 확인
    body = response.json()
    assert "request_id" in body
    assert body["request_id"] == header_request_id
    print(f"✓ 응답 본문에 request_id 포함: {body['request_id']}")

    print("\n모든 테스트를 통과했습니다!")
