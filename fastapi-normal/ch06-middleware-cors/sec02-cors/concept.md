# 섹션 02: CORS 설정

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 미들웨어 기본 완료
> **예상 학습 시간**: 1시간

---

## 학습 목표

- CORS가 필요한 이유를 이해하고 설명할 수 있다
- FastAPI에서 `CORSMiddleware`를 사용하여 CORS를 설정할 수 있다
- Preflight 요청의 동작 방식을 이해할 수 있다
- `allow_origins=["*"]`의 보안 위험성을 인식할 수 있다

---

## CORS란?

**CORS(Cross-Origin Resource Sharing, 교차 출처 리소스 공유)**는
웹 브라우저가 **서로 다른 출처(Origin)**의 리소스에 접근할 수 있도록 허용하는 HTTP 메커니즘입니다.

### 출처(Origin)란?

출처는 **프로토콜 + 호스트 + 포트**의 조합입니다.

```
https://example.com:443
  │         │        │
프로토콜    호스트     포트
```

| URL A | URL B | 같은 출처? |
|-------|-------|-----------|
| `http://localhost:3000` | `http://localhost:8000` | ❌ 다른 출처 (포트 다름) |
| `http://example.com` | `https://example.com` | ❌ 다른 출처 (프로토콜 다름) |
| `https://api.example.com` | `https://example.com` | ❌ 다른 출처 (호스트 다름) |
| `https://example.com/page1` | `https://example.com/page2` | ✅ 같은 출처 |

### 왜 CORS가 필요한가?

일반적인 웹 개발 환경에서 프론트엔드와 백엔드는 서로 다른 포트에서 실행됩니다.

```
프론트엔드 (React)          백엔드 (FastAPI)
http://localhost:3000  →→→  http://localhost:8000
      │                              │
      └── 다른 출처(Origin)이므로 ──┘
          브라우저가 요청을 차단합니다!
```

브라우저는 보안상의 이유로 **동일 출처 정책(Same-Origin Policy)**을 적용하여,
다른 출처로의 요청을 기본적으로 **차단**합니다.
CORS를 설정하면 백엔드가 "이 출처에서 오는 요청은 허용한다"고 브라우저에 알려줄 수 있습니다.

> **중요**: CORS는 **브라우저**에서만 적용됩니다. `curl`이나 Postman 같은 도구는 CORS 제약이 없습니다.

---

## Preflight 요청

브라우저는 실제 요청을 보내기 전에, **OPTIONS 메서드**로 "이 요청을 보내도 되나요?"라고
서버에 먼저 확인합니다. 이것을 **Preflight(사전 검증) 요청**이라고 합니다.

```
브라우저                          서버
  │                                │
  │─── OPTIONS /api/data ────────→│   ← Preflight 요청
  │    Origin: http://localhost:3000
  │    Access-Control-Request-Method: POST
  │                                │
  │←── 200 OK ─────────────────────│   ← Preflight 응답
  │    Access-Control-Allow-Origin: http://localhost:3000
  │    Access-Control-Allow-Methods: POST
  │                                │
  │─── POST /api/data ───────────→│   ← 실제 요청
  │    Origin: http://localhost:3000
  │                                │
  │←── 200 OK ─────────────────────│   ← 실제 응답
  │    Access-Control-Allow-Origin: http://localhost:3000
```

### 언제 Preflight가 발생하나?

- `GET`, `HEAD`, `POST` 외의 메서드 사용 시
- `Content-Type`이 `application/json`인 경우
- 커스텀 헤더가 포함된 경우

---

## FastAPI에서 CORS 설정하기

### 핵심 코드

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 허용할 출처 목록
    allow_credentials=True,                    # 쿠키 포함 허용
    allow_methods=["*"],                       # 허용할 HTTP 메서드
    allow_headers=["*"],                       # 허용할 요청 헤더
)


@app.get("/api/data")
async def get_data():
    return {"message": "프론트엔드에서 접근 가능"}
```

### `CORSMiddleware` 주요 매개변수

| 매개변수 | 설명 | 예시 |
|----------|------|------|
| `allow_origins` | 허용할 출처 목록 | `["http://localhost:3000"]` |
| `allow_origin_regex` | 정규식으로 출처 허용 | `"https://.*\.example\.com"` |
| `allow_methods` | 허용할 HTTP 메서드 | `["GET", "POST"]` 또는 `["*"]` |
| `allow_headers` | 허용할 요청 헤더 | `["Authorization"]` 또는 `["*"]` |
| `allow_credentials` | 쿠키 포함 허용 여부 | `True` / `False` |
| `expose_headers` | 브라우저에 노출할 응답 헤더 | `["X-Custom-Header"]` |
| `max_age` | Preflight 캐시 시간(초) | `600` (10분) |

---

## 코드 예제: 프론트엔드와 통신을 위한 CORS 설정

### 개발 환경 설정

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 개발 환경에서 허용할 출처 목록
origins = [
    "http://localhost:3000",      # React 개발 서버
    "http://localhost:5173",      # Vite 개발 서버
    "http://127.0.0.1:3000",     # localhost 대체
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=600,  # Preflight 캐시 10분
)


@app.get("/api/users")
async def get_users():
    return [
        {"id": 1, "name": "홍길동"},
        {"id": 2, "name": "김철수"},
    ]


@app.post("/api/users")
async def create_user(name: str):
    return {"id": 3, "name": name}
```

### 운영 환경 설정

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 환경 변수에서 허용 출처를 읽어오는 패턴
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://myapp.com,https://www.myapp.com"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 보안 주의 사항

### `allow_origins=["*"]`의 위험성

```python
# ⚠️ 위험: 모든 출처를 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 아무 웹사이트에서나 API에 접근 가능!
)
```

| 상황 | `allow_origins=["*"]` | 출처 제한 |
|------|----------------------|----------|
| 개발 단계 | 편리하지만 습관 주의 | 권장 |
| 운영 환경 | ❌ 절대 사용 금지 | ✅ 반드시 사용 |
| 내부 API | ❌ 사용 금지 | ✅ 반드시 사용 |

**`allow_origins=["*"]`를 사용하면 안 되는 이유:**
1. 악의적인 웹사이트가 사용자의 브라우저를 통해 API에 접근할 수 있음
2. CSRF(Cross-Site Request Forgery) 공격에 취약해짐
3. `allow_credentials=True`와 함께 사용할 수 없음 (브라우저가 거부)

### 올바른 설정 원칙

```python
# ✅ 좋은 예: 필요한 출처만 명시적으로 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_methods=["GET", "POST"],          # 필요한 메서드만
    allow_headers=["Authorization"],        # 필요한 헤더만
    allow_credentials=True,
)
```

---

## 핵심 정리

1. **CORS**는 브라우저의 동일 출처 정책을 완화하여 다른 출처 간 통신을 허용하는 메커니즘이다
2. **Preflight 요청**은 브라우저가 OPTIONS 메서드로 서버에 사전 확인하는 것이다
3. `CORSMiddleware`의 `allow_origins`에 **허용할 출처를 명시적으로** 지정해야 한다
4. `allow_origins=["*"]`는 **개발 편의용일 뿐, 운영 환경에서는 절대 사용하지 않는다**
5. `allow_credentials=True`와 `allow_origins=["*"]`는 **동시에 사용할 수 없다**

---

## 다음 단계

[sec03-custom-middleware](../sec03-custom-middleware/concept.md)에서 클래스 기반 커스텀 미들웨어를 학습합니다.
