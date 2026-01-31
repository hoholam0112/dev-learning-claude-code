# 실행 방법: uvicorn example-01:app --reload
# 커스텀 validator와 제네릭 모델 예제
# 필요 패키지: pip install fastapi uvicorn pydantic

from datetime import datetime, date
from typing import TypeVar, Generic, Optional
import re

from fastapi import FastAPI, HTTPException, Query
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    field_serializer,
    ConfigDict,
)

app = FastAPI(title="고급 Pydantic 패턴 - 커스텀 Validator & 제네릭 모델")


# ============================================================
# 1. 커스텀 Validator 체인
# ============================================================

class UserCreate(BaseModel):
    """
    사용자 생성 모델.
    여러 단계의 검증을 거쳐 데이터 무결성을 보장한다.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(
        min_length=3,
        max_length=30,
        description="사용자명 (영문, 숫자, 밑줄만 허용)",
    )
    email: str = Field(description="이메일 주소")
    password: str = Field(min_length=8, description="비밀번호")
    password_confirm: str = Field(description="비밀번호 확인")
    birth_date: date = Field(description="생년월일")
    phone: Optional[str] = Field(None, description="전화번호 (선택)")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        사용자명 규칙:
        - 영문 소문자, 숫자, 밑줄만 허용
        - 숫자로 시작할 수 없음
        """
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(
                "사용자명은 영문 소문자로 시작하고, "
                "영문 소문자/숫자/밑줄만 사용할 수 있습니다"
            )
        # 예약어 검사
        reserved = {"admin", "root", "system", "api", "null", "undefined"}
        if v in reserved:
            raise ValueError(f"'{v}'는 예약된 사용자명입니다")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """간단한 이메일 형식 검증"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("유효한 이메일 형식이 아닙니다")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        비밀번호 강도 검증:
        - 8자 이상 (Field에서 처리)
        - 대문자, 소문자, 숫자, 특수문자 각각 1개 이상
        """
        checks = [
            (r"[A-Z]", "대문자"),
            (r"[a-z]", "소문자"),
            (r"[0-9]", "숫자"),
            (r"[!@#$%^&*(),.?\":{}|<>]", "특수문자"),
        ]
        missing = [name for pattern, name in checks if not re.search(pattern, v)]
        if missing:
            raise ValueError(
                f"비밀번호에 다음이 포함되어야 합니다: {', '.join(missing)}"
            )
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        """생년월일 유효성 검증"""
        today = date.today()
        age = (today - v).days // 365
        if age < 14:
            raise ValueError("14세 미만은 가입할 수 없습니다")
        if age > 150:
            raise ValueError("유효하지 않은 생년월일입니다")
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        """
        전화번호 정규화 (before 모드: 타입 변환 전 실행).
        다양한 형식의 전화번호를 통일된 형식으로 변환한다.
        """
        if v is None:
            return v
        # 숫자만 추출
        digits = re.sub(r"[^\d]", "", str(v))
        if len(digits) == 11 and digits.startswith("010"):
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        elif len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif digits:
            raise ValueError(
                f"유효하지 않은 전화번호 형식입니다: {v}"
            )
        return None

    @model_validator(mode="after")
    def validate_passwords_match(self) -> "UserCreate":
        """비밀번호와 확인 비밀번호가 일치하는지 검증"""
        if self.password != self.password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return self

    @field_serializer("password", "password_confirm")
    def mask_password(self, v: str) -> str:
        """직렬화 시 비밀번호 마스킹"""
        return "********"


class UserResponse(BaseModel):
    """응답용 사용자 모델 (민감 정보 제외)"""
    id: int
    username: str
    email: str
    birth_date: date
    phone: Optional[str] = None
    created_at: datetime

    @field_serializer("birth_date")
    def serialize_date(self, v: date) -> str:
        return v.strftime("%Y년 %m월 %d일")

    @field_serializer("created_at")
    def serialize_datetime(self, v: datetime) -> str:
        return v.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 2. 제네릭 모델
