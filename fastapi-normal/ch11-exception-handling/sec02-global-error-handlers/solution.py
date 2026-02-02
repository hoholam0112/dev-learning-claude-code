# 모범 답안: 전역 에러 핸들러
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from datetime import datetime
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel


# ============================================================
# 공통: 예외 계층 구조 (sec01에서 학습한 내용)
# ============================================================

class ErrorCode(str, Enum):
    """에러 코드 Enum"""
    USER_NOT_FOUND = "USER_NOT_FOUND"
    DUPLICATE_EMAIL = "DUPLICATE_EMAIL"
    INVALID_INPUT = "INVALID_INPUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppException(Exception):
    """애플리케이션 예외 기반 클래스"""

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
        error_code: str = ErrorCode.USER_NOT_FOUND,
        message: str = "요청한 리소스를 찾을 수 없습니다",
        detail: dict | None = None,
    ):
        super().__init__(status_code=404, error_code=error_code, message=message, detail=detail)


class DuplicateError(AppException):
    """중복된 리소스가 존재할 때 발생하는 예외 (409)"""

    def __init__(
        self,
        error_code: str = ErrorCode.DUPLICATE_EMAIL,
        message: str = "이미 존재하는 리소스입니다",
        detail: dict | None = None,
    ):
        super().__init__(status_code=409, error_code=error_code, message=message, detail=detail)


# ============================================================
# 문제 1 해답: 표준 에러 응답과 전역 핸들러
# ============================================================

class ErrorResponse(BaseModel):
    """표준 에러 응답 모델.

    모든 에러 응답이 이 형식을 따릅니다.

    Attributes:
        error_code: 에러 종류를 구분하는 코드
        message: 사용자에게 표시할 메시지
        detail: 추가 상세 정보 (검증 오류 목록 등)
        timestamp: 에러 발생 시각 (ISO 8601)
    """
    error_code: str
    message: str
    detail: dict | list | None = None
    timestamp: str


app = FastAPI()


# 전역 핸들러 1: AppException (비즈니스 에러)
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """AppException과 모든 하위 클래스를 ErrorResponse 형식으로 변환합니다."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            detail=exc.detail,
            timestamp=datetime.now().isoformat(),
        ).model_dump(),
    )


# 전역 핸들러 2: RequestValidationError (입력 검증 에러)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 검증 오류를 ErrorResponse 형식으로 변환합니다."""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="요청 데이터가 유효하지 않습니다",
            detail=exc.errors(),
            timestamp=datetime.now().isoformat(),
        ).model_dump(),
    )


# 전역 핸들러 3: Exception catch-all (예상치 못한 에러)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """모든 미처리 예외를 500 ErrorResponse로 변환합니다."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="내부 서버 오류가 발생했습니다",
            detail=None,
            timestamp=datetime.now().isoformat(),
        ).model_dump(),
    )


# 문제 1 테스트용 엔드포인트
@app.get("/test/app-error")
async def test_app_error():
    """AppException 핸들러 테스트"""
    raise NotFoundException(
        error_code=ErrorCode.USER_NOT_FOUND,
        message="사용자를 찾을 수 없습니다",
        detail={"user_id": 999},
    )


class TestBody(BaseModel):
    name: str
    age: int


@app.post("/test/validation")
async def test_validation(body: TestBody):
    """RequestValidationError 핸들러 테스트 (잘못된 바디를 보내면 발생)"""
    return {"name": body.name, "age": body.age}


@app.get("/test/crash")
async def test_crash():
    """catch-all 핸들러 테스트 (의도적 RuntimeError)"""
    raise RuntimeError("예상치 못한 서버 오류!")


# ============================================================
# 문제 2 해답: 에러 핸들러 통합 테스트
# ============================================================

