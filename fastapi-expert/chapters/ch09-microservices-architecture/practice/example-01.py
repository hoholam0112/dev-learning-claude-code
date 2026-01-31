# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn
"""
서브 앱 마운트와 API 버전 관리 예제.

주요 학습 포인트:
- FastAPI 서브 애플리케이션으로 모듈화
- URL 기반 API 버전 관리 (v1, v2)
- 하위 호환성 유지 전략
- 공유 의존성과 서브 앱별 독립 의존성
- API 게이트웨이 패턴 (간단한 프록시)
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ──────────────────────────────────────────────
# 1. 공유 모델 및 데이터 저장소
# ──────────────────────────────────────────────
# 시뮬레이션용 인메모리 데이터
users_db: dict[int, dict] = {
    1: {"id": 1, "name": "홍길동", "email": "hong@test.com", "role": "admin", "department": "개발팀"},
    2: {"id": 2, "name": "김철수", "email": "kim@test.com", "role": "user", "department": "기획팀"},
    3: {"id": 3, "name": "이영희", "email": "lee@test.com", "role": "user", "department": "디자인팀"},
}

orders_db: dict[int, dict] = {
    1: {"id": 1, "user_id": 1, "product": "노트북", "amount": 1500000, "status": "completed"},
    2: {"id": 2, "user_id": 2, "product": "키보드", "amount": 150000, "status": "pending"},
    3: {"id": 3, "user_id": 1, "product": "마우스", "amount": 80000, "status": "shipping"},
}


# ──────────────────────────────────────────────
# 2. API v1 (기본 버전)
# ──────────────────────────────────────────────
class UserResponseV1(BaseModel):
    """v1: 기본 사용자 정보만 반환"""
    id: int
    name: str
    email: str


class OrderResponseV1(BaseModel):
    """v1: 기본 주문 정보"""
    id: int
    product: str
    amount: int
    status: str


v1_router = APIRouter(prefix="/api/v1", tags=["API v1"])


@v1_router.get("/users", response_model=list[UserResponseV1])
async def list_users_v1():
    """[v1] 사용자 목록 조회"""
    return [
        UserResponseV1(id=u["id"], name=u["name"], email=u["email"])
        for u in users_db.values()
    ]


@v1_router.get("/users/{user_id}", response_model=UserResponseV1)
async def get_user_v1(user_id: int):
    """[v1] 사용자 상세 조회"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다")
    return UserResponseV1(id=user["id"], name=user["name"], email=user["email"])


@v1_router.get("/orders", response_model=list[OrderResponseV1])
async def list_orders_v1():
    """[v1] 주문 목록 조회"""
    return [OrderResponseV1(**o) for o in orders_db.values()]


# ──────────────────────────────────────────────
# 3. API v2 (확장 버전 - 하위 호환 유지)
# ──────────────────────────────────────────────
class UserResponseV2(BaseModel):
    """v2: 확장된 사용자 정보 (role, department 추가)"""
    id: int
    name: str
    email: str
    role: str          # v2에서 추가
    department: str    # v2에서 추가


class OrderResponseV2(BaseModel):
    """v2: 확장된 주문 정보 (user_name 추가, 중첩 구조)"""
    id: int
    product: str
    amount: int
    status: str
    user: UserResponseV1  # v2: 사용자 정보 중첩


class PaginatedResponse(BaseModel):
    """v2: 페이징 응답 래퍼"""
    items: list
    total: int
    page: int
    size: int
    has_next: bool


v2_router = APIRouter(prefix="/api/v2", tags=["API v2"])


@v2_router.get("/users", response_model=PaginatedResponse)
async def list_users_v2(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    role: Optional[str] = None,
):
    """
    [v2] 사용자 목록 (페이징 + 필터 추가).
    v1과의 차이: 페이징 래퍼, role 필터 추가
    """
    items = list(users_db.values())
    if role:
        items = [u for u in items if u["role"] == role]

    total = len(items)
    start = (page - 1) * size
    end = start + size
    page_items = items[start:end]

    return PaginatedResponse(
        items=[UserResponseV2(**u) for u in page_items],
        total=total,
        page=page,
        size=size,
        has_next=end < total,
    )


