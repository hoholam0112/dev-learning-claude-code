# 실행: uvicorn exercise:app --reload --port 8001
# 테스트: python exercise.py

from fastapi import FastAPI
from fastapi.testclient import TestClient

# TODO: FastAPI 인스턴스를 생성하세요
# title="나의 학습 API", description="FastAPI 학습용 API 서버", version="0.1.0"
app = FastAPI()


# TODO: GET / 루트 엔드포인트를 작성하세요
# 반환값: {"app": "나의 학습 API", "version": "0.1.0"}


# TODO: GET /health 헬스체크 엔드포인트를 작성하세요
# 반환값: {"status": "healthy"}


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
