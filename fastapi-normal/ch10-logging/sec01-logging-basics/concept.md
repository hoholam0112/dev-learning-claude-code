# 섹션 01: 로깅 기본

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: Ch06 미들웨어와 CORS 완료
> **예상 학습 시간**: 1시간

---

## 학습 목표

- Python `logging` 모듈의 기본 구조를 이해하고 사용할 수 있다
- 로그 레벨(DEBUG, INFO, WARNING, ERROR, CRITICAL)의 차이를 설명할 수 있다
- Logger, Handler, Formatter의 관계를 이해할 수 있다
- `print()` 대신 `logging`을 사용해야 하는 이유를 설명할 수 있다

---

## print vs logging

### `print()`의 한계

```python
# ❌ 운영 환경에서 문제가 되는 패턴
def create_user(name: str):
    print(f"사용자 생성 시작: {name}")       # 어떤 레벨? 언제 발생?
    print(f"DB에 저장 완료")                  # 끄고 싶으면?
    print(f"에러 발생: ...")                   # 파일에 기록하려면?
```

### `logging`의 장점

```python
import logging

logger = logging.getLogger(__name__)

# ✅ 체계적인 로깅
def create_user(name: str):
    logger.info("사용자 생성 시작: %s", name)     # INFO 레벨
    logger.debug("DB 쿼리 실행 중...")             # DEBUG 레벨 (운영 시 숨김)
    logger.error("사용자 생성 실패: %s", name)     # ERROR 레벨 (항상 표시)
```

| 비교 항목 | `print()` | `logging` |
|-----------|-----------|-----------|
| 레벨 구분 | 없음 | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| 출력 제어 | 코드 수정 필요 | 설정으로 제어 |
| 출력 대상 | stdout만 | 콘솔, 파일, 네트워크 등 |
| 타임스탬프 | 수동 추가 | 자동 포함 가능 |
| 포맷 지정 | 수동 | Formatter로 일괄 지정 |
| 멀티모듈 | 관리 어려움 | 모듈별 로거 |

---

## 핵심 개념

### 1. 로그 레벨

Python `logging`은 5가지 기본 로그 레벨을 제공합니다.

| 레벨 | 숫자 값 | 용도 | 예시 |
|------|---------|------|------|
| `DEBUG` | 10 | 상세한 디버깅 정보 | 변수 값, SQL 쿼리 내용 |
| `INFO` | 20 | 일반적인 정보 | 서버 시작, 요청 처리 완료 |
| `WARNING` | 30 | 주의가 필요한 상황 | 디스크 용량 부족 경고 |
| `ERROR` | 40 | 에러 발생 | DB 연결 실패, API 호출 실패 |
| `CRITICAL` | 50 | 치명적 에러 | 시스템 다운, 데이터 손실 |

```python
import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)  # DEBUG 이상 모든 레벨 허용

logger.debug("디버깅 정보")      # 레벨 10
logger.info("일반 정보")         # 레벨 20
logger.warning("경고 메시지")    # 레벨 30
logger.error("에러 발생")        # 레벨 40
logger.critical("치명적 에러")   # 레벨 50
```

> **핵심**: 로거의 레벨을 `WARNING`으로 설정하면, `DEBUG`와 `INFO` 메시지는 출력되지 않습니다.

### 2. Logger, Handler, Formatter 관계

```
┌─────────────────────────────────────────────┐
│ Logger (로거)                                │
│  - 로그 메시지를 생성하고 Handler에 전달       │
│  - 이름(name)으로 계층 구조 형성              │
│  - 최소 로그 레벨 설정                        │
├─────────────────────────────────────────────┤
│ Handler (핸들러)                              │
│  - 로그를 어디로 보낼지 결정                   │
│  - StreamHandler: 콘솔 출력                   │
│  - FileHandler: 파일 기록                     │
│  - 각 핸들러마다 별도 레벨 설정 가능           │
├─────────────────────────────────────────────┤
│ Formatter (포매터)                            │
│  - 로그의 출력 형식을 결정                     │
│  - 타임스탬프, 레벨, 메시지 등의 배치          │
└─────────────────────────────────────────────┘
```

```python
import logging

# 1. 로거 생성
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# 2. 핸들러 생성 (콘솔 출력)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)  # 핸들러는 INFO 이상만 출력

# 3. 포매터 생성
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 4. 핸들러에 포매터 연결
handler.setFormatter(formatter)

# 5. 로거에 핸들러 추가
logger.addHandler(handler)

# 사용
logger.info("서버가 시작되었습니다")
# 출력: 2024-01-15 10:30:00,123 - myapp - INFO - 서버가 시작되었습니다
```

### 3. Formatter 포맷 문자열

자주 사용하는 포맷 속성:

| 속성 | 형식 | 설명 |
|------|------|------|
| `%(asctime)s` | `2024-01-15 10:30:00,123` | 로그 생성 시간 |
| `%(name)s` | `myapp` | 로거 이름 |
| `%(levelname)s` | `INFO` | 로그 레벨 이름 |
| `%(message)s` | `서버 시작` | 로그 메시지 |
| `%(filename)s` | `main.py` | 소스 파일명 |
| `%(lineno)d` | `42` | 소스 라인 번호 |
| `%(funcName)s` | `create_user` | 함수 이름 |

---

## FastAPI에서 logging 사용하기

### 기본 패턴

```python
import logging
from fastapi import FastAPI

# 로거 설정
logger = logging.getLogger("myapi")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    logger.info("사용자 조회 요청: user_id=%d", user_id)

    if user_id <= 0:
        logger.warning("잘못된 user_id: %d", user_id)
        return {"error": "잘못된 사용자 ID"}

    logger.debug("DB에서 사용자 검색 중...")
    return {"user_id": user_id, "name": "홍길동"}
```

### 미들웨어에서 로깅 활용

```python
import time
import logging
from fastapi import FastAPI, Request

logger = logging.getLogger("myapi")

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info("요청 시작: %s %s", request.method, request.url.path)

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        "요청 완료: %s %s - 상태: %d - 소요: %.3fs",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    return response
```

---

## 테스트에서의 로그 캡처

테스트 시에는 로그 메시지를 리스트에 수집하여 검증할 수 있습니다.

```python
import logging


class ListHandler(logging.Handler):
    """테스트용: 로그 레코드를 리스트에 저장하는 핸들러"""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(self.format(record))


# 사용 예
logger = logging.getLogger("test")
handler = ListHandler()
handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(handler)

logger.info("테스트 메시지")
assert handler.records[0] == "INFO - 테스트 메시지"
```

---

## 핵심 정리

1. `print()` 대신 `logging`을 사용하면 레벨 제어, 출력 대상 설정, 포맷 지정이 가능하다
2. 로그 레벨은 `DEBUG < INFO < WARNING < ERROR < CRITICAL` 순서이다
3. **Logger**는 메시지를 생성하고, **Handler**는 출력 대상을, **Formatter**는 출력 형식을 결정한다
4. `logging.getLogger(name)`으로 이름 기반의 로거를 생성한다
5. 하나의 로거에 여러 핸들러를 추가하여 다양한 출력 대상에 동시에 로그를 남길 수 있다

---

## 다음 단계

[sec02-structured-logging](../sec02-structured-logging/concept.md)에서 JSON 포맷의 구조화된 로깅을 학습합니다.