# ============================================================

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    모든 API 응답을 감싸는 제네릭 래퍼.
    일관된 응답 형식을 보장한다.
    """
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def validate_consistency(self) -> "ApiResponse[T]":
        """응답 일관성 검증: 성공이면 데이터 필수, 실패면 에러 필수"""
        if self.success and self.data is None:
            # 성공이지만 데이터가 없는 경우도 허용 (204 No Content 등)
            pass
        if not self.success and self.error is None:
            raise ValueError("실패 응답에는 에러 메시지가 필수입니다")
        return self

    @field_serializer("timestamp")
    def serialize_timestamp(self, v: datetime) -> str:
        return v.isoformat()


class PaginatedResponse(BaseModel, Generic[T]):
    """
    제네릭 페이지네이션 응답.
    어떤 타입의 아이템이든 페이지네이션할 수 있다.
    """
    items: list[T]
    total: int = Field(ge=0, description="전체 아이템 수")
    page: int = Field(ge=1, description="현재 페이지 (1부터 시작)")
    page_size: int = Field(ge=1, le=100, description="페이지당 아이템 수")
    total_pages: int = Field(ge=0, description="전체 페이지 수")
    has_next: bool
    has_prev: bool

    @model_validator(mode="after")
    def validate_pagination(self) -> "PaginatedResponse[T]":
        """페이지네이션 메타데이터 일관성 검증"""
        expected_total_pages = (
            (self.total + self.page_size - 1) // self.page_size
            if self.total > 0
            else 0
        )
        if self.total_pages != expected_total_pages:
            raise ValueError(
                f"total_pages({self.total_pages})가 "
                f"예상값({expected_total_pages})과 다릅니다"
            )
        if self.has_next != (self.page < self.total_pages):
            raise ValueError("has_next 값이 올바르지 않습니다")
        if self.has_prev != (self.page > 1):
            raise ValueError("has_prev 값이 올바르지 않습니다")
        return self


def create_paginated_response(
    items: list[T],
    total: int,
    page: int,
    page_size: int,
) -> dict:
    """페이지네이션 응답 생성 헬퍼 함수"""
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


# ============================================================
# 3. 엔드포인트 정의
# ============================================================

# 임시 저장소
fake_users: list[dict] = []
next_user_id = 1


@app.post(
    "/users",
    response_model=ApiResponse[UserResponse],
    status_code=201,
)
async def create_user(user_data: UserCreate):
    """
    사용자 생성 엔드포인트.
    Pydantic 모델이 자동으로 입력 데이터를 검증한다.
    """
    global next_user_id

    # 중복 검사
    for existing in fake_users:
        if existing["username"] == user_data.username:
            raise HTTPException(
                status_code=409,
                detail="이미 존재하는 사용자명입니다",
            )
        if existing["email"] == user_data.email:
            raise HTTPException(
                status_code=409,
                detail="이미 존재하는 이메일입니다",
            )

    # 사용자 생성
    new_user = {
        "id": next_user_id,
        "username": user_data.username,
        "email": user_data.email,
        "birth_date": user_data.birth_date,
        "phone": user_data.phone,
        "created_at": datetime.now(),
    }
    fake_users.append(new_user)
    next_user_id += 1

    return ApiResponse(
        success=True,
        data=UserResponse(**new_user),
    )


@app.get(
    "/users",
    response_model=ApiResponse[PaginatedResponse[UserResponse]],
)
async def list_users(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
):
    """
    사용자 목록 조회 (페이지네이션).
    제네릭 모델이 중첩되어 ApiResponse[PaginatedResponse[UserResponse]] 형태이다.
    """
    total = len(fake_users)
    start = (page - 1) * size
    end = start + size
    page_items = fake_users[start:end]

    user_responses = [UserResponse(**u) for u in page_items]

    return ApiResponse(
        success=True,
        data=PaginatedResponse(**create_paginated_response(
            items=user_responses,
            total=total,
            page=page,
            page_size=size,
        )),
    )


@app.get("/users/{user_id}", response_model=ApiResponse[UserResponse])
async def get_user(user_id: int):
    """단일 사용자 조회"""
    for user in fake_users:
        if user["id"] == user_id:
            return ApiResponse(
                success=True,
                data=UserResponse(**user),
            )
    raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")


@app.get("/validation-demo")
async def validation_demo():
    """validator 체인의 동작을 보여주는 데모"""
    # 정상적인 데이터
    valid_data = {
        "username": "hong_gildong",
        "email": "hong@example.com",
        "password": "Secure1234!",
        "password_confirm": "Secure1234!",
        "birth_date": "1990-01-01",
        "phone": "010-1234-5678",
    }

    # 검증 실행
    user = UserCreate.model_validate(valid_data)

    # 직렬화 (비밀번호 마스킹 확인)
    serialized = user.model_dump()

    # 다양한 전화번호 형식 테스트
    phone_tests = [
        "010-1234-5678",   # 정상 형식
        "01012345678",     # 숫자만
        "010.1234.5678",   # 점 구분
        "(010) 1234-5678", # 괄호 포함
    ]
    normalized_phones = []
    for phone in phone_tests:
        test_data = {**valid_data, "phone": phone}
        result = UserCreate.model_validate(test_data)
        normalized_phones.append({
            "입력": phone,
            "정규화": result.phone,
        })

    return {
        "검증된_데이터": serialized,
        "전화번호_정규화_결과": normalized_phones,
        "설명": "비밀번호가 마스킹되고, 전화번호가 통일된 형식으로 변환됩니다",
    }


if __name__ == "__main__":
    import uvicorn

    print("커스텀 Validator & 제네릭 모델 서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print("검증 데모: http://localhost:8000/validation-demo")
    uvicorn.run(app, host="0.0.0.0", port=8000)
