# 실행 방법: uvicorn solution:app --reload
# 챕터 01 연습문제 모범 답안
# 필요 패키지: pip install fastapi uvicorn starlette

import json
import time
import logging
from datetime import datetime, timezone

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, Router, Mount
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# 문제 1: 순수 ASGI 앱에서 라우팅 구현하기
# ============================================================

async def send_json_response(send, status: int, data: dict) -> None:
    """JSON 응답을 전송하는 헬퍼 함수"""
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            [b"content-type", b"application/json; charset=utf-8"],
        ],
    })
    await send({
        "type": "http.response.body",
        "body": body,
        "more_body": False,
    })


async def read_request_body(receive) -> bytes:
    """요청 본문을 완전히 읽는 헬퍼 함수"""
    body = b""
    while True:
        message = await receive()
        body += message.get("body", b"")
        if not message.get("more_body", False):
            break
    return body


async def handle_home(scope, receive, send):
    """GET / 핸들러"""
    await send_json_response(send, 200, {"message": "홈페이지"})


async def handle_health(scope, receive, send):
    """GET /health 핸들러"""
    now = datetime.now(timezone.utc).isoformat()
    await send_json_response(send, 200, {
        "status": "healthy",
        "timestamp": now,
    })


async def handle_echo(scope, receive, send):
    """POST /echo 핸들러"""
    body = await read_request_body(receive)
    await send_json_response(send, 200, {
        "received_body": body.decode("utf-8") if body else "",
        "body_length": len(body),
    })


# 라우팅 테이블: (메서드, 경로) → 핸들러
ROUTE_TABLE = {
    ("GET", "/"): handle_home,
    ("GET", "/health"): handle_health,
    ("POST", "/echo"): handle_echo,
}

# 경로별 허용 메서드 (405 판별용)
PATH_METHODS = {}
for (method, path) in ROUTE_TABLE:
    if path not in PATH_METHODS:
        PATH_METHODS[path] = set()
    PATH_METHODS[path].add(method)


async def pure_asgi_router(scope: dict, receive, send) -> None:
    """
    문제 1 답안: 순수 ASGI 라우터 구현.
    라우팅 테이블을 사용하여 요청을 적절한 핸들러로 전달한다.
    """
    if scope["type"] == "lifespan":
        # lifespan 이벤트 처리
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
        return

    if scope["type"] != "http":
        return

    method = scope["method"]
    path = scope["path"]

    # 라우팅 테이블에서 핸들러 검색
    handler = ROUTE_TABLE.get((method, path))

    if handler:
        await handler(scope, receive, send)
    elif path in PATH_METHODS:
        # 경로는 존재하지만 메서드가 다른 경우 → 405
        await send_json_response(send, 405, {
            "error": "허용되지 않은 메서드",
            "allowed_methods": list(PATH_METHODS[path]),
        })
    else:
        # 경로 자체가 존재하지 않는 경우 → 404
        await send_json_response(send, 404, {
            "error": "경로를 찾을 수 없습니다",
            "path": path,
        })


# ============================================================
# 문제 2: 요청/응답 본문을 기록하는 미들웨어
# ============================================================

# --- 방식 A: BaseHTTPMiddleware 기반 ---

class BodyLoggingMiddlewareHTTP(BaseHTTPMiddleware):
    """
    BaseHTTPMiddleware 기반 요청/응답 본문 로깅 미들웨어.

    주의: BaseHTTPMiddleware는 응답 본문을 메모리에 버퍼링하므로
    대용량 응답에서는 메모리 문제가 발생할 수 있다.
    """
    MAX_LOG_SIZE = 1024  # 최대 로깅 크기 (1KB)

    def _is_binary(self, content_type: str) -> bool:
        """바이너리 콘텐츠 타입인지 판별"""
        text_types = ("application/json", "text/", "application/xml")
        return not any(content_type.startswith(t) for t in text_types)

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        # 요청 본문 캡처
        request_body = await request.body()
        if request_body:
            body_preview = request_body[:self.MAX_LOG_SIZE].decode(
                "utf-8", errors="replace"
            )
            logger.info(
                f"[요청] {request.method} {request.url.path} | "
                f"본문: {body_preview} ({len(request_body)} bytes)"
            )
        else:
            logger.info(
                f"[요청] {request.method} {request.url.path} | 본문: (없음)"
            )

        # 응답 처리
        response = await call_next(request)

        # 응답 본문 캡처 (body_iterator 소비 후 재구성)
        response_body_chunks = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            response_body_chunks.append(chunk)

        response_body = b"".join(response_body_chunks)
        duration = time.perf_counter() - start_time

        # 응답 본문 로깅
        content_type = response.headers.get("content-type", "")
        if self._is_binary(content_type):
            body_preview = "<바이너리 데이터>"
        else:
            body_preview = response_body[:self.MAX_LOG_SIZE].decode(
                "utf-8", errors="replace"
            )

        logger.info(
            f"[응답] {request.method} {request.url.path} | "
            f"상태: {response.status_code} | "
            f"본문: {body_preview} ({len(response_body)} bytes) | "
            f"소요: {duration:.4f}s"
        )

        # 응답 본문을 재구성하여 반환
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


