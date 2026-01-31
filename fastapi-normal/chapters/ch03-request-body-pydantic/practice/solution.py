# 실행 방법: uvicorn solution:app --reload
# 챕터 03 연습 문제 모범 답안

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="챕터 03 연습 문제 답안",
    description="요청 본문과 Pydantic 모델 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 상품 등록 API
# ============================================================


class ProductCreate(BaseModel):
    """상품 생성 요청 모델"""

    name: str = Field(..., min_length=1, max_length=100, description="상품명")
    price: int = Field(..., ge=100, description="가격 (100원 이상)")
    description: Optional[str] = Field(
        default=None, max_length=500, description="상품 설명"
    )
    category: str = Field(..., description="카테고리")
    in_stock: bool = Field(default=True, description="재고 여부")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "무선 키보드",
                    "price": 89000,
                    "description": "블루투스 5.0 지원",
                    "category": "electronics",
                    "in_stock": True,
                }
            ]
        }
    }


# 상품 저장소
products_db: dict[int, dict] = {}
product_next_id: int = 1


@app.post("/products", tags=["문제1-상품"])
def create_product(product: ProductCreate):
    """상품을 등록합니다."""
    global product_next_id

    product_data = {"id": product_next_id, **product.model_dump()}
    products_db[product_next_id] = product_data
    product_next_id += 1

    return {"message": "상품이 등록되었습니다", "product": product_data}


@app.get("/products", tags=["문제1-상품"])
def get_products():
    """전체 상품 목록을 조회합니다."""
    return {"total": len(products_db), "products": list(products_db.values())}


@app.get("/products/{product_id}", tags=["문제1-상품"])
def get_product(product_id: int):
    """특정 상품을 조회합니다."""
    if product_id not in products_db:
        return {"error": "상품을 찾을 수 없습니다"}
    return products_db[product_id]


# ============================================================
# 문제 2: 주문 생성 API
# ============================================================


class OrderItem(BaseModel):
    """주문 항목 모델"""

    product_name: str = Field(..., description="상품명")
    quantity: int = Field(..., ge=1, description="수량 (1개 이상)")
    unit_price: int = Field(..., ge=100, description="단가 (100원 이상)")


class OrderCreate(BaseModel):
    """주문 생성 요청 모델"""

    customer_name: str = Field(..., min_length=2, description="고객명")
    items: List[OrderItem] = Field(
        ..., min_length=1, description="주문 항목 (1개 이상)"
    )
    note: Optional[str] = Field(
        default=None, max_length=200, description="배송 메모"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "customer_name": "홍길동",
                    "items": [
                        {
                            "product_name": "노트북",
                            "quantity": 1,
                            "unit_price": 1200000,
                        },
                        {
                            "product_name": "마우스",
                            "quantity": 2,
                            "unit_price": 45000,
                        },
                    ],
                    "note": "부재 시 경비실에 맡겨주세요",
                }
            ]
        }
    }


# 주문 저장소
orders_db: dict[int, dict] = {}
order_next_id: int = 1


@app.post("/orders", tags=["문제2-주문"])
def create_order(order: OrderCreate):
    """주문을 생성합니다.

    주문 항목의 수량 * 단가를 합산하여 총 금액을 자동 계산합니다.
    """
    global order_next_id

    # 총 금액 계산
    total_price = sum(item.quantity * item.unit_price for item in order.items)

    order_data = {
        "id": order_next_id,
        **order.model_dump(),
        "total_price": total_price,
    }
    orders_db[order_next_id] = order_data
    order_next_id += 1

    return {"message": "주문이 생성되었습니다", "order": order_data}


@app.get("/orders", tags=["문제2-주문"])
def get_orders():
    """전체 주문 목록을 조회합니다."""
    return {"total": len(orders_db), "orders": list(orders_db.values())}


@app.get("/orders/{order_id}", tags=["문제2-주문"])
def get_order(order_id: int):
    """특정 주문을 조회합니다."""
    if order_id not in orders_db:
        return {"error": "주문을 찾을 수 없습니다"}
    return orders_db[order_id]


