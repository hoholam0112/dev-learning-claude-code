# sec01: async/await 기본

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: Python 기본 문법, FastAPI 기본
> **예상 학습 시간**: 40~50분

---

## 학습 목표

- `async def`와 `def`의 차이를 FastAPI에서 설명할 수 있다
- `asyncio.sleep`과 `time.sleep`의 차이를 이해하고 올바르게 사용할 수 있다
- 이벤트 루프의 기본 개념을 이해할 수 있다

---

## 핵심 개념

### 1. 동기(Synchronous) vs 비동기(Asynchronous)

**동기 프로그래밍**은 코드가 순서대로 한 줄씩 실행됩니다.
하나의 작업이 완료될 때까지 다음 작업은 **기다려야** 합니다.

**비동기 프로그래밍**은 I/O 작업을 기다리는 동안 다른 작업을 처리할 수 있습니다.
`await` 키워드를 만나면 이벤트 루프에 제어권을 넘기고, 다른 대기 중인 작업을 실행합니다.

```python
# 동기 방식: 순서대로 실행 (총 3초)
import time

def sync_work():
    time.sleep(1)  # 1초 대기 (블로킹)
    time.sleep(1)  # 1초 대기 (블로킹)
    time.sleep(1)  # 1초 대기 (블로킹)

# 비동기 방식: 동시 실행 가능 (총 1초)
import asyncio

async def async_work():
    await asyncio.gather(
        asyncio.sleep(1),  # 1초 대기 (논블로킹)
        asyncio.sleep(1),  # 1초 대기 (논블로킹)
        asyncio.sleep(1),  # 1초 대기 (논블로킹)
    )
```

### 2. 이벤트 루프 (Event Loop)

이벤트 루프는 비동기 프로그래밍의 **핵심 엔진**입니다.
여러 비동기 작업을 관리하며, 준비된 작업을 순서대로 실행합니다.

```
이벤트 루프 동작 원리:

┌──────────────────────────────────────┐
│          이벤트 루프 (Event Loop)       │
│                                      │
│  1. 준비된 작업이 있는지 확인           │
│  2. 있으면 실행                        │
│  3. await를 만나면 다음 작업으로 이동    │
│  4. I/O 완료 알림을 받으면 재개          │
│  5. 1번으로 돌아감                     │
│                                      │
│  [작업A: 실행중] → await → [대기]       │
│  [작업B: 대기]   → [실행중] → await     │
│  [작업C: 대기]   → [대기]   → [실행중]  │
└──────────────────────────────────────┘
```

### 3. FastAPI에서 `def` vs `async def`

FastAPI에서는 엔드포인트 함수를 `def` 또는 `async def`로 정의할 수 있습니다.
각각의 동작 방식이 다릅니다.

| 특성 | `def` (동기) | `async def` (비동기) |
|------|-------------|---------------------|
| 실행 환경 | 별도 스레드 풀 | 이벤트 루프 (메인 스레드) |
| I/O 대기 시 | 해당 스레드 블로킹 | 이벤트 루프에 제어권 반환 |
| `await` 사용 | 불가 | 가능 |
| 적합한 경우 | CPU 바운드 작업, 동기 라이브러리 사용 | I/O 바운드 작업, async 라이브러리 사용 |
| 동시성 | 스레드 풀 크기만큼 | 수천 개의 동시 연결 가능 |

```python
from fastapi import FastAPI
import asyncio
import time

app = FastAPI()

# ✅ 비동기 엔드포인트: 이벤트 루프에서 직접 실행
@app.get("/async-endpoint")
async def async_endpoint():
    await asyncio.sleep(1)  # 논블로킹 대기
    return {"type": "async", "message": "비동기 완료"}

# ✅ 동기 엔드포인트: 스레드 풀에서 실행
@app.get("/sync-endpoint")
def sync_endpoint():
    time.sleep(1)  # 블로킹 대기 (스레드 풀에서 실행되므로 괜찮음)
    return {"type": "sync", "message": "동기 완료"}
```

> **중요**: `async def` 안에서 `time.sleep()`을 호출하면 이벤트 루프 전체가 블로킹됩니다!
> 비동기 함수에서는 반드시 `await asyncio.sleep()`을 사용하세요.

### 4. `asyncio.sleep` vs `time.sleep`

