# 섹션 03: 개발 서버 활용

> **난이도**: ⭐ (1/5)
> **선수 지식**: sec01, sec02 완료
> **학습 목표**: Uvicorn 개발 서버를 설정하고 핫 리로드를 활용할 수 있다

---

## 핵심 개념

### 1. Uvicorn 개발 서버

Uvicorn은 Python ASGI 웹 서버입니다. FastAPI 앱을 실행하려면 반드시 서버가 필요하며, 개발 단계에서는 Uvicorn을 사용합니다.

#### 기본 실행

```bash
uvicorn main:app
```

이 명령어의 의미:
- `main` : Python 파일 이름 (main.py에서 `.py`를 뺀 것)
- `app` : FastAPI 인스턴스 변수명
- `:` : 파일과 변수를 구분하는 구분자

```
uvicorn 파일이름:변수이름
         │          │
         │          └── app = FastAPI()의 'app'
         └── main.py의 'main'
```

#### 하위 디렉토리의 파일 실행

```bash
# src/server.py 안에 my_app = FastAPI()가 있는 경우
uvicorn src.server:my_app
```

---

### 2. 핫 리로드 (--reload)

`--reload` 옵션은 코드가 변경되면 **서버를 자동으로 재시작**합니다.
개발 중에 코드를 수정할 때마다 서버를 수동으로 껐다 켤 필요가 없습니다.

```bash
# 핫 리로드 활성화 (개발 모드)
uvicorn main:app --reload
```

```
코드 수정 → 파일 저장 → Uvicorn이 변경 감지 → 서버 자동 재시작
                                                    │
                                              1~2초 내에 완료
```

> **주의**: `--reload`는 개발 환경에서만 사용하세요.
> 프로덕션(배포) 환경에서는 성능 저하가 발생할 수 있습니다.

---

### 3. 호스트와 포트 설정

#### `--host`: 접근 허용 범위 설정

```bash
# 기본값: 127.0.0.1 (로컬에서만 접근 가능)
uvicorn main:app --host 127.0.0.1

# 모든 네트워크에서 접근 가능 (같은 네트워크의 다른 기기에서도)
uvicorn main:app --host 0.0.0.0
```

| 호스트 | 의미 | 사용 상황 |
|--------|------|-----------|
| `127.0.0.1` | 로컬만 접근 | 혼자 개발할 때 (기본값) |
| `0.0.0.0` | 모든 네트워크 접근 | 같은 네트워크의 다른 기기에서 테스트할 때 |

#### `--port`: 포트 번호 변경

```bash
# 기본값: 8000
uvicorn main:app --port 8000

# 다른 포트 사용
uvicorn main:app --port 3000
uvicorn main:app --port 8080
```

> 포트가 이미 사용 중이면 오류가 발생합니다.
> 이 경우 다른 포트 번호를 지정하세요.

#### 옵션 조합

```bash
# 가장 많이 사용하는 개발 실행 명령어
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### 4. `fastapi dev` 명령어

FastAPI 0.111.0 이상에서는 `fastapi` CLI 명령어를 사용할 수 있습니다.
`fastapi[standard]`를 설치했다면 이 명령어를 사용할 수 있습니다.

```bash
# 개발 모드로 실행 (--reload 자동 활성화)
fastapi dev main.py

# 프로덕션 모드로 실행
fastapi run main.py
```

#### `fastapi dev` vs `uvicorn --reload` 비교

| 항목 | `fastapi dev` | `uvicorn main:app --reload` |
|------|---------------|----------------------------|
| 핫 리로드 | 자동 활성화 | `--reload` 옵션 필요 |
| 호스트 | 기본 `127.0.0.1` | 기본 `127.0.0.1` |
| 포트 | 기본 `8000` | 기본 `8000` |
| 파일 지정 | `main.py` (파일명) | `main:app` (모듈:변수) |
| 디버그 로그 | 자동 활성화 | 별도 설정 필요 |

```bash
# 두 명령어는 거의 동일한 결과를 냅니다
fastapi dev main.py
# ≈
uvicorn main:app --reload
```

> **팁**: `fastapi dev`가 더 간편하지만, `uvicorn` 명령어를 알아두면
> 세밀한 설정이 필요할 때 유용합니다.

---

### 5. 자동 문서 페이지

FastAPI는 두 가지 자동 문서를 제공합니다. 서버를 실행한 후 브라우저에서 접근할 수 있습니다.

#### Swagger UI (`/docs`)

```
http://localhost:8000/docs
```

**특징:**
- 인터랙티브(대화형) 문서
- "Try it out" 버튼으로 실시간 API 테스트 가능
- 요청 매개변수를 직접 입력하고 실행 가능
- 응답 코드, 헤더, 본문을 확인 가능

**사용 방법:**
1. `/docs`에 접속합니다.
2. 테스트할 엔드포인트를 클릭합니다.
3. "Try it out" 버튼을 클릭합니다.
4. 필요한 매개변수를 입력합니다.
5. "Execute" 버튼을 클릭합니다.
6. 아래에서 응답 결과를 확인합니다.

#### ReDoc (`/redoc`)

```
http://localhost:8000/redoc
```

**특징:**
- 읽기 전용 문서 (테스트 기능 없음)
- 깔끔하고 전문적인 레이아웃
- 세 개의 패널: 왼쪽(목차), 가운데(설명), 오른쪽(코드 예시)
- API 문서를 외부에 공유할 때 적합

#### Swagger UI vs ReDoc 비교

| 항목 | Swagger UI (`/docs`) | ReDoc (`/redoc`) |
|------|---------------------|------------------|
| API 테스트 | 가능 (Try it out) | 불가능 |
| 레이아웃 | 단일 컬럼 | 3단 컬럼 |
| 주 용도 | 개발 중 테스트 | 문서 공유/배포 |
| 코드 예시 | curl 명령어 제공 | 다양한 언어 코드 예시 |

---

## 코드 예제

### 앱 메타데이터 설정

FastAPI 인스턴스에 앱 정보를 설정하면 자동 문서에 반영됩니다.

```python
from fastapi import FastAPI

