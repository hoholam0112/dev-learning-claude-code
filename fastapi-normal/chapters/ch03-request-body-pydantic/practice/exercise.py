# 실행 방법: uvicorn exercise:app --reload
# 챕터 03 연습 문제 - 직접 코드를 작성해보세요!

from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="챕터 03 연습 문제",
    description="요청 본문과 Pydantic 모델 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 상품 등록 API
# POST /products — 상품 등록
# GET /products — 전체 상품 목록
# GET /products/{product_id} — 특정 상품 조회
# ============================================================


# TODO: ProductCreate 모델을 정의하세요
# - name (str): 필수, 1~100자
# - price (int): 필수, 100 이상
# - description (Optional[str]): 선택적, 최대 500자
# - category (str): 필수
# - in_stock (bool): 기본값 True


# 상품 저장소
products_db: dict[int, dict] = {}
product_next_id: int = 1


@app.post("/products", tags=["문제1-상품"])
def create_product(product):  # TODO: 파라미터 타입을 ProductCreate로 지정하세요
    """상품을 등록합니다."""
    # TODO: 상품을 products_db에 저장하고 결과를 반환하세요
    # 힌트: global product_next_id, product.model_dump()
    pass


@app.get("/products", tags=["문제1-상품"])
def get_products():
    """전체 상품 목록을 조회합니다."""
    # TODO: products_db의 전체 상품 목록을 반환하세요
    pass


@app.get("/products/{product_id}", tags=["문제1-상품"])
def get_product(product_id: int):
    """특정 상품을 조회합니다."""
    # TODO: product_id가 없으면 에러 메시지를, 있으면 해당 상품을 반환하세요
    pass


# ============================================================
# 문제 2: 주문 생성 API
# 중첩 모델 활용: OrderItem → OrderCreate
# POST /orders — 주문 생성 (총 금액 자동 계산)
# GET /orders — 전체 주문 목록
# GET /orders/{order_id} — 특정 주문 조회
# ============================================================


# TODO: OrderItem 모델을 정의하세요
# - product_name (str): 상품명
# - quantity (int): 수량, 1 이상
# - unit_price (int): 단가, 100 이상


# TODO: OrderCreate 모델을 정의하세요
# - customer_name (str): 고객명
# - items (List[OrderItem]): 주문 항목 리스트, 1개 이상
# - note (Optional[str]): 선택적, 배송 메모, 최대 200자


# 주문 저장소
orders_db: dict[int, dict] = {}
order_next_id: int = 1


@app.post("/orders", tags=["문제2-주문"])
def create_order(order):  # TODO: 파라미터 타입을 OrderCreate로 지정하세요
    """주문을 생성합니다. 총 금액을 자동 계산합니다."""
    # TODO: 총 금액 계산 후 주문을 orders_db에 저장하세요
    # 힌트: sum(item.quantity * item.unit_price for item in order.items)
    pass


@app.get("/orders", tags=["문제2-주문"])
def get_orders():
    """전체 주문 목록을 조회합니다."""
    # TODO: orders_db의 전체 주문 목록을 반환하세요
    pass


@app.get("/orders/{order_id}", tags=["문제2-주문"])
def get_order(order_id: int):
    """특정 주문을 조회합니다."""
    # TODO: order_id가 없으면 에러 메시지를, 있으면 해당 주문을 반환하세요
    pass


# ============================================================
# 문제 3: 필드 유효성 검증 (회원가입)
# POST /signup — 회원가입
# 유효성 검증 실패 시 422 자동 반환
# 성공 시 비밀번호를 제외한 정보 반환
# ============================================================


# TODO: SignupRequest 모델을 정의하세요
# - username (str): 필수, 3~20자, 영문+숫자만 (pattern=r"^[a-zA-Z0-9]+$")
# - email (str): 필수, 이메일 형식 (pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
# - password (str): 필수, 8~100자
# - age (int): 필수, 14~120
# - nickname (Optional[str]): 선택적, 2~30자


# 회원 저장소
members_db: dict[int, dict] = {}
member_next_id: int = 1


@app.post("/signup", tags=["문제3-회원가입"])
def signup(request):  # TODO: 파라미터 타입을 SignupRequest로 지정하세요
    """회원가입을 처리합니다. 비밀번호를 제외한 정보를 반환합니다."""
    # TODO: 비밀번호를 제외한 사용자 정보를 반환하세요
    # 힌트: request.model_dump(exclude={"password"})
    pass


# ============================================================
# 문제 4: 선택적 필드를 가진 프로필 업데이트 API
# POST /profiles — 프로필 생성
# PATCH /profiles/{profile_id} — 프로필 부분 수정 (전달된 필드만 수정)
# GET /profiles/{profile_id} — 프로필 조회
# ============================================================


# TODO: ProfileCreate 모델을 정의하세요 (생성용 - 대부분 필수 필드)
# - name (str): 필수
# - email (str): 필수
# - age (int): 필수
# - bio (Optional[str]): 선택적
# - website (Optional[str]): 선택적


# TODO: ProfileUpdate 모델을 정의하세요 (수정용 - 모든 필드 선택적)
# - name, email, age, bio, website 모두 Optional


# 프로필 저장소
profiles_db: dict[int, dict] = {}
profile_next_id: int = 1


@app.post("/profiles", tags=["문제4-프로필"])
def create_profile(profile):  # TODO: 파라미터 타입을 ProfileCreate로 지정하세요
    """프로필을 생성합니다."""
    # TODO: 프로필을 profiles_db에 저장하고 반환하세요
    pass


@app.patch("/profiles/{profile_id}", tags=["문제4-프로필"])
def update_profile(profile_id: int, profile):  # TODO: 파라미터 타입을 ProfileUpdate로 지정하세요
    """프로필을 부분 수정합니다. 전달된 필드만 업데이트됩니다."""
    # TODO: exclude_unset=True로 전달된 필드만 추출 후 업데이트하세요
    # 힌트: profile.model_dump(exclude_unset=True)
    pass


@app.get("/profiles/{profile_id}", tags=["문제4-프로필"])
def get_profile(profile_id: int):
    """프로필을 조회합니다."""
    # TODO: profile_id가 없으면 에러 메시지를, 있으면 해당 프로필을 반환하세요
    pass
