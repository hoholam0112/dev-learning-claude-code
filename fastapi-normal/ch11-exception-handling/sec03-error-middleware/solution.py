# 모범 답안: 에러 미들웨어
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

import uuid
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel


# ============================================================
# 공통: 예외 계층 구조와 ErrorResponse (sec01, sec02에서 학습)
# ============================================================

class ErrorCode(str, Enum):
    """에러 코드 Enum"""
    USER_NOT_FOUND = "USER_NOT_FOUND"
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


class ErrorResponse(BaseModel):
    """표준 에러 응답 모델"""
    error_code: str
    message: str
    detail: dict | list | None = None
    timestamp: str
    trace_id: str | None = None


# FastAPI 앱 생성
app = FastAPI()


# 테스트용 에러 로그 저장소 (문제 2에서 사용)
error_log: list[dict] = []


# ============================================================
# 미들웨어 등록
# ============================================================
# @app.middleware("http") 데코레이터는 나중에 등록한 것이 바깥쪽(먼저 실행)입니다.
# 등록 순서:
#   1. error_logging_middleware (먼저 등록 = 안쪽)
#   2. trace_id_middleware (나중에 등록 = 바깥쪽, 먼저 실행)
# 실행 순서: trace_id(바깥) → error_logging(안쪽) → 라우트 핸들러


# ============================================================
# 문제 2 해답: 에러 로깅 미들웨어 (안쪽, 먼저 등록)
# ============================================================

@app.middleware("http")
async def error_logging_middleware(request: Request, call_next):
    """에러 로깅 미들웨어.

    에러 응답(status_code >= 400)이 발생하면 error_log에 기록합니다.

    주의: @app.middleware("http") 미들웨어에서 call_next()는
    등록된 exception_handler가 처리하지 못한 예외를 그대로 전파할 수 있습니다.
    따라서 try-except로 예외를 직접 잡아서 에러 응답을 생성하고 로깅해야 합니다.
    """
    try:
        response = await call_next(request)
    except Exception:
        # 미들웨어까지 전파된 예외 → 500 에러 응답 생성
        trace_id = getattr(request.state, "trace_id", "unknown")
        response = JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error_code="INTERNAL_ERROR",
                message="내부 서버 오류가 발생했습니다",
                detail=None,
                timestamp=datetime.now().isoformat(),
                trace_id=trace_id if trace_id != "unknown" else None,
            ).model_dump(),
        )

    # 에러 응답(4xx, 5xx)인 경우 로깅
    if response.status_code >= 400:
        error_log.append({
            "trace_id": getattr(request.state, "trace_id", "unknown"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "error_type": f"HTTP_{response.status_code}",
            "error_message": f"에러 응답 반환: {response.status_code}",
        })

    return response


# ============================================================
# 문제 1 해답: trace_id 미들웨어 (바깥쪽, 나중에 등록)
# ============================================================

@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    """trace_id 미들웨어.

    모든 요청에 고유한 trace_id를 부여합니다.
    - uuid4로 trace_id 생성
    - request.state.trace_id에 저장
    - 응답 헤더 X-Trace-ID에 추가

    예외가 발생해도 trace_id를 응답 헤더에 추가하기 위해
    try-except로 감싸고, 에러 시 500 응답을 직접 생성합니다.
    """
    # trace_id 생성
    trace_id = str(uuid.uuid4())

    # request.state에 저장 (핸들러와 에러 핸들러에서 사용 가능)
    request.state.trace_id = trace_id

    # 요청 처리 (예외가 전파될 수 있음)
    try:
        response = await call_next(request)
    except Exception:
        # 미처리 예외 → 500 에러 응답 생성
        response = JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error_code="INTERNAL_ERROR",
                message="내부 서버 오류가 발생했습니다",
                detail=None,
                timestamp=datetime.now().isoformat(),
                trace_id=trace_id,
            ).model_dump(),
        )

    # 응답 헤더에 trace_id 추가
    response.headers["X-Trace-ID"] = trace_id

    return response


# 전역 핸들러: AppException
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """AppException을 ErrorResponse 형식으로 변환합니다.
    request.state.trace_id를 에러 응답에 포함합니다.
    """
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            detail=exc.detail,
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
        ).model_dump(),
    )


# 전역 핸들러: catch-all
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """모든 미처리 예외를 500 ErrorResponse로 변환합니다."""
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="내부 서버 오류가 발생했습니다",
            detail=None,
            timestamp=datetime.now().isoformat(),
            trace_id=trace_id,
        ).model_dump(),
    )


# 엔드포인트
@app.get("/health")
async def health():
    """정상 응답 엔드포인트"""
    return {"status": "ok"}


@app.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    """사용자 조회 - trace_id를 응답에 포함"""
    fake_users = {1: {"id": 1, "name": "홍길동"}, 2: {"id": 2, "name": "김철수"}}
    if user_id not in fake_users:
        raise NotFoundException(
            error_code=ErrorCode.USER_NOT_FOUND,
            message="사용자를 찾을 수 없습니다",
            detail={"user_id": user_id},
        )
    user = fake_users[user_id]
    user["trace_id"] = getattr(request.state, "trace_id", None)
    return user


