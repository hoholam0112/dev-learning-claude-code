# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn

"""
챕터 08 모범 답안: 에러 처리와 미들웨어

문제 1~3의 통합 솔루션입니다.
커스텀 에러 포맷 + 처리 시간 측정 + IP 접근 제한을 포함합니다.
"""

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
# ══════════════════════════════════════════════════════════

class AppException(Exception):
    """모든 앱 예외의 기반 클래스"""
    def __init__(self, message: str, code: str, details: dict | None = None):
        self.message = message
        self.code = code
        self.details = details or {}


class ResourceNotFoundError(AppException):
    """리소스를 찾을 수 없을 때 발생"""
    def __init__(self, resource: str, resource_id: int | str):
        super().__init__(
            message=f"요청한 {resource}을(를) 찾을 수 없습니다",
            code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "id": resource_id},
        )


class AuthenticationError(AppException):
    """인증 실패 시 발생"""
    def __init__(self, message: str = "인증에 실패했습니다"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
        )


class PermissionDeniedError(AppException):
    """권한 부족 시 발생"""
    def __init__(self, required_role: str = "admin"):
        super().__init__(
            message="이 작업을 수행할 권한이 없습니다",
            code="PERMISSION_DENIED",
            details={"required_role": required_role},
        )


class CustomValidationError(AppException):
    """비즈니스 로직 검증 실패 시 발생"""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field},
        )


# ══════════════════════════════════════════════════════════
# 문제 2: 처리 시간 측정 미들웨어
# ══════════════════════════════════════════════════════════

class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    요청 처리 시간을 측정하고 통계를 수집하는 미들웨어입니다.
    느린 요청에 대해 경고/에러 로그를 출력합니다.
    """

    SLOW_THRESHOLD = 1.0      # 경고 임계값 (초)
    CRITICAL_THRESHOLD = 5.0  # 에러 임계값 (초)

    def __init__(self, app):
        super().__init__(app)
        # 통계 데이터 저장
        self.request_times: list[float] = []
        self.slow_count: int = 0
        self.start_timestamp: float = time.time()

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 엔드포인트 처리
        response = await call_next(request)

        # 처리 시간 계산
        process_time = time.time() - start_time

        # 통계 수집 (/stats 엔드포인트 자체는 제외)
        if request.url.path != "/stats":
            self.request_times.append(process_time)

            # 느린 요청 감지
            if process_time > self.CRITICAL_THRESHOLD:
                logger.error(
                    f"매우 느린 요청: {request.method} {request.url.path} "
                    f"- {process_time:.4f}초"
                )
                self.slow_count += 1
            elif process_time > self.SLOW_THRESHOLD:
                logger.warning(
                    f"느린 요청: {request.method} {request.url.path} "
                    f"- {process_time:.4f}초"
                )
                self.slow_count += 1

        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response

    def get_stats(self) -> dict:
        """현재까지의 통계 데이터를 반환합니다."""
        total = len(self.request_times)
        uptime = time.time() - self.start_timestamp
        return {
            "total_requests": total,
            "average_time": round(mean(self.request_times), 4) if total > 0 else 0,
            "max_time": round(max(self.request_times), 4) if total > 0 else 0,
            "slow_requests": self.slow_count,
            "uptime_seconds": round(uptime, 1),
        }


# ══════════════════════════════════════════════════════════
# 문제 3: IP 기반 접근 제한 미들웨어
# ══════════════════════════════════════════════════════════

class IPAccessControlMiddleware(BaseHTTPMiddleware):
    """
    IP 기반 접근 제한과 속도 제한을 적용하는 미들웨어입니다.
    """

    # IP 제한에서 제외할 경로 목록
    WHITELIST_PATHS = ["/health", "/docs", "/openapi.json", "/redoc"]

    # 속도 제한: 분당 최대 요청 수
    RATE_LIMIT = 60
    RATE_WINDOW = 60  # 초 단위 (1분)

    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips: set[str] = set()
        # IP별 요청 타임스탬프 기록
        self.request_log: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # 화이트리스트 경로는 제한 없이 통과
        if any(path.startswith(wp) for wp in self.WHITELIST_PATHS):
            return await call_next(request)

        # 1. 차단된 IP 확인
        if client_ip in self.blocked_ips:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "ACCESS_DENIED",
                    "message": "접근이 차단된 IP 주소입니다",
                    "client_ip": client_ip,
                },
            )

        # 2. 속도 제한 확인
        now = time.time()
        # 1분이 지난 요청 기록 제거
        self.request_log[client_ip] = [
            t for t in self.request_log[client_ip]
            if now - t < self.RATE_WINDOW
        ]

        # 현재 요청 기록 추가
        self.request_log[client_ip].append(now)

        # 제한 초과 확인
        if len(self.request_log[client_ip]) > self.RATE_LIMIT:
            # 가장 오래된 요청과의 시간 차이로 retry_after 계산
            oldest = self.request_log[client_ip][0]
            retry_after = int(self.RATE_WINDOW - (now - oldest))

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "요청 횟수가 제한을 초과했습니다. 잠시 후 다시 시도해주세요.",
                    "retry_after": max(retry_after, 1),
                },
                headers={"Retry-After": str(max(retry_after, 1))},
            )

        return await call_next(request)


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="챕터 08 종합 솔루션", description="에러 처리 + 미들웨어 종합 예제")

# 미들웨어 인스턴스 (엔드포인트에서 접근하기 위해 별도 생성)
process_time_middleware = ProcessTimeMiddleware
ip_access_middleware = IPAccessControlMiddleware

# 미들웨어 등록
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(IPAccessControlMiddleware)


# ══════════════════════════════════════════════════════════
# 문제 1: 전역 예외 핸들러
# ══════════════════════════════════════════════════════════

def create_error_response(
    status_code: int, code: str, message: str, details: dict | None = None
) -> JSONResponse:
    """일관된 에러 응답을 생성하는 헬퍼 함수"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return create_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return create_error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(CustomValidationError)
