# 모범 답안: 예외 계층 구조
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from enum import Enum
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


# ============================================================
# 문제 1 해답: 커스텀 예외 계층 구조
# ============================================================

class ErrorCode(str, Enum):
    """에러 코드 Enum - 도메인별 에러 코드를 정의합니다."""
    USER_NOT_FOUND = "USER_NOT_FOUND"
    DUPLICATE_EMAIL = "DUPLICATE_EMAIL"
    INVALID_INPUT = "INVALID_INPUT"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"


class AppException(Exception):
    """애플리케이션 예외 기반 클래스.

    모든 커스텀 예외의 부모 클래스로, 구조화된 에러 응답을 위한
    공통 속성을 제공합니다.

    Attributes:
        status_code: HTTP 상태 코드
        error_code: 도메인별 에러 코드 (ErrorCode Enum)
        message: 사용자에게 표시할 에러 메시지
        detail: 추가 상세 정보 (선택)
    """

    def __init__(
        self,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        message: str = "내부 서버 오류가 발생했습니다",
        detail: dict | None = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.detail = detail
        super().__init__(message)


class NotFoundException(AppException):
    """리소스를 찾을 수 없을 때 발생하는 예외 (404)"""

    def __init__(
        self,
        error_code: str = ErrorCode.RESOURCE_NOT_FOUND,
        message: str = "요청한 리소스를 찾을 수 없습니다",
        detail: dict | None = None,
    ):
        super().__init__(
            status_code=404,
            error_code=error_code,
            message=message,
            detail=detail,
        )


class DuplicateError(AppException):
    """중복된 리소스가 존재할 때 발생하는 예외 (409)"""

    def __init__(
        self,
        error_code: str = ErrorCode.DUPLICATE_RESOURCE,
        message: str = "이미 존재하는 리소스입니다",
        detail: dict | None = None,
    ):
        super().__init__(
            status_code=409,
            error_code=error_code,
            message=message,
            detail=detail,
        )


class CustomValidationError(AppException):
    """비즈니스 로직 검증 실패 시 발생하는 예외 (422)"""

    def __init__(
        self,
        error_code: str = ErrorCode.INVALID_INPUT,
        message: str = "입력값이 유효하지 않습니다",
        detail: dict | None = None,
    ):
        super().__init__(
            status_code=422,
            error_code=error_code,
            message=message,
            detail=detail,
        )


class AuthorizationError(AppException):
    """인가 실패 시 발생하는 예외 (403)"""

    def __init__(
        self,
        error_code: str = ErrorCode.AUTHORIZATION_FAILED,
        message: str = "접근 권한이 없습니다",
        detail: dict | None = None,
    ):
        super().__init__(
            status_code=403,
            error_code=error_code,
            message=message,
            detail=detail,
        )


# AppException 전역 핸들러 등록
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """AppException을 구조화된 JSON 응답으로 변환합니다."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
        },
    )


# 문제 1 테스트용 엔드포인트
@app.get("/test/not-found")
async def test_not_found():
    """NotFoundException 발생 테스트"""
    raise NotFoundException(
        error_code=ErrorCode.USER_NOT_FOUND,
        message="사용자를 찾을 수 없습니다",
        detail={"user_id": 999},
    )


@app.get("/test/duplicate")
async def test_duplicate():
    """DuplicateError 발생 테스트"""
    raise DuplicateError(
        error_code=ErrorCode.DUPLICATE_EMAIL,
        message="이미 등록된 이메일입니다",
        detail={"email": "test@example.com"},
    )


@app.get("/test/validation")
async def test_validation():
    """CustomValidationError 발생 테스트"""
    raise CustomValidationError(
        error_code=ErrorCode.INVALID_INPUT,
        message="나이는 0보다 커야 합니다",
        detail={"field": "age", "value": -1},
    )


@app.get("/test/authorization")
async def test_authorization():
    """AuthorizationError 발생 테스트"""
    raise AuthorizationError(
        message="관리자만 접근할 수 있습니다",
        detail={"required_role": "admin"},
    )


# ============================================================
# 문제 2 해답: 도메인별 예외 활용
# ============================================================

# 가상 사용자 데이터
fake_users_db: dict[int, dict] = {
    1: {"id": 1, "name": "홍길동", "email": "hong@example.com", "age": 30},
    2: {"id": 2, "name": "김철수", "email": "kim@example.com", "age": 25},
}
next_user_id = 3


class UserCreate(BaseModel):
    name: str
    email: str
    age: int


@app.post("/users", status_code=201)
async def create_user(user: UserCreate):
    """사용자 생성 - 이메일 중복 시 DuplicateError 발생"""
    global next_user_id

    # 이메일 중복 검사
    for existing_user in fake_users_db.values():
        if existing_user["email"] == user.email:
            raise DuplicateError(
                error_code=ErrorCode.DUPLICATE_EMAIL,
                message="이미 등록된 이메일입니다",
                detail={"email": user.email},
            )

    new_user = {"id": next_user_id, "name": user.name, "email": user.email, "age": user.age}
    fake_users_db[next_user_id] = new_user
    next_user_id += 1
    return new_user


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """사용자 조회 - 존재하지 않으면 NotFoundException 발생"""
    if user_id not in fake_users_db:
        raise NotFoundException(
            error_code=ErrorCode.USER_NOT_FOUND,
            message="사용자를 찾을 수 없습니다",
            detail={"user_id": user_id},
        )
    return fake_users_db[user_id]


@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserCreate):
    """사용자 수정 - 존재하지 않으면 NotFoundException, 유효하지 않은 데이터면 CustomValidationError"""
    if user_id not in fake_users_db:
        raise NotFoundException(
            error_code=ErrorCode.USER_NOT_FOUND,
            message="사용자를 찾을 수 없습니다",
            detail={"user_id": user_id},
        )

    # 비즈니스 로직 검증: 나이는 0보다 커야 함
    if user.age <= 0:
        raise CustomValidationError(
            error_code=ErrorCode.INVALID_INPUT,
            message="나이는 0보다 커야 합니다",
            detail={"field": "age", "value": user.age},
        )

    # 이메일 중복 검사 (자기 자신 제외)
    for uid, existing_user in fake_users_db.items():
        if uid != user_id and existing_user["email"] == user.email:
            raise DuplicateError(
                error_code=ErrorCode.DUPLICATE_EMAIL,
                message="이미 등록된 이메일입니다",
                detail={"email": user.email},
            )

    fake_users_db[user_id] = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
    }
    return fake_users_db[user_id]


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 테스트
    print("=" * 50)
    print("문제 1: 커스텀 예외 계층 구조 테스트")
    print("=" * 50)

    # 테스트 1-1: NotFoundException
    response = client.get("/test/not-found")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert "message" in data
    assert data["detail"]["user_id"] == 999
    print("  [통과] NotFoundException 테스트 (404)")

    # 테스트 1-2: DuplicateError
    response = client.get("/test/duplicate")
    assert response.status_code == 409
    data = response.json()
    assert data["error_code"] == "DUPLICATE_EMAIL"
    assert "message" in data
    assert data["detail"]["email"] == "test@example.com"
    print("  [통과] DuplicateError 테스트 (409)")

    # 테스트 1-3: CustomValidationError
    response = client.get("/test/validation")
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "INVALID_INPUT"
    assert "message" in data
    assert data["detail"]["field"] == "age"
    print("  [통과] CustomValidationError 테스트 (422)")

    # 테스트 1-4: AuthorizationError
    response = client.get("/test/authorization")
    assert response.status_code == 403
    data = response.json()
    assert data["error_code"] == "AUTHORIZATION_FAILED"
    assert "message" in data
    assert data["detail"]["required_role"] == "admin"
    print("  [통과] AuthorizationError 테스트 (403)")

    # 테스트 1-5: 에러 응답 구조 검증 (일관된 형식)
    for path in ["/test/not-found", "/test/duplicate", "/test/validation", "/test/authorization"]:
        response = client.get(path)
        data = response.json()
        assert "error_code" in data, f"{path}: error_code 필드 누락"
        assert "message" in data, f"{path}: message 필드 누락"
        assert "detail" in data, f"{path}: detail 필드 누락"
    print("  [통과] 모든 에러 응답이 일관된 구조를 가짐")

    # 문제 2 테스트
    print()
    print("=" * 50)
    print("문제 2: 도메인별 예외 활용 테스트")
    print("=" * 50)

    # 테스트 2-1: 사용자 조회 성공
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "홍길동"
    print("  [통과] 사용자 조회 성공 테스트")

    # 테스트 2-2: 존재하지 않는 사용자 조회 -> NotFoundException
    response = client.get("/users/999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert data["detail"]["user_id"] == 999
    print("  [통과] 존재하지 않는 사용자 조회 테스트 (404)")

    # 테스트 2-3: 사용자 생성 성공
    response = client.post("/users", json={"name": "이영희", "email": "lee@example.com", "age": 28})
    assert response.status_code == 201
    assert response.json()["name"] == "이영희"
    print("  [통과] 사용자 생성 성공 테스트")

    # 테스트 2-4: 중복 이메일로 생성 -> DuplicateError
    response = client.post("/users", json={"name": "홍길동2", "email": "hong@example.com", "age": 35})
    assert response.status_code == 409
    data = response.json()
    assert data["error_code"] == "DUPLICATE_EMAIL"
    assert data["detail"]["email"] == "hong@example.com"
    print("  [통과] 중복 이메일 생성 테스트 (409)")

    # 테스트 2-5: 사용자 수정 시 유효하지 않은 나이 -> CustomValidationError
    response = client.put("/users/1", json={"name": "홍길동", "email": "hong@example.com", "age": -1})
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "INVALID_INPUT"
    assert data["detail"]["field"] == "age"
    print("  [통과] 유효하지 않은 데이터 수정 테스트 (422)")

    # 테스트 2-6: 존재하지 않는 사용자 수정 -> NotFoundException
    response = client.put("/users/999", json={"name": "없는사람", "email": "none@example.com", "age": 20})
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    print("  [통과] 존재하지 않는 사용자 수정 테스트 (404)")

    print()
    print("모든 테스트를 통과했습니다!")
