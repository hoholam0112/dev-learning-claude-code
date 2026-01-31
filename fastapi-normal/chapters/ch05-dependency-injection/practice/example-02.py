# 실행 방법: uvicorn example-02:app --reload
# 클래스 기반 의존성과 하위 의존성 예제

from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query, status

app = FastAPI(title="클래스 의존성 예제", description="클래스 기반 DI와 하위 의존성")

# ============================================================
# 클래스 기반 의존성
# ============================================================


class Pagination:
    """페이지네이션 의존성 클래스

    클래스를 의존성으로 사용하면 인스턴스 속성에 접근할 수 있어
    IDE 자동완성과 타입 체크가 향상됩니다.
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="페이지 번호"),
        page_size: int = Query(default=10, ge=1, le=50, description="페이지 크기"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size


class DateRangeFilter:
    """날짜 범위 필터 의존성 클래스"""

    def __init__(
        self,
        start_date: str = Query(
            default=None,
            description="시작 날짜 (YYYY-MM-DD)",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
        end_date: str = Query(
            default=None,
            description="종료 날짜 (YYYY-MM-DD)",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ):
        self.start_date = start_date
        self.end_date = end_date

        # 날짜 파싱 (유효한 경우)
        self.start = (
            datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        )
        self.end = (
            datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        )


# ============================================================
# 하위 의존성 체인
# ============================================================


def get_api_key(
    api_key: str = Query(..., description="API 키"),
):
    """1단계 의존성: API 키 검증

    유효한 API 키인지 확인합니다.
    """
    valid_keys = {"key-123", "key-456", "admin-key-789"}
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 API 키입니다",
        )
    return api_key


def get_current_user(
    api_key: str = Depends(get_api_key),  # get_api_key에 의존
):
    """2단계 의존성: 현재 사용자 조회

    API 키를 기반으로 사용자 정보를 반환합니다.
    get_api_key 의존성이 먼저 실행됩니다.
    """
    # API 키에 따른 사용자 매핑 (실제로는 DB 조회)
    user_map = {
        "key-123": {"id": 1, "name": "홍길동", "role": "user"},
        "key-456": {"id": 2, "name": "김철수", "role": "user"},
        "admin-key-789": {"id": 3, "name": "관리자", "role": "admin"},
    }
    return user_map.get(api_key, {"id": 0, "name": "알 수 없음", "role": "guest"})


def require_admin(
    current_user: dict = Depends(get_current_user),  # get_current_user에 의존
):
    """3단계 의존성: 관리자 권한 확인

    현재 사용자가 관리자인지 확인합니다.
    get_current_user → get_api_key 순서로 의존성 체인이 해결됩니다.
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return current_user


# ============================================================
# 임시 데이터
# ============================================================

LOGS = [
    {"id": 1, "action": "로그인", "user": "홍길동", "date": "2024-01-15"},
    {"id": 2, "action": "상품 등록", "user": "김철수", "date": "2024-01-16"},
    {"id": 3, "action": "결제", "user": "홍길동", "date": "2024-02-01"},
    {"id": 4, "action": "로그인", "user": "이영희", "date": "2024-02-10"},
    {"id": 5, "action": "상품 수정", "user": "김철수", "date": "2024-03-01"},
]

ITEMS = [
    {"id": 1, "name": "노트북", "price": 1200000},
    {"id": 2, "name": "키보드", "price": 89000},
    {"id": 3, "name": "마우스", "price": 45000},
]

# ============================================================
# API 엔드포인트
# ============================================================


@app.get("/logs", tags=["로그"])
def get_logs(
    pagination: Pagination = Depends(),
    date_filter: DateRangeFilter = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """활동 로그를 조회합니다.

    - 클래스 의존성: Pagination, DateRangeFilter
    - 함수 의존성: get_current_user (get_api_key에 의존)

    테스트: GET /logs?api_key=key-123&page=1&page_size=5
    """
    result = LOGS.copy()

    # 날짜 필터 적용
    if date_filter.start:
        result = [
            log for log in result
            if datetime.strptime(log["date"], "%Y-%m-%d") >= date_filter.start
        ]
    if date_filter.end:
        result = [
            log for log in result
            if datetime.strptime(log["date"], "%Y-%m-%d") <= date_filter.end
        ]

    total = len(result)
    paginated = result[pagination.skip : pagination.skip + pagination.page_size]

    return {
        "current_user": current_user["name"],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "logs": paginated,
    }


@app.get("/items", tags=["아이템"])
def get_items(
    pagination: Pagination = Depends(),
    current_user: dict = Depends(get_current_user),
):
    """아이템 목록을 조회합니다.

    일반 사용자도 접근 가능한 엔드포인트입니다.

    테스트: GET /items?api_key=key-123
    """
    total = len(ITEMS)
    paginated = ITEMS[pagination.skip : pagination.skip + pagination.page_size]

    return {
        "current_user": current_user["name"],
        "total": total,
        "items": paginated,
    }


@app.get("/admin/dashboard", tags=["관리자"])
def admin_dashboard(
    admin: dict = Depends(require_admin),
):
    """관리자 대시보드를 반환합니다.

    3단계 의존성 체인: require_admin → get_current_user → get_api_key
    관리자만 접근 가능합니다.

    테스트 (성공): GET /admin/dashboard?api_key=admin-key-789
    테스트 (실패): GET /admin/dashboard?api_key=key-123 → 403 에러
    """
    return {
        "message": f"환영합니다, {admin['name']}님!",
        "role": admin["role"],
        "stats": {
            "total_users": 5,
            "total_items": len(ITEMS),
            "total_logs": len(LOGS),
        },
    }


@app.delete("/admin/logs", tags=["관리자"])
def clear_logs(admin: dict = Depends(require_admin)):
    """로그를 초기화합니다. 관리자만 가능합니다.

    테스트: DELETE /admin/logs?api_key=admin-key-789
    """
    LOGS.clear()
    return {"message": "모든 로그가 삭제되었습니다", "admin": admin["name"]}
