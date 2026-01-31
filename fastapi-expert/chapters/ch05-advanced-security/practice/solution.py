# 실행 방법: uvicorn solution:app --reload
# 챕터 05 연습문제 모범 답안
# 필요 패키지: pip install fastapi uvicorn

import fnmatch
import hashlib
import hmac
import json
import logging
import re
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# 문제 1: 다중 인증 전략 (JWT + API 키)
# ============================================================

class AuthResult(BaseModel):
    """통합 인증 결과"""
    method: str = Field(description="인증 방법: jwt 또는 api_key")
    user_id: str = Field(description="사용자 ID 또는 키 소유자")
    scopes: list[str] = Field(default=[], description="허용된 스코프")
    metadata: dict = Field(default={}, description="추가 정보")


# JWT 시뮬레이션
SECRET_KEY = "your-secret-key-change-in-production"

# 시뮬레이션 사용자 DB
USERS = {
    "user1": {
        "id": "1",
        "username": "user1",
        "scopes": ["read", "write"],
        "role": "editor",
    },
    "admin": {
        "id": "2",
        "username": "admin",
        "scopes": ["read", "write", "admin"],
        "role": "admin",
    },
}

# 시뮬레이션 토큰 DB (토큰 → 사용자명)
VALID_TOKENS = {
    "test-jwt-token-user1": "user1",
    "test-jwt-token-admin": "admin",
}

# API 키 DB (해시 → 정보)
API_KEYS: dict[str, dict] = {}

# 초기 API 키 생성
def _init_api_key(owner, name, scopes, rate_limit=100):
    raw_key = f"sk_{secrets.token_urlsafe(24)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    API_KEYS[key_hash] = {
        "owner": owner,
        "name": name,
        "scopes": scopes,
        "rate_limit": rate_limit,
        "is_active": True,
        "created_at": time.time(),
    }
    return raw_key

demo_api_key = _init_api_key("demo_user", "데모 키", ["read", "write"], 10)
readonly_api_key = _init_api_key("readonly_user", "읽기전용 키", ["read"], 30)

# 인증 로그
auth_logs: deque = deque(maxlen=500)

# OAuth2 + API Key 스키마 (auto_error=False로 둘 다 선택적)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def log_auth_event(
    request: Request,
    method: str,
    success: bool,
    user_id: str = "",
    detail: str = "",
):
    """인증 이벤트 로깅"""
    client_ip = request.client.host if request.client else "unknown"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client_ip": client_ip,
        "method": method,
        "success": success,
        "user_id": user_id,
        "detail": detail,
        "path": request.url.path,
    }
    auth_logs.append(entry)
    level = "INFO" if success else "WARNING"
    logger.log(
        logging.INFO if success else logging.WARNING,
        f"[인증 {level}] {method} | IP={client_ip} | "
        f"사용자={user_id} | {detail}",
    )


