# sec01: 예외 계층 구조 - 연습 문제

> `exercise.py` 파일을 열고 TODO 부분을 완성하세요.
> 테스트 실행: `python exercise.py`

---

## 문제 1: 커스텀 예외 계층 구조

### 요구사항

커스텀 예외 계층 구조를 설계하세요.

- **ErrorCode Enum** 정의:
  - `USER_NOT_FOUND`, `DUPLICATE_EMAIL`, `INVALID_INPUT`, `AUTHORIZATION_FAILED`, `RESOURCE_NOT_FOUND`, `DUPLICATE_RESOURCE`

- **AppException** 기반 클래스:
  - `status_code` (int, 기본값 500)
  - `error_code` (str, 기본값 `"INTERNAL_ERROR"`)
  - `message` (str, 기본값 `"내부 서버 오류가 발생했습니다"`)
  - `detail` (dict | None, 기본값 None)

- **하위 예외 클래스** 4개:
  - `NotFoundException` (404)
  - `DuplicateError` (409)
  - `CustomValidationError` (422)
  - `AuthorizationError` (403)

- **전역 핸들러** 등록:
  - `AppException`을 JSON으로 변환: `{"error_code": "...", "message": "...", "detail": ...}`

### 테스트 엔드포인트

```
GET /test/not-found      -> 404, error_code: "USER_NOT_FOUND"
GET /test/duplicate      -> 409, error_code: "DUPLICATE_EMAIL"
GET /test/validation     -> 422, error_code: "INVALID_INPUT"
GET /test/authorization  -> 403, error_code: "AUTHORIZATION_FAILED"
```

---

## 문제 2: 도메인별 예외 활용

### 요구사항

간단한 사용자 관리 시스템에서 커스텀 예외를 활용하세요.

- **POST /users**: 사용자 생성
  - 이메일이 중복이면 `DuplicateError` 발생 (409)
- **GET /users/{user_id}**: 사용자 조회
  - 존재하지 않으면 `NotFoundException` 발생 (404)
- **PUT /users/{user_id}**: 사용자 수정
  - 존재하지 않으면 `NotFoundException` 발생 (404)
  - 나이가 0 이하이면 `CustomValidationError` 발생 (422)

### 에러 응답 형식

모든 에러 응답은 다음 형식을 따릅니다:

```json
{
    "error_code": "USER_NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다",
    "detail": {"user_id": 999}
}
```

### 테스트 케이스

```
GET /users/1             -> 200, 사용자 정보 반환
GET /users/999           -> 404, error_code: "USER_NOT_FOUND"
POST /users (중복 이메일)  -> 409, error_code: "DUPLICATE_EMAIL"
PUT /users/1 (나이: -1)   -> 422, error_code: "INVALID_INPUT"
```

---

## 힌트

1. `AppException`은 Python의 `Exception`을 상속하되, 추가 속성을 `__init__`에서 설정합니다.
2. `str, Enum`을 사용하면 JSON 직렬화 시 자동으로 문자열로 변환됩니다.
3. `@app.exception_handler(AppException)`은 모든 하위 클래스도 자동으로 처리합니다.

```python
class AppException(Exception):
    def __init__(self, status_code=500, error_code="INTERNAL_ERROR", message="...", detail=None):
        self.status_code = status_code
        # ...
        super().__init__(message)
```
