# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

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
# 문제 1: 표준 에러 응답과 전역 핸들러
# ============================================================

# TODO: ErrorResponse Pydantic 모델을 정의하세요
# - error_code: str (에러 코드)
# - message: str (에러 메시지)
# - detail: dict | list | None = None (추가 상세 정보)
# - timestamp: str (에러 발생 시각, ISO 8601)


app = FastAPI()


# TODO: AppException 전역 핸들러를 등록하세요
# - @app.exception_handler(AppException) 데코레이터 사용
# - ErrorResponse 모델을 사용하여 JSONResponse 반환
# - timestamp는 datetime.now().isoformat()으로 생성
# - content에는 ErrorResponse(...).model_dump()를 사용


# TODO: RequestValidationError 전역 핸들러를 등록하세요
# - @app.exception_handler(RequestValidationError) 데코레이터 사용
# - status_code: 422
# - error_code: "VALIDATION_ERROR"
# - message: "요청 데이터가 유효하지 않습니다"
# - detail: exc.errors() (Pydantic 검증 오류 목록)
# - timestamp: datetime.now().isoformat()


# TODO: Exception catch-all 전역 핸들러를 등록하세요
# - @app.exception_handler(Exception) 데코레이터 사용
# - status_code: 500
# - error_code: "INTERNAL_ERROR"
# - message: "내부 서버 오류가 발생했습니다"
# - detail: None (내부 에러 정보를 클라이언트에 노출하지 않음)
# - timestamp: datetime.now().isoformat()


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
# 문제 2: 에러 핸들러 통합 테스트
# ============================================================

# 가상 사용자 데이터
fake_users_db: dict[int, dict] = {
    1: {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    2: {"id": 2, "name": "김철수", "email": "kim@example.com"},
}


class UserCreate(BaseModel):
    name: str
    email: str


# TODO: GET /users/{user_id} 엔드포인트를 작성하세요
# - user_id가 fake_users_db에 없으면 NotFoundException 발생
#   error_code=ErrorCode.USER_NOT_FOUND, message="사용자를 찾을 수 없습니다",
#   detail={"user_id": user_id}
# - 존재하면 사용자 정보 반환


# TODO: POST /users 엔드포인트를 작성하세요 (status_code=201)
# - UserCreate 모델로 요청 바디를 받음
# - 이메일 중복 시 DuplicateError 발생
# - 새 사용자 추가 후 반환


# TODO: GET /crash 엔드포인트를 작성하세요
# - RuntimeError("데이터베이스 연결 실패!") 발생
# - catch-all 핸들러에 의해 처리됨


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