async def multi_auth(
    request: Request,
    jwt_token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
) -> AuthResult:
    """
    문제 1 답안: JWT와 API 키를 모두 지원하는 다중 인증 의존성.
    """
    # 1. JWT 토큰 확인
    if jwt_token:
        username = VALID_TOKENS.get(jwt_token)
        if username:
            user = USERS.get(username)
            if user:
                log_auth_event(request, "jwt", True, user["id"])
                return AuthResult(
                    method="jwt",
                    user_id=user["id"],
                    scopes=user["scopes"],
                    metadata={
                        "username": user["username"],
                        "role": user["role"],
                        "token_prefix": jwt_token[:10],
                    },
                )
        log_auth_event(request, "jwt", False, detail="유효하지 않은 토큰")
        raise HTTPException(
            status_code=401,
            detail="JWT 토큰이 유효하지 않거나 만료되었습니다",
        )

    # 2. API 키 확인
    if api_key:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        for stored_hash, record in API_KEYS.items():
            if hmac.compare_digest(key_hash, stored_hash):
                if not record["is_active"]:
                    log_auth_event(
                        request, "api_key", False,
                        detail="비활성화된 API 키",
                    )
                    raise HTTPException(
                        status_code=403,
                        detail="비활성화된 API 키입니다",
                    )
                log_auth_event(request, "api_key", True, record["owner"])
                return AuthResult(
                    method="api_key",
                    user_id=record["owner"],
                    scopes=record["scopes"],
                    metadata={
                        "key_name": record["name"],
                        "rate_limit": record["rate_limit"],
                        "key_prefix": api_key[:11],
                    },
                )
        log_auth_event(request, "api_key", False, detail="유효하지 않은 키")
        raise HTTPException(
            status_code=403,
            detail="유효하지 않은 API 키입니다",
        )

    # 3. 둘 다 없음
    log_auth_event(request, "none", False, detail="인증 정보 없음")
    raise HTTPException(
        status_code=401,
        detail="인증 정보가 없습니다. JWT 토큰(Authorization 헤더) "
               "또는 API 키(X-API-Key 헤더)를 전달하세요.",
    )


# ============================================================
# 문제 2: 동적 권한 관리 시스템
# ============================================================

class RoleCreate(BaseModel):
    name: str
    permissions: list[str]
    description: str = ""


class UserRoleAssign(BaseModel):
    role_name: str


# 동적 역할/권한 저장소
dynamic_roles: dict[str, dict] = {
    "viewer": {
        "permissions": ["users:read", "orders:read"],
        "description": "읽기 전용",
    },
    "editor": {
        "permissions": ["users:read", "users:write", "orders:*"],
        "description": "읽기/쓰기",
    },
    "admin": {
        "permissions": ["*"],
        "description": "모든 권한",
    },
}

# 사용자-역할 매핑
user_roles: dict[str, list[str]] = {
    "1": ["viewer"],
    "2": ["editor"],
    "3": ["admin"],
}

# 권한 변경 감사 로그
permission_audit_log: deque = deque(maxlen=200)


def check_permission(
    user_permissions: set[str], resource: str, action: str
) -> tuple[bool, Optional[str]]:
    """
    권한 확인 (와일드카드 지원).
    반환: (허용 여부, 매칭된 권한 문자열)
    """
    required = f"{resource}:{action}"

    for perm in user_permissions:
        # 전체 와일드카드
        if perm == "*":
            return True, "*"
        # fnmatch로 와일드카드 매칭
        if fnmatch.fnmatch(required, perm):
            return True, perm
        # 정확한 매칭
        if perm == required:
            return True, perm

    return False, None


def get_user_permissions(user_id: str) -> set[str]:
    """사용자의 최종 권한 (모든 역할의 합집합)"""
    roles = user_roles.get(user_id, [])
    permissions = set()
    for role_name in roles:
        role = dynamic_roles.get(role_name, {})
        permissions.update(role.get("permissions", []))
    return permissions


# ============================================================
# 문제 3: IP 기반 Rate Limiter
# ============================================================

