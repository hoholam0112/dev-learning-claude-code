# 실행 방법: uvicorn example-02:app --reload
# API 메타데이터와 태그를 활용한 문서화 예제

from fastapi import FastAPI

# API 메타데이터 설정
# 이 정보들은 /docs와 /redoc 페이지에 표시됩니다
app = FastAPI(
    title="학습용 API",
    description="FastAPI 학습을 위한 예제 API입니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# 태그를 사용한 엔드포인트 그룹화
# tags 파라미터를 통해 Swagger UI에서 엔드포인트를 그룹별로 분류할 수 있습니다
@app.get("/health", tags=["시스템"])
def health_check():
    """서버 상태를 확인합니다.

    서버가 정상적으로 동작 중인지 확인하는 헬스체크 엔드포인트입니다.
    로드밸런서나 모니터링 도구에서 주기적으로 호출합니다.
    """
    return {"status": "healthy"}


@app.get("/info", tags=["시스템"])
def get_info():
    """API 정보를 반환합니다.

    API의 이름, 버전 등 기본 정보를 제공합니다.
    """
    return {
        "name": "학습용 API",
        "version": "1.0.0",
        "description": "FastAPI 학습을 위한 예제",
    }


@app.get("/hello/{name}", tags=["인사"])
def say_hello(name: str):
    """이름을 받아 인사 메시지를 반환합니다.

    Args:
        name: 인사할 대상의 이름

    사용 예시:
        GET /hello/홍길동 → {"message": "안녕하세요, 홍길동님!"}
    """
    return {"message": f"안녕하세요, {name}님!"}