# ============================================================
# 문제 3: 필드 유효성 검증 (회원가입)
# ============================================================


class SignupRequest(BaseModel):
    """회원가입 요청 모델"""

    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9]+$",
        description="사용자명 (영문+숫자, 3~20자)",
    )
    email: str = Field(
        ...,
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        description="이메일 주소",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="비밀번호 (8~100자)",
    )
    age: int = Field(..., ge=14, le=120, description="나이 (14~120)")
    nickname: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=30,
        description="닉네임 (선택, 2~30자)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "hong123",
                    "email": "hong@example.com",
                    "password": "securePass123",
                    "age": 25,
                    "nickname": "길동이",
                }
            ]
        }
    }


# 회원 저장소
members_db: dict[int, dict] = {}
member_next_id: int = 1


@app.post("/signup", tags=["문제3-회원가입"])
def signup(request: SignupRequest):
    """회원가입을 처리합니다.

    유효성 검증 통과 후, 비밀번호를 제외한 정보를 반환합니다.
    """
    global member_next_id

    # 비밀번호를 제외한 사용자 정보 생성
    user_data = {
        "id": member_next_id,
        **request.model_dump(exclude={"password"}),
    }
    # 내부 저장소에는 비밀번호 포함하여 저장 (실제로는 해시화 필요)
    members_db[member_next_id] = {
        "id": member_next_id,
        **request.model_dump(),
    }
    member_next_id += 1

    return {"message": "회원가입이 완료되었습니다", "user": user_data}


# ============================================================
# 문제 4: 선택적 필드를 가진 프로필 업데이트 API
# ============================================================


class ProfileCreate(BaseModel):
    """프로필 생성 요청 모델"""

    name: str = Field(..., min_length=2, max_length=50, description="이름")
    email: str = Field(..., description="이메일")
    age: int = Field(..., ge=0, le=150, description="나이")
    bio: Optional[str] = Field(
        default=None, max_length=300, description="자기소개"
    )
    website: Optional[str] = Field(default=None, description="웹사이트 URL")


class ProfileUpdate(BaseModel):
    """프로필 수정 요청 모델 - 모든 필드가 선택적"""

    name: Optional[str] = Field(
        default=None, min_length=2, max_length=50, description="이름"
    )
    email: Optional[str] = Field(default=None, description="이메일")
    age: Optional[int] = Field(default=None, ge=0, le=150, description="나이")
    bio: Optional[str] = Field(
        default=None, max_length=300, description="자기소개"
    )
    website: Optional[str] = Field(default=None, description="웹사이트 URL")


# 프로필 저장소
profiles_db: dict[int, dict] = {}
profile_next_id: int = 1


@app.post("/profiles", tags=["문제4-프로필"])
def create_profile(profile: ProfileCreate):
    """프로필을 생성합니다."""
    global profile_next_id

    profile_data = {"id": profile_next_id, **profile.model_dump()}
    profiles_db[profile_next_id] = profile_data
    profile_next_id += 1

    return {"message": "프로필이 생성되었습니다", "profile": profile_data}


@app.patch("/profiles/{profile_id}", tags=["문제4-프로필"])
def update_profile(profile_id: int, profile: ProfileUpdate):
    """프로필을 부분 수정합니다.

    전달된 필드만 업데이트됩니다.
    exclude_unset=True 옵션으로 요청에 포함된 필드만 추출합니다.
    """
    if profile_id not in profiles_db:
        return {"error": "프로필을 찾을 수 없습니다"}

    # 실제로 전달된 필드만 추출 (None 포함, 미전달 필드 제외)
    update_data = profile.model_dump(exclude_unset=True)

    # 전달된 필드만 업데이트
    for key, value in update_data.items():
        profiles_db[profile_id][key] = value

    return {"message": "프로필이 수정되었습니다", "profile": profiles_db[profile_id]}


@app.get("/profiles/{profile_id}", tags=["문제4-프로필"])
def get_profile(profile_id: int):
    """프로필을 조회합니다."""
    if profile_id not in profiles_db:
        return {"error": "프로필을 찾을 수 없습니다"}
    return profiles_db[profile_id]
