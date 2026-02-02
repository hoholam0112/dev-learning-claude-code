# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 가상 데이터베이스
fake_db = {}
user_id_counter = 0


# TODO: UserCreate 모델을 정의하세요 (요청용)
# - username: str
# - email: str
# - password: str
# - full_name: Optional[str] = None


# TODO: UserResponse 모델을 정의하세요 (응답용 - password 제외)
# - id: int
# - username: str
# - email: str
# - full_name: Optional[str] = None


# TODO: POST /users 엔드포인트를 작성하세요
# - response_model=UserResponse 를 지정하세요
# - user_id_counter를 증가시키고 fake_db에 저장
# - UserResponse 형태로 반환 (password가 응답에 포함되지 않아야 함)


# TODO: GET /users/{user_id} 엔드포인트를 작성하세요
# - response_model=UserResponse
# - fake_db에서 조회하여 반환


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 1: 사용자 생성 - password가 응답에 포함되지 않아야 함
    response = client.post("/users", json={
        "username": "hong",
        "email": "hong@example.com",
        "password": "secret123",
        "full_name": "홍길동"
    })
    assert response.status_code == 200
    data = response.json()
    assert "password" not in data, "응답에 password가 포함되면 안 됩니다!"
    assert data["username"] == "hong"
    assert data["email"] == "hong@example.com"
    assert data["full_name"] == "홍길동"
    assert "id" in data
    print("✓ 사용자 생성 (password 필터링) 테스트 통과")

    # 테스트 2: 사용자 조회
    user_id = data["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "password" not in data, "조회 응답에도 password가 포함되면 안 됩니다!"
    assert data["username"] == "hong"
    assert data["id"] == user_id
    print("✓ 사용자 조회 테스트 통과")

    # 테스트 3: full_name 없이 생성
    response = client.post("/users", json={
        "username": "kim",
        "email": "kim@example.com",
        "password": "pass456"
    })
    assert response.status_code == 200
    data = response.json()
    assert "password" not in data
    assert data["username"] == "kim"
    assert data["full_name"] is None
    print("✓ full_name 없는 사용자 생성 테스트 통과")

    print("\n모든 테스트를 통과했습니다!")
