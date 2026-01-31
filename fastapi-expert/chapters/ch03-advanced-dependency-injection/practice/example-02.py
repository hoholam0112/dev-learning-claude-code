# 실행 방법: uvicorn example-02:app --reload
# 복잡한 의존성 그래프와 스코프 제어 예제
# 필요 패키지: pip install fastapi uvicorn

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# 1. 도메인 모델 및 서비스 레이어
# ============================================================

class UserData(BaseModel):
    """사용자 데이터 모델"""
    id: int
    name: str
    email: str
    role: str = "user"


class OrderData(BaseModel):
    """주문 데이터 모델"""
    id: int
    user_id: int
    product: str
    amount: float


@dataclass
class Settings:
    """앱 설정"""
    db_url: str = "postgresql://localhost/mydb"
    cache_url: str = "redis://localhost"
    secret_key: str = "dev-secret-key"
    debug: bool = True


# ============================================================
# 2. 리포지토리 레이어 (의존성 그래프의 중간 계층)
# ============================================================

class BaseRepository:
    """리포지토리 기본 클래스"""

    def __init__(self, db_session: dict):
        self.db = db_session
        self._name = self.__class__.__name__
        logger.info(f"    [{self._name}] 생성됨")

    async def close(self):
        logger.info(f"    [{self._name}] 정리됨")


class UserRepository(BaseRepository):
    """사용자 리포지토리"""

    # 시뮬레이션 데이터
    _users = {
        1: UserData(id=1, name="홍길동", email="hong@example.com", role="admin"),
        2: UserData(id=2, name="김영희", email="kim@example.com", role="user"),
        3: UserData(id=3, name="이철수", email="lee@example.com", role="user"),
    }

    async def get_by_id(self, user_id: int) -> Optional[UserData]:
        return self._users.get(user_id)

    async def get_all(self) -> list[UserData]:
        return list(self._users.values())


class OrderRepository(BaseRepository):
    """주문 리포지토리"""

    _orders = {
        1: OrderData(id=1, user_id=1, product="노트북", amount=1500000),
        2: OrderData(id=2, user_id=1, product="키보드", amount=150000),
        3: OrderData(id=3, user_id=2, product="마우스", amount=50000),
    }

    async def get_by_user(self, user_id: int) -> list[OrderData]:
        return [o for o in self._orders.values() if o.user_id == user_id]


# ============================================================
# 3. 서비스 레이어 (의존성 그래프의 상위 계층)
# ============================================================

class UserService:
    """사용자 서비스"""

    def __init__(self, user_repo: UserRepository, order_repo: OrderRepository):
        self.user_repo = user_repo
        self.order_repo = order_repo
        logger.info("    [UserService] 생성됨")

    async def get_user_profile(self, user_id: int) -> dict:
        """사용자 프로필과 주문 내역을 함께 조회"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"사용자 {user_id}를 찾을 수 없습니다")

        orders = await self.order_repo.get_by_user(user_id)
        total_amount = sum(o.amount for o in orders)

        return {
            "user": user.model_dump(),
            "orders": [o.model_dump() for o in orders],
            "total_orders": len(orders),
            "total_amount": total_amount,
        }


class AuthService:
    """인증 서비스"""

    def __init__(self, user_repo: UserRepository, settings: Settings):
        self.user_repo = user_repo
        self.settings = settings
        logger.info("    [AuthService] 생성됨")

    async def authenticate(self, user_id: int) -> UserData:
        """간단한 인증 시뮬레이션"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("인증 실패")
        return user

    async def authorize(self, user: UserData, required_role: str) -> bool:
        """권한 확인"""
        role_hierarchy = {"admin": 3, "manager": 2, "user": 1}
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        return user_level >= required_level


# ============================================================
# 4. lifespan 및 의존성 함수 정의
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """앱 생명주기 관리"""
    logger.info("=" * 50)
    logger.info("[lifespan] 앱 시작: 설정 로딩")

    app.state.settings = Settings()
    app.state.call_counter = 0

    logger.info("[lifespan] 초기화 완료")
    logger.info("=" * 50)

    yield

    logger.info("=" * 50)
    logger.info("[lifespan] 앱 종료")
    logger.info(f"[lifespan] 총 요청 처리 수: {app.state.call_counter}")
    logger.info("=" * 50)


app = FastAPI(
    title="복잡한 의존성 그래프와 스코프 제어",
    lifespan=lifespan,
)


# --- 기본 의존성 ---

def get_settings(request: Request) -> Settings:
    """설정 의존성 (앱 스코프)"""
    logger.info("  [의존성] get_settings 호출")
    return request.app.state.settings


