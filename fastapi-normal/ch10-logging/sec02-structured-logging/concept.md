# 섹션 02: 구조화된 로깅

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 로깅 기본 완료
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

- JSON 포맷의 구조화된 로그를 생성할 수 있다
- request_id를 사용하여 요청 단위로 로그를 추적할 수 있다
- 미들웨어와 연계한 컨텍스트 로깅을 구현할 수 있다
- 구조화된 로그의 장점을 설명할 수 있다

---

## 왜 구조화된 로깅인가?

### 일반 로그 vs 구조화된 로그

```
# 일반 텍스트 로그 (파싱 어려움)
2024-01-15 10:30:00 - INFO - 사용자 조회 완료: user_id=42, 소요시간=0.023초

# JSON 구조화 로그 (파싱 용이, 검색 가능)
{"timestamp": "2024-01-15T10:30:00", "level": "INFO", "message": "사용자 조회 완료", "user_id": 42, "duration": 0.023}
```

| 비교 항목 | 텍스트 로그 | 구조화된 로그 |
|-----------|------------|--------------|
| 검색/필터링 | 정규식 필요 | 필드 기반 검색 |
| 분석 도구 연동 | 파서 필요 | 바로 사용 가능 |
| 추가 컨텍스트 | 문자열 조합 | 필드 추가 |
| 로그 집계 시스템 | 복잡한 파싱 | JSON 파싱 |
| 일관성 | 포맷 불일치 가능 | 항상 동일 구조 |

---

## 핵심 개념

### 1. JSON Formatter 만들기

Python `logging`의 `Formatter`를 상속하여 JSON 포맷으로 출력하는 커스텀 포매터를 만들 수 있습니다.

```python
import json
import logging
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """로그를 JSON 형식으로 포맷하는 커스텀 포매터"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # extra 필드가 있으면 추가
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)
```

### 2. Extra 데이터 전달하기

로그 메시지에 추가 컨텍스트를 포함하는 방법:

```python
# 방법 1: extra 파라미터 사용
logger.info("사용자 조회", extra={"extra_data": {"user_id": 42}})

# 방법 2: LoggerAdapter 사용
adapter = logging.LoggerAdapter(logger, extra={"extra_data": {"service": "api"}})
adapter.info("서비스 시작")
```

### 3. request_id를 이용한 요청 추적

마이크로서비스 환경에서는 하나의 사용자 요청이 여러 서비스를 거칠 수 있습니다.
`request_id`를 사용하면 관련된 모든 로그를 추적할 수 있습니다.

```
# 같은 request_id로 묶인 로그들
{"request_id": "abc-123", "message": "요청 수신", "path": "/users/1"}
{"request_id": "abc-123", "message": "DB 쿼리 실행", "query": "SELECT ..."}
{"request_id": "abc-123", "message": "응답 전송", "status": 200}
```

---

## 코드 예제 1: JSON 포맷 로거

```python
import json
import logging
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Request

app = FastAPI()


class JSONFormatter(logging.Formatter):
    """JSON 포맷 로그 포매터"""

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
logger = logging.getLogger("structured")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info(
        "사용자 조회",
        extra={"extra_data": {"user_id": user_id, "action": "get_user"}},
    )
    return {"user_id": user_id, "name": "홍길동"}
```

---

## 코드 예제 2: request_id 미들웨어

```python
import uuid
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """모든 요청에 고유 request_id를 부여하는 미들웨어"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/api/data")
async def get_data(request: Request):
    request_id = request.state.request_id
    logger.info(
        "데이터 조회",
        extra={"extra_data": {"request_id": request_id}},
    )
    return {"data": "샘플", "request_id": request_id}
```

---

## 핵심 정리

1. **JSON Formatter**를 만들어 로그를 구조화된 형식으로 출력할 수 있다
2. `extra` 파라미터를 사용하여 로그에 **추가 컨텍스트**를 포함할 수 있다
3. **request_id**를 미들웨어에서 생성하여 요청 단위 추적이 가능하다
4. 구조화된 로그는 **검색, 필터링, 분석**이 텍스트 로그보다 훨씬 용이하다
5. `request.state`를 활용하여 미들웨어와 핸들러 간 **컨텍스트를 공유**할 수 있다

---

## 다음 단계

[sec03-logging-configuration](../sec03-logging-configuration/concept.md)에서 `dictConfig`를 사용한 체계적인 로깅 설정을 학습합니다.
