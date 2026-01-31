# 실행 방법: pytest example-02.py -v
# 필요 패키지: pip install fastapi uvicorn pytest httpx

"""
챕터 10 예제 02: TestClient를 사용한 API 테스트

이 파일은 실행용 앱이 아닌 **테스트 파일**입니다.
pytest로 실행하여 API 동작을 검증합니다.

실행: pytest example-02.py -v
"""

import pytest
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.testclient import TestClient
from pydantic import BaseModel


# ── 테스트 대상 앱 (간단한 Todo API) ──────────────────────
app = FastAPI(title="테스트 대상 앱")

# 임시 데이터 저장소
todos_db: dict[int, dict] = {}
next_id = 1


class TodoCreate(BaseModel):
    title: str
    description: str = ""


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = {
        "id": next_id,
        "title": todo.title,
        "description": todo.description,
        "completed": False,
    }
    todos_db[next_id] = new_todo
    next_id += 1
    return new_todo


@app.get("/todos")
def list_todos():
    return list(todos_db.values())


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")
    return todos_db[todo_id]


@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")
    update_data = todo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        todos_db[todo_id][field] = value
    return todos_db[todo_id]


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    if todo_id not in todos_db:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다")
    del todos_db[todo_id]


# ── TestClient 생성 ────────────────────────────────────────
client = TestClient(app)


# ── fixture: 매 테스트마다 데이터 초기화 ───────────────────
@pytest.fixture(autouse=True)
def reset_database():
    """
    각 테스트 전에 데이터베이스를 초기화합니다.
    autouse=True: 모든 테스트에 자동으로 적용됩니다.
    """
    global next_id
    todos_db.clear()
    next_id = 1
    yield  # 테스트 실행
    # 테스트 후 정리 (필요한 경우)


@pytest.fixture
def sample_todo() -> dict:
    """테스트용 샘플 할 일 데이터"""
    return {"title": "FastAPI 공부하기", "description": "챕터 10까지 완료"}


@pytest.fixture
def created_todo(sample_todo) -> dict:
    """DB에 미리 생성된 할 일"""
    response = client.post("/todos", json=sample_todo)
    return response.json()


# ══════════════════════════════════════════════════════════
# 테스트 1: 할 일 생성
# ══════════════════════════════════════════════════════════

class TestCreateTodo:
    """할 일 생성 API 테스트"""

    def test_할일_생성_성공(self, sample_todo):
        """정상적인 할 일 생성을 테스트합니다."""
        response = client.post("/todos", json=sample_todo)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_todo["title"]
        assert data["description"] == sample_todo["description"]
        assert data["completed"] is False
        assert "id" in data

    def test_할일_생성_제목만(self):
        """제목만으로 할 일을 생성합니다. description은 기본값(빈 문자열)."""
        response = client.post("/todos", json={"title": "간단한 할 일"})

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "간단한 할 일"
        assert data["description"] == ""

    def test_할일_생성_제목_누락(self):
        """제목이 없으면 422 유효성 검증 에러가 발생합니다."""
        response = client.post("/todos", json={"description": "제목 없음"})

        assert response.status_code == 422

    def test_할일_생성_빈_본문(self):
        """빈 JSON을 보내면 422 에러가 발생합니다."""
        response = client.post("/todos", json={})

        assert response.status_code == 422

    def test_할일_연속_생성_ID_증가(self):
        """연속으로 생성하면 ID가 순차적으로 증가합니다."""
        response1 = client.post("/todos", json={"title": "첫 번째"})
        response2 = client.post("/todos", json={"title": "두 번째"})
        response3 = client.post("/todos", json={"title": "세 번째"})

        assert response1.json()["id"] == 1
        assert response2.json()["id"] == 2
        assert response3.json()["id"] == 3


# ══════════════════════════════════════════════════════════
# 테스트 2: 할 일 조회
# ══════════════════════════════════════════════════════════

class TestReadTodo:
    """할 일 조회 API 테스트"""

    def test_빈_목록_조회(self):
        """데이터가 없을 때 빈 목록을 반환합니다."""
        response = client.get("/todos")

        assert response.status_code == 200
        assert response.json() == []

    def test_목록_조회(self, created_todo):
        """생성된 할 일이 목록에 포함됩니다."""
        response = client.get("/todos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == created_todo["id"]

    def test_단일_조회_성공(self, created_todo):
        """ID로 특정 할 일을 조회합니다."""
        response = client.get(f"/todos/{created_todo['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_todo["id"]
        assert data["title"] == created_todo["title"]

    def test_존재하지_않는_할일_조회(self):
        """존재하지 않는 ID로 조회하면 404를 반환합니다."""
        response = client.get("/todos/99999")

        assert response.status_code == 404
        assert "찾을 수 없습니다" in response.json()["detail"]


# ══════════════════════════════════════════════════════════
# 테스트 3: 할 일 수정
# ══════════════════════════════════════════════════════════

class TestUpdateTodo:
    """할 일 수정 API 테스트"""

    def test_제목_수정(self, created_todo):
        """할 일의 제목을 수정합니다."""
        response = client.patch(
            f"/todos/{created_todo['id']}",
            json={"title": "수정된 제목"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "수정된 제목"

    def test_완료_상태_변경(self, created_todo):
        """할 일의 완료 상태를 변경합니다."""
        response = client.patch(
            f"/todos/{created_todo['id']}",
            json={"completed": True},
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True

    def test_존재하지_않는_할일_수정(self):
        """존재하지 않는 ID의 할 일을 수정하면 404를 반환합니다."""
        response = client.patch("/todos/99999", json={"title": "없는 할 일"})

        assert response.status_code == 404


# ══════════════════════════════════════════════════════════
# 테스트 4: 할 일 삭제
# ══════════════════════════════════════════════════════════

class TestDeleteTodo:
    """할 일 삭제 API 테스트"""

    def test_삭제_성공(self, created_todo):
        """할 일을 삭제하면 204를 반환합니다."""
        response = client.delete(f"/todos/{created_todo['id']}")

        assert response.status_code == 204

        # 삭제 후 조회하면 404
        response = client.get(f"/todos/{created_todo['id']}")
        assert response.status_code == 404

    def test_존재하지_않는_할일_삭제(self):
        """존재하지 않는 ID를 삭제하면 404를 반환합니다."""
        response = client.delete("/todos/99999")

        assert response.status_code == 404

    def test_삭제_후_목록에서_제거됨(self, created_todo):
        """삭제 후 목록에서도 제거되어야 합니다."""
        # 삭제 전: 1개
        assert len(client.get("/todos").json()) == 1

        # 삭제
        client.delete(f"/todos/{created_todo['id']}")

        # 삭제 후: 0개
        assert len(client.get("/todos").json()) == 0
