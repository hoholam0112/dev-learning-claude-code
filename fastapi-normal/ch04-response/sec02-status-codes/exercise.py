# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 가상 데이터베이스
todos_db = {}
todo_id_counter = 0


# ── Pydantic 모델 ──

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False


# TODO: POST /todos 엔드포인트를 작성하세요
# - status_code=status.HTTP_201_CREATED 를 지정하세요
# - response_model=TodoResponse
# - todo_id_counter를 증가시키고 todos_db에 저장
# - completed의 기본값은 False


# TODO: GET /todos 엔드포인트를 작성하세요
# - response_model=list[TodoResponse]
# - todos_db의 모든 할일을 리스트로 반환


# TODO: GET /todos/{todo_id} 엔드포인트를 작성하세요
# - response_model=TodoResponse
# - todos_db에서 해당 ID의 할일을 조회하여 반환


# TODO: PUT /todos/{todo_id} 엔드포인트를 작성하세요
# - response_model=TodoResponse
# - TodoUpdate에서 전달된 필드만 업데이트
# - 힌트: todo_update.model_dump(exclude_unset=True) 활용


# TODO: DELETE /todos/{todo_id} 엔드포인트를 작성하세요
# - status_code=status.HTTP_204_NO_CONTENT
# - todos_db에서 해당 ID의 할일을 삭제
# - 아무것도 반환하지 않음


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 1: 할일 생성 (201 Created)
    response = client.post("/todos", json={
        "title": "FastAPI 공부",
        "description": "Ch04 응답 모델 학습"
    })
    assert response.status_code == 201, f"기대값: 201, 실제값: {response.status_code}"
    data = response.json()
    assert data["title"] == "FastAPI 공부"
    assert data["completed"] is False
    assert "id" in data
    todo_id = data["id"]
    print("✓ POST /todos - 201 Created 테스트 통과")

    # 테스트 2: 전체 조회 (200 OK)
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    print("✓ GET /todos - 200 OK 테스트 통과")

    # 테스트 3: 단건 조회 (200 OK)
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "FastAPI 공부"
    print("✓ GET /todos/{id} - 200 OK 테스트 통과")

    # 테스트 4: 수정 (200 OK)
    response = client.put(f"/todos/{todo_id}", json={
        "completed": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["title"] == "FastAPI 공부"  # 변경하지 않은 필드는 유지
    print("✓ PUT /todos/{id} - 200 OK 테스트 통과")

    # 테스트 5: 삭제 (204 No Content)
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204, f"기대값: 204, 실제값: {response.status_code}"
    assert response.content == b"", "204 응답에는 본문이 없어야 합니다"
    print("✓ DELETE /todos/{id} - 204 No Content 테스트 통과")

    # 테스트 6: 삭제 후 목록이 비어있는지 확인
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 0
    print("✓ 삭제 후 목록 비어있음 확인")

    print("\n모든 테스트를 통과했습니다!")
