# 실행 방법: uvicorn example-01:app --reload
# 사용자 CRUD - 입력/출력 모델 분리 예제

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="사용자 CRUD API", description="입력/출력 모델 분리 예제")

# ============================================================
# Pydantic 모델 정의 — 입력/출력/내부 분리
# ============================================================


class UserCreate(BaseModel):
    """입력 모델: 사용자 생성 요청"""

    name: str = Field(..., min_length=2, max_length=50, description="이름")
    email: str = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=8, description="비밀번호 (8자 이상)")
    age: Optional[int] = Field(default=None, ge=0, le=150, description="나이")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "홍길동",
                    "email": "hong@example.com",
                    "password": "secure1234",
                    "age": 25,
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """출력 모델: 비밀번호를 제외한 사용자 정보"""

    id: int
    name: str
    email: str
    age: Optional[int] = None
    created_at: str


class UserListResponse(BaseModel):
    """출력 모델: 사용자 목록"""

    total: int
    users: List[UserResponse]


# ============================================================
# 임시 저장소
# ============================================================

users_db: dict[int, dict] = {}
next_id: int = 1

# ============================================================
# API 엔드포인트
# ============================================================


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["사용자"],
)
def create_user(user: UserCreate):
    """사용자를 생성합니다.

    - 입력: UserCreate (비밀번호 포함)
    - 출력: UserResponse (비밀번호 제외)
    - 상태 코드: 201 Created
    """
    global next_id

    user_data = {
        "id": next_id,
        "name": user.name,
        "email": user.email,
        "password_hash": f"hashed_{user.password}",  # 실제로는 해시 처리 필요
        "age": user.age,
        "created_at": datetime.now().isoformat(),
    }
    users_db[next_id] = user_data
    next_id += 1

    # password_hash가 포함된 딕셔너리를 반환하지만
    # response_model=UserResponse 덕분에 비밀번호는 자동으로 필터링됩니다
    return user_data


@app.get(
    "/users",
    response_model=UserListResponse,
    tags=["사용자"],
)
def get_users():
    """전체 사용자 목록을 반환합니다.

    response_model을 통해 각 사용자의 비밀번호가 자동 필터링됩니다.
    """
    return {
        "total": len(users_db),
        "users": list(users_db.values()),
    }


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["사용자"],
    responses={
        404: {
            "description": "사용자를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "사용자를 찾을 수 없습니다"}
                }
            },
        },
    },
)
def get_user(user_id: int):
    """특정 사용자를 조회합니다.

    존재하지 않는 사용자 ID로 요청하면 404 에러가 반환됩니다.
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    return users_db[user_id]


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["사용자"],
)
def delete_user(user_id: int):
    """사용자를 삭제합니다.

    성공 시 204 No Content를 반환합니다 (응답 본문 없음).
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    del users_db[user_id]
    return None  # 204 응답은 본문이 없습니다