async def get_db_session(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator:
    """
    DB 세션 의존성 (요청 스코프).
    설정에서 DB URL을 가져와 세션을 생성한다.
    """
    logger.info(f"  [의존성] get_db_session 시작 (DB: {settings.db_url})")
    session = {"url": settings.db_url, "active": True}
    try:
        yield session
    finally:
        session["active"] = False
        logger.info("  [의존성] get_db_session 정리")


# --- 리포지토리 의존성 ---

async def get_user_repo(
    session: dict = Depends(get_db_session),
) -> AsyncGenerator:
    """사용자 리포지토리 의존성"""
    logger.info("  [의존성] get_user_repo 시작")
    repo = UserRepository(session)
    try:
        yield repo
    finally:
        await repo.close()


async def get_order_repo(
    session: dict = Depends(get_db_session),
) -> AsyncGenerator:
    """
    주문 리포지토리 의존성.
    get_db_session에 의존하지만, get_user_repo와 같은 세션을 공유한다.
    (FastAPI의 의존성 캐싱 덕분)
    """
    logger.info("  [의존성] get_order_repo 시작")
    repo = OrderRepository(session)
    try:
        yield repo
    finally:
        await repo.close()


# --- 서비스 의존성 ---

async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    order_repo: OrderRepository = Depends(get_order_repo),
) -> UserService:
    """
    사용자 서비스 의존성.
    UserRepository와 OrderRepository를 주입받는다.

    의존성 그래프:
    get_settings → get_db_session → get_user_repo  → get_user_service
                                  → get_order_repo → get_user_service
    """
    logger.info("  [의존성] get_user_service 호출")
    return UserService(user_repo, order_repo)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    """인증 서비스 의존성"""
    logger.info("  [의존성] get_auth_service 호출")
    return AuthService(user_repo, settings)


# --- 복합 의존성 (인증 + 권한) ---

async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserData:
    """
    현재 인증된 사용자를 반환하는 의존성.
    실제로는 토큰에서 사용자 ID를 추출하지만, 여기서는 헤더로 시뮬레이션.
    """
    user_id_str = request.headers.get("X-User-Id", "1")
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="유효하지 않은 사용자 ID")

    try:
        user = await auth_service.authenticate(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="인증 실패")

    request.app.state.call_counter += 1
    return user


def require_role(role: str):
    """
    특정 역할을 요구하는 의존성 팩토리.
    클로저를 사용하여 파라미터화된 의존성을 생성한다.
    """
    async def role_checker(
        current_user: UserData = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
    ) -> UserData:
        has_permission = await auth_service.authorize(current_user, role)
        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail=f"'{role}' 역할이 필요합니다. "
                       f"현재 역할: '{current_user.role}'",
            )
        return current_user

    return role_checker


# ============================================================
# 5. 엔드포인트 정의
# ============================================================

@app.get("/")
async def root():
    """의존성 그래프 정보"""
    return {
        "message": "복잡한 의존성 그래프와 스코프 제어 예제",
        "의존성_그래프": {
            "레벨 1 (리프)": ["get_settings"],
            "레벨 2": ["get_db_session (depends: settings)"],
            "레벨 3": [
                "get_user_repo (depends: session)",
                "get_order_repo (depends: session)",
            ],
            "레벨 4": [
                "get_user_service (depends: user_repo, order_repo)",
                "get_auth_service (depends: user_repo, settings)",
            ],
            "레벨 5": ["get_current_user (depends: auth_service)"],
            "레벨 6": ["require_role (depends: current_user, auth_service)"],
        },
        "사용법": "X-User-Id 헤더로 사용자를 지정 (1=admin, 2=user, 3=user)",
    }


@app.get("/users/me")
async def get_my_profile(
    current_user: UserData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    내 프로필 조회.
    콘솔에서 의존성 실행 순서와 캐싱을 확인하세요.
    """
    logger.info("\n[엔드포인트] /users/me 처리 시작")
    profile = await user_service.get_user_profile(current_user.id)
    logger.info("[엔드포인트] /users/me 처리 완료\n")
    return profile


@app.get("/admin/dashboard")
async def admin_dashboard(
    admin_user: UserData = Depends(require_role("admin")),
):
    """
    관리자 전용 대시보드.
    admin 역할이 없으면 403 Forbidden이 반환된다.

    테스트:
    - curl -H "X-User-Id: 1" http://localhost:8000/admin/dashboard  (성공)
    - curl -H "X-User-Id: 2" http://localhost:8000/admin/dashboard  (403)
    """
    return {
        "대시보드": "관리자 전용",
        "사용자": admin_user.model_dump(),
    }


@app.get("/users")
async def list_users(
    _: UserData = Depends(require_role("admin")),
    user_service: UserService = Depends(get_user_service),
):
    """사용자 목록 (관리자 전용)"""
    users = await user_service.user_repo.get_all()
    return {"users": [u.model_dump() for u in users]}


@app.get("/dependency-graph-demo")
async def dependency_graph_demo(
    settings: Settings = Depends(get_settings),
    current_user: UserData = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    의존성 그래프 캐싱 데모.
    여러 의존성이 공통 하위 의존성을 공유하는 것을 확인한다.

    콘솔 출력을 보면:
    - get_settings는 한 번만 호출됨
    - get_db_session은 한 번만 호출됨
    - get_user_repo는 한 번만 호출됨 (auth_service와 user_service가 공유)
    """
    logger.info("\n[엔드포인트] /dependency-graph-demo 처리")
    return {
        "settings_debug": settings.debug,
        "current_user": current_user.name,
        "설명": (
            "콘솔에서 각 의존성이 몇 번 호출되었는지 확인하세요. "
            "공유 의존성은 한 번만 실행됩니다."
        ),
    }


if __name__ == "__main__":
    import uvicorn

    print("복잡한 의존성 그래프 서버를 시작합니다...")
    print("\n사용법:")
    print("  curl -H 'X-User-Id: 1' http://localhost:8000/users/me")
    print("  curl -H 'X-User-Id: 1' http://localhost:8000/admin/dashboard")
    print("  curl -H 'X-User-Id: 2' http://localhost:8000/admin/dashboard")
    print("\nAPI 문서: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