@app.get("/error/not-found")
async def error_not_found():
    """NotFoundException 발생 테스트"""
    raise NotFoundException(
        error_code=ErrorCode.USER_NOT_FOUND,
        message="사용자를 찾을 수 없습니다",
        detail={"user_id": 999},
    )


@app.get("/error/runtime")
async def error_runtime():
    """RuntimeError 발생 테스트"""
    raise RuntimeError("예상치 못한 오류 발생!")


# --- 테스트 ---
if __name__ == "__main__":
    # 매 테스트 실행 전 에러 로그 초기화
    error_log.clear()

    client = TestClient(app, raise_server_exceptions=False)

    # 문제 1 테스트
    print("=" * 50)
    print("문제 1: trace_id 미들웨어 테스트")
    print("=" * 50)

    # 테스트 1-1: 정상 응답에 X-Trace-ID 헤더 포함
    response = client.get("/health")
    assert response.status_code == 200
    assert "x-trace-id" in response.headers
    trace_id_1 = response.headers["x-trace-id"]
    assert len(trace_id_1) == 36  # UUID 형식
    print(f"  [통과] 정상 응답에 X-Trace-ID 포함: {trace_id_1}")

    # 테스트 1-2: 매 요청마다 새로운 trace_id 생성
    response2 = client.get("/health")
    trace_id_2 = response2.headers["x-trace-id"]
    assert trace_id_1 != trace_id_2
    print("  [통과] 매 요청마다 새로운 trace_id 생성")

    # 테스트 1-3: 에러 응답에도 trace_id 포함 (응답 바디)
    response = client.get("/users/999")
    assert response.status_code == 404
    data = response.json()
    assert "trace_id" in data
    assert data["trace_id"] is not None
    assert len(data["trace_id"]) == 36
    print(f"  [통과] 에러 응답 바디에 trace_id 포함: {data['trace_id']}")

    # 테스트 1-4: 에러 응답 헤더에도 X-Trace-ID 포함
    assert "x-trace-id" in response.headers
    header_trace_id = response.headers["x-trace-id"]
    assert len(header_trace_id) == 36
    print(f"  [통과] 에러 응답 헤더에 X-Trace-ID 포함: {header_trace_id}")

    # 테스트 1-5: 정상 응답에서 핸들러가 trace_id 접근 가능
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "홍길동"
    assert "trace_id" in data
    assert data["trace_id"] is not None
    print("  [통과] 엔드포인트에서 request.state.trace_id 접근 가능")

    # 문제 2 테스트
    print()
    print("=" * 50)
    print("문제 2: 에러 로깅 미들웨어 테스트")
    print("=" * 50)

    # 에러 로그 초기화
    error_log.clear()

    # 테스트 2-1: NotFoundException 발생 시 에러 로그 기록
    response = client.get("/error/not-found")
    assert response.status_code == 404
    assert len(error_log) >= 1
    last_log = error_log[-1]
    assert last_log["method"] == "GET"
    assert last_log["path"] == "/error/not-found"
    assert last_log["status_code"] == 404
    assert "trace_id" in last_log
    print(f"  [통과] NotFoundException 에러 로그 기록 (status: {last_log['status_code']})")

    # 테스트 2-2: RuntimeError 발생 시 에러 로그 기록
    response = client.get("/error/runtime")
    assert response.status_code == 500
    assert len(error_log) >= 2
    last_log = error_log[-1]
    assert last_log["method"] == "GET"
    assert last_log["path"] == "/error/runtime"
    assert last_log["status_code"] == 500
    print(f"  [통과] RuntimeError 에러 로그 기록 (status: {last_log['status_code']})")

    # 테스트 2-3: 에러 로그에 trace_id 포함
    for log_entry in error_log:
        assert "trace_id" in log_entry
        assert log_entry["trace_id"] != "unknown"
    print("  [통과] 모든 에러 로그에 trace_id 포함")

    # 테스트 2-4: 정상 요청 시 에러 로그 추가되지 않음
    log_count_before = len(error_log)
    response = client.get("/health")
    assert response.status_code == 200
    assert len(error_log) == log_count_before
    print("  [통과] 정상 요청 시 에러 로그 추가되지 않음")

    # 테스트 2-5: 에러 응답이 여전히 올바른 ErrorResponse 형식
    response = client.get("/error/not-found")
    data = response.json()
    assert data["error_code"] == "USER_NOT_FOUND"
    assert "message" in data
    assert "timestamp" in data
    assert "trace_id" in data
    print("  [통과] 에러 로깅 후에도 올바른 ErrorResponse 형식 유지")

    # 테스트 2-6: 에러 로그 전체 구조 검증
    assert len(error_log) >= 3  # not-found, runtime, not-found
    for log_entry in error_log:
        assert "trace_id" in log_entry
        assert "method" in log_entry
        assert "path" in log_entry
        assert "status_code" in log_entry
        assert "error_type" in log_entry
        assert "error_message" in log_entry
    print("  [통과] 모든 에러 로그가 올바른 구조를 가짐")

    print()
    print("모든 테스트를 통과했습니다!")
