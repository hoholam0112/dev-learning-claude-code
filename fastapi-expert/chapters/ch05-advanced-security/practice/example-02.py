# 실행 방법: uvicorn example-02:app --reload
# API 키 + Rate Limiting 예제
# 필요 패키지: pip install fastapi uvicorn

import hashlib
import hmac
import logging
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="API 키 + Rate Limiting 예제")


# ============================================================
# 1. API 키 관리 시스템
# ============================================================

@dataclass
class APIKeyRecord:
    """API 키 레코드"""
    key_hash: str           # 해시된 키 (저장용)
    owner: str              # 키 소유자
    name: str               # 키 이름
    created_at: float       # 생성 시간
    rate_limit: int = 100   # 분당 최대 요청 수
    is_active: bool = True  # 활성 상태
    scopes: list[str] = field(default_factory=lambda: ["read"])


class APIKeyManager:
    """API 키 생성, 검증, 관리"""

    def __init__(self):
        self._keys: dict[str, APIKeyRecord] = {}  # key_hash → record
        self._prefix_index: dict[str, str] = {}   # key_prefix → key_hash

    def generate_key(
        self,
        owner: str,
        name: str,
        rate_limit: int = 100,
        scopes: list[str] = None,
    ) -> tuple[str, APIKeyRecord]:
        """
        새 API 키 생성.
        반환: (평문 키, 레코드) - 평문 키는 이 시점에서만 노출된다
        """
        # 안전한 랜덤 키 생성 (sk_ 접두사로 식별)
        raw_key = f"sk_{secrets.token_urlsafe(32)}"

        # SHA-256 해시 (저장용)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        # 접두사 인덱스 (키 식별용, 처음 8자)
        key_prefix = raw_key[:11]  # "sk_" + 8자

        record = APIKeyRecord(
            key_hash=key_hash,
            owner=owner,
            name=name,
            created_at=time.time(),
            rate_limit=rate_limit,
            scopes=scopes or ["read"],
        )

        self._keys[key_hash] = record
        self._prefix_index[key_prefix] = key_hash

        logger.info(f"[API 키] 생성: {name} (소유자: {owner})")
        return raw_key, record

    def verify_key(self, raw_key: str) -> Optional[APIKeyRecord]:
        """
        API 키 검증.
        타이밍 공격에 안전한 비교를 사용한다.
        """
        provided_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        for stored_hash, record in self._keys.items():
            # 타이밍 공격 방지: 항상 일정한 시간에 비교
            if hmac.compare_digest(provided_hash, stored_hash):
                if not record.is_active:
                    return None
                return record

        return None

    def revoke_key(self, key_prefix: str) -> bool:
        """API 키 비활성화"""
        key_hash = self._prefix_index.get(key_prefix)
        if key_hash and key_hash in self._keys:
            self._keys[key_hash].is_active = False
            logger.info(f"[API 키] 비활성화: {key_prefix}")
            return True
        return False

    def list_keys(self, owner: Optional[str] = None) -> list[dict]:
        """API 키 목록 (해시 미포함)"""
        keys = []
        for prefix, key_hash in self._prefix_index.items():
            record = self._keys[key_hash]
            if owner and record.owner != owner:
                continue
            keys.append({
                "prefix": prefix,
                "name": record.name,
                "owner": record.owner,
                "rate_limit": record.rate_limit,
                "scopes": record.scopes,
                "is_active": record.is_active,
                "created_at": record.created_at,
            })
        return keys


# ============================================================
# 2. Rate Limiter (슬라이딩 윈도우)
# ============================================================