class MultiLayerRateLimiter:
    """다계층 IP 기반 Rate Limiter"""

    def __init__(self):
        # 계층별 설정: (윈도우_초, 최대_요청)
        self.layers = {
            "second": (1, 10),
            "minute": (60, 100),
            "hour": (3600, 1000),
        }
        # IP별 요청 기록
        self._requests: dict[str, list[float]] = defaultdict(list)
        # 화이트리스트/블랙리스트
        self.whitelist: set[str] = {"127.0.0.1"}
        self.blacklist: set[str] = set()

    def _clean_old_requests(self, ip: str, now: float):
        """오래된 요청 기록 정리"""
        max_window = max(w for w, _ in self.layers.values())
        self._requests[ip] = [
            t for t in self._requests[ip] if now - t < max_window
        ]

    def check(self, ip: str) -> tuple[bool, dict]:
        """
        모든 계층의 Rate Limit을 확인한다.
        반환: (허용 여부, Rate Limit 정보)
        """
        # 블랙리스트 확인
        if ip in self.blacklist:
            return False, {
                "reason": "blacklisted",
                "detail": "블랙리스트에 등록된 IP입니다",
            }

        # 화이트리스트 확인
        if ip in self.whitelist:
            return True, {"reason": "whitelisted"}

        now = time.time()
        self._clean_old_requests(ip, now)

        rate_info = {}
        for layer_name, (window, max_req) in self.layers.items():
            count = sum(1 for t in self._requests[ip] if now - t < window)
            remaining = max(0, max_req - count)
            rate_info[layer_name] = {
                "used": count,
                "limit": max_req,
                "remaining": remaining,
                "window": f"{window}초",
            }

            if count >= max_req:
                # 가장 오래된 요청의 만료 시간
                oldest_in_window = min(
                    (t for t in self._requests[ip] if now - t < window),
                    default=now,
                )
                retry_after = int(oldest_in_window + window - now)
                rate_info["exceeded_layer"] = layer_name
                rate_info["retry_after"] = max(1, retry_after)
                return False, rate_info

        # 요청 기록
        self._requests[ip].append(now)
        return True, rate_info

    def get_stats(self, ip: Optional[str] = None) -> dict:
        """Rate Limit 현황 조회"""
        now = time.time()
        if ip:
            return self._get_ip_stats(ip, now)

        stats = {}
        for client_ip in list(self._requests.keys()):
            self._clean_old_requests(client_ip, now)
            if self._requests[client_ip]:
                stats[client_ip] = self._get_ip_stats(client_ip, now)
        return stats

    def _get_ip_stats(self, ip: str, now: float) -> dict:
        result = {}
        for layer_name, (window, max_req) in self.layers.items():
            count = sum(1 for t in self._requests[ip] if now - t < window)
            result[layer_name] = {"used": count, "limit": max_req}
        return result

    def reset(self, ip: str):
        """특정 IP의 Rate Limit 초기화"""
        self._requests.pop(ip, None)


ip_rate_limiter = MultiLayerRateLimiter()


# ============================================================
# 문제 4: 보안 감사 로그 미들웨어
# ============================================================

# 감사 로그 저장소
audit_logs: deque = deque(maxlen=1000)

# 인증 실패 추적 (브루트포스 감지)
auth_failures: dict[str, list[float]] = defaultdict(list)

# 보안 경고
security_alerts: deque = deque(maxlen=100)

# 민감 필드 패턴
SENSITIVE_FIELDS = {"password", "secret", "token", "api_key", "authorization"}

# 비정상 경로 패턴
SUSPICIOUS_PATTERNS = [
    r"\.\./",              # 디렉토리 탐색
    r"%2e%2e",             # URL 인코딩된 ../
    r"<script",            # XSS 시도
    r"union\s+select",     # SQL 인입 시도
    r"etc/passwd",         # 파일 접근 시도
]


def mask_sensitive_data(data: Any, depth: int = 0) -> Any:
    """민감 정보를 재귀적으로 마스킹"""
    if depth > 10:
        return data

    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(s in key.lower() for s in SENSITIVE_FIELDS):
                if isinstance(value, str) and len(value) > 4:
                    masked[key] = value[:4] + "****"
                else:
                    masked[key] = "***"
            else:
                masked[key] = mask_sensitive_data(value, depth + 1)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, depth + 1) for item in data[:10]]
    elif isinstance(data, str) and len(data) > 100:
        return data[:100] + "...(truncated)"
    return data


def detect_suspicious_path(path: str) -> Optional[str]:
    """비정상 경로 접근 감지"""
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, path, re.IGNORECASE):
            return pattern
    return None


