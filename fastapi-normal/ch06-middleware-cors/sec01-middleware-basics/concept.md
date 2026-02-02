# 섹션 01: 미들웨어 기본

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: Ch05 의존성 주입 완료
> **예상 학습 시간**: 1시간

---

## 학습 목표

- FastAPI 미들웨어의 동작 원리를 이해하고 기본 미들웨어를 작성할 수 있다
- `call_next`를 사용하여 요청 전처리와 응답 후처리를 구현할 수 있다
- 미들웨어 체인의 실행 순서를 설명할 수 있다

---

## 미들웨어란?

**미들웨어(Middleware)**는 모든 요청/응답에 대해 공통적으로 실행되는 코드입니다.
라우트 핸들러가 실행되기 **전**과 **후**에 추가적인 로직을 수행할 수 있습니다.

### 언제 미들웨어를 사용하나?

| 사용 사례 | 설명 |
|-----------|------|
| 로깅 | 모든 요청의 메서드, URL, 처리 시간 기록 |
| 인증/인가 | 요청 헤더에서 토큰 검증 |
| CORS | 크로스 오리진 요청에 대한 헤더 추가 |
| 에러 핸들링 | 예외를 잡아 일관된 에러 응답 반환 |
| 압축 | 응답 본문을 GZip으로 압축 |
| 커스텀 헤더 | 응답에 추가 메타데이터 헤더 삽입 |

---

## 핵심 개념

### 1. `@app.middleware("http")` 데코레이터

FastAPI에서 미들웨어를 가장 간단하게 작성하는 방법입니다.

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def my_middleware(request: Request, call_next):
    # ① 요청 전처리 (라우트 핸들러 실행 전)
    print(f"요청 도착: {request.method} {request.url}")

    # ② 다음 미들웨어 또는 라우트 핸들러 호출
    response = await call_next(request)

    # ③ 응답 후처리 (라우트 핸들러 실행 후)
    print(f"응답 상태: {response.status_code}")

    return response
```

### 2. `request` 객체

`Request` 객체에서 요청 정보를 읽을 수 있습니다.

| 속성/메서드 | 설명 | 예시 |
|-------------|------|------|
| `request.method` | HTTP 메서드 | `"GET"`, `"POST"` |
| `request.url` | 전체 URL | `http://localhost:8000/items?q=test` |
| `request.url.path` | URL 경로 | `/items` |
| `request.headers` | 요청 헤더 | `request.headers["user-agent"]` |
| `request.query_params` | 쿼리 매개변수 | `request.query_params["q"]` |
| `request.client.host` | 클라이언트 IP | `"127.0.0.1"` |

### 3. `call_next` 함수

`call_next`는 요청을 **다음 미들웨어** 또는 **라우트 핸들러**로 전달하는 함수입니다.
반드시 `await`와 함께 호출해야 하며, 반환값은 `Response` 객체입니다.

```python
# call_next를 호출하지 않으면 요청이 라우트 핸들러에 도달하지 않습니다!
response = await call_next(request)
```

### 4. `response` 객체

`call_next`에서 반환된 응답을 수정하거나, 추가 헤더를 붙일 수 있습니다.

```python
response = await call_next(request)
response.headers["X-Custom-Header"] = "커스텀 값"
return response
```

---

