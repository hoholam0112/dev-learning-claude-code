# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

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


# TODO 1: JSONFormatter 클래스를 구현하세요
# - logging.Formatter를 상속
# - format 메서드에서 로그 레코드를 JSON 문자열로 변환
# - JSON에 포함할 필드:
#   - "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
#   - "level": record.levelname
#   - "message": record.getMessage()
# - record에 extra_data 속성이 있으면 log_data에 update로 병합
# - json.dumps(log_data, ensure_ascii=False) 반환
#
# 힌트:
# class JSONFormatter(logging.Formatter):
#     def format(self, record):
#         log_data = { ... }
#         if hasattr(record, "extra_data"):
#             log_data.update(record.extra_data)
#         return json.dumps(log_data, ensure_ascii=False)


# TODO 2: 로거를 설정하세요
# - "structured_app" 이름의 로거 생성
# - DEBUG 레벨로 설정
# - ListHandler 인스턴스를 생성하고 JSONFormatter를 적용
# - 로거에 핸들러 추가
#
# 힌트:
# logger = logging.getLogger("structured_app")
# list_handler = ListHandler()
# list_handler.setFormatter(JSONFormatter())
# logger.addHandler(list_handler)


# TODO 3: request_id 미들웨어를 구현하세요
# - uuid.uuid4()로 request_id 생성
# - request.state.request_id에 저장
# - 응답 헤더 X-Request-ID에 request_id 추가
#
# 힌트:
# @app.middleware("http")
# async def request_id_middleware(request: Request, call_next):
#     request_id = str(uuid.uuid4())
#     request.state.request_id = request_id
#     response = await call_next(request)
#     response.headers["X-Request-ID"] = request_id
#     return response


# TODO 4: GET /items 엔드포인트를 구현하세요
# - logger.info("아이템 목록 조회", extra={"extra_data": {"action": "list_items", "count": 3}}) 호출
# - {"items": ["아이템1", "아이템2", "아이템3"]} 반환


# TODO 5: GET /users/{user_id} 엔드포인트를 구현하세요
# - request.state.request_id를 가져와서
# - logger.info("사용자 조회", extra={"extra_data": {"request_id": request_id, "user_id": user_id, "action": "get_user"}}) 호출
# - {"user_id": user_id, "name": "홍길동", "request_id": request_id} 반환


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 전 상태 초기화
    list_handler.records.clear()

    # === 문제 1 테스트: JSON 포맷 로거 ===

    # 테스트 1: GET /items 요청 후 JSON 로그 확인
    response = client.get("/items")
    assert response.status_code == 200, (
        f"GET /items의 상태 코드가 200이어야 합니다. 현재: {response.status_code}"
    )

    # 로그가 기록되었는지 확인
    assert len(list_handler.records) >= 1, (
        "로그가 기록되지 않았습니다. JSONFormatter와 로거 설정을 확인하세요."
    )
    log_entry = json.loads(list_handler.records[0])

    # 테스트 2: timestamp 필드 확인
    assert "timestamp" in log_entry, (
        f"로그에 timestamp 필드가 없습니다. 현재 필드: {list(log_entry.keys())}"
    )
    print(f"✓ JSON 포맷 로그에 timestamp 필드 존재: {log_entry['timestamp']}")

    # 테스트 3: level 필드 확인
    assert "level" in log_entry, (
        f"로그에 level 필드가 없습니다. 현재 필드: {list(log_entry.keys())}"
    )
    assert log_entry["level"] == "INFO", (
        f"로그 level이 INFO여야 합니다. 현재: {log_entry['level']}"
    )
    print(f"✓ JSON 포맷 로그에 level 필드 존재: {log_entry['level']}")

    # 테스트 4: message 필드 확인
    assert "message" in log_entry, (
        f"로그에 message 필드가 없습니다. 현재 필드: {list(log_entry.keys())}"
    )
    assert log_entry["message"] == "아이템 목록 조회", (
        f"로그 message가 '아이템 목록 조회'여야 합니다. 현재: {log_entry['message']}"
    )
    print(f"✓ JSON 포맷 로그에 message 필드 존재: {log_entry['message']}")

    # 테스트 5: extra_data 필드 병합 확인
    assert "action" in log_entry, (
        f"로그에 action 필드가 없습니다. extra_data가 병합되지 않았습니다. 현재 필드: {list(log_entry.keys())}"
    )
    assert log_entry["action"] == "list_items", (
        f"action이 'list_items'여야 합니다. 현재: {log_entry['action']}"
    )
    assert "count" in log_entry, (
        f"로그에 count 필드가 없습니다. 현재 필드: {list(log_entry.keys())}"
    )
    assert log_entry["count"] == 3, (
        f"count가 3이어야 합니다. 현재: {log_entry['count']}"
    )
    print(f"✓ JSON 포맷 로그에 extra_data 필드가 병합됨: action={log_entry['action']}, count={log_entry['count']}")

    # === 문제 2 테스트: request_id 기반 요청 추적 ===

    list_handler.records.clear()

    # 테스트 6: GET /users/42 요청
    response = client.get("/users/42")
    assert response.status_code == 200, (
        f"GET /users/42의 상태 코드가 200이어야 합니다. 현재: {response.status_code}"
    )

    # 응답 헤더에 X-Request-ID 확인
    assert "x-request-id" in response.headers, (
        "응답 헤더에 X-Request-ID가 없습니다. request_id 미들웨어를 구현하세요."
    )
    header_request_id = response.headers["x-request-id"]
    print(f"✓ 응답 헤더에 X-Request-ID 포함: {header_request_id}")

    # 테스트 7: 로그에 request_id 확인
    assert len(list_handler.records) >= 1, (
        "로그가 기록되지 않았습니다. /users/{{user_id}} 엔드포인트에서 로그를 기록하세요."
    )
    log_entry = json.loads(list_handler.records[0])
    assert "request_id" in log_entry, (
        f"로그에 request_id 필드가 없습니다. extra_data에 request_id를 포함하세요. 현재 필드: {list(log_entry.keys())}"
    )
    print(f"✓ 로그에 request_id 필드 존재: {log_entry['request_id']}")

    # 테스트 8: 응답 본문에 request_id 확인
    body = response.json()
    assert "request_id" in body, (
        f"응답 본문에 request_id가 없습니다. 현재: {body}"
    )
    assert body["request_id"] == header_request_id, (
        f"응답 본문의 request_id가 헤더의 값과 일치해야 합니다. "
        f"본문: {body['request_id']}, 헤더: {header_request_id}"
    )
    print(f"✓ 응답 본문에 request_id 포함: {body['request_id']}")

    print("\n모든 테스트를 통과했습니다!")
