# sec02: 전역 에러 핸들러 (Global Error Handlers)

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 예외 계층 구조 완료
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

- 표준화된 `ErrorResponse` Pydantic 모델을 설계할 수 있다
- `app.exception_handler()`로 여러 종류의 전역 핸들러를 등록할 수 있다
- `RequestValidationError`를 커스텀 핸들러로 변환할 수 있다
- catch-all 핸들러로 예상치 못한 에러도 일관되게 처리할 수 있다

---

## 핵심 개념

### 1. 표준화된 ErrorResponse 모델

sec01에서는 에러 응답을 딕셔너리로 직접 구성했습니다.
실제 프로젝트에서는 **Pydantic 모델**로 에러 응답의 스키마를 정의하는 것이 좋습니다.

```python
from datetime import datetime
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """표준 에러 응답 모델"""
    error_code: str               # 에러 코드 (예: "USER_NOT_FOUND")
    message: str                  # 사용자 표시용 메시지
    detail: dict | list | None = None  # 추가 상세 정보
    timestamp: str                # 에러 발생 시각 (ISO 8601)
```

**장점:**
- Swagger UI에서 에러 응답 스키마를 문서화할 수 있음
- 응답 형식의 일관성을 보장
- 타입 검증으로 실수 방지

### 2. app.exception_handler() 데코레이터

FastAPI는 `@app.exception_handler(ExceptionType)`으로 특정 예외에 대한 전역 핸들러를 등록할 수 있습니다.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            detail=exc.detail,
            timestamp=datetime.now().isoformat(),
        ).model_dump(),
    )
```

### 3. RequestValidationError 커스텀 핸들러

FastAPI는 요청 데이터가 Pydantic 모델과 맞지 않으면 자동으로 `RequestValidationError`를 발생시킵니다.
기본 응답 형식은 다음과 같습니다:

```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "name"],
            "msg": "Field required",
            "input": {}
        }
    ]
}
```

이것을 우리의 `ErrorResponse` 형식으로 변환할 수 있습니다:

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="요청 데이터가 유효하지 않습니다",
            detail=exc.errors(),
            timestamp=datetime.now().isoformat(),
        ).model_dump(),
    )
```

### 4. Exception catch-all 핸들러 (500 에러)

예상치 못한 에러(코드 버그, 외부 서비스 장애 등)도 일관된 형식으로 반환해야 합니다.
`Exception` 타입에 핸들러를 등록하면 **모든 미처리 예외**를 잡을 수 있습니다.

```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="내부 서버 오류가 발생했습니다",
            detail=None,  # 프로덕션에서는 내부 에러 정보를 노출하지 않음
            timestamp=datetime.now().isoformat(),
        ).model_dump(),
    )
```

> **주의**: 프로덕션에서는 `str(exc)`와 같은 내부 에러 메시지를 클라이언트에 노출하면 안 됩니다.
> 대신 서버 측 로그에만 기록합니다.

### 5. 핸들러 우선순위

여러 핸들러가 등록되어 있을 때, FastAPI는 **가장 구체적인 예외 타입**의 핸들러를 먼저 매칭합니다.

```
예외 발생
    │
    ├── AppException (또는 하위 클래스)?
    │   └── app_exception_handler 실행
    │
    ├── RequestValidationError?
    │   └── validation_exception_handler 실행
    │
    └── 그 외 Exception?
        └── general_exception_handler 실행
```

---

## 에러 응답 일관성의 중요성

### Before: 불일관한 에러 응답

```json
// FastAPI 기본 HTTPException 응답
{"detail": "Not Found"}

// Pydantic ValidationError 응답
{"detail": [{"type": "missing", "loc": ["body", "name"], ...}]}

// 서버 에러 (HTML 페이지!)
<h1>Internal Server Error</h1>
```

### After: 일관된 ErrorResponse

```json
// 모든 에러가 같은 형식
{
    "error_code": "USER_NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다",
    "detail": {"user_id": 999},
    "timestamp": "2024-01-15T10:30:00"
}

{
    "error_code": "VALIDATION_ERROR",
    "message": "요청 데이터가 유효하지 않습니다",
    "detail": [{"type": "missing", "loc": ["body", "name"], ...}],
    "timestamp": "2024-01-15T10:30:00"
}

{
    "error_code": "INTERNAL_ERROR",
    "message": "내부 서버 오류가 발생했습니다",
    "detail": null,
    "timestamp": "2024-01-15T10:30:00"
}
```

---

## 핵심 정리

1. **ErrorResponse 모델**로 에러 응답의 스키마를 표준화한다
2. **AppException 핸들러**로 비즈니스 에러를 일관되게 처리한다
3. **RequestValidationError 핸들러**로 입력 검증 에러를 변환한다
4. **catch-all 핸들러**로 예상치 못한 에러도 안전하게 처리한다
5. 프로덕션에서는 **내부 에러 정보를 클라이언트에 노출하지 않는다**

---

## 다음 단계

- `exercise.md`를 확인하고 연습 문제를 풀어보세요.
- 다음 섹션: [sec03-error-middleware](../sec03-error-middleware/concept.md) - 에러 미들웨어
