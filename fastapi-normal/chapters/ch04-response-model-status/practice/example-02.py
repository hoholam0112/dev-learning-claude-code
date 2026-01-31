# 실행 방법: uvicorn example-02:app --reload
# 다중 상태 코드와 응답 모델 예제

from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="다중 응답 예제", description="다양한 상태 코드와 응답 모델")


# ============================================================
# 모델 정의
# ============================================================


class TaskCreate(BaseModel):
    """작업 생성 요청 모델"""

    title: str = Field(..., min_length=1, max_length=200, description="작업 제목")
    description: Optional[str] = Field(default=None, description="작업 설명")
    priority: int = Field(default=3, ge=1, le=5, description="우선순위 (1=최고, 5=최저)")


class TaskResponse(BaseModel):
    """작업 응답 모델"""

    id: int
    title: str
    description: Optional[str] = None
    priority: int
    completed: bool


class TaskSummary(BaseModel):
    """작업 요약 모델 (간소화된 응답)"""

    id: int
    title: str
    completed: bool


class ErrorResponse(BaseModel):
    """에러 응답 모델"""

    error: str
    detail: str


# ============================================================
# 임시 저장소
# ============================================================

tasks_db: dict[int, dict] = {}
next_id: int = 1


# ============================================================
# API 엔드포인트
# ============================================================


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["작업"],
    summary="새 작업 생성",
)
def create_task(task: TaskCreate):
    """새 작업을 생성하고 201 상태 코드를 반환합니다."""
    global next_id

    task_data = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "completed": False,
    }
    tasks_db[next_id] = task_data
    next_id += 1

    return task_data


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["작업"],
    responses={
        200: {"description": "작업 조회 성공", "model": TaskResponse},
        404: {
            "description": "작업을 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "작업을 찾을 수 없습니다 (ID: 999)"}
                }
            },
        },
    },
)
def get_task(task_id: int):
    """특정 작업을 조회합니다.

    작업이 존재하지 않으면 404 에러를 반환합니다.
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작업을 찾을 수 없습니다 (ID: {task_id})",
        )
    return tasks_db[task_id]


@app.get(
    "/tasks/{task_id}/summary",
    response_model=TaskSummary,
    tags=["작업"],
)
def get_task_summary(task_id: int):
    """작업의 요약 정보만 반환합니다.

    TaskSummary 모델을 사용하여 최소한의 정보만 포함합니다.
    """
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작업을 찾을 수 없습니다 (ID: {task_id})",
        )
    return tasks_db[task_id]


@app.patch(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
    tags=["작업"],
)
def complete_task(task_id: int):
    """작업을 완료 상태로 변경합니다."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작업을 찾을 수 없습니다 (ID: {task_id})",
        )

    tasks_db[task_id]["completed"] = True
    return tasks_db[task_id]


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["작업"],
)
def delete_task(task_id: int):
    """작업을 삭제합니다. 성공 시 204 (본문 없음)를 반환합니다."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작업을 찾을 수 없습니다 (ID: {task_id})",
        )
    del tasks_db[task_id]
    return None


@app.post(
    "/tasks/bulk",
    tags=["작업"],
    summary="작업 일괄 생성 (JSONResponse 직접 반환)",
)
def create_tasks_bulk(tasks: list[TaskCreate]):
    """여러 작업을 한 번에 생성합니다.

    JSONResponse를 직접 사용하여 커스텀 헤더를 포함하는 예제입니다.
    """
    global next_id

    created_tasks = []
    for task in tasks:
        task_data = {
            "id": next_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "completed": False,
        }
        tasks_db[next_id] = task_data
        created_tasks.append(task_data)
        next_id += 1

    # JSONResponse를 직접 반환하여 커스텀 헤더를 추가합니다
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"{len(created_tasks)}개의 작업이 생성되었습니다",
            "tasks": created_tasks,
        },
        headers={"X-Total-Created": str(len(created_tasks))},
    )
