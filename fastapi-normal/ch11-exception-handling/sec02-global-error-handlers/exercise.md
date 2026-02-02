# sec02: 전역 에러 핸들러 - 연습 문제

> `exercise.py` 파일을 열고 TODO 부분을 완성하세요.
> 테스트 실행: `python exercise.py`

---

## 문제 1: 표준 에러 응답과 전역 핸들러

### 요구사항

표준화된 에러 응답 모델과 전역 핸들러를 구현하세요.

- **ErrorResponse** Pydantic 모델:
  - `error_code` (str): 에러 코드
  - `message` (str): 에러 메시지
  - `detail` (dict | list | None): 추가 상세 정보
  - `timestamp` (str): 에러 발생 시각 (ISO 8601)

- **전역 핸들러 3개 등록**:
  1. `AppException` 핸들러 -> `ErrorResponse` 형식으로 반환
  2. `RequestValidationError` 핸들러 -> `ErrorResponse` 형식으로 변환 (error_code: `"VALIDATION_ERROR"`)
  3. `Exception` catch-all 핸들러 -> 500 `ErrorResponse` 반환 (error_code: `"INTERNAL_ERROR"`)

### 테스트 케이스

```
GET /test/app-error       -> 404, ErrorResponse 형식 (timestamp 포함)
POST /test/validation     -> 422, ErrorResponse 형식 (detail에 검증 오류 목록)
GET /test/crash           -> 500, ErrorResponse 형식 (INTERNAL_ERROR)
```

---

## 문제 2: 에러 핸들러 통합 테스트

### 요구사항

사용자 CRUD API에서 모든 에러 타입을 테스트하세요.

- **GET /users/{user_id}**: 존재하지 않으면 `NotFoundException`
- **POST /users**: `UserCreate` 모델로 검증 (RequestValidationError 자동 발생)
- **GET /crash**: 의도적으로 `RuntimeError` 발생 -> catch-all 핸들러로 처리

### 모든 에러 응답 공통 검증

- `error_code` 필드 존재
- `message` 필드 존재
- `timestamp` 필드 존재

---

## 힌트

1. `RequestValidationError`는 `from fastapi.exceptions import RequestValidationError`로 임포트합니다.
2. `exc.errors()`는 Pydantic 검증 오류의 상세 목록을 반환합니다.
3. `datetime.now().isoformat()`으로 ISO 8601 형식의 타임스탬프를 생성합니다.
4. catch-all 핸들러에서는 내부 에러 정보를 클라이언트에 노출하지 않습니다.

```python
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
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