# --- 방식 B: 순수 ASGI 미들웨어 ---

class BodyLoggingMiddlewareASGI:
    """
    순수 ASGI 기반 요청/응답 본문 로깅 미들웨어.

    BaseHTTPMiddleware와 달리 스트리밍 응답도 올바르게 처리하며,
    응답 본문을 완전히 버퍼링하지 않고 청크 단위로 로깅한다.
    """
    MAX_LOG_SIZE = 1024

    def __init__(self, app: ASGIApp):
        self.app = app

    def _is_binary(self, headers: list) -> bool:
        """응답 헤더에서 바이너리 콘텐츠 여부 판별"""
        for key, value in headers:
            if key == b"content-type":
                ct = value.decode("utf-8", errors="replace")
                text_types = ("application/json", "text/", "application/xml")
                return not any(ct.startswith(t) for t in text_types)
        return True

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        method = scope["method"]
        path = scope["path"]

        # 요청 본문 캡처를 위한 receive 래핑
        request_body_parts: list[bytes] = []

        async def receive_wrapper():
            message = await receive()
            if message["type"] == "http.request":
                request_body_parts.append(message.get("body", b""))
                if not message.get("more_body", False):
                    full_body = b"".join(request_body_parts)
                    if full_body:
                        preview = full_body[:self.MAX_LOG_SIZE].decode(
                            "utf-8", errors="replace"
                        )
                        logger.info(
                            f"[요청] {method} {path} | "
                            f"본문: {preview} ({len(full_body)} bytes)"
                        )
                    else:
                        logger.info(
                            f"[요청] {method} {path} | 본문: (없음)"
                        )
            return message

        # 응답 캡처를 위한 send 래핑
        response_status = 0
        response_body_parts: list[bytes] = []
        is_binary = False

        async def send_wrapper(message: dict):
            nonlocal response_status, is_binary

            if message["type"] == "http.response.start":
                response_status = message["status"]
                is_binary = self._is_binary(
                    message.get("headers", [])
                )

            elif message["type"] == "http.response.body":
                body_chunk = message.get("body", b"")
                response_body_parts.append(body_chunk)

                # 마지막 청크일 때 로깅
                if not message.get("more_body", False):
                    duration = time.perf_counter() - start_time
                    full_body = b"".join(response_body_parts)

                    if is_binary:
                        preview = "<바이너리 데이터>"
                    else:
                        preview = full_body[:self.MAX_LOG_SIZE].decode(
                            "utf-8", errors="replace"
                        )

                    logger.info(
                        f"[응답] {method} {path} | "
                        f"상태: {response_status} | "
                        f"본문: {preview} ({len(full_body)} bytes) | "
                        f"소요: {duration:.4f}s"
                    )

            await send(message)

        await self.app(scope, receive_wrapper, send_wrapper)


# ============================================================
# 문제 3: Starlette의 라우팅 동작을 직접 사용해보기
# ============================================================

# --- Starlette 핸들러 함수들 ---

async def homepage(request: Request) -> JSONResponse:
    """GET / 핸들러"""
    return JSONResponse({
        "message": "Starlette 라우터 직접 사용",
        "설명": "FastAPI 없이 Starlette의 라우팅 기능을 사용합니다",
    })


async def get_user(request: Request) -> JSONResponse:
    """GET /users/{user_id} 핸들러"""
    user_id = request.path_params["user_id"]
    return JSONResponse({
        "user_id": user_id,
        "타입": type(user_id).__name__,
        "설명": f"사용자 {user_id}의 상세 정보",
    })


