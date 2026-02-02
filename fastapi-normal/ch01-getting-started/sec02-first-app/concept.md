# 섹션 02: 첫 번째 FastAPI 앱

> **난이도**: ⭐ (1/5)
> **선수 지식**: sec01 완료 (FastAPI 설치됨)
> **학습 목표**: FastAPI 인스턴스를 생성하고 기본 엔드포인트를 작성할 수 있다

---

## 핵심 개념

### 1. FastAPI 인스턴스 생성

FastAPI 앱은 `FastAPI()` 클래스의 인스턴스를 만드는 것에서 시작합니다.
이 인스턴스가 모든 API의 진입점(entry point)이 됩니다.

```python
from fastapi import FastAPI

# FastAPI 앱 인스턴스 생성
app = FastAPI()
```

`app`이라는 변수명은 관례적으로 사용됩니다. 나중에 서버를 실행할 때 이 이름을 참조합니다.

---

### 2. 경로 함수 (Path Operation Function)

FastAPI에서는 **데코레이터**를 사용하여 URL 경로와 HTTP 메서드를 함수에 연결합니다.

```python
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
```

위 코드를 분석하면:

| 요소 | 설명 |
|------|------|
| `@app.get` | HTTP GET 메서드를 사용하겠다는 의미 |
| `"/"` | URL 경로 (루트 경로) |
| `def read_root()` | 이 경로로 요청이 오면 실행될 함수 |
| `return {"message": ...}` | 딕셔너리를 반환하면 자동으로 JSON 응답이 됨 |

#### HTTP 메서드별 데코레이터

```python
@app.get("/items")       # GET: 데이터 조회
@app.post("/items")      # POST: 데이터 생성
@app.put("/items/{id}")  # PUT: 데이터 전체 수정
@app.patch("/items/{id}")# PATCH: 데이터 부분 수정
@app.delete("/items/{id}")# DELETE: 데이터 삭제
```

> 이 챕터에서는 GET 메서드만 다룹니다. 나머지는 이후 챕터에서 학습합니다.

---

### 3. JSON 응답

FastAPI는 Python 딕셔너리를 반환하면 **자동으로 JSON 형식**으로 변환해줍니다.

```python
@app.get("/info")
def get_info():
    # Python 딕셔너리
    return {
        "name": "FastAPI",
        "version": "0.115.0",
        "features": ["빠름", "쉬움", "자동 문서화"]
    }
```

위 함수의 응답 (JSON):
```json
{
    "name": "FastAPI",
    "version": "0.115.0",
    "features": ["빠름", "쉬움", "자동 문서화"]
}
```

리스트, 문자열, 숫자 등도 반환할 수 있습니다:
```python
@app.get("/items")
def get_items():
    return [{"id": 1, "name": "사과"}, {"id": 2, "name": "바나나"}]

@app.get("/count")
def get_count():
    return 42  # 숫자도 가능
```

---

### 4. 경로 매개변수 (Path Parameters)

URL 경로에 중괄호(`{}`)를 사용하면 **동적 경로**를 만들 수 있습니다.

```python
@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"안녕하세요, {name}님!"}
```

- `/greet/홍길동` 으로 요청하면 `name`에 `"홍길동"`이 들어갑니다.
- `/greet/Alice` 로 요청하면 `name`에 `"Alice"`가 들어갑니다.

> 경로 매개변수는 다음 챕터(Ch02)에서 더 자세히 다룹니다.

---

### 5. 요청-응답 흐름

FastAPI에서 요청이 처리되는 전체 흐름입니다:

```
┌─────────────┐    HTTP 요청     ┌──────────────┐    경로 매칭    ┌──────────────┐
│             │  GET /hello     │              │  @app.get()   │              │
│  클라이언트  │ ──────────────→ │   Uvicorn    │ ────────────→ │   FastAPI    │
│  (브라우저)  │                 │   (서버)      │               │   (앱)       │
│             │ ←────────────── │              │ ←──────────── │              │
└─────────────┘   JSON 응답     └──────────────┘   dict 반환    └──────────────┘
                 {"message":                                    def hello():
                  "안녕하세요"}                                    return {...}
```

**단계별 설명:**
1. 클라이언트(브라우저)가 `GET /hello` 요청을 보냅니다.
2. Uvicorn 서버가 요청을 받아 FastAPI 앱으로 전달합니다.
3. FastAPI는 URL 경로(`/hello`)와 HTTP 메서드(`GET`)를 보고 해당하는 함수를 찾습니다.
4. 함수가 실행되고 딕셔너리를 반환합니다.
5. FastAPI가 딕셔너리를 JSON으로 변환하여 클라이언트에 응답합니다.

