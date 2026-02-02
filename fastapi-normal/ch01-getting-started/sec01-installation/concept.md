# 섹션 01: 설치 및 환경 설정

> **난이도**: ⭐ (1/5)
> **선수 지식**: Python 3.8+ 설치됨
> **학습 목표**: Python 가상환경을 만들고 FastAPI와 필수 패키지를 설치할 수 있다

---

## 핵심 개념

### 1. 가상환경 (Virtual Environment)

가상환경은 Python 프로젝트마다 독립적인 패키지 공간을 제공합니다.
프로젝트 A에서 FastAPI 0.100을 쓰고, 프로젝트 B에서 FastAPI 0.110을 쓸 수 있게 해줍니다.

```
프로젝트별 독립 환경:

프로젝트 A (가상환경 A)        프로젝트 B (가상환경 B)
├── FastAPI 0.100.0           ├── FastAPI 0.110.0
├── Pydantic 2.0              ├── Pydantic 2.5
└── uvicorn 0.23              └── uvicorn 0.27
```

#### 가상환경 생성 및 활성화

```bash
# 1. 가상환경 생성
python -m venv .venv

# 2. 가상환경 활성화
# macOS / Linux:
source .venv/bin/activate

# Windows (CMD):
.venv\Scripts\activate.bat

# Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

> **주의**: 가상환경을 활성화하면 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다.
> 이것이 보이지 않으면 가상환경이 활성화되지 않은 것입니다!

```bash
# 활성화 전
$ python --version

# 활성화 후 (앞에 (.venv)가 보임)
(.venv) $ python --version
```

---

### 2. pip (Python 패키지 관리자)

pip는 Python의 공식 패키지 관리 도구입니다. PyPI(Python Package Index)에서 패키지를 다운로드하고 설치합니다.

```bash
# pip 자체를 최신 버전으로 업그레이드
pip install --upgrade pip

# 특정 패키지 설치
pip install 패키지이름

# 설치된 패키지 목록 확인
pip list

# 특정 패키지 정보 확인
pip show 패키지이름
```

---

### 3. FastAPI 설치

FastAPI는 두 가지 방식으로 설치할 수 있습니다.

#### 방법 1: `fastapi[standard]` (권장)

```bash
pip install "fastapi[standard]"
```

이 방식은 FastAPI와 함께 개발에 필요한 모든 패키지를 한 번에 설치합니다:
- **uvicorn**: ASGI 서버 (API 서버를 실행하는 엔진)
- **httptools**: HTTP 파싱 성능 향상
- **python-multipart**: 폼 데이터 처리
- **email-validator**: 이메일 유효성 검사
- 기타 유용한 패키지들

#### 방법 2: `fastapi` (최소 설치)

```bash
pip install fastapi
pip install uvicorn
```

이 방식은 FastAPI 코어만 설치하고, 나머지는 필요할 때 직접 설치합니다.

> **권장**: 학습 단계에서는 `fastapi[standard]`를 사용하세요.
> 필요한 대부분의 패키지가 자동으로 설치됩니다.

---

### 4. Uvicorn

Uvicorn은 ASGI(Asynchronous Server Gateway Interface) 서버입니다.
쉽게 말해, FastAPI로 작성한 코드를 실제로 실행해주는 **웹 서버**입니다.

```
[클라이언트/브라우저] ←→ [Uvicorn 서버] ←→ [FastAPI 앱]
```

Flask에서 `flask run`을 사용하듯이, FastAPI에서는 `uvicorn`을 사용합니다.

```bash
# 기본 실행
uvicorn main:app

# 개발 모드 (자동 재시작)
uvicorn main:app --reload
```

---

## 실습: 전체 설치 과정

아래 명령어를 순서대로 실행하세요.

### Step 1: 프로젝트 디렉토리 생성

```bash
mkdir my-fastapi-project
cd my-fastapi-project
```

### Step 2: 가상환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# 또는
.venv\Scripts\activate.bat   # Windows
```

### Step 3: pip 업그레이드

```bash
pip install --upgrade pip
```

### Step 4: FastAPI 설치

```bash
pip install "fastapi[standard]"
```

### Step 5: 설치 확인

```bash
# FastAPI 버전 확인
python -c "import fastapi; print(fastapi.__version__)"

# Uvicorn 버전 확인
python -c "import uvicorn; print(uvicorn.__version__)"

# Pydantic 버전 확인
python -c "import pydantic; print(pydantic.VERSION)"

# 설치된 모든 패키지 확인
pip list
```

### Step 6: 설치 확인 스크립트 실행

```bash
python exercise.py
```

정상적으로 설치되었다면 다음과 같은 출력이 나옵니다:

```
FastAPI 버전: 0.115.x
Uvicorn 버전: 0.32.x
Pydantic 버전: 2.x.x

모든 패키지가 정상적으로 설치되었습니다!
```

---

## 주의 사항

### 가상환경 활성화를 잊지 마세요!

가장 흔한 실수는 가상환경을 활성화하지 않고 패키지를 설치하는 것입니다.
이렇게 하면 시스템 전역 Python에 패키지가 설치되어 프로젝트 간 충돌이 발생할 수 있습니다.

```bash
# 나쁜 예: 가상환경 없이 설치
pip install fastapi  # 시스템 전역에 설치됨!

# 좋은 예: 가상환경 활성화 후 설치
source .venv/bin/activate
pip install fastapi  # 가상환경에만 설치됨
```

### `fastapi[standard]` vs `fastapi` 차이

| 설치 방법 | 포함 패키지 | 용도 |
|-----------|------------|------|
| `fastapi[standard]` | FastAPI + uvicorn + httptools + 기타 | 개발/학습 (권장) |
| `fastapi` | FastAPI 코어만 | 프로덕션 (필요한 것만 직접 설치) |

### 대괄호 주의

셸에 따라 대괄호(`[]`)가 특수 문자로 해석될 수 있습니다.
따옴표로 감싸서 설치하세요.

```bash
# 올바른 방법
pip install "fastapi[standard]"

# zsh에서 따옴표 없이 하면 오류 발생 가능
pip install fastapi[standard]  # 오류 가능!
```

---

## 정리

| 명령어 | 설명 |
|--------|------|
| `python -m venv .venv` | 가상환경 생성 |
| `source .venv/bin/activate` | 가상환경 활성화 (macOS/Linux) |
| `.venv\Scripts\activate.bat` | 가상환경 활성화 (Windows CMD) |
| `deactivate` | 가상환경 비활성화 |
| `pip install --upgrade pip` | pip 업그레이드 |
| `pip install "fastapi[standard]"` | FastAPI + 관련 패키지 설치 |
| `pip install fastapi` | FastAPI 코어만 설치 |
| `pip install uvicorn` | Uvicorn 서버 설치 |
| `pip list` | 설치된 패키지 목록 확인 |
| `pip show fastapi` | FastAPI 패키지 상세 정보 확인 |
| `pip freeze > requirements.txt` | 설치된 패키지를 파일로 저장 |
| `pip install -r requirements.txt` | 파일에서 패키지 일괄 설치 |

---

## 다음 단계

설치가 완료되었다면, 다음 섹션에서 첫 번째 FastAPI 앱을 만들어 보겠습니다!

> [sec02-first-app: 첫 번째 FastAPI 앱](../sec02-first-app/concept.md)
