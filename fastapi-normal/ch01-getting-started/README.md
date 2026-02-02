# 챕터 01: FastAPI 시작하기

> **난이도**: ⭐ (1/5) | **예상 학습 시간**: 1~2시간

---

## 개요

이 챕터에서는 FastAPI를 설치하고, 첫 번째 API 서버를 만들어 실행하는 과정을 다룹니다.
Python과 pip만 설치되어 있다면 누구나 따라할 수 있는 가장 기초적인 내용입니다.

---

## 왜 FastAPI인가?

FastAPI는 현대 Python 웹 프레임워크 중 가장 빠르게 성장하고 있는 프레임워크입니다.
다음과 같은 이유로 많은 개발자들이 FastAPI를 선택합니다:

### 1. 고성능 (High Performance)
- Node.js, Go와 비교해도 뒤지지 않는 성능
- 내부적으로 Starlette(웹 부분)과 Pydantic(데이터 부분)을 활용
- 비동기(async/await) 지원으로 높은 동시 처리 능력

### 2. 타입 힌트 기반 (Type Hints)
- Python 3.6+의 표준 타입 힌트를 적극 활용
- 코드 작성 시 IDE 자동 완성 지원이 뛰어남
- 런타임에 자동으로 데이터 검증 수행

### 3. 자동 문서화 (Auto Documentation)
- 코드를 작성하면 **Swagger UI** (`/docs`)와 **ReDoc** (`/redoc`)이 자동 생성
- API 문서를 별도로 작성할 필요 없음
- 문서에서 바로 API 테스트 가능

### 4. 쉬운 학습 곡선
- Flask처럼 직관적인 데코레이터 패턴
- 공식 문서가 매우 잘 정리되어 있음
- Python을 알면 빠르게 학습 가능

---

## 포함된 섹션

| 섹션 | 제목 | 핵심 내용 |
|------|------|-----------|
| [sec01-installation](./sec01-installation/) | 설치 및 환경 설정 | Python 가상환경, pip, FastAPI 설치 |
| [sec02-first-app](./sec02-first-app/) | 첫 번째 FastAPI 앱 | FastAPI 인스턴스, 엔드포인트, JSON 응답 |
| [sec03-dev-server](./sec03-dev-server/) | 개발 서버 활용 | Uvicorn, 핫 리로드, Swagger UI |

---

## 학습 순서

```
sec01-installation → sec02-first-app → sec03-dev-server
```

1. **sec01**: FastAPI를 설치하고 개발 환경을 준비합니다.
2. **sec02**: 첫 번째 API 엔드포인트를 작성합니다.
3. **sec03**: 개발 서버를 실행하고 자동 문서를 확인합니다.

---

## 사전 준비

- Python 3.8 이상이 설치되어 있어야 합니다.
- 터미널(명령 프롬프트)을 사용할 수 있어야 합니다.
- 코드 에디터(VS Code 권장)가 준비되어 있어야 합니다.

```bash
# Python 버전 확인
python --version
# 또는
python3 --version
```

---

## 이 챕터를 마치면

- FastAPI 개발 환경을 독립적으로 구축할 수 있습니다.
- 간단한 GET 엔드포인트를 작성할 수 있습니다.
- Swagger UI에서 API를 테스트할 수 있습니다.
- 핫 리로드를 활용하여 효율적으로 개발할 수 있습니다.