---

## 코드 예제: Hello World API

### 완전한 Hello World 앱

```python
# main.py
from fastapi import FastAPI

# 1. FastAPI 인스턴스 생성
app = FastAPI()


# 2. 루트 경로 엔드포인트
@app.get("/")
def read_root():
    """루트 경로 - API의 기본 정보를 반환합니다."""
    return {"message": "Hello, FastAPI!", "docs": "/docs"}


# 3. 인사 엔드포인트
@app.get("/hello")
def say_hello():
    """간단한 인사 메시지를 반환합니다."""
    return {"message": "안녕하세요, FastAPI!"}


# 4. 이름으로 인사하는 엔드포인트
@app.get("/hello/{name}")
def say_hello_to(name: str):
    """특정 이름으로 인사합니다."""
    return {"message": f"안녕하세요, {name}님!"}
```

### 실행 방법

```bash
# 서버 실행 (개발 모드)
uvicorn main:app --reload
```

- `main`: 파일 이름 (main.py)
- `app`: FastAPI 인스턴스 변수명
- `--reload`: 코드 변경 시 자동 재시작

### 테스트 방법

서버가 실행되면 브라우저에서:
- `http://localhost:8000/` - 루트 경로
- `http://localhost:8000/hello` - 인사 메시지
- `http://localhost:8000/hello/홍길동` - 이름으로 인사

또는 터미널에서 curl 사용:
```bash
curl http://localhost:8000/hello
# 결과: {"message":"안녕하세요, FastAPI!"}

curl http://localhost:8000/hello/홍길동
# 결과: {"message":"안녕하세요, 홍길동님!"}
```

---

## 자동 문서 페이지

FastAPI의 가장 강력한 기능 중 하나는 **자동 API 문서**입니다.
코드를 작성하기만 하면 문서가 자동으로 생성됩니다!

### Swagger UI (`/docs`)

```
http://localhost:8000/docs
```

- **인터랙티브 문서**: 브라우저에서 바로 API를 테스트할 수 있습니다.
- "Try it out" 버튼을 클릭하면 요청을 보낼 수 있습니다.
- 요청/응답 예시를 확인할 수 있습니다.

### ReDoc (`/redoc`)

```
http://localhost:8000/redoc
```

- **읽기 전용 문서**: 깔끔한 레이아웃의 API 문서입니다.
- API를 공유하거나 문서화할 때 유용합니다.
- 세 개의 패널(목차, 설명, 코드 예시)로 구성됩니다.

### OpenAPI 스키마 (`/openapi.json`)

```
http://localhost:8000/openapi.json
```

- Swagger UI와 ReDoc의 원본 데이터입니다.
- OpenAPI 3.0 표준 형식의 JSON 파일입니다.
- 다른 도구(Postman 등)에서 import할 수 있습니다.

---

## TestClient를 활용한 테스트

서버를 실행하지 않고도 코드를 테스트할 수 있습니다.
FastAPI는 `TestClient`를 제공합니다.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/hello")
def say_hello():
    return {"message": "안녕하세요!"}


# 테스트
client = TestClient(app)
response = client.get("/hello")

print(response.status_code)  # 200
print(response.json())       # {"message": "안녕하세요!"}
```

`TestClient`는 실제 HTTP 서버를 띄우지 않고 앱을 직접 호출합니다.
이를 통해 `exercise.py`에서 `python exercise.py`만으로 테스트할 수 있습니다.

---

## 정리

| 개념 | 설명 | 예시 |
|------|------|------|
| `FastAPI()` | 앱 인스턴스 생성 | `app = FastAPI()` |
| `@app.get(경로)` | GET 엔드포인트 정의 | `@app.get("/hello")` |
| 경로 함수 | 요청을 처리하는 함수 | `def hello(): return {...}` |
| 경로 매개변수 | URL에 동적 값 포함 | `"/greet/{name}"` |
| JSON 응답 | 딕셔너리 → 자동 JSON 변환 | `return {"key": "value"}` |
| `/docs` | Swagger UI 자동 문서 | 인터랙티브 테스트 가능 |
| `/redoc` | ReDoc 자동 문서 | 읽기 전용 문서 |
| `TestClient` | 서버 없이 테스트 | `client.get("/hello")` |

---

## 다음 단계

첫 번째 앱을 만들었으니, 다음 섹션에서 개발 서버를 더 자세히 알아보겠습니다!

> [sec03-dev-server: 개발 서버 활용](../sec03-dev-server/concept.md)
