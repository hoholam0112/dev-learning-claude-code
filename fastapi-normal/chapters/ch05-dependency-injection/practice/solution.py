# 실행 방법: uvicorn solution:app --reload
# 챕터 05 연습 문제 모범 답안

import math
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status

app = FastAPI(
    title="챕터 05 연습 문제 답안",
    description="의존성 주입 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 페이지네이션 의존성
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


class Pagination:
    """페이지네이션 의존성 클래스

    여러 엔드포인트에서 재사용할 수 있는 페이지네이션 로직을 캡슐화합니다.
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="페이지 번호"),
        page_size: int = Query(default=10, ge=1, le=50, description="페이지 크기"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size

    def paginate(self, items: list) -> dict:
        """리스트에 페이지네이션을 적용하고 결과를 반환합니다."""
        total = len(items)
        total_pages = math.ceil(total / self.page_size) if total > 0 else 1
        paginated_items = items[self.skip : self.skip + self.page_size]

        return {
            "total": total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": total_pages,
            "items": paginated_items,
        }


@app.get("/products", tags=["문제1-페이지네이션"])
def get_products(pagination: Pagination = Depends()):
    """상품 목록을 조회합니다.

    Pagination 의존성으로 페이지네이션을 처리합니다.
    """
    return pagination.paginate(PRODUCTS)


@app.get("/reviews", tags=["문제1-페이지네이션"])
def get_reviews(
    pagination: Pagination = Depends(),
    product_id: Optional[int] = Query(default=None, ge=1, description="상품 ID 필터"),
):
    """리뷰 목록을 조회합니다.

    동일한 Pagination 의존성을 재사용합니다.
    """
    result = REVIEWS.copy()

    # 상품 ID 필터링
    if product_id is not None:
        result = [r for r in result if r["product_id"] == product_id]

    return pagination.paginate(result)


# ============================================================
# 문제 2: 인증 상태 확인 의존성
# ============================================================

# 유효한 토큰 매핑 (실제로는 DB에서 조회)
VALID_TOKENS = {
    "token-abc-123": {"id": 1, "name": "홍길동", "email": "hong@example.com"},
    "token-def-456": {"id": 2, "name": "김철수", "email": "kim@example.com"},
}


def verify_token(
    authorization: Optional[str] = Header(default=None, description="Bearer 토큰"),
) -> str:
    """토큰을 검증하는 의존성 (1단계)

    Authorization 헤더에서 Bearer 토큰을 추출하고 유효성을 확인합니다.
    """
    # 헤더 존재 확인
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Bearer 형식 확인
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="올바른 인증 형식이 아닙니다. 'Bearer <토큰>' 형식을 사용하세요",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰 추출
    token = authorization.replace("Bearer ", "")

    # 토큰 유효성 확인
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


def get_current_user(
    token: str = Depends(verify_token),  # verify_token에 의존
) -> dict:
    """현재 사용자를 조회하는 의존성 (2단계)

    검증된 토큰으로 사용자 정보를 반환합니다.
    """
    return VALID_TOKENS[token]


@app.get("/public/info", tags=["문제2-인증"])
def public_info():
    """공개 엔드포인트 - 인증이 필요하지 않습니다."""
    return {
        "message": "이 엔드포인트는 누구나 접근할 수 있습니다",
        "tip": "인증이 필요한 엔드포인트에는 Authorization 헤더가 필요합니다",
    }


@app.get("/protected/profile", tags=["문제2-인증"])
def get_profile(current_user: dict = Depends(get_current_user)):
    """사용자 프로필 - 인증 필요

    테스트: Authorization 헤더에 'Bearer token-abc-123'을 설정하세요.
    """
    return {"user": current_user}


@app.get("/protected/settings", tags=["문제2-인증"])
def get_settings(current_user: dict = Depends(get_current_user)):
    """사용자 설정 - 인증 필요

    동일한 get_current_user 의존성을 재사용합니다.
    """
    return {
        "user": current_user["name"],
        "settings": {
            "theme": "dark",
            "language": "ko",
            "notifications": True,
        },
    }


# ============================================================
# 문제 3: 중첩 의존성 체인
# ============================================================

# 사용자 데이터 (DB 시뮬레이션)
USERS_DB = {
    "admin": {"id": 1, "name": "관리자", "password": "admin123", "role": "admin"},
    "editor1": {"id": 2, "name": "편집자", "password": "edit123", "role": "editor"},
    "user1": {"id": 3, "name": "일반사용자", "password": "user123", "role": "user"},
}


def get_database() -> dict:
    """1단계 의존성: 데이터베이스 연결

    데이터베이스 연결 정보를 반환합니다.
    실제 애플리케이션에서는 DB 세션을 생성하고 yield로 반환합니다.
    """
    return {
        "status": "connected",
        "connected_at": datetime.now().isoformat(),
        "users": USERS_DB,
    }


def get_authenticated_user(
    username: str = Query(..., description="사용자명"),
    password: str = Query(..., description="비밀번호"),
    db: dict = Depends(get_database),  # get_database에 의존
) -> dict:
    """2단계 의존성: 사용자 인증

    DB에서 사용자를 조회하고 비밀번호를 검증합니다.
    """
    users = db["users"]

    # 사용자 존재 확인
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="존재하지 않는 사용자입니다",
        )

    user = users[username]

    # 비밀번호 확인
    if user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 일치하지 않습니다",
        )

    # 비밀번호를 제외한 사용자 정보 반환
    return {
        "id": user["id"],
        "name": user["name"],
        "role": user["role"],
        "db_status": db["status"],
    }


def require_role(required_role: str):
    """3단계 의존성 팩토리: 역할 기반 권한 확인

    특정 역할을 가진 사용자만 접근을 허용하는 의존성을 생성합니다.

    사용법:
        Depends(require_role("admin"))
        Depends(require_role("editor"))
    """

    def role_checker(
        user: dict = Depends(get_authenticated_user),  # get_authenticated_user에 의존
    ) -> dict:
        if user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role} 역할이 필요합니다 (현재: {user['role']})",
            )
        return user

    return role_checker


@app.get("/dashboard", tags=["문제3-의존성체인"])
def get_dashboard(user: dict = Depends(get_authenticated_user)):
    """대시보드 - 모든 인증된 사용자 접근 가능

    2단계 의존성 체인: get_authenticated_user → get_database

    테스트: GET /dashboard?username=admin&password=admin123
    """
    return {
        "message": f"환영합니다, {user['name']}님!",
        "role": user["role"],
        "db_status": user["db_status"],
    }


@app.get("/admin/panel", tags=["문제3-의존성체인"])
def admin_panel(admin: dict = Depends(require_role("admin"))):
    """관리자 패널 - admin 역할만 접근 가능

    3단계 의존성 체인: require_role("admin") → get_authenticated_user → get_database

    테스트 (성공): GET /admin/panel?username=admin&password=admin123
    테스트 (실패): GET /admin/panel?username=editor1&password=edit123
    """
    return {
        "message": f"관리자 패널에 오신 것을 환영합니다, {admin['name']}님!",
        "admin_tools": ["사용자 관리", "시스템 설정", "로그 조회"],
    }


@app.get("/editor/posts", tags=["문제3-의존성체인"])
def editor_posts(editor: dict = Depends(require_role("editor"))):
    """편집자 게시글 관리 - editor 역할만 접근 가능

    동일한 require_role 팩토리를 다른 역할로 재사용합니다.

    테스트 (성공): GET /editor/posts?username=editor1&password=edit123
    테스트 (실패): GET /editor/posts?username=admin&password=admin123
    """
    return {
        "message": f"편집자 페이지입니다, {editor['name']}님!",
        "posts": [
            {"id": 1, "title": "작성 중인 기사", "status": "draft"},
            {"id": 2, "title": "검토 대기 기사", "status": "pending"},
        ],
    }
