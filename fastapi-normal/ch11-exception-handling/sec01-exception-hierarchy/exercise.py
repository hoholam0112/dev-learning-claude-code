# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from enum import Enum
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


# ============================================================
# 문제 1: 커스텀 예외 계층 구조
# ============================================================

# TODO: ErrorCode Enum을 정의하세요
# - str과 Enum을 동시에 상속 (JSON 직렬화를 위해)
# - 값: USER_NOT_FOUND, DUPLICATE_EMAIL, INVALID_INPUT,
#        AUTHORIZATION_FAILED, RESOURCE_NOT_FOUND, DUPLICATE_RESOURCE


# TODO: AppException 기반 클래스를 구현하세요
# - Exception을 상속
# - __init__ 매개변수: status_code (int, 기본값 500),
#   error_code (str, 기본값 "INTERNAL_ERROR"),
#   message (str, 기본값 "내부 서버 오류가 발생했습니다"),
#   detail (dict | None, 기본값 None)
# - 각 매개변수를 인스턴스 속성으로 저장
# - super().__init__(message) 호출


# TODO: NotFoundException 클래스를 구현하세요
# - AppException을 상속
# - 기본 status_code: 404
# - 기본 error_code: ErrorCode.RESOURCE_NOT_FOUND
# - 기본 message: "요청한 리소스를 찾을 수 없습니다"


# TODO: DuplicateError 클래스를 구현하세요
# - AppException을 상속
# - 기본 status_code: 409
# - 기본 error_code: ErrorCode.DUPLICATE_RESOURCE
# - 기본 message: "이미 존재하는 리소스입니다"


# TODO: CustomValidationError 클래스를 구현하세요
# - AppException을 상속
# - 기본 status_code: 422
# - 기본 error_code: ErrorCode.INVALID_INPUT
# - 기본 message: "입력값이 유효하지 않습니다"


# TODO: AuthorizationError 클래스를 구현하세요
# - AppException을 상속
# - 기본 status_code: 403
# - 기본 error_code: ErrorCode.AUTHORIZATION_FAILED
# - 기본 message: "접근 권한이 없습니다"


# TODO: AppException 전역 핸들러를 등록하세요
# - @app.exception_handler(AppException) 데코레이터 사용
# - JSONResponse를 반환:
#   status_code=exc.status_code,
#   content={"error_code": exc.error_code, "message": exc.message, "detail": exc.detail}


# TODO: 테스트용 엔드포인트를 작성하세요
# GET /test/not-found -> NotFoundException 발생
#   error_code: ErrorCode.USER_NOT_FOUND, message: "사용자를 찾을 수 없습니다", detail: {"user_id": 999}

# GET /test/duplicate -> DuplicateError 발생
#   error_code: ErrorCode.DUPLICATE_EMAIL, message: "이미 등록된 이메일입니다", detail: {"email": "test@example.com"}

# GET /test/validation -> CustomValidationError 발생
#   error_code: ErrorCode.INVALID_INPUT, message: "나이는 0보다 커야 합니다", detail: {"field": "age", "value": -1}

# GET /test/authorization -> AuthorizationError 발생
#   message: "관리자만 접근할 수 있습니다", detail: {"required_role": "admin"}


# ============================================================
# 문제 2: 도메인별 예외 활용
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


# TODO: POST /users 엔드포인트를 작성하세요 (status_code=201)
# - UserCreate 모델로 요청 바디를 받음
# - fake_users_db에서 이메일 중복 검사
#   - 중복이면 DuplicateError(error_code=ErrorCode.DUPLICATE_EMAIL, message="이미 등록된 이메일입니다", detail={"email": user.email})
# - 새 사용자를 fake_users_db에 추가하고 반환
# - next_user_id를 global로 사용하여 증가


# TODO: GET /users/{user_id} 엔드포인트를 작성하세요
# - user_id가 fake_users_db에 없으면 NotFoundException 발생
#   error_code=ErrorCode.USER_NOT_FOUND, message="사용자를 찾을 수 없습니다", detail={"user_id": user_id}
# - 존재하면 사용자 정보 반환


# TODO: PUT /users/{user_id} 엔드포인트를 작성하세요
# - user_id가 fake_users_db에 없으면 NotFoundException 발생
# - user.age가 0 이하이면 CustomValidationError 발생
#   error_code=ErrorCode.INVALID_INPUT, message="나이는 0보다 커야 합니다", detail={"field": "age", "value": user.age}
# - 이메일 중복 검사 (자기 자신 제외)
#   - 중복이면 DuplicateError 발생
# - fake_users_db 업데이트 후 반환


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