class SlidingWindowRateLimiter:
    """슬라이딩 윈도우 기반 Rate Limiter"""

    def __init__(self):
        # 클라이언트별 요청 기록: client_id → [timestamp, ...]
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(
        self, client_id: str, max_requests: int, window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        요청 허용 여부를 확인하고, Rate Limit 정보를 반환.

        반환: (허용 여부, {limit, remaining, reset})
        """
        now = time.time()
        window_start = now - window_seconds

        # 윈도우 밖의 오래된 요청 제거
        self._requests[client_id] = [
            t for t in self._requests[client_id] if t > window_start
        ]

        current_count = len(self._requests[client_id])
        remaining = max(0, max_requests - current_count)

        # 가장 오래된 요청의 만료 시간
        if self._requests[client_id]:
            reset_time = self._requests[client_id][0] + window_seconds
        else:
            reset_time = now + window_seconds

        rate_info = {
            "limit": max_requests,
            "remaining": remaining,
            "reset": int(reset_time),
            "retry_after": max(0, int(reset_time - now)) if remaining == 0 else 0,
        }

        if current_count >= max_requests:
            return False, rate_info

        # 요청 기록 추가
        self._requests[client_id].append(now)
        rate_info["remaining"] = remaining - 1

        return True, rate_info

    def get_stats(self) -> dict:
        """전체 Rate Limiter 통계"""
        now = time.time()
        active_clients = 0
        total_requests = 0
        for client_id, timestamps in self._requests.items():
            recent = [t for t in timestamps if now - t < 60]
            if recent:
                active_clients += 1
                total_requests += len(recent)
        return {
            "active_clients": active_clients,
            "total_requests_last_minute": total_requests,
        }


# ============================================================
# 3. 전역 인스턴스 초기화
# ============================================================

key_manager = APIKeyManager()
rate_limiter = SlidingWindowRateLimiter()

# 초기 API 키 생성 (데모용)
demo_key, _ = key_manager.generate_key(
    owner="demo",
    name="데모용 API 키",
    rate_limit=10,  # 분당 10회
    scopes=["read", "write"],
)
readonly_key, _ = key_manager.generate_key(
    owner="readonly",
    name="읽기 전용 API 키",
    rate_limit=30,
    scopes=["read"],
)
print(f"\n데모용 API 키: {demo_key}")
print(f"읽기 전용 API 키: {readonly_key}\n")


# ============================================================
# 4. 보안 헤더 미들웨어
# ============================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더를 모든 응답에 추가하는 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # XSS 방지
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 클릭재킹 방지
        response.headers["X-Frame-Options"] = "DENY"

        # 참조 정보 제한
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 서버 정보 숨김
        if "server" in response.headers:
            del response.headers["server"]

        return response


app.add_middleware(SecurityHeadersMiddleware)


# ============================================================
# 5. API 키 인증 의존성
# ============================================================

# 두 가지 방법으로 API 키를 전달할 수 있음
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    header_key: Optional[str] = Depends(api_key_header),
    query_key: Optional[str] = Depends(api_key_query),
) -> APIKeyRecord:
    """
    API 키를 검증하는 의존성.
    헤더 또는 쿼리 파라미터에서 키를 추출하여 검증한다.
    """
    raw_key = header_key or query_key
    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API 키가 필요합니다. X-API-Key 헤더 또는 api_key 파라미터를 전달하세요.",
        )

    record = key_manager.verify_key(raw_key)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않거나 비활성화된 API 키입니다.",
        )

    return record


def require_scope(*scopes: str):
    """특정 스코프를 요구하는 의존성 팩토리"""
    async def scope_checker(
        api_record: APIKeyRecord = Depends(get_api_key),
    ) -> APIKeyRecord:
        missing = [s for s in scopes if s not in api_record.scopes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API 키에 필요한 스코프가 없습니다: {missing}. "
                       f"현재 스코프: {api_record.scopes}",
            )
        return api_record
    return scope_checker


# ============================================================
# 6. Rate Limiting 의존성
# ============================================================

async def check_rate_limit(
    request: Request,
    api_record: APIKeyRecord = Depends(get_api_key),
) -> APIKeyRecord:
    """
    Rate Limit을 확인하는 의존성.
    API 키의 rate_limit 설정에 따라 요청을 제한한다.
    """
    # 클라이언트 ID = API 키 해시 (또는 소유자)
    client_id = api_record.key_hash[:16]

    allowed, rate_info = rate_limiter.is_allowed(
        client_id=client_id,
        max_requests=api_record.rate_limit,
        window_seconds=60,
    )

    # Rate Limit 헤더를 응답에 추가하기 위해 request.state에 저장
    request.state.rate_limit_info = rate_info

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "요청 한도를 초과했습니다",
                "limit": rate_info["limit"],
                "retry_after": rate_info["retry_after"],
            },
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_info["reset"]),
                "Retry-After": str(rate_info["retry_after"]),
            },
        )

    return api_record


# Rate Limit 헤더를 응답에 추가하는 미들웨어
class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # request.state에 rate_limit_info가 있으면 헤더 추가
        rate_info = getattr(request.state, "rate_limit_info", None)
        if rate_info:
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(
                rate_info["remaining"]
            )
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])

        return response


app.add_middleware(RateLimitHeadersMiddleware)


# ============================================================
# 7. 엔드포인트 정의
# ============================================================

@app.get("/")
async def root():
    """API 정보 (인증 불필요)"""
    return {
        "message": "API 키 + Rate Limiting 예제",
        "인증_방법": {
            "헤더": "X-API-Key: <your-api-key>",
            "쿼리": "?api_key=<your-api-key>",
        },
        "API_키_관리": {
            "생성": "POST /api-keys/generate",
            "목록": "GET /api-keys",
            "비활성화": "DELETE /api-keys/{prefix}",
        },
    }


@app.get("/protected/read")
async def protected_read(
    api_record: APIKeyRecord = Depends(check_rate_limit),
):
    """
    읽기 전용 보호 엔드포인트.
    API 키가 필요하며, Rate Limit이 적용된다.
    """
    return {
        "message": "읽기 성공",
        "api_key_owner": api_record.owner,
        "api_key_name": api_record.name,
        "rate_limit": f"분당 {api_record.rate_limit}회",
    }


@app.post("/protected/write")
async def protected_write(
    api_record: APIKeyRecord = Depends(require_scope("write")),
):
    """
    쓰기 보호 엔드포인트.
    'write' 스코프가 있는 API 키만 접근 가능하다.
    """
    return {
        "message": "쓰기 성공 (시뮬레이션)",
        "api_key_owner": api_record.owner,
        "scopes": api_record.scopes,
    }


@app.post("/api-keys/generate")
async def generate_api_key(
    owner: str = "user",
    name: str = "새 API 키",
    rate_limit: int = 100,
    scopes: str = "read",
):
    """
    새 API 키 생성.
    생성된 키는 이 응답에서만 확인할 수 있으므로 반드시 저장하세요.
    """
    scope_list = [s.strip() for s in scopes.split(",")]
    raw_key, record = key_manager.generate_key(
        owner=owner,
        name=name,
        rate_limit=rate_limit,
        scopes=scope_list,
    )

    return {
        "api_key": raw_key,
        "경고": "이 키는 다시 확인할 수 없습니다. 안전한 곳에 저장하세요!",
        "정보": {
            "owner": record.owner,
            "name": record.name,
            "rate_limit": f"분당 {record.rate_limit}회",
            "scopes": record.scopes,
        },
    }


@app.get("/api-keys")
async def list_api_keys():
    """등록된 API 키 목록 (해시 미포함)"""
    return {"keys": key_manager.list_keys()}


@app.delete("/api-keys/{prefix}")
async def revoke_api_key(prefix: str):
    """API 키 비활성화"""
    if key_manager.revoke_key(prefix):
        return {"message": f"API 키 '{prefix}...' 가 비활성화되었습니다"}
    raise HTTPException(status_code=404, detail="API 키를 찾을 수 없습니다")


@app.get("/rate-limit/stats")
async def rate_limit_stats():
    """Rate Limiter 통계"""
    return rate_limiter.get_stats()


@app.get("/rate-limit/test")
async def rate_limit_test(
    api_record: APIKeyRecord = Depends(check_rate_limit),
):
    """
    Rate Limit 테스트 엔드포인트.
    여러 번 빠르게 호출하여 Rate Limit 동작을 확인하세요.

    테스트: for i in $(seq 1 15); do curl -H "X-API-Key: <key>" http://localhost:8000/rate-limit/test; done
    """
    return {
        "message": f"요청 성공",
        "rate_limit": f"분당 {api_record.rate_limit}회",
        "시간": time.strftime("%H:%M:%S"),
    }


@app.get("/security-headers/check")
async def check_security_headers():
    """
    보안 헤더 확인용 엔드포인트.
    curl -v로 응답 헤더를 확인하세요.

    테스트: curl -v http://localhost:8000/security-headers/check
    """
    return {
        "message": "응답 헤더에 보안 헤더가 포함되어 있습니다",
        "확인_방법": "curl -v http://localhost:8000/security-headers/check",
        "설정된_헤더": [
            "X-Content-Type-Options: nosniff",
            "X-XSS-Protection: 1; mode=block",
            "X-Frame-Options: DENY",
            "Referrer-Policy: strict-origin-when-cross-origin",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("API 키 + Rate Limiting 서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print(f"\n데모용 API 키: {demo_key}")
    print(f"읽기 전용 API 키: {readonly_key}")
    print("\n사용법:")
    print(f'  curl -H "X-API-Key: {demo_key}" http://localhost:8000/protected/read')
    uvicorn.run(app, host="0.0.0.0", port=8000)
