# sec02: 비동기 I/O 작업

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 async/await 기본 완료
> **예상 학습 시간**: 50~60분

---

## 학습 목표

- `asyncio.gather`를 사용하여 여러 비동기 작업을 동시에 실행할 수 있다
- 순차 실행과 동시 실행의 성능 차이를 이해하고 측정할 수 있다
- 비동기 I/O 작업에서의 에러 처리 방법을 이해할 수 있다

---

## 핵심 개념

### 1. 외부 API 호출과 비동기

실전에서 API 서버는 다른 서비스를 호출하는 경우가 많습니다.

```
사용자 요청 → [우리 서버] → [사용자 DB]
                          → [상품 DB]
                          → [결제 서비스]
                          → 모든 결과 합쳐서 응답
```

동기 방식으로 3개의 서비스를 각각 1초씩 호출하면 **총 3초**가 걸리지만,
비동기 방식으로 동시에 호출하면 **약 1초**로 줄일 수 있습니다.

### 2. httpx.AsyncClient (개념 소개)

실제 외부 API를 호출할 때는 `httpx` 라이브러리의 `AsyncClient`를 사용합니다.

```python
import httpx

async def fetch_user_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users")
        return response.json()
```

| 라이브러리 | 타입 | 사용 위치 |
|-----------|------|----------|
| `requests` | 동기 | `def` 함수 내부 |
| `httpx.AsyncClient` | 비동기 | `async def` 함수 내부 |
| `aiohttp` | 비동기 | `async def` 함수 내부 |

> **참고**: 이 연습에서는 외부 라이브러리 설치 없이 `asyncio.sleep`으로 I/O를 시뮬레이션합니다.

### 3. asyncio.gather - 동시 실행의 핵심

`asyncio.gather`는 여러 코루틴을 **동시에** 실행하고, 모든 결과를 모아서 반환합니다.

```python
import asyncio

async def fetch_users():
    await asyncio.sleep(1)  # 1초 걸리는 API 호출 시뮬레이션
    return {"users": ["홍길동", "김영희"]}

async def fetch_products():
    await asyncio.sleep(1)  # 1초 걸리는 API 호출 시뮬레이션
    return {"products": ["노트북", "마우스"]}

async def fetch_orders():
    await asyncio.sleep(1)  # 1초 걸리는 API 호출 시뮬레이션
    return {"orders": ["주문1", "주문2"]}

# 동시 실행: 3개를 동시에 → 약 1초 소요
users, products, orders = await asyncio.gather(
    fetch_users(),
    fetch_products(),
    fetch_orders(),
)
```

### 4. 순차 실행 vs 동시 실행 비교

```python
# ❌ 순차 실행: 총 3초 소요
async def sequential():
    users = await fetch_users()       # 1초
    products = await fetch_products() # 1초
    orders = await fetch_orders()     # 1초
    return users, products, orders    # 총 3초

# ✅ 동시 실행: 총 1초 소요
async def concurrent():
    users, products, orders = await asyncio.gather(
        fetch_users(),     # 1초 ─┐
        fetch_products(),  # 1초 ─┤ 동시 실행
        fetch_orders(),    # 1초 ─┘
    )
    return users, products, orders  # 총 1초
```

```
순차 실행 타이밍:
├─ fetch_users   ████████ (1초)
│                        ├─ fetch_products ████████ (1초)
│                                                  ├─ fetch_orders ████████ (1초)
총: ─────────────────────────────────────────────────────────────── 3초

동시 실행 타이밍:
├─ fetch_users   ████████ (1초)  ─┐
├─ fetch_products ████████ (1초) ─┤ 동시!
├─ fetch_orders  ████████ (1초)  ─┘
총: ──────────────────────── 1초
```

### 5. asyncio.gather의 에러 처리

기본적으로 `asyncio.gather`는 하나의 코루틴이 예외를 발생시키면 전체가 실패합니다.
`return_exceptions=True`를 사용하면 예외도 결과로 반환받을 수 있습니다.

```python
async def may_fail():
    raise ValueError("실패!")

async def will_succeed():
    return "성공"

# return_exceptions=False (기본값): 예외가 발생하면 전체 실패
try:
    results = await asyncio.gather(may_fail(), will_succeed())
except ValueError as e:
    print(f"에러: {e}")

# return_exceptions=True: 예외도 결과로 반환
results = await asyncio.gather(
    may_fail(),
    will_succeed(),
    return_exceptions=True,
)
# results = [ValueError("실패!"), "성공"]
```

### 6. 비동기 배치 처리

여러 아이템을 동시에 처리하는 패턴입니다.

```python
async def process_item(item_id: int) -> dict:
    """단일 아이템 처리"""
    await asyncio.sleep(0.5)  # I/O 시뮬레이션
    return {"id": item_id, "result": f"처리완료_{item_id}"}

async def batch_process(item_ids: list[int]) -> list[dict]:
    """여러 아이템을 동시에 처리"""
    tasks = [process_item(item_id) for item_id in item_ids]
    results = await asyncio.gather(*tasks)
    return list(results)

# 10개 아이템 처리: 순차 5초 → 동시 0.5초
results = await batch_process([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
```

---

## 코드 예제: 데이터 수집 시뮬레이션

```python
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()


async def fetch_from_source(source_name: str, delay: float) -> dict:
    """외부 데이터 소스에서 데이터를 가져오는 시뮬레이션"""
    await asyncio.sleep(delay)
    return {
        "source": source_name,
        "data": f"{source_name}에서 가져온 데이터",
    }


@app.get("/aggregate")
async def aggregate_data():
    """여러 소스에서 동시에 데이터를 수집"""
    start = time.time()

    users, products, orders = await asyncio.gather(
        fetch_from_source("사용자DB", 0.3),
        fetch_from_source("상품DB", 0.2),
        fetch_from_source("주문DB", 0.4),
    )

    elapsed = time.time() - start
    return {
        "users": users,
        "products": products,
        "orders": orders,
        "elapsed_seconds": round(elapsed, 2),
        # 동시 실행이므로 약 0.4초 (가장 긴 작업 기준)
    }
```

---

## 실전 패턴: async context manager

외부 클라이언트 연결은 보통 컨텍스트 매니저로 관리합니다.

```python
import httpx

# 실전에서의 사용 패턴 (httpx 설치 필요)
async def fetch_multiple_apis():
    async with httpx.AsyncClient() as client:
        # 여러 API를 동시에 호출
        tasks = [
            client.get("https://api.example.com/users"),
            client.get("https://api.example.com/products"),
            client.get("https://api.example.com/orders"),
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```

---

## 핵심 정리

1. `asyncio.gather`는 여러 코루틴을 동시에 실행하는 핵심 함수
2. 순차 실행(N초) → 동시 실행(가장 긴 작업 시간)으로 성능 개선
3. `return_exceptions=True`로 예외를 결과와 함께 받을 수 있음
4. 외부 API 호출은 `httpx.AsyncClient`를, 시뮬레이션은 `asyncio.sleep`을 사용
5. 배치 처리에서 `asyncio.gather`는 극적인 성능 향상을 가져옴

---

## 다음 단계

[sec03-background-tasks](../sec03-background-tasks/concept.md)에서 응답 후 실행되는 백그라운드 작업을 학습합니다.
