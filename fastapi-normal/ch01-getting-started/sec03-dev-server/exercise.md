# 섹션 03: 개발 서버 활용 - 연습 문제

> **난이도**: ⭐ (1/5)
> **파일**: `exercise.py`

---

## 문제 1: FastAPI 앱 메타데이터 커스터마이징

### 목표
FastAPI 인스턴스에 앱 정보(title, description, version)를 설정하세요.

### 요구 사항

| 항목 | 값 |
|------|-----|
| `title` | `"나의 학습 API"` |
| `description` | `"FastAPI 학습용 API 서버"` |
| `version` | `"0.1.0"` |

### 힌트

```python
app = FastAPI(
    title="제목",
    description="설명",
    version="버전",
)
```

---

## 문제 2: 루트 엔드포인트 (`/`) 구현

### 목표
루트 경로에 접속하면 앱 이름과 버전 정보를 반환하는 엔드포인트를 만드세요.

### 요구 사항

| 항목 | 값 |
|------|-----|
| HTTP 메서드 | GET |
| 경로 | `/` |
| 반환값 | `{"app": "나의 학습 API", "version": "0.1.0"}` |

### 힌트

- `app.title`과 `app.version`을 활용하면 하드코딩을 피할 수 있습니다.
- 하지만 직접 문자열을 넣어도 됩니다.

---

## 문제 3: 헬스체크 엔드포인트 (`/health`) 구현

### 목표
서버가 정상 작동 중인지 확인하는 헬스체크 엔드포인트를 만드세요.

### 요구 사항

| 항목 | 값 |
|------|-----|
| HTTP 메서드 | GET |
| 경로 | `/health` |
| 반환값 | `{"status": "healthy"}` |

### 헬스체크란?

헬스체크(Health Check)는 서버가 정상적으로 동작하고 있는지 확인하는 엔드포인트입니다.
로드 밸런서나 모니터링 도구에서 주기적으로 이 엔드포인트를 호출하여 서버 상태를 확인합니다.

---

## 실행 및 검증

### 방법 1: 자체 테스트 실행

```bash
python exercise.py
```

성공 시 출력:
```
✓ 앱 메타데이터 테스트 통과
✓ / 루트 엔드포인트 테스트 통과
✓ /health 테스트 통과

모든 테스트를 통과했습니다!
```

### 방법 2: 다양한 옵션으로 서버 실행해보기

```bash
# 기본 실행
uvicorn exercise:app --reload

# 포트 변경하여 실행
uvicorn exercise:app --reload --port 8001

# fastapi CLI로 실행 (FastAPI 0.111.0+)
fastapi dev exercise.py
```

브라우저에서 확인:
- `http://localhost:8000/` (또는 설정한 포트)
- `http://localhost:8000/health`
- `http://localhost:8000/docs` (Swagger UI에서 앱 제목 확인)
- `http://localhost:8000/redoc` (ReDoc 문서 확인)

---

## 추가 도전 과제 (선택)

1. `--port 3000`, `--port 8080` 등 다른 포트로 서버를 실행해보세요.
2. Swagger UI(`/docs`)에서 앱 제목과 설명이 정상적으로 표시되는지 확인해보세요.
3. ReDoc(`/redoc`)에 접속하여 Swagger UI와 어떤 차이가 있는지 비교해보세요.
4. `uvicorn exercise:app --reload --log-level debug`로 실행하여 디버그 로그를 확인해보세요.