def check_brute_force(ip: str) -> Optional[dict]:
    """브루트포스 시도 감지 (5분 내 5회 이상 실패)"""
    now = time.time()
    window = 300  # 5분
    threshold = 5

    # 오래된 기록 정리
    auth_failures[ip] = [t for t in auth_failures[ip] if now - t < window]

    if len(auth_failures[ip]) >= threshold:
        alert = {
            "type": "brute_force_attempt",
            "ip": ip,
            "failures": len(auth_failures[ip]),
            "window": "5분",
            "first_attempt": datetime.fromtimestamp(
                auth_failures[ip][0], tz=timezone.utc
            ).isoformat(),
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }
        security_alerts.append(alert)
        logger.warning(f"[보안 경고] 브루트포스 의심: IP={ip}, 실패={len(auth_failures[ip])}회")
        return alert
    return None


class AuditLogMiddleware(BaseHTTPMiddleware):
    """보안 감사 로그 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"

        # 요청 본문 캡처 (가능한 경우)
        request_body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        request_body = json.loads(body_bytes)
                    except json.JSONDecodeError:
                        request_body = f"<non-json: {len(body_bytes)} bytes>"
            except Exception:
                request_body = "<읽기 실패>"

        # 비정상 경로 감지
        suspicious = detect_suspicious_path(request.url.path)
        if suspicious:
            security_alerts.append({
                "type": "suspicious_path",
                "ip": client_ip,
                "path": request.url.path,
                "pattern": suspicious,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            })
            logger.warning(
                f"[보안 경고] 비정상 경로: IP={client_ip}, "
                f"경로={request.url.path}"
            )

        # 요청 처리
        try:
            response = await call_next(request)
        except Exception as exc:
            response = None
            status_code = 500
            raise
        else:
            status_code = response.status_code

        duration_ms = (time.perf_counter() - start_time) * 1000

        # 이벤트 타입 분류
        if status_code == 401:
            event_type = "auth_failure"
            auth_failures[client_ip].append(time.time())
            check_brute_force(client_ip)
        elif status_code == 403:
            event_type = "permission_denied"
        elif status_code == 429:
            event_type = "rate_limited"
        elif suspicious:
            event_type = "suspicious_request"
        elif status_code >= 500:
            event_type = "server_error"
        else:
            event_type = "normal"

        # 인증 정보 추출 및 마스킹
        auth_info = {}
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            parts = auth_header.split(" ", 1)
            auth_info = {
                "type": parts[0] if parts else "unknown",
                "token_prefix": parts[1][:10] + "****" if len(parts) > 1 and len(parts[1]) > 10 else "****",
            }
        api_key = request.headers.get("x-api-key", "")
        if api_key:
            auth_info = {
                "type": "api_key",
                "key_prefix": api_key[:11] + "****" if len(api_key) > 11 else "****",
            }

        # 감사 로그 항목 생성
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) if request.query_params else None,
            "auth": auth_info if auth_info else None,
            "request_body": mask_sensitive_data(request_body) if request_body else None,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "event_type": event_type,
        }

        audit_logs.append(log_entry)

        return response


app = FastAPI(
    title="챕터 05 연습문제 모범 답안",
)

# 미들웨어 등록
app.add_middleware(AuditLogMiddleware)


# ============================================================
# 엔드포인트 정의
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "챕터 05 연습문제 모범 답안",
        "문제1": "/auth/* (다중 인증)",
        "문제2": "/roles/* (동적 권한 관리)",
        "문제3": "/rate/* (IP Rate Limiting)",
        "문제4": "/audit/* (감사 로그)",
        "테스트_인증": {
            "JWT": 'Authorization: Bearer test-jwt-token-admin',
            "API_키": f"X-API-Key: {demo_api_key}",
        },
    }


# --- 문제 1: 다중 인증 엔드포인트 ---

@app.get("/auth/me")
async def auth_me(auth: AuthResult = Depends(multi_auth)):
    """현재 인증된 사용자 정보 (JWT 또는 API 키)"""
    return auth.model_dump()


@app.get("/auth/protected")
async def auth_protected(auth: AuthResult = Depends(multi_auth)):
    """보호된 리소스"""
    return {
        "message": "인증 성공",
        "auth_method": auth.method,
        "user": auth.user_id,
    }


@app.get("/auth/logs")
async def get_auth_logs(limit: int = 20):
    """인증 로그 조회"""
    return {"logs": list(auth_logs)[-limit:]}


# --- 문제 2: 동적 권한 관리 엔드포인트 ---

@app.post("/roles")
async def create_role(role_data: RoleCreate):
    """역할 생성"""
    if role_data.name in dynamic_roles:
        raise HTTPException(status_code=409, detail="이미 존재하는 역할입니다")

    dynamic_roles[role_data.name] = {
        "permissions": role_data.permissions,
        "description": role_data.description,
    }

    permission_audit_log.append({
        "action": "role_created",
        "role": role_data.name,
        "permissions": role_data.permissions,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return {"message": f"역할 '{role_data.name}' 생성 완료", "role": dynamic_roles[role_data.name]}


@app.get("/roles")
async def list_roles():
    """역할 목록 조회"""
    return {
        "roles": {
            name: {**data, "name": name}
            for name, data in dynamic_roles.items()
        }
    }


@app.put("/roles/{role_name}")
async def update_role(role_name: str, role_data: RoleCreate):
    """역할 수정"""
    if role_name not in dynamic_roles:
        raise HTTPException(status_code=404, detail="역할을 찾을 수 없습니다")

    old_permissions = dynamic_roles[role_name]["permissions"]
    dynamic_roles[role_name]["permissions"] = role_data.permissions
    dynamic_roles[role_name]["description"] = role_data.description

    permission_audit_log.append({
        "action": "role_updated",
        "role": role_name,
        "old_permissions": old_permissions,
        "new_permissions": role_data.permissions,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return {"message": f"역할 '{role_name}' 수정 완료"}


@app.delete("/roles/{role_name}")
async def delete_role(role_name: str):
    """역할 삭제"""
    if role_name not in dynamic_roles:
        raise HTTPException(status_code=404, detail="역할을 찾을 수 없습니다")

    del dynamic_roles[role_name]

    # 사용자에서도 해당 역할 제거
    for uid in user_roles:
        user_roles[uid] = [r for r in user_roles[uid] if r != role_name]

    permission_audit_log.append({
        "action": "role_deleted",
        "role": role_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return {"message": f"역할 '{role_name}' 삭제 완료"}


@app.post("/users/{user_id}/roles")
async def assign_role(user_id: str, data: UserRoleAssign):
    """사용자에게 역할 부여"""
    if data.role_name not in dynamic_roles:
        raise HTTPException(status_code=404, detail="역할을 찾을 수 없습니다")

    if user_id not in user_roles:
        user_roles[user_id] = []

    if data.role_name not in user_roles[user_id]:
        user_roles[user_id].append(data.role_name)

    return {
        "user_id": user_id,
        "roles": user_roles[user_id],
        "permissions": sorted(get_user_permissions(user_id)),
    }


@app.get("/auth/check")
async def check_auth(resource: str, action: str, user_id: str = "1"):
    """권한 확인 (와일드카드 지원)"""
    permissions = get_user_permissions(user_id)
    allowed, matched = check_permission(permissions, resource, action)

    return {
        "user_id": user_id,
        "resource": resource,
        "action": action,
        "allowed": allowed,
        "matched_permission": matched,
        "user_roles": user_roles.get(user_id, []),
        "all_permissions": sorted(permissions),
    }


@app.get("/permissions/audit")
async def get_permission_audit():
    """권한 변경 감사 로그"""
    return {"audit_log": list(permission_audit_log)}


# --- 문제 3: IP Rate Limiting 엔드포인트 ---

@app.get("/rate/test")
async def rate_limit_test(request: Request):
    """Rate Limit 테스트 엔드포인트"""
    ip = request.client.host if request.client else "unknown"
    allowed, info = ip_rate_limiter.check(ip)

    if not allowed:
        retry_after = info.get("retry_after", 1)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "요청 한도 초과",
                "exceeded_layer": info.get("exceeded_layer"),
                "retry_after": retry_after,
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(
                    info.get(info.get("exceeded_layer", "minute"), {}).get("limit", 0)
                ),
                "X-RateLimit-Remaining": "0",
            },
        )

    return {
        "message": "요청 성공",
        "ip": ip,
        "rate_info": info,
    }


@app.get("/admin/rate-limits")
async def get_rate_limits(ip: Optional[str] = None):
    """Rate Limit 현황 조회"""
    return {"stats": ip_rate_limiter.get_stats(ip)}


@app.post("/admin/blacklist")
async def add_to_blacklist(data: dict):
    """IP 블랙리스트 추가"""
    ip = data.get("ip")
    if not ip:
        raise HTTPException(status_code=400, detail="IP 주소가 필요합니다")
    ip_rate_limiter.blacklist.add(ip)
    return {"message": f"{ip}를 블랙리스트에 추가했습니다"}


@app.delete("/admin/blacklist/{ip}")
async def remove_from_blacklist(ip: str):
    """IP 블랙리스트 제거"""
    ip_rate_limiter.blacklist.discard(ip)
    return {"message": f"{ip}를 블랙리스트에서 제거했습니다"}


@app.post("/admin/whitelist")
async def add_to_whitelist(data: dict):
    """IP 화이트리스트 추가"""
    ip = data.get("ip")
    if not ip:
        raise HTTPException(status_code=400, detail="IP 주소가 필요합니다")
    ip_rate_limiter.whitelist.add(ip)
    return {"message": f"{ip}를 화이트리스트에 추가했습니다"}


@app.post("/admin/rate-limits/reset/{ip}")
async def reset_rate_limit(ip: str):
    """특정 IP의 Rate Limit 초기화"""
    ip_rate_limiter.reset(ip)
    return {"message": f"{ip}의 Rate Limit을 초기화했습니다"}


# --- 문제 4: 감사 로그 엔드포인트 ---

@app.get("/audit/logs")
async def get_audit_logs(
    limit: int = 20,
    event_type: Optional[str] = None,
):
    """감사 로그 조회"""
    logs = list(audit_logs)

    if event_type:
        logs = [log for log in logs if log["event_type"] == event_type]

    return {
        "total": len(logs),
        "logs": logs[-limit:],
        "event_types": list(set(log["event_type"] for log in audit_logs)),
    }


@app.get("/audit/alerts")
async def get_security_alerts(limit: int = 20):
    """보안 경고 목록"""
    return {
        "total": len(security_alerts),
        "alerts": list(security_alerts)[-limit:],
    }


@app.get("/audit/stats")
async def get_audit_stats():
    """감사 로그 통계"""
    event_counts = defaultdict(int)
    status_counts = defaultdict(int)
    for log in audit_logs:
        event_counts[log["event_type"]] += 1
        status_counts[str(log["status_code"])] += 1

    return {
        "총_로그": len(audit_logs),
        "이벤트별": dict(event_counts),
        "상태코드별": dict(status_counts),
        "보안_경고_수": len(security_alerts),
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("챕터 05 연습문제 모범 답안 서버")
    print("=" * 60)
    print(f"\n데모 API 키: {demo_api_key}")
    print(f"읽기전용 API 키: {readonly_api_key}")
    print("\nJWT 테스트 토큰:")
    print("  일반: test-jwt-token-user1")
    print("  관리자: test-jwt-token-admin")
    print("\n주요 엔드포인트:")
    print("  문제1: GET  /auth/me")
    print("  문제2: GET  /roles | POST /roles")
    print("  문제3: GET  /rate/test")
    print("  문제4: GET  /audit/logs | /audit/alerts")
    print(f"\nAPI 문서: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
