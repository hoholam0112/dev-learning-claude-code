# 실행 방법: uvicorn exercise:app --reload
# 챕터 08 연습 문제 - 직접 코드를 작성해보세요!

import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime
from statistics import mean

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

# ── 로깅 설정 ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api")


# ══════════════════════════════════════════════════════════
# 문제 1: 커스텀 예외 클래스
# 일관된 에러 응답 형식을 위한 예외 계층 구조를 만드세요
# ══════════════════════════════════════════════════════════

# TODO: AppException 기반 클래스를 정의하세요
# __init__(self, message, code, details=None)


# TODO: ResourceNotFoundError를 정의하세요 (AppException 상속)
# __init__(self, resource, resource_id)
# code: "RESOURCE_NOT_FOUND"


# TODO: AuthenticationError를 정의하세요 (AppException 상속)
# code: "AUTHENTICATION_FAILED"


# TODO: PermissionDeniedError를 정의하세요 (AppException 상속)
# code: "PERMISSION_DENIED", details에 required_role 포함


# TODO: CustomValidationError를 정의하세요 (AppException 상속)
# code: "VALIDATION_ERROR", details에 field 포함


# ══════════════════════════════════════════════════════════
# 문제 2: 처리 시간 측정 미들웨어
# ══════════════════════════════════════════════════════════

# TODO: ProcessTimeMiddleware를 정의하세요 (BaseHTTPMiddleware 상속)
# - dispatch 메서드에서 요청 처리 시간을 측정
# - 응답 헤더에 X-Process-Time 추가
# - 1초 초과 → 경고 로그, 5초 초과 → 에러 로그
# - 통계 수집: total_requests, average_time, max_time, slow_count


# ══════════════════════════════════════════════════════════
# 문제 3: IP 기반 접근 제한 미들웨어
# ══════════════════════════════════════════════════════════

# TODO: IPAccessControlMiddleware를 정의하세요 (BaseHTTPMiddleware 상속)
# - 차단된 IP → 403 반환
# - 분당 요청 횟수 제한 (RATE_LIMIT = 60)
# - 제한 초과 → 429 반환
# - 화이트리스트 경로는 제한 없이 통과: /health, /docs, /openapi.json, /redoc


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="챕터 08 연습 문제", description="에러 처리 + 미들웨어")

# TODO: 미들웨어를 등록하세요
# app.add_middleware(ProcessTimeMiddleware)
# app.add_middleware(IPAccessControlMiddleware)


# ══════════════════════════════════════════════════════════
# 문제 1: 전역 예외 핸들러
# ══════════════════════════════════════════════════════════

def create_error_response(
    status_code: int, code: str, message: str, details: dict | None = None
) -> JSONResponse:
    """일관된 에러 응답을 생성하는 헬퍼 함수"""
    # TODO: JSONResponse를 반환하세요
    # 형식: {"success": False, "error": {"code": ..., "message": ..., "details": ...}, "timestamp": ...}
    pass


# TODO: 각 커스텀 예외에 대한 exception_handler를 등록하세요
# @app.exception_handler(ResourceNotFoundError) → 404
# @app.exception_handler(AuthenticationError) → 401
# @app.exception_handler(PermissionDeniedError) → 403
# @app.exception_handler(CustomValidationError) → 422
# @app.exception_handler(RequestValidationError) → 422 (커스텀 형식)
# @app.exception_handler(Exception) → 500 (전역 핸들러)


# ── Pydantic 모델 ─────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: int = Field(gt=0, lt=150)


# ── 임시 데이터 ────────────────────────────────────────────
users_db = {
    1: {"id": 1, "username": "admin", "email": "admin@example.com", "role": "admin"},
    2: {"id": 2, "username": "user1", "email": "user1@example.com", "role": "user"},
}


# ── 에러 테스트 엔드포인트 ─────────────────────────────────

@app.get("/error-test/not-found/{user_id}", tags=["에러 테스트"])
async def test_not_found(user_id: int):
    """ResourceNotFoundError를 발생시킵니다."""
    # TODO: user_id가 users_db에 없으면 ResourceNotFoundError 발생
    pass


@app.get("/error-test/auth", tags=["에러 테스트"])
async def test_auth_error():
    """AuthenticationError를 발생시킵니다."""
    # TODO: AuthenticationError 발생
    pass


@app.get("/error-test/permission", tags=["에러 테스트"])
async def test_permission_error():
    """PermissionDeniedError를 발생시킵니다."""
    # TODO: PermissionDeniedError 발생
    pass


@app.post("/error-test/validation", tags=["에러 테스트"])
async def test_validation_error(user: UserCreate):
    """잘못된 입력값을 보내면 검증 에러가 발생합니다."""
    return {"message": "검증 통과", "user": user.model_dump()}


@app.get("/slow/{seconds}", tags=["통계"])
async def slow_endpoint(seconds: float = 1.0):
    """느린 요청 시뮬레이션 (미들웨어 테스트용)"""
    await asyncio.sleep(min(seconds, 10))
    return {"message": f"{seconds}초 대기 완료"}


@app.get("/health", tags=["헬스체크"])
async def health_check():
    """서버 상태 확인 — IP 제한 없이 접근 가능"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
