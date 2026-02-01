# 실행 방법: uvicorn exercise:app --reload
# 챕터 05 연습 문제 - 직접 코드를 작성해보세요!

import math
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status

app = FastAPI(
    title="챕터 05 연습 문제",
    description="의존성 주입 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 페이지네이션 의존성
# Pagination 클래스를 의존성으로 사용하여 여러 엔드포인트에서 재사용
# GET /products — 상품 목록 (페이지네이션)
# GET /reviews — 리뷰 목록 (페이지네이션 + 상품 ID 필터)
# ============================================================

# 임시 데이터
PRODUCTS = [
    {"id": i, "name": f"상품_{i}", "price": i * 10000}
    for i in range(1, 21)  # 20개 상품
]

REVIEWS = [
    {"id": i, "product_id": (i % 5) + 1, "content": f"리뷰_{i}", "rating": (i % 5) + 1}
    for i in range(1, 31)  # 30개 리뷰
]


# TODO: Pagination 클래스를 정의하세요
# __init__에서 page, page_size 쿼리 파라미터를 받고 skip을 계산
# paginate(items) 메서드로 리스트에 페이지네이션 적용
# 반환: {"total": ..., "page": ..., "page_size": ..., "total_pages": ..., "items": [...]}


@app.get("/products", tags=["문제1-페이지네이션"])
def get_products(pagination=Depends()):  # TODO: Pagination 타입 힌트 추가
    """상품 목록을 조회합니다."""
    # TODO: pagination.paginate(PRODUCTS)를 사용하세요
    pass


@app.get("/reviews", tags=["문제1-페이지네이션"])
def get_reviews(
    pagination=Depends(),  # TODO: Pagination 타입 힌트 추가
    product_id: Optional[int] = Query(default=None, ge=1),
):
    """리뷰 목록을 조회합니다."""
    # TODO: product_id가 있으면 필터링 후 pagination.paginate() 사용
    pass


# ============================================================
# 문제 2: 인증 상태 확인 의존성
# verify_token → get_current_user 의존성 체인
# GET /public/info — 공개 (인증 불필요)
# GET /protected/profile — 인증 필요
# GET /protected/settings — 인증 필요
# ============================================================

# 유효한 토큰 매핑
VALID_TOKENS = {
    "token-abc-123": {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    "token-def-456": {"id": 2, "name": "김철수", "email": "kim@example.com"},
}


def verify_token(
    authorization: Optional[str] = Header(default=None),
) -> str:
    """토큰을 검증하는 의존성 (1단계)"""
    # TODO: Authorization 헤더에서 Bearer 토큰을 추출하고 유효성을 확인하세요
    # 1. 헤더가 없으면 → 401 (인증이 필요합니다)
    # 2. "Bearer "로 시작하지 않으면 → 401
    # 3. 토큰이 VALID_TOKENS에 없으면 → 401
    # 4. 유효하면 토큰 문자열 반환
    pass


def get_current_user(
    token: str = Depends(verify_token),
) -> dict:
    """현재 사용자를 조회하는 의존성 (2단계)"""
    # TODO: 검증된 토큰으로 VALID_TOKENS에서 사용자 정보를 반환하세요
    pass


@app.get("/public/info", tags=["문제2-인증"])
def public_info():
    """공개 엔드포인트 — 인증 불필요"""
    return {"message": "이 엔드포인트는 누구나 접근할 수 있습니다"}


@app.get("/protected/profile", tags=["문제2-인증"])
def get_profile(current_user: dict = Depends(get_current_user)):
    """사용자 프로필 — 인증 필요"""
    # TODO: 현재 사용자 정보를 반환하세요
    pass


@app.get("/protected/settings", tags=["문제2-인증"])
def get_settings(current_user: dict = Depends(get_current_user)):
    """사용자 설정 — 인증 필요"""
    # TODO: 사용자 이름과 설정 정보를 반환하세요
    pass


# ============================================================
# 문제 3: 중첩 의존성 체인
# get_database → get_authenticated_user → require_role(역할)
# GET /dashboard — 모든 인증된 사용자
# GET /admin/panel — admin 역할만
# GET /editor/posts — editor 역할만
# ============================================================

USERS_DB = {
    "admin": {"id": 1, "name": "관리자", "password": "admin123", "role": "admin"},
    "editor1": {"id": 2, "name": "편집자", "password": "edit123", "role": "editor"},
    "user1": {"id": 3, "name": "일반사용자", "password": "user123", "role": "user"},
}


def get_database() -> dict:
    """1단계 의존성: 데이터베이스 연결"""
    # TODO: 데이터베이스 상태와 사용자 데이터를 반환하세요
    pass


def get_authenticated_user(
    username: str = Query(..., description="사용자명"),
    password: str = Query(..., description="비밀번호"),
    db: dict = Depends(get_database),
) -> dict:
    """2단계 의존성: 사용자 인증"""
    # TODO: DB에서 사용자를 조회하고 비밀번호를 검증하세요
    # 사용자 없음 → 401, 비밀번호 불일치 → 401
    # 성공 시 비밀번호를 제외한 사용자 정보 반환
    pass


def require_role(required_role: str):
    """3단계 의존성 팩토리: 역할 기반 권한 확인"""
    # TODO: 내부 함수 role_checker를 정의하세요
    # get_authenticated_user에 의존하여 사용자의 역할을 확인
    # 역할 불일치 시 403 에러
    pass


@app.get("/dashboard", tags=["문제3-의존성체인"])
def get_dashboard(user: dict = Depends(get_authenticated_user)):
    """대시보드 — 모든 인증된 사용자 접근 가능
    테스트: GET /dashboard?username=admin&password=admin123
    """
    # TODO: 환영 메시지와 사용자 정보를 반환하세요
    pass


@app.get("/admin/panel", tags=["문제3-의존성체인"])
def admin_panel(admin: dict = Depends(require_role("admin"))):
    """관리자 패널 — admin 역할만 접근 가능"""
    # TODO: 관리자 패널 정보를 반환하세요
    pass


@app.get("/editor/posts", tags=["문제3-의존성체인"])
def editor_posts(editor: dict = Depends(require_role("editor"))):
    """편집자 게시글 관리 — editor 역할만 접근 가능"""
    # TODO: 편집자 페이지 정보를 반환하세요
    pass
