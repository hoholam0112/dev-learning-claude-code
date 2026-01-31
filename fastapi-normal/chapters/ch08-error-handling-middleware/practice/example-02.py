# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn

"""
챕터 08 예제 02: CORS와 로깅 미들웨어

이 예제에서는 다음을 학습합니다:
- CORS 미들웨어 설정
- 요청/응답 로깅 미들웨어 구현
- 요청 처리 시간 측정
- 커스텀 응답 헤더 추가
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ── 로깅 설정 ──────────────────────────────────────────────
# 로거를 설정하여 콘솔에 로그를 출력합니다
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api")


# ── 커스텀 미들웨어 1: 요청 로깅 ──────────────────────────
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    모든 요청과 응답을 로깅하는 미들웨어입니다.
    요청 ID를 생성하여 추적에 활용합니다.
    """

    async def dispatch(self, request: Request, call_next):
        # 고유 요청 ID 생성
        request_id = str(uuid.uuid4())[:8]

        # 요청 시작 시간 기록
        start_time = time.time()

        # 요청 정보 로깅
        logger.info(
            f"[{request_id}] 요청 시작: {request.method} {request.url.path} "
            f"- 클라이언트: {request.client.host if request.client else 'unknown'}"
        )

        # 다음 미들웨어 또는 엔드포인트로 전달
        response = await call_next(request)

        # 처리 시간 계산
        process_time = time.time() - start_time

        # 응답 정보 로깅
        logger.info(
            f"[{request_id}] 요청 완료: {request.method} {request.url.path} "
            f"- 상태: {response.status_code} "
            f"- 처리 시간: {process_time:.4f}초"
        )

        # 응답 헤더에 유용한 정보 추가
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response


# ── 커스텀 미들웨어 2: 요청 크기 제한 ─────────────────────
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    요청 본문의 크기를 제한하는 미들웨어입니다.
    Content-Length 헤더를 확인하여 큰 요청을 거부합니다.
    """

    def __init__(self, app, max_size: int = 1_000_000):
        super().__init__(app)
        self.max_size = max_size  # 기본값: 1MB

    async def dispatch(self, request: Request, call_next):
        # Content-Length 헤더 확인
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            return JSONResponse(
                status_code=413,
                content={
                    "error": "REQUEST_TOO_LARGE",
                    "message": f"요청 크기가 제한({self.max_size}바이트)을 초과했습니다",
                },
            )

        response = await call_next(request)
        return response


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="미들웨어 예제", description="CORS, 로깅, 커스텀 미들웨어 예제")


# ── 미들웨어 등록 (순서 중요!) ─────────────────────────────
# 주의: 미들웨어는 등록 순서의 역순으로 실행됩니다
# 아래 코드에서 실제 실행 순서: RequestSizeLimit -> Logging -> CORS

# 1. CORS 미들웨어 (가장 먼저 등록 = 가장 나중에 실행)
app.add_middleware(
    CORSMiddleware,
    # 허용할 출처 목록 (프론트엔드 주소)
    allow_origins=[
        "http://localhost:3000",      # React 개발 서버
        "http://localhost:5173",      # Vite 개발 서버
        "http://127.0.0.1:5500",      # VS Code Live Server
    ],
    allow_credentials=True,            # 쿠키 전송 허용
    allow_methods=["*"],               # 모든 HTTP 메서드 허용
    allow_headers=["*"],               # 모든 헤더 허용
    max_age=600,                       # 프리플라이트 캐시: 10분
)

# 2. 로깅 미들웨어
app.add_middleware(RequestLoggingMiddleware)

# 3. 요청 크기 제한 미들웨어 (가장 나중에 등록 = 가장 먼저 실행)
app.add_middleware(RequestSizeLimitMiddleware, max_size=5_000_000)  # 5MB 제한


# ── @app.middleware 데코레이터 방식 ─────────────────────────
# 간단한 미들웨어는 데코레이터 방식으로도 작성 가능합니다
@app.middleware("http")
async def add_custom_header(request: Request, call_next):
    """모든 응답에 커스텀 헤더를 추가하는 간단한 미들웨어"""
    response = await call_next(request)
    response.headers["X-API-Version"] = "1.0.0"
    response.headers["X-Powered-By"] = "FastAPI"
    return response


# ── 엔드포인트 ─────────────────────────────────────────────

@app.get("/", summary="홈")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "미들웨어 예제 API입니다",
        "description": "응답 헤더에서 X-Request-ID와 X-Process-Time을 확인하세요",
    }


@app.get("/slow", summary="느린 요청 시뮬레이션")
async def slow_endpoint():
    """
    의도적으로 느린 요청을 시뮬레이션합니다.
    로깅 미들웨어에서 처리 시간이 기록됩니다.
    """
    import asyncio
    await asyncio.sleep(2)  # 2초 대기
    return {"message": "느린 작업이 완료되었습니다"}


@app.get("/items", summary="아이템 목록")
async def list_items():
    """테스트용 아이템 목록을 반환합니다."""
    return {
        "items": [
            {"id": 1, "name": "키보드", "price": 50000},
            {"id": 2, "name": "마우스", "price": 30000},
            {"id": 3, "name": "모니터", "price": 300000},
        ]
    }


@app.post("/echo", summary="에코")
async def echo(request: Request):
    """
    전송된 JSON 본문을 그대로 반환합니다.
    큰 본문을 보내면 RequestSizeLimitMiddleware가 차단합니다.
    """
    body = await request.json()
    return {
        "message": "요청 본문을 그대로 반환합니다",
        "received": body,
    }


@app.get("/cors-test", summary="CORS 테스트")
async def cors_test():
    """
    CORS 테스트용 엔드포인트입니다.

    브라우저 콘솔에서 다음 코드로 테스트할 수 있습니다:
    ```javascript
    fetch('http://localhost:8000/cors-test')
      .then(res => res.json())
      .then(data => console.log(data))
    ```
    """
    return {
        "message": "CORS가 정상 작동합니다",
        "allowed_origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5500",
        ],
    }


@app.get("/headers-info", summary="요청 헤더 정보")
async def headers_info(request: Request):
    """요청 헤더 정보를 반환합니다. 미들웨어 동작 확인에 유용합니다."""
    return {
        "client_host": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_type": request.headers.get("content-type", "없음"),
        "authorization": "있음" if request.headers.get("authorization") else "없음",
    }
