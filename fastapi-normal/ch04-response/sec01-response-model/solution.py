# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 가상 데이터베이스
fake_db = {}
user_id_counter = 0


# 요청용 모델: 클라이언트가 보내는 데이터
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


# 응답용 모델: 서버가 돌려주는 데이터 (password 제외)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None


# 사용자 생성 엔드포인트
# response_model=UserResponse를 지정하면
# 반환 데이터에서 password가 자동으로 제거됩니다.
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    global user_id_counter
    user_id_counter += 1

    # 사용자 데이터를 딕셔너리로 변환하고 ID 추가
    user_data = user.model_dump()
    user_data["id"] = user_id_counter

    # 가상 데이터베이스에 저장 (password 포함)
    fake_db[user_id_counter] = user_data

    # user_data에는 password가 포함되어 있지만,
    # response_model=UserResponse 덕분에 응답에서 자동 제외됩니다.
    return user_data


# 사용자 조회 엔드포인트
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user_data = fake_db.get(user_id)
    if not user_data:
        return {"id": 0, "username": "", "email": ""}
    # 마찬가지로 password는 응답에서 자동 제외됩니다.
    return user_data


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
