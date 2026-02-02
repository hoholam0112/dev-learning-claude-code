# 연습 문제: CORS 설정

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: 기본 CORS 설정

FastAPI 앱에 `CORSMiddleware`를 추가하여 프론트엔드(React 개발 서버)에서
API에 접근할 수 있도록 CORS를 설정하세요.

### 요구 사항

- 허용 출처: `http://localhost:3000`, `http://localhost:5173`
- 허용 메서드: `GET`, `POST`, `PUT`, `DELETE`
- 허용 헤더: 모두 (`*`)
- 자격 증명(쿠키) 포함: 허용

### 힌트

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[...],
    ...
)
```

---

## 문제 2: Preflight 응답 검증

설정이 올바른지 OPTIONS 요청(Preflight)을 보내서 확인합니다.
테스트 코드가 이미 작성되어 있으니, CORS 설정만 올바르게 하면 통과됩니다.

### 검증 항목

- `Access-Control-Allow-Origin` 헤더에 허용 출처가 포함되어야 함
- `Access-Control-Allow-Methods` 헤더에 허용 메서드가 포함되어야 함
- 허용되지 않은 출처에서의 요청은 CORS 헤더가 없어야 함

---

## 테스트 기대 결과

```
✓ CORS 기본 설정 확인 - localhost:3000 허용됨
✓ CORS 추가 출처 확인 - localhost:5173 허용됨
✓ 허용되지 않은 출처 차단 확인
✓ Preflight 요청 응답 확인

모든 테스트를 통과했습니다!
```
