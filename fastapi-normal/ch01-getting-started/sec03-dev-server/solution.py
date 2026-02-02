# 실행: uvicorn solution:app --reload --port 8001
# 테스트: python solution.py
#
# 이 파일은 exercise.py의 모범 답안입니다.

from fastapi import FastAPI
from fastapi.testclient import TestClient

# FastAPI 인스턴스 생성 시 메타데이터를 설정합니다.
# title: Swagger UI 상단에 표시되는 API 이름
# description: API에 대한 설명 (Swagger UI에 표시됨)
# version: API 버전 (Swagger UI에 표시됨)
# 이 정보들은 /docs, /redoc 페이지에 자동으로 반영됩니다.
app = FastAPI(
    title="나의 학습 API",
    description="FastAPI 학습용 API 서버",
    version="0.1.0",
)


# GET / 루트 엔드포인트
# app.title과 app.version을 사용하여 중복을 피합니다.
# 이렇게 하면 FastAPI 인스턴스의 메타데이터를 변경해도
# 이 엔드포인트의 응답이 자동으로 업데이트됩니다.
@app.get("/")
def read_root():
    return {"app": app.title, "version": app.version}


# GET /health 헬스체크 엔드포인트
# 헬스체크는 서버가 정상 작동 중인지 확인하는 용도입니다.
# 로드 밸런서, 컨테이너 오케스트레이션(Kubernetes 등),
# 모니터링 도구에서 이 엔드포인트를 주기적으로 호출합니다.
# 단순히 "healthy"를 반환하는 것이 일반적입니다.
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# --- 테스트 (수정하지 마세요) ---
if __name__ == "__main__":
    client = TestClient(app)

    assert app.title == "나의 학습 API"
    assert app.version == "0.1.0"
    print("✓ 앱 메타데이터 테스트 통과")

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"app": "나의 학습 API", "version": "0.1.0"}
    print("✓ / 루트 엔드포인트 테스트 통과")

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    print("✓ /health 테스트 통과")

    print("\n모든 테스트를 통과했습니다!")