async def create_user(request: Request) -> JSONResponse:
    """POST /users 핸들러"""
    body = await request.body()
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        return JSONResponse(
            {"error": "잘못된 JSON 형식"}, status_code=400
        )

    return JSONResponse(
        {"message": "사용자 생성 완료", "data": data},
        status_code=201,
    )


async def admin_dashboard(request: Request) -> JSONResponse:
    """GET /admin/dashboard 핸들러"""
    return JSONResponse({
        "page": "관리자 대시보드",
        "경로_정보": {
            "path": str(request.url.path),
            "path_params": dict(request.path_params),
        },
    })


async def admin_users(request: Request) -> JSONResponse:
    """GET /admin/users 핸들러"""
    return JSONResponse({
        "page": "사용자 관리",
        "사용자_목록": [
            {"id": 1, "name": "관리자"},
            {"id": 2, "name": "사용자1"},
        ],
    })


async def not_found(request: Request, exc: Exception) -> JSONResponse:
    """커스텀 404 핸들러"""
    return JSONResponse(
        {
            "error": "경로를 찾을 수 없습니다",
            "path": str(request.url.path),
            "method": request.method,
        },
        status_code=404,
    )


async def server_error(request: Request, exc: Exception) -> JSONResponse:
    """커스텀 500 핸들러"""
    return JSONResponse(
        {"error": "내부 서버 오류", "detail": str(exc)},
        status_code=500,
    )


# --- 서브 라우터 (관리자 섹션) ---
admin_routes = [
    Route("/dashboard", admin_dashboard, methods=["GET"]),
    Route("/users", admin_users, methods=["GET"]),
]

# --- 메인 라우터 구성 ---
#
# 경로 매칭 우선순위 실험:
# 1. 정적 경로("/users/me")가 동적 경로("/users/{user_id}")보다 먼저 등록되어야 함
# 2. routes 리스트에서 위에 있는 것이 먼저 매칭됨
# 3. Mount는 접두사 매칭이므로 /admin/* 모든 요청을 받음

main_routes = [
    Route("/", homepage, methods=["GET"]),
    # 주의: 순서가 중요! /users/me 같은 정적 경로가 있다면
    # /users/{user_id} 보다 위에 배치해야 한다.
    Route("/users/{user_id:int}", get_user, methods=["GET"]),
    Route("/users", create_user, methods=["POST"]),
    Mount("/admin", routes=admin_routes),
]

# --- Starlette 앱 생성 ---
#
# 에러 핸들러 등록과 미들웨어 구성
starlette_app = Starlette(
    routes=main_routes,
    exception_handlers={
        404: not_found,
        500: server_error,
    },
    middleware=[
        Middleware(BodyLoggingMiddlewareHTTP),
    ],
)


# ============================================================
# 메인 앱: 문제 3의 Starlette 앱을 기본으로 사용
# (문제 1의 순수 ASGI 앱은 /pure-asgi 에 마운트)
# ============================================================

# 문제 1의 순수 ASGI 앱을 /pure-asgi 경로에 마운트
# 이를 통해 세 문제의 답안을 모두 하나의 서버에서 확인할 수 있다
main_routes_with_asgi = main_routes + [
    Mount("/pure-asgi", app=pure_asgi_router),
]

app = Starlette(
    routes=main_routes_with_asgi,
    exception_handlers={
        404: not_found,
        500: server_error,
    },
    middleware=[
        # 문제 2의 순수 ASGI 미들웨어 적용
        Middleware(BodyLoggingMiddlewareASGI),
    ],
)


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("챕터 01 연습문제 모범 답안 서버")
    print("=" * 60)
    print("\n문제 1 (순수 ASGI 라우터):")
    print("  GET  http://localhost:8000/pure-asgi/")
    print("  GET  http://localhost:8000/pure-asgi/health")
    print("  POST http://localhost:8000/pure-asgi/echo")
    print("\n문제 2 (본문 로깅 미들웨어):")
    print("  모든 요청/응답의 본문이 콘솔에 로깅됩니다")
    print("\n문제 3 (Starlette 라우팅):")
    print("  GET  http://localhost:8000/")
    print("  GET  http://localhost:8000/users/42")
    print("  POST http://localhost:8000/users")
    print("  GET  http://localhost:8000/admin/dashboard")
    print("  GET  http://localhost:8000/admin/users")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