@v2_router.get("/users/{user_id}", response_model=UserResponseV2)
async def get_user_v2(user_id: int):
    """[v2] 사용자 상세 (확장 필드 포함)"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다")
    return UserResponseV2(**user)


@v2_router.get("/orders", response_model=PaginatedResponse)
async def list_orders_v2(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
):
    """
    [v2] 주문 목록 (페이징 + 필터 + 사용자 정보 중첩).
    v1과의 차이: 페이징, 필터, 중첩된 사용자 정보
    """
    items = list(orders_db.values())
    if status:
        items = [o for o in items if o["status"] == status]
    if user_id:
        items = [o for o in items if o["user_id"] == user_id]

    total = len(items)
    start = (page - 1) * size
    end = start + size
    page_items = items[start:end]

    result_items = []
    for order in page_items:
        user = users_db.get(order["user_id"], {})
        result_items.append(OrderResponseV2(
            id=order["id"],
            product=order["product"],
            amount=order["amount"],
            status=order["status"],
            user=UserResponseV1(
                id=user.get("id", 0),
                name=user.get("name", "알 수 없음"),
                email=user.get("email", ""),
            ),
        ))

    return PaginatedResponse(
        items=result_items,
        total=total,
        page=page,
        size=size,
        has_next=end < total,
    )


# ──────────────────────────────────────────────
# 4. 서브 애플리케이션 (독립 서비스 시뮬레이션)
# ──────────────────────────────────────────────
# 인증 서브 앱
auth_app = FastAPI(
    title="인증 서비스",
    description="사용자 인증과 토큰 관리",
    version="1.0.0",
)


@auth_app.get("/status")
async def auth_status():
    """인증 서비스 상태"""
    return {"service": "auth", "status": "running"}


@auth_app.post("/login")
async def login(username: str, password: str):
    """로그인 (간단한 시뮬레이션)"""
    user = next(
        (u for u in users_db.values() if u["name"] == username),
        None,
    )
    if not user:
        raise HTTPException(401, "잘못된 인증 정보")
    return {"token": f"fake-jwt-{user['id']}", "user_id": user["id"]}


# 알림 서브 앱
notification_app = FastAPI(
    title="알림 서비스",
    description="사용자 알림 관리",
    version="1.0.0",
)

notifications: list[dict] = []


@notification_app.get("/")
async def list_notifications(user_id: Optional[int] = None):
    """알림 목록"""
    items = notifications
    if user_id:
        items = [n for n in items if n["user_id"] == user_id]
    return items


@notification_app.post("/", status_code=201)
async def create_notification(user_id: int, message: str):
    """알림 생성"""
    notification = {
        "id": len(notifications) + 1,
        "user_id": user_id,
        "message": message,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False,
    }
    notifications.append(notification)
    return notification


# ──────────────────────────────────────────────
# 5. 헬스 체크
# ──────────────────────────────────────────────
class HealthCheckResponse(BaseModel):
    status: str
    version: str
    services: dict[str, str]
    timestamp: str


# ──────────────────────────────────────────────
# 6. 메인 앱 조립
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기: 시작 시 초기화, 종료 시 정리"""
    print("[시작] 마이크로서비스 앱 초기화 완료")
    yield
    print("[종료] 앱 정리 완료")


app = FastAPI(
    title="마이크로서비스 게이트웨이",
    description="API 버전 관리와 서브 앱 마운트 예제",
    version="2.0.0",
    lifespan=lifespan,
)

# API 버전 라우터 등록
app.include_router(v1_router)
app.include_router(v2_router)

# 서브 앱 마운트 (독립 서비스 시뮬레이션)
app.mount("/services/auth", auth_app)
app.mount("/services/notifications", notification_app)


@app.get("/")
async def root():
    """API 게이트웨이 정보"""
    return {
        "name": "마이크로서비스 게이트웨이",
        "version": "2.0.0",
        "api_versions": ["v1", "v2"],
        "services": {
            "auth": "/services/auth/docs",
            "notifications": "/services/notifications/docs",
        },
        "docs": {
            "v1": "/docs (v1 태그 확인)",
            "v2": "/docs (v2 태그 확인)",
        },
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """종합 헬스 체크"""
    return HealthCheckResponse(
        status="healthy",
        version="2.0.0",
        services={
            "auth": "running",
            "notifications": "running",
            "database": "connected",
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/versions")
async def api_versions():
    """사용 가능한 API 버전 정보"""
    return {
        "current": "v2",
        "supported": ["v1", "v2"],
        "deprecated": [],
        "sunset": {
            "v1": "v1은 2025-06-01에 지원 종료 예정입니다. v2로 마이그레이션하세요.",
        },
        "migration_guide": {
            "v1_to_v2": {
                "changes": [
                    "목록 응답에 페이징 래퍼 추가",
                    "사용자 응답에 role, department 필드 추가",
                    "주문 응답에 user 객체 중첩",
                    "목록 필터링 파라미터 추가",
                ],
                "breaking": False,
                "note": "v1 응답 필드는 모두 v2에 포함됩니다 (하위 호환)",
            },
        },
    }
