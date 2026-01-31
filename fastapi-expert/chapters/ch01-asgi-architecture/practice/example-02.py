# 실행 방법: uvicorn example-02:app --reload
# 커스텀 미들웨어 스택 구현 (양파 모델 시연)
# 필요 패키지: pip install fastapi uvicorn

import time
import json
import logging
from typing import Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="미들웨어 양파 모델 시연")


# ============================================================
# 1. BaseHTTPMiddleware 기반 미들웨어 (고수준)
# ============================================================

class OuterMiddleware(BaseHTTPMiddleware):
    """
    가장 바깥쪽 미들웨어 (Layer 1).
    요청 진입과 최종 응답 시점에 로그를 남긴다.
    """

    async def dispatch(self, request: Request, call_next):
        logger.info("[Layer 1 - 진입] OuterMiddleware: 요청 수신")
        logger.info(f"  경로: {request.url.path}")

        response = await call_next(request)

        logger.info("[Layer 1 - 복귀] OuterMiddleware: 응답 전송")
        response.headers["X-Layer-1"] = "OuterMiddleware"
        return response


class MiddleMiddleware(BaseHTTPMiddleware):
    """
    중간 미들웨어 (Layer 2).
    처리 시간을 측정한다.
    """

    async def dispatch(self, request: Request, call_next):
        logger.info("  [Layer 2 - 진입] MiddleMiddleware: 타이밍 시작")
        start = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start
        logger.info(f"  [Layer 2 - 복귀] MiddleMiddleware: "
                     f"처리 시간 {duration:.4f}초")
        response.headers["X-Layer-2"] = f"MiddleMiddleware ({duration:.4f}s)"
        return response


class InnerMiddleware(BaseHTTPMiddleware):
    """
    가장 안쪽 미들웨어 (Layer 3).
    요청/응답 직전에 로그를 남긴다.
    """

    async def dispatch(self, request: Request, call_next):
        logger.info("    [Layer 3 - 진입] InnerMiddleware: 핸들러 호출 직전")

        response = await call_next(request)

        logger.info("    [Layer 3 - 복귀] InnerMiddleware: 핸들러 완료 직후")
        response.headers["X-Layer-3"] = "InnerMiddleware"
        return response


# ============================================================
# 2. 순수 ASGI 미들웨어 (저수준, 고성능)
# ============================================================

class PureASGITimingMiddleware:
    """
    순수 ASGI 프로토콜 기반 타이밍 미들웨어.

    BaseHTTPMiddleware와 달리 응답 본문을 버퍼링하지 않으므로
    스트리밍 응답에서도 효율적으로 동작한다.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # HTTP 요청이 아닌 경우 그대로 통과
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()

        async def send_wrapper(message: dict):
            """send를 감싸서 응답 헤더에 타이밍 정보 추가"""
            if message["type"] == "http.response.start":
                duration = time.perf_counter() - start_time
                # 기존 헤더를 복사하고 새 헤더 추가
                headers = list(message.get("headers", []))
                headers.append(
                    (b"x-asgi-timing", f"{duration:.6f}".encode())
                )
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)


class PureASGIRequestLoggerMiddleware:
    """
    순수 ASGI 기반 요청 로깅 미들웨어.

    요청 본문을 가로채서 로깅하되, 원래 핸들러에도 동일한
    본문을 전달한다 (receive 래핑).
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 요청 본문을 캡처하기 위해 receive를 래핑
        request_body_chunks: list[bytes] = []
        request_complete = False

        async def receive_wrapper():
            """receive를 감싸서 요청 본문을 캡처"""
            nonlocal request_complete
            message = await receive()

            if message["type"] == "http.request":
                request_body_chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    request_complete = True
                    full_body = b"".join(request_body_chunks)
                    logger.info(
                        f"[ASGI 로거] 요청 본문 ({len(full_body)} 바이트): "
                        f"{full_body[:200]}"  # 처음 200바이트만 로깅
                    )
            return message

        # 응답 상태 코드를 캡처하기 위해 send도 래핑
        response_status = None

        async def send_wrapper(message: dict):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                if not message.get("more_body", False):
                    logger.info(
                        f"[ASGI 로거] 응답 완료: "
                        f"상태={response_status}, "
                        f"경로={scope['path']}, "
                        f"메서드={scope['method']}"
                    )
            await send(message)

        await self.app(scope, receive_wrapper, send_wrapper)


