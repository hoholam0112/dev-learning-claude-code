# 실행 방법: uvicorn example-01:app --reload
# ASGI 프로토콜의 내부 동작을 이해하기 위한 예제
# 필요 패키지: pip install fastapi uvicorn

import json
import time

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


# ============================================================
# 1. 순수 ASGI 애플리케이션
# ============================================================

async def raw_asgi_app(scope: dict, receive, send) -> None:
    """
    가장 기본적인 ASGI 애플리케이션.
    FastAPI 없이 ASGI 프로토콜만으로 HTTP 요청을 처리한다.

    이 함수를 uvicorn으로 직접 실행하려면:
    uvicorn example-01:raw_asgi_app
    """
    if scope["type"] == "http":
        # 요청 본문 수신 (chunked 전송 대응)
        body = b""
        while True:
            message = await receive()
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        # 요청 정보를 파싱하여 응답 생성
        response_data = {
            "message": "순수 ASGI 응답입니다",
            "method": scope["method"],
            "path": scope["path"],
            "query_string": scope["query_string"].decode("utf-8"),
            "request_body_length": len(body),
        }
        response_body = json.dumps(
            response_data, ensure_ascii=False
        ).encode("utf-8")

        # 응답 전송: 반드시 start → body 순서
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"application/json; charset=utf-8"],
                [b"x-powered-by", b"raw-asgi"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": response_body,
            "more_body": False,  # 단일 청크 응답
        })

    elif scope["type"] == "lifespan":
        # 서버 시작/종료 이벤트 처리
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                print("[순수 ASGI] 서버 시작")
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                print("[순수 ASGI] 서버 종료")
                await send({"type": "lifespan.shutdown.complete"})
                return


# ============================================================
# 2. FastAPI가 내부적으로 하는 일을 보여주는 비교
# ============================================================

app = FastAPI(
    title="ASGI 아키텍처 학습",
    description="ASGI 프로토콜의 내부 동작을 학습하기 위한 예제 애플리케이션",
    version="1.0.0",
)


class RequestLifecycleMiddleware(BaseHTTPMiddleware):
    """
    요청 생명주기를 추적하는 미들웨어.
    각 요청의 ASGI scope 정보와 처리 시간을 로깅한다.
    """

    async def dispatch(self, request: Request, call_next):
        # 요청 시작 시점 기록
        start_time = time.perf_counter()

        # ASGI scope 정보 출력
        print(f"\n{'='*60}")
        print(f"[ASGI Scope] type={request.scope['type']}, "
              f"path={request.scope['path']}, "
              f"method={request.scope['method']}")
        print(f"[ASGI Scope] http_version={request.scope.get('http_version')}")
        print(f"[ASGI Scope] server={request.scope.get('server')}")
        print(f"[ASGI Scope] client={request.scope.get('client')}")

        # 다음 미들웨어/핸들러 호출
        response = await call_next(request)

        # 처리 시간 측정 및 헤더 추가
        duration = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{duration:.6f}"
        print(f"[응답 완료] 상태={response.status_code}, 소요시간={duration:.4f}초")
        print(f"{'='*60}\n")

        return response


# 미들웨어 등록
app.add_middleware(RequestLifecycleMiddleware)


@app.get("/")
async def root():
    """기본 엔드포인트 - FastAPI가 ASGI 위에서 동작함을 확인"""
    return {"message": "FastAPI는 ASGI 위에서 동작합니다"}


@app.get("/scope-info")
async def scope_info(request: Request):
    """
    현재 요청의 ASGI scope 정보를 반환합니다.
    ASGI 프로토콜이 어떤 정보를 전달하는지 직접 확인할 수 있습니다.
    """
    return {
        "type": request.scope["type"],
        "asgi_version": request.scope.get("asgi", {}),
        "http_version": request.scope.get("http_version"),
        "method": request.method,
        "path": request.url.path,
        "query_string": str(request.query_params),
        "headers": dict(request.headers),
        "server": request.scope.get("server"),
        "client": request.scope.get("client"),
        "path_params": request.path_params,
    }


@app.get("/compare")
async def compare_approaches():
    """
    순수 ASGI vs FastAPI 접근 방식을 비교 설명합니다.
    """
    return {
        "순수_ASGI": {
            "장점": [
                "프로토콜 수준의 완전한 제어",
                "최소 오버헤드",
                "의존성 없음",
            ],
            "단점": [
                "모든 것을 수동 구현해야 함",
                "타입 검증/직렬화 없음",
                "API 문서 자동 생성 없음",
            ],
        },
        "FastAPI": {
            "장점": [
                "자동 타입 검증 (Pydantic)",
                "OpenAPI 문서 자동 생성",
                "의존성 주입 시스템",
                "미들웨어/이벤트 고수준 추상화",
            ],
            "단점": [
                "추가 추상화 계층에 의한 약간의 오버헤드",
                "내부 동작 이해 없이는 디버깅 어려움",
            ],
        },
        "내부_관계": "FastAPI → Starlette → ASGI (계층 구조)",
    }


# ============================================================
# 3. 순수 ASGI 앱을 FastAPI에 마운트하는 예제
# ============================================================

async def mounted_asgi_app(scope, receive, send):
    """FastAPI 앱에 마운트되는 순수 ASGI 앱"""
    if scope["type"] == "http":
        response_data = {
            "message": "이것은 FastAPI에 마운트된 순수 ASGI 앱입니다",
            "original_path": scope["path"],
            "root_path": scope.get("root_path", ""),
        }
        response_body = json.dumps(
            response_data, ensure_ascii=False
        ).encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"application/json; charset=utf-8"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": response_body,
        })


# 순수 ASGI 앱을 /raw 경로에 마운트
app.mount("/raw", mounted_asgi_app)


if __name__ == "__main__":
    import uvicorn

    print("서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print("ASGI scope 확인: http://localhost:8000/scope-info")
    print("마운트된 ASGI 앱: http://localhost:8000/raw/anything")
    uvicorn.run(app, host="0.0.0.0", port=8000)
