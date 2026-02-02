# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

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


# ── CREATE: 201 Created ──
# 새로운 리소스를 생성했으므로 201을 반환합니다.
@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    global todo_id_counter
    todo_id_counter += 1

    todo_data = todo.model_dump()
    todo_data["id"] = todo_id_counter
    todo_data["completed"] = False  # 기본값: 미완료

    todos_db[todo_id_counter] = todo_data
    return todo_data


# ── READ ALL: 200 OK (기본값) ──
# 목록 조회는 기본 상태 코드 200을 사용합니다.
@app.get("/todos", response_model=list[TodoResponse])
async def read_todos():
    return list(todos_db.values())


# ── READ ONE: 200 OK ──
# 단건 조회도 기본 상태 코드 200을 사용합니다.
@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def read_todo(todo_id: int):
    return todos_db[todo_id]


# ── UPDATE: 200 OK ──
# 수정 후 변경된 데이터를 응답에 포함하여 200으로 반환합니다.
@app.put("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    stored_todo = todos_db[todo_id]

    # exclude_unset=True: 클라이언트가 실제로 보낸 필드만 추출
    # 예: {"completed": True}만 보냈다면, title과 description은 건드리지 않음
    update_data = todo_update.model_dump(exclude_unset=True)
    stored_todo.update(update_data)

    return stored_todo


# ── DELETE: 204 No Content ──
# 삭제 후 돌려줄 데이터가 없으므로 204를 반환합니다.
# 204는 응답 본문이 없어야 하므로 아무것도 return하지 않습니다.
@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    del todos_db[todo_id]
    # return 없음 - 204 No Content


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