async def custom_validation_handler(request: Request, exc: CustomValidationError):
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    """FastAPI 기본 422 에러를 커스텀 형식으로 변환"""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = " -> ".join(str(loc) for loc in first_error.get("loc", []))

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message=f"입력값 검증에 실패했습니다: {field}",
        details={"errors": [{"field": field, "message": e.get("msg", "")} for e in errors]},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """모든 미처리 예외를 잡는 전역 핸들러"""
    logger.error(f"미처리 예외: {type(exc).__name__}: {exc}")
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    )


# ── Pydantic 모델 ─────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: int = Field(gt=0, lt=150)


class BlockIPRequest(BaseModel):
    ip: str


# ── 임시 데이터 ────────────────────────────────────────────
users_db = {
    1: {"id": 1, "username": "admin", "email": "admin@example.com", "role": "admin"},
    2: {"id": 2, "username": "user1", "email": "user1@example.com", "role": "user"},
}


# ── 엔드포인트 ─────────────────────────────────────────────

# 문제 1: 에러 테스트 엔드포인트
@app.get("/error-test/not-found/{user_id}", tags=["에러 테스트"], summary="404 에러 테스트")
async def test_not_found(user_id: int):
    """ResourceNotFoundError를 발생시킵니다."""
    if user_id not in users_db:
        raise ResourceNotFoundError("user", user_id)
    return users_db[user_id]


@app.get("/error-test/auth", tags=["에러 테스트"], summary="401 에러 테스트")
async def test_auth_error():
    """AuthenticationError를 발생시킵니다."""
    raise AuthenticationError("토큰이 유효하지 않습니다")


@app.get("/error-test/permission", tags=["에러 테스트"], summary="403 에러 테스트")
async def test_permission_error():
    """PermissionDeniedError를 발생시킵니다."""
    raise PermissionDeniedError(required_role="admin")


@app.post("/error-test/validation", tags=["에러 테스트"], summary="422 에러 테스트")
async def test_validation_error(user: UserCreate):
    """잘못된 입력값을 보내면 RequestValidationError가 발생합니다."""
    return {"message": "검증 통과", "user": user.model_dump()}


