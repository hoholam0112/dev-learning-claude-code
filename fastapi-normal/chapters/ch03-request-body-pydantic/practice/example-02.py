# 실행 방법: uvicorn example-02:app --reload
# 중첩 모델 예제 - 주소가 포함된 사용자 프로필

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="중첩 모델 예제", description="Pydantic 중첩 모델 활용")

# ============================================================
# 중첩 Pydantic 모델 정의
# ============================================================


class Address(BaseModel):
    """주소 모델"""

    city: str = Field(..., description="도시", examples=["서울"])
    district: str = Field(..., description="구/군", examples=["강남구"])
    detail: str = Field(..., description="상세 주소", examples=["테헤란로 123"])
    zip_code: str = Field(
        ...,
        pattern=r"^\d{5}$",
        description="우편번호 (5자리 숫자)",
        examples=["06100"],
    )


class SocialLink(BaseModel):
    """소셜 미디어 링크 모델"""

    platform: str = Field(..., description="플랫폼명", examples=["github"])
    url: str = Field(..., description="프로필 URL", examples=["https://github.com/user"])


class UserProfile(BaseModel):
    """사용자 프로필 모델 (중첩 모델 포함)"""

    name: str = Field(..., min_length=2, max_length=50, description="이름")
    email: str = Field(..., description="이메일")
    age: int = Field(..., ge=0, le=150, description="나이")

    # 중첩 모델: 단일 객체
    address: Address = Field(..., description="주소 정보")

    # 중첩 모델: 리스트
    social_links: List[SocialLink] = Field(
        default=[],
        description="소셜 미디어 링크 목록",
    )

    # 선택적 필드
    phone: Optional[str] = Field(default=None, description="전화번호")
    hobbies: List[str] = Field(default=[], description="취미 목록")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "홍길동",
                    "email": "hong@example.com",
                    "age": 25,
                    "address": {
                        "city": "서울",
                        "district": "강남구",
                        "detail": "테헤란로 123",
                        "zip_code": "06100",
                    },
                    "social_links": [
                        {
                            "platform": "github",
                            "url": "https://github.com/honggildong",
                        }
                    ],
                    "phone": "010-1234-5678",
                    "hobbies": ["코딩", "독서"],
                }
            ]
        }
    }


# ============================================================
# 임시 저장소
# ============================================================

profiles_db: dict[int, dict] = {}
next_id: int = 1


# ============================================================
# API 엔드포인트
# ============================================================


@app.post("/profiles", tags=["프로필"])
def create_profile(profile: UserProfile):
    """사용자 프로필을 생성합니다.

    중첩 모델(주소, 소셜 링크)을 포함한 복잡한 데이터를 처리합니다.
    모든 중첩 모델도 자동으로 검증됩니다.
    """
    global next_id

    profile_data = {"id": next_id, **profile.model_dump()}
    profiles_db[next_id] = profile_data
    next_id += 1

    return {
        "message": f"{profile.name}님의 프로필이 생성되었습니다",
        "profile": profile_data,
    }


@app.get("/profiles", tags=["프로필"])
def get_profiles():
    """전체 프로필 목록을 반환합니다."""
    return {"total": len(profiles_db), "profiles": list(profiles_db.values())}


@app.get("/profiles/{profile_id}", tags=["프로필"])
def get_profile(profile_id: int):
    """특정 프로필을 조회합니다."""
    if profile_id not in profiles_db:
        return {"error": "프로필을 찾을 수 없습니다"}
    return profiles_db[profile_id]


@app.put("/profiles/{profile_id}/address", tags=["프로필"])
def update_address(profile_id: int, address: Address):
    """프로필의 주소만 업데이트합니다.

    중첩 모델을 독립적으로 받아 처리하는 예제입니다.
    """
    if profile_id not in profiles_db:
        return {"error": "프로필을 찾을 수 없습니다"}

    profiles_db[profile_id]["address"] = address.model_dump()
    return {
        "message": "주소가 업데이트되었습니다",
        "address": address.model_dump(),
    }


@app.post("/profiles/{profile_id}/social-links", tags=["프로필"])
def add_social_link(profile_id: int, link: SocialLink):
    """프로필에 소셜 링크를 추가합니다.

    중첩 모델의 리스트에 항목을 추가하는 예제입니다.
    """
    if profile_id not in profiles_db:
        return {"error": "프로필을 찾을 수 없습니다"}

    profiles_db[profile_id]["social_links"].append(link.model_dump())
    return {
        "message": f"{link.platform} 링크가 추가되었습니다",
        "social_links": profiles_db[profile_id]["social_links"],
    }
