# 실행: uvicorn exercise:app --reload
# 테스트: http://localhost:8000/docs 에서 확인
# 또는: python exercise.py (자체 테스트)

from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


# TODO: GET /hello 엔드포인트를 작성하세요
# 반환값: {"message": "안녕하세요, FastAPI!"}


# TODO: GET /greet/{name} 엔드포인트를 작성하세요
# 반환값: {"message": "안녕하세요, {name}님!"}


# --- 테스트 (수정하지 마세요) ---
if __name__ == "__main__":
    client = TestClient(app)

    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "안녕하세요, FastAPI!"}
    print("✓ /hello 테스트 통과")

    response = client.get("/greet/홍길동")
    assert response.status_code == 200
    assert response.json() == {"message": "안녕하세요, 홍길동님!"}
    print("✓ /greet/{name} 테스트 통과")

    print("\n모든 테스트를 통과했습니다!")