## 코드 예제 1: 요청 처리 시간 측정 미들웨어

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """모든 응답에 처리 시간(초)을 헤더로 추가하는 미들웨어"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    # 응답 헤더에 처리 시간 추가
    response.headers["X-Process-Time"] = str(round(process_time, 4))

    return response


@app.get("/")
async def root():
    return {"message": "안녕하세요"}


@app.get("/slow")
async def slow_endpoint():
    """일부러 느린 엔드포인트 (테스트용)"""
    import asyncio
    await asyncio.sleep(1)
    return {"message": "느린 응답"}
```

**테스트 결과:**
```bash
# /에 요청
curl -i http://localhost:8000/
# → X-Process-Time: 0.0003

# /slow에 요청
curl -i http://localhost:8000/slow
# → X-Process-Time: 1.0012
```

---

## 코드 예제 2: 커스텀 헤더 추가 미들웨어

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    """모든 응답에 서버 정보 헤더를 추가하는 미들웨어"""
    response = await call_next(request)

    # 서버 정보 헤더 추가
    response.headers["X-App-Version"] = "1.0.0"
    response.headers["X-Powered-By"] = "FastAPI"

    return response


@app.get("/info")
async def get_info():
    return {"name": "내 API", "version": "1.0.0"}
```

---

## 미들웨어 체인과 실행 순서

여러 미들웨어를 등록하면 **양파 껍질(Onion)** 구조로 동작합니다.
**나중에 등록된 미들웨어가 먼저 실행**됩니다 (LIFO: Last In, First Out).

```python
@app.middleware("http")
async def middleware_a(request: Request, call_next):
    print("A: 요청 전처리")    # ①
    response = await call_next(request)
    print("A: 응답 후처리")    # ⑥
    return response

@app.middleware("http")
async def middleware_b(request: Request, call_next):
    print("B: 요청 전처리")    # ②  (← B가 나중에 등록되었지만, 등록 역순으로 실행)
    response = await call_next(request)
    print("B: 응답 후처리")    # ⑤
    return response

# 주의: FastAPI에서는 @app.middleware 데코레이터로 등록 시
# 나중에 등록된 것이 바깥쪽 껍질이 됩니다.
```

### 실행 순서 다이어그램

```
요청 도착
    │
    ├─→ 미들웨어 B (전처리)     ← 나중에 등록된 미들웨어가 바깥쪽
    │       │
    │       ├─→ 미들웨어 A (전처리)
    │       │       │
    │       │       ├─→ 라우트 핸들러 실행
    │       │       │
    │       │       ├─→ 미들웨어 A (후처리)
    │       │
    │       ├─→ 미들웨어 B (후처리)
    │
    ├─→ 응답 반환
```

> **핵심 포인트**: `call_next(request)` 호출 **이전** 코드는 요청 시 실행되고,
> `call_next(request)` 호출 **이후** 코드는 응답 시 실행됩니다.

---

## 주의 사항

### 1. 미들웨어에서 요청 본문 읽기

미들웨어에서 `await request.body()`를 호출하면, 라우트 핸들러에서 본문을 다시 읽을 수 없습니다.
요청 본문은 **스트림**이므로 한 번만 읽을 수 있습니다.

```python
# ❌ 주의: 이렇게 하면 라우트 핸들러에서 본문을 읽을 수 없음
@app.middleware("http")
async def bad_middleware(request: Request, call_next):
    body = await request.body()  # 본문 소비됨!
    response = await call_next(request)
    return response
```

### 2. 미들웨어 vs 의존성 주입

| 특성 | 미들웨어 | 의존성 주입 (Depends) |
|------|----------|----------------------|
| 적용 범위 | **모든 요청** | 특정 라우트만 |
| 실행 시점 | 라우트 매칭 전 | 라우트 매칭 후 |
| 응답 수정 | 가능 | 불가능 |
| 사용 사례 | 로깅, CORS, 인증 헤더 | DB 세션, 권한 검사 |

---

## 핵심 정리

1. `@app.middleware("http")`로 미들웨어를 등록한다
2. `call_next(request)`를 호출하여 다음 단계로 요청을 전달한다
3. `call_next` **이전** 코드 = 요청 전처리, **이후** 코드 = 응답 후처리
4. 여러 미들웨어는 양파 껍질(Onion) 구조로 동작한다
5. 응답 헤더 추가, 로깅 등에 미들웨어를 활용할 수 있다

---

## 다음 단계

[sec02-cors](../sec02-cors/concept.md)에서 CORS 미들웨어 설정을 학습합니다.