| 특성 | `asyncio.sleep(n)` | `time.sleep(n)` |
|------|-------------------|-----------------|
| 타입 | 코루틴 (비동기) | 일반 함수 (동기) |
| 사용법 | `await asyncio.sleep(n)` | `time.sleep(n)` |
| 블로킹 | 논블로킹 (이벤트 루프 계속 실행) | 블로킹 (스레드 정지) |
| 사용 위치 | `async def` 함수 내부 | `def` 함수 내부 |

```python
# ❌ 나쁜 예: async def 안에서 time.sleep 사용
@app.get("/bad")
async def bad_endpoint():
    time.sleep(5)  # 이벤트 루프 전체가 5초간 멈춤!
    return {"message": "나쁜 예"}

# ✅ 좋은 예: async def 안에서 asyncio.sleep 사용
@app.get("/good")
async def good_endpoint():
    await asyncio.sleep(5)  # 5초 대기 중 다른 요청 처리 가능
    return {"message": "좋은 예"}

# ✅ 좋은 예: def 안에서 time.sleep 사용
@app.get("/also-good")
def also_good_endpoint():
    time.sleep(5)  # 별도 스레드에서 실행되므로 괜찮음
    return {"message": "이것도 괜찮음"}
```

### 5. 코루틴 (Coroutine)

`async def`로 정의한 함수는 **코루틴 함수**이며, 호출하면 **코루틴 객체**를 반환합니다.
코루틴은 `await`로 실행해야 합니다.

```python
async def fetch_data():
    await asyncio.sleep(1)
    return {"data": "결과"}

# 코루틴 함수 호출 -> 코루틴 객체 생성 (아직 실행되지 않음)
coro = fetch_data()  # <coroutine object fetch_data at 0x...>

# await로 실행
result = await coro  # 이제 실행됨 → {"data": "결과"}
```

---

## 코드 예제 1: async/await 기본 사용

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()


@app.get("/sync")
def sync_hello():
    """동기 엔드포인트: 스레드 풀에서 실행"""
    return {"message": "안녕하세요 (동기)", "type": "sync"}


@app.get("/async")
async def async_hello():
    """비동기 엔드포인트: 이벤트 루프에서 실행"""
    await asyncio.sleep(0)  # 이벤트 루프에 제어권 양보
    return {"message": "안녕하세요 (비동기)", "type": "async"}
```

---

## 코드 예제 2: 비동기 데이터 처리

```python
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()


async def process_item(item: str) -> dict:
    """아이템을 비동기적으로 처리 (I/O 시뮬레이션)"""
    await asyncio.sleep(0.1)  # 0.1초 I/O 시뮬레이션
    return {"item": item, "status": "processed"}


@app.get("/process")
async def process_items():
    """여러 아이템을 비동기적으로 처리"""
    items = ["아이템A", "아이템B", "아이템C"]
    start = time.time()

    # 모든 아이템을 동시에 처리
    results = await asyncio.gather(
        *[process_item(item) for item in items]
    )

    elapsed = time.time() - start
    return {
        "results": results,
        "elapsed_seconds": round(elapsed, 2),
        "message": "3개 아이템이 동시에 처리되어 약 0.1초 소요"
    }
```

---

## FastAPI의 내부 동작

```
클라이언트 요청 → uvicorn (ASGI 서버)
                    │
                    ├─ async def 엔드포인트 → 이벤트 루프에서 직접 실행
                    │   └─ await 만나면 → 다른 요청 처리 가능
                    │
                    └─ def 엔드포인트 → 스레드 풀로 위임
                        └─ 블로킹 I/O 사용 가능 (다른 스레드에서 실행)
```

> **실전 가이드**:
> - 비동기 라이브러리(asyncio, aiohttp, asyncpg 등)를 사용하면 → `async def`
> - 동기 라이브러리(requests, psycopg2, SQLAlchemy 동기 모드)를 사용하면 → `def`
> - 단순 연산만 하는 경우 → 둘 다 상관없음 (성능 차이 미미)

---

## 핵심 정리

1. `async def`는 이벤트 루프에서 직접 실행되며, `await`을 사용할 수 있다
2. `def`는 FastAPI가 자동으로 스레드 풀에서 실행한다
3. `async def` 안에서 `time.sleep()` 같은 블로킹 호출은 절대 금지
4. `asyncio.sleep()`은 논블로킹이므로 `async def`에서 안전하게 사용 가능
5. FastAPI는 두 가지 방식을 모두 지원하므로, 사용하는 라이브러리에 맞게 선택

---

## 다음 단계

[sec02-async-io-operations](../sec02-async-io-operations/concept.md)에서 비동기 I/O 작업과 동시 실행을 학습합니다.