app = FastAPI(
    title="나의 학습 API",
    description="FastAPI 학습용 API 서버입니다.",
    version="0.1.0",
)
```

Swagger UI(`/docs`)에 접속하면 제목과 설명이 표시됩니다.

#### 더 많은 메타데이터 옵션

```python
app = FastAPI(
    title="나의 학습 API",
    description="""
    ## FastAPI 학습용 API 서버

    이 API는 다음 기능을 제공합니다:
    - 기본 인사 기능
    - 헬스 체크
    """,
    version="0.1.0",
    contact={
        "name": "학습자",
        "email": "learner@example.com",
    },
    license_info={
        "name": "MIT",
    },
)
```

### 여러 엔드포인트가 있는 앱

```python
from fastapi import FastAPI

app = FastAPI(
    title="나의 학습 API",
    description="FastAPI 학습용 API 서버",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """루트 경로 - 앱 정보를 반환합니다."""
    return {"app": app.title, "version": app.version}


@app.get("/health")
def health_check():
    """헬스 체크 - 서버 상태를 확인합니다."""
    return {"status": "healthy"}


@app.get("/hello/{name}")
def say_hello(name: str):
    """이름으로 인사합니다."""
    return {"message": f"안녕하세요, {name}님!"}
```

### 실행 옵션 모음

```bash
# 기본 실행
uvicorn main:app

# 개발 모드 (핫 리로드)
uvicorn main:app --reload

# 포트 변경
uvicorn main:app --reload --port 3000

# 외부 접근 허용 + 포트 변경
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# fastapi CLI 사용 (FastAPI 0.111.0+)
fastapi dev main.py

# 로그 레벨 설정
uvicorn main:app --reload --log-level debug
```

---

### Python 코드 내에서 서버 실행

`uvicorn.run()`을 사용하면 Python 코드 안에서 직접 서버를 실행할 수 있습니다.

```python
# main.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello!"}


# 파일을 직접 실행할 때 서버 시작
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

```bash
# 이제 이렇게 실행할 수 있습니다
python main.py
```

> **참고**: `uvicorn.run()`에서 `reload=True`를 사용하려면
> 첫 번째 인자를 문자열(`"main:app"`)로 전달해야 합니다.
> `app` 객체를 직접 전달하면 리로드가 동작하지 않습니다.

---

## 주의 사항

### 1. 포트 충돌

이미 다른 프로세스가 해당 포트를 사용 중이면 오류가 발생합니다.

```
ERROR: [Errno 48] Address already in use
```

해결 방법:
```bash
# 다른 포트 사용
uvicorn main:app --port 8001

# 또는 해당 포트를 사용 중인 프로세스 찾기 (macOS/Linux)
lsof -i :8000
```

### 2. `--reload`는 개발 환경에서만 사용

```bash
# 개발 환경
uvicorn main:app --reload

# 프로덕션 환경 (--reload 없이)
uvicorn main:app --workers 4
```

### 3. 파일 경로 구분자

```bash
# 올바른 방법 (점으로 구분)
uvicorn src.main:app

# 잘못된 방법 (슬래시 사용 불가)
uvicorn src/main:app  # 오류!
```

---

## 정리

| 명령어/옵션 | 설명 | 예시 |
|-------------|------|------|
| `uvicorn main:app` | 기본 실행 | 포트 8000 |
| `--reload` | 코드 변경 시 자동 재시작 | 개발 모드 |
| `--host` | 접근 허용 범위 설정 | `0.0.0.0` |
| `--port` | 포트 번호 변경 | `--port 3000` |
| `--log-level` | 로그 상세도 설정 | `debug`, `info`, `warning` |
| `--workers` | 워커 프로세스 수 | 프로덕션용 |
| `fastapi dev` | FastAPI CLI 개발 모드 | `fastapi dev main.py` |
| `fastapi run` | FastAPI CLI 프로덕션 모드 | `fastapi run main.py` |
| `/docs` | Swagger UI 문서 | 인터랙티브 테스트 |
| `/redoc` | ReDoc 문서 | 읽기 전용 |
| `/openapi.json` | OpenAPI 스키마 | JSON 형식 |

---

## 다음 단계

이 챕터의 모든 섹션을 완료했습니다! 다음 챕터에서는 경로 매개변수와 쿼리 매개변수를 자세히 알아봅니다.

> [챕터 02: 경로 매개변수와 쿼리 매개변수](../../ch02-path-query-params/)