@app.get("/error-test/custom-validation", tags=["에러 테스트"], summary="커스텀 검증 에러 테스트")
async def test_custom_validation(age: int = 0):
    """비즈니스 로직 수준의 검증 에러를 발생시킵니다."""
    if age < 18:
        raise CustomValidationError(
            field="age",
            message="이 서비스는 18세 이상만 이용 가능합니다",
        )
    return {"message": "접근 허용", "age": age}


@app.get("/error-test/server-error", tags=["에러 테스트"], summary="500 에러 테스트")
async def test_server_error():
    """의도적인 서버 내부 오류를 발생시킵니다."""
    raise RuntimeError("의도적인 테스트 오류")


# 문제 2: 처리 시간 통계
@app.get("/stats", tags=["통계"], summary="요청 처리 통계")
async def get_stats(request: Request):
    """요청 처리 시간 통계를 반환합니다."""
    # app.state를 통해 미들웨어에 접근
    # 주의: 이 방법은 미들웨어의 내부 상태에 직접 접근하는 것이므로
    # 프로덕션에서는 별도의 메트릭 시스템을 사용하는 것이 좋습니다
    for middleware in request.app.middleware_stack.__dict__.get("app", {}).__dict__.values():
        if isinstance(middleware, ProcessTimeMiddleware):
            return middleware.get_stats()

    # 미들웨어를 찾지 못한 경우 기본 응답
    return {
        "total_requests": 0,
        "average_time": 0,
        "max_time": 0,
        "slow_requests": 0,
        "uptime_seconds": 0,
        "note": "통계 미들웨어에 접근할 수 없습니다",
    }


@app.get("/slow/{seconds}", tags=["통계"], summary="느린 요청 시뮬레이션")
async def slow_endpoint(seconds: float = 1.0):
    """
    지정된 시간만큼 대기하는 느린 엔드포인트입니다.
    처리 시간 측정 미들웨어를 테스트합니다.

    - 1초 초과: 경고 로그
    - 5초 초과: 에러 로그
    """
    if seconds > 10:
        raise CustomValidationError(
            field="seconds",
            message="최대 대기 시간은 10초입니다",
        )
    await asyncio.sleep(seconds)
    return {"message": f"{seconds}초 대기 완료"}


# 문제 3: IP 접근 제한
@app.get("/health", tags=["헬스체크"], summary="서버 상태 확인")
async def health_check():
    """서버 상태를 확인합니다. IP 제한 없이 접근 가능합니다."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/admin/blocked-ips", tags=["관리자"], summary="차단된 IP 목록")
async def get_blocked_ips(request: Request):
    """현재 차단된 IP 주소 목록을 반환합니다."""
    # 미들웨어의 blocked_ips에 접근
    # 실제로는 데이터베이스에 저장하는 것이 좋습니다
    for mw in getattr(request.app, "_middleware", []):
        if isinstance(mw, IPAccessControlMiddleware):
            return {"blocked_ips": list(mw.blocked_ips)}

    return {"blocked_ips": [], "note": "IP 제한 미들웨어에 접근할 수 없습니다"}


@app.post("/admin/block-ip", tags=["관리자"], summary="IP 차단 추가")
async def block_ip(request_body: BlockIPRequest):
    """특정 IP 주소를 차단 목록에 추가합니다."""
    # 주의: 이 예제에서는 미들웨어에 직접 접근하기 어려우므로
    # 실제로는 데이터베이스나 공유 상태를 사용해야 합니다
    return {
        "message": f"IP {request_body.ip}이(가) 차단되었습니다",
        "note": "실제로는 데이터베이스에 저장하여 미들웨어에서 참조해야 합니다",
    }


@app.get("/protected", tags=["보호된 자원"], summary="보호된 엔드포인트")
async def protected_resource():
    """IP 제한과 속도 제한이 적용되는 보호된 엔드포인트입니다."""
    return {"message": "보호된 데이터에 접근했습니다", "data": "비밀 정보"}
