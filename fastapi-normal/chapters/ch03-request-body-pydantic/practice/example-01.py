# 실행 방법: uvicorn example-01:app --reload
# 사용자 등록 API - Pydantic BaseModel 활용 예제

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="사용자 등록 API", description="Pydantic 모델 활용 예제")

# ============================================================
# Pydantic 모델 정의
# ============================================================


class UserCreate(BaseModel):
    """사용자 생성 요청 모델"""

    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="사용자 이름 (2~50자)",
        examples=["홍길동"],
    )
    email: str = Field(
        ...,
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        description="이메일 주소",
        examples=["hong@example.com"],
    )
    age: int = Field(
        ...,
        ge=0,
        le=150,
        description="나이 (0~150)",
        examples=[25],
    )
    bio: Optional[str] = Field(
        default=None,
        max_length=200,
        description="자기소개 (선택, 최대 200자)",
    )

    # API 문서에 표시될 예제 데이터
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "홍길동",
                    "email": "hong@example.com",
                    "age": 25,
                    "bio": "안녕하세요! 백엔드 개발자입니다.",
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """사용자 수정 요청 모델 - 모든 필드가 선택적"""

    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    email: Optional[str] = Field(default=None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: Optional[int] = Field(default=None, ge=0, le=150)
    bio: Optional[str] = Field(default=None, max_length=200)


# ============================================================
# 임시 데이터 저장소
# ============================================================

# 메모리 기반 임시 저장소 (서버 재시작 시 초기화됨)
users_db: dict[int, dict] = {}
next_id: int = 1

# ============================================================
# API 엔드포인트
# ============================================================


@app.post("/users", tags=["사용자"])
def create_user(user: UserCreate):
    """새 사용자를 등록합니다.

    요청 본문(JSON)을 Pydantic 모델로 자동 파싱하고 검증합니다.
    검증에 실패하면 422 에러가 자동으로 반환됩니다.
    """
    global next_id

    user_data = {
        "id": next_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "bio": user.bio,
    }
    users_db[next_id] = user_data
    next_id += 1

    return {"message": f"{user.name}님이 등록되었습니다", "user": user_data}


@app.put("/users/{user_id}", tags=["사용자"])
def update_user(user_id: int, user: UserUpdate):
    """사용자 정보를 수정합니다.

    전달된 필드만 업데이트합니다 (부분 수정 지원).
    None이 아닌 필드만 반영됩니다.
    """
    if user_id not in users_db:
        return {"error": "사용자를 찾을 수 없습니다"}

    # None이 아닌 필드만 업데이트
    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        users_db[user_id][key] = value

    return {"message": "수정되었습니다", "user": users_db[user_id]}


@app.get("/users", tags=["사용자"])
def get_users():
    """등록된 전체 사용자 목록을 반환합니다."""
    return {"total": len(users_db), "users": list(users_db.values())}


@app.get("/users/{user_id}", tags=["사용자"])
def get_user(user_id: int):
    """특정 사용자를 조회합니다."""
    if user_id not in users_db:
        return {"error": "사용자를 찾을 수 없습니다"}
    return users_db[user_id]
