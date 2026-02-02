# 섹션 01: 설치 및 환경 설정 - 연습 문제

> **난이도**: ⭐ (1/5)
> **파일**: `exercise.py`

---

## 문제 1: 가상환경 생성 및 활성화 후 FastAPI 설치하기

### 목표
Python 가상환경을 직접 만들고, 활성화한 뒤, FastAPI를 설치합니다.

### 단계

1. 터미널을 열고 이 디렉토리로 이동합니다.
2. 아래 명령어를 **순서대로** 실행합니다.

```bash
# 1. 가상환경 생성
python -m venv .venv

# 2. 가상환경 활성화
# macOS / Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate.bat

# 3. pip 업그레이드
pip install --upgrade pip

# 4. FastAPI 설치 (standard 옵션 포함)
pip install "fastapi[standard]"
```

### 확인 방법

- 터미널 프롬프트 앞에 `(.venv)`가 표시되는지 확인합니다.
- `pip list`를 실행하여 `fastapi`, `uvicorn`, `pydantic`이 목록에 있는지 확인합니다.

---

## 문제 2: 설치된 패키지 버전 확인하기

### 목표
`exercise.py` 파일의 TODO 부분을 완성하여, 설치된 패키지의 버전을 확인하는 스크립트를 만듭니다.

### 요구 사항

| 함수명 | 해야 할 일 |
|--------|-----------|
| `check_fastapi_installed()` | `fastapi` 모듈을 import하고 `__version__`을 반환 |
| `check_uvicorn_installed()` | `uvicorn` 모듈을 import하고 `__version__`을 반환 |
| `check_pydantic_installed()` | `pydantic` 모듈을 import하고 `VERSION`을 반환 |

### 힌트

- Python에서 모듈의 버전을 확인하는 일반적인 방법:
  ```python
  import 모듈이름
  print(모듈이름.__version__)
  ```
- Pydantic은 `__version__` 대신 `VERSION`을 사용합니다.

### 실행 및 검증

```bash
python exercise.py
```

### 기대 출력

```
FastAPI 버전: 0.115.x
Uvicorn 버전: 0.32.x
Pydantic 버전: 2.x.x

모든 패키지가 정상적으로 설치되었습니다!
```

> 버전 번호는 설치 시점에 따라 다를 수 있습니다.

---

## 추가 도전 과제 (선택)

1. `pip freeze > requirements.txt` 명령어를 실행하여 `requirements.txt` 파일을 생성해보세요.
2. 생성된 `requirements.txt` 파일의 내용을 확인해보세요.
3. 가상환경을 `deactivate`로 비활성화한 후, 다시 활성화해보세요.