# 가상 사용자 데이터
fake_users_db: dict[int, dict] = {
    1: {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    2: {"id": 2, "name": "김철수", "email": "kim@example.com"},
}


class UserCreate(BaseModel):
    name: str
    email: str


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """사용자 조회 - 존재하지 않으면 NotFoundException"""
    if user_id not in fake_users_db:
        raise NotFoundException(
            error_code=ErrorCode.USER_NOT_FOUND,
            message="사용자를 찾을 수 없습니다",
            detail={"user_id": user_id},
        )
    return fake_users_db[user_id]


@app.post("/users", status_code=201)
async def create_user(user: UserCreate):
    """사용자 생성 - 이메일 중복 시 DuplicateError"""
    for existing_user in fake_users_db.values():
        if existing_user["email"] == user.email:
            raise DuplicateError(
                error_code=ErrorCode.DUPLICATE_EMAIL,
                message="이미 등록된 이메일입니다",
                detail={"email": user.email},
            )

    new_id = max(fake_users_db.keys()) + 1
    new_user = {"id": new_id, "name": user.name, "email": user.email}
    fake_users_db[new_id] = new_user
    return new_user


@app.get("/crash")
async def crash_endpoint():
    """의도적 서버 오류 발생"""
    raise RuntimeError("데이터베이스 연결 실패!")


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)

    # 문제 1 테스트
    print("=" * 50)
    print("문제 1: 표준 에러 응답과 전역 핸들러 테스트")
    print("=" * 50)

    # 테스트 1-1: AppException 핸들러 - NotFoundException
    response = client.get("/test/app-error")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert data["message"] == "사용자를 찾을 수 없습니다"
    assert "timestamp" in data
    assert data["detail"]["user_id"] == 999
    print("  [통과] AppException 핸들러 테스트 (404, ErrorResponse 형식)")

    # 테스트 1-2: RequestValidationError 핸들러
    response = client.post("/test/validation", json={"invalid": "data"})
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert data["message"] == "요청 데이터가 유효하지 않습니다"
    assert "timestamp" in data
    assert isinstance(data["detail"], list)
    assert len(data["detail"]) > 0
    print("  [통과] RequestValidationError 핸들러 테스트 (422, ErrorResponse 형식)")

    # 테스트 1-3: catch-all 핸들러 - RuntimeError
    response = client.get("/test/crash")
    assert response.status_code == 500
    data = response.json()
    assert data["error_code"] == "INTERNAL_ERROR"
    assert data["message"] == "내부 서버 오류가 발생했습니다"
    assert "timestamp" in data
    assert data["detail"] is None
    print("  [통과] catch-all 핸들러 테스트 (500, ErrorResponse 형식)")

    # 테스트 1-4: 정상 요청은 ErrorResponse가 아닌 일반 응답
    response = client.post("/test/validation", json={"name": "홍길동", "age": 30})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "홍길동"
    assert data["age"] == 30
    print("  [통과] 정상 요청은 일반 응답 반환")

    # 문제 2 테스트
    print()
    print("=" * 50)
    print("문제 2: 에러 핸들러 통합 테스트")
    print("=" * 50)

    # 테스트 2-1: 사용자 조회 성공
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "홍길동"
    print("  [통과] 사용자 조회 성공")

    # 테스트 2-2: 존재하지 않는 사용자 -> NotFoundException -> ErrorResponse
    response = client.get("/users/999")
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert "timestamp" in data
    print("  [통과] NotFoundException -> ErrorResponse 형식 (404)")

    # 테스트 2-3: 잘못된 요청 바디 -> RequestValidationError -> ErrorResponse
    response = client.post("/users", json={"wrong_field": "value"})
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "timestamp" in data
    assert isinstance(data["detail"], list)
    print("  [통과] RequestValidationError -> ErrorResponse 형식 (422)")

    # 테스트 2-4: 서버 크래시 -> catch-all -> ErrorResponse
    response = client.get("/crash")
    assert response.status_code == 500
    data = response.json()
    assert data["error_code"] == "INTERNAL_ERROR"
    assert "timestamp" in data
    print("  [통과] RuntimeError -> ErrorResponse 형식 (500)")

    # 테스트 2-5: 모든 에러 응답 구조 일관성 검증
    error_endpoints = [
        ("/users/999", "GET"),
        ("/crash", "GET"),
    ]
    for path, method in error_endpoints:
        if method == "GET":
            response = client.get(path)
        data = response.json()
        assert "error_code" in data, f"{path}: error_code 누락"
        assert "message" in data, f"{path}: message 누락"
        assert "timestamp" in data, f"{path}: timestamp 누락"
    print("  [통과] 모든 에러 응답이 일관된 ErrorResponse 구조")

    print()
    print("모든 테스트를 통과했습니다!")