# ============================================================
# 3. 미들웨어 등록 (양파 모델 순서 주의!)
# ============================================================

# 등록 순서: 나중에 등록한 것이 더 안쪽에 위치
# 실행 순서 (요청): Outer → Middle → Inner → 핸들러
# 실행 순서 (응답): 핸들러 → Inner → Middle → Outer
app.add_middleware(OuterMiddleware)      # Layer 1 (가장 바깥)
app.add_middleware(MiddleMiddleware)     # Layer 2
app.add_middleware(InnerMiddleware)      # Layer 3 (가장 안쪽)

# 순수 ASGI 미들웨어는 add_middleware로도 등록 가능
# (Starlette가 ASGI 호환 클래스를 자동 감지)
# app.add_middleware(PureASGITimingMiddleware)


# ============================================================
# 4. 엔드포인트 정의
# ============================================================

@app.get("/")
async def root():
    """기본 엔드포인트 - 미들웨어 실행 순서를 콘솔에서 확인하세요"""
    logger.info("      [핸들러] root 실행 중...")
    return {
        "message": "미들웨어 양파 모델 시연",
        "설명": "콘솔 출력에서 미들웨어 실행 순서를 확인하세요",
        "실행_순서": {
            "요청": "Outer → Middle → Inner → 핸들러",
            "응답": "핸들러 → Inner → Middle → Outer",
        },
    }


@app.get("/middleware-order")
async def middleware_order():
    """
    미들웨어 실행 순서를 응답 헤더로 확인할 수 있는 엔드포인트.
    응답 헤더에 X-Layer-1, X-Layer-2, X-Layer-3이 추가됩니다.
    """
    return {
        "message": "응답 헤더에서 각 미들웨어의 흔적을 확인하세요",
        "확인_방법": "curl -v http://localhost:8000/middleware-order",
    }


@app.post("/echo")
async def echo(request: Request):
    """요청 본문을 그대로 반환하여 미들웨어의 본문 가로채기를 테스트"""
    body = await request.body()
    return {
        "요청_본문": body.decode("utf-8") if body else "(비어있음)",
        "본문_크기": len(body),
        "content_type": request.headers.get("content-type", "없음"),
    }


# ============================================================
# 5. 조건부 미들웨어 (특정 경로에만 적용)
# ============================================================

class ConditionalMiddleware(BaseHTTPMiddleware):
    """
    특정 경로에만 적용되는 조건부 미들웨어.
    실무에서 /api/* 경로에만 인증을 적용할 때 유용하다.
    """

    def __init__(self, app: ASGIApp, target_prefix: str = "/api"):
        super().__init__(app)
        self.target_prefix = target_prefix

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(self.target_prefix):
            logger.info(f"[조건부 미들웨어] {request.url.path} - 적용됨")
            response = await call_next(request)
            response.headers["X-Conditional"] = "applied"
            return response
        else:
            logger.info(f"[조건부 미들웨어] {request.url.path} - 건너뜀")
            return await call_next(request)


app.add_middleware(ConditionalMiddleware, target_prefix="/api")


@app.get("/api/protected")
async def protected_endpoint():
    """조건부 미들웨어가 적용되는 엔드포인트"""
    return {"message": "이 엔드포인트에는 조건부 미들웨어가 적용됩니다"}


@app.get("/public")
async def public_endpoint():
    """조건부 미들웨어가 적용되지 않는 엔드포인트"""
    return {"message": "이 엔드포인트에는 조건부 미들웨어가 적용되지 않습니다"}


# ============================================================
# 6. 에러 처리 미들웨어
# ============================================================

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    전역 에러 처리 미들웨어.
    핸들러에서 발생하는 예외를 포착하여 일관된 에러 응답을 반환한다.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"[에러 미들웨어] 예외 발생: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "내부 서버 오류",
                    "detail": str(exc),
                    "path": request.url.path,
                },
            )


app.add_middleware(ErrorHandlingMiddleware)


@app.get("/error-test")
async def error_test():
    """의도적으로 에러를 발생시켜 에러 처리 미들웨어를 테스트"""
    raise ValueError("이것은 테스트용 에러입니다")


if __name__ == "__main__":
    import uvicorn

    print("미들웨어 양파 모델 시연 서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print("\n콘솔 출력에서 미들웨어 실행 순서를 확인하세요!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
