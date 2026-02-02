# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from fastapi import FastAPI, Depends, Header, HTTPException, APIRouter
from fastapi.testclient import TestClient

app = FastAPI()


# ============================================================
# 가상 데이터 및 헬퍼 클래스
# ============================================================

# 토큰 -> 사용자 매핑
fake_users = {
    "token-user1": {"user_id": 1, "username": "홍길동", "role": "user"},
    "token-user2": {"user_id": 2, "username": "김영희", "role": "user"},
    "token-admin": {"user_id": 99, "username": "관리자", "role": "admin"},
}

# 가상 주문 데이터
fake_orders = [
    {"order_id": 1, "user_id": 1, "item": "노트북", "price": 1500000, "status": "배송중"},
    {"order_id": 2, "user_id": 1, "item": "마우스", "price": 50000, "status": "완료"},
    {"order_id": 3, "user_id": 2, "item": "키보드", "price": 120000, "status": "준비중"},
    {"order_id": 4, "user_id": 2, "item": "모니터", "price": 800000, "status": "배송중"},
    {"order_id": 5, "user_id": 99, "item": "서버", "price": 5000000, "status": "완료"},
]


class FakeDB:
    """가상 데이터베이스 클래스"""

    def __init__(self):
        self.connected = False
        self.closed = False

    def connect(self):
        """DB 연결 시뮬레이션"""
        self.connected = True

    def close(self):
        """DB 연결 종료 시뮬레이션"""
        self.connected = False
        self.closed = True

    def get_orders(self) -> list[dict]:
        """모든 주문 반환"""
        return fake_orders

    def get_order(self, order_id: int) -> dict | None:
        """특정 주문 반환 (없으면 None)"""
        for order in fake_orders:
            if order["order_id"] == order_id:
                return order
        return None


class OrderRepository:
    """주문 리포지토리"""

    def __init__(self, db: FakeDB):
        self.db = db

    def find_all(self) -> list[dict]:
        """모든 주문 조회"""
        return self.db.get_orders()

    def find_by_user_id(self, user_id: int) -> list[dict]:
        """특정 사용자의 주문만 조회"""
        return [o for o in self.db.get_orders() if o["user_id"] == user_id]

    def find_by_id(self, order_id: int) -> dict | None:
        """특정 주문 조회"""
        return self.db.get_order(order_id)


# ============================================================
# 문제 1 해답: yield를 사용한 DB 세션 의존성
# ============================================================

def get_db():
    """
    DB 세션 의존성 (yield 사용).
    요청 시작 시 DB를 연결하고, 요청 완료 후 자동으로 세션을 닫습니다.
    """
    db = FakeDB()
    db.connect()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 문제 2 해답: 중첩 의존성 체인
# ============================================================

def get_current_user(x_token: str = Header()) -> dict:
    """
    현재 사용자 인증 의존성.
    x-token 헤더에서 토큰을 읽고, 해당 사용자를 반환합니다.
    유효하지 않은 토큰이면 401 에러를 발생시킵니다.
    """
    user = fake_users.get(x_token)
    if user is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰")
    return user


def get_order_repository(db: FakeDB = Depends(get_db)) -> OrderRepository:
    """
    주문 리포지토리 의존성.
    get_db에 의존하여 DB 세션을 받고, OrderRepository 인스턴스를 생성합니다.

    의존성 체인: get_db -> get_order_repository
    """
    return OrderRepository(db)


@app.get("/orders")
def read_orders(
    user: dict = Depends(get_current_user),
    repo: OrderRepository = Depends(get_order_repository),
):
    """
    현재 사용자의 주문 목록 조회.

    의존성 체인:
    - get_current_user: 헤더에서 사용자 인증
    - get_db -> get_order_repository: DB 세션 생성 및 리포지토리 생성
    """
    orders = repo.find_by_user_id(user["user_id"])
    return {
        "user": user["username"],
        "orders": orders,
    }


@app.get("/orders/{order_id}")
def read_order(
    order_id: int,
    user: dict = Depends(get_current_user),
    repo: OrderRepository = Depends(get_order_repository),
):
    """
    특정 주문 상세 조회.
    본인의 주문만 조회할 수 있습니다.
    """
    # 주문 조회
    order = repo.find_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")

    # 권한 확인: 본인의 주문인지 체크
    if order["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="다른 사용자의 주문입니다")

    return order


# ============================================================
# 문제 3 해답: 라우터 수준 의존성
# ============================================================

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    관리자 권한 확인 의존성.
    get_current_user에 의존하여 사용자를 먼저 인증한 후,
    role이 "admin"인지 확인합니다.

    의존성 체인: get_current_user -> require_admin
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return user


# 라우터 수준 의존성 설정:
# admin_router의 모든 엔드포인트에 require_admin이 자동 적용됩니다.
admin_router = APIRouter(
    prefix="/admin",
    tags=["관리자"],
    dependencies=[Depends(require_admin)],
)


@admin_router.get("/stats")
def get_admin_stats(
    repo: OrderRepository = Depends(get_order_repository),
):
    """
    관리자용 주문 통계 엔드포인트.

    라우터 수준에서 require_admin 의존성이 이미 적용되어 있으므로,
    이 엔드포인트에서는 별도로 인증 의존성을 추가할 필요가 없습니다.

    의존성 체인:
    - [라우터 수준] get_current_user -> require_admin (인증 + 권한 확인)
    - [엔드포인트 수준] get_db -> get_order_repository (데이터 조회)
    """
    all_orders = repo.find_all()

    # 상태별 주문 수 집계
    status_counts: dict[str, int] = {}
    for order in all_orders:
        status = order["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "total_orders": len(all_orders),
        "total_revenue": sum(order["price"] for order in all_orders),
        "status_counts": status_counts,
    }


# 라우터를 앱에 등록
app.include_router(admin_router)


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 & 2 테스트: 중첩 의존성 체인
    print("=" * 50)
    print("문제 1 & 2: 중첩 의존성 체인 테스트")
    print("=" * 50)

    # 인증된 요청 - user1의 주문 조회
    response = client.get("/orders", headers={"x-token": "token-user1"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "홍길동"
    assert len(data["orders"]) == 2
    assert all(o["user_id"] == 1 for o in data["orders"])
    print("  [통과] user1 주문 목록 조회 (2건)")

    # 인증된 요청 - user2의 주문 조회
    response = client.get("/orders", headers={"x-token": "token-user2"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "김영희"
    assert len(data["orders"]) == 2
    print("  [통과] user2 주문 목록 조회 (2건)")

    # 인증 실패
    response = client.get("/orders", headers={"x-token": "invalid-token"})
    assert response.status_code == 401
    print("  [통과] 잘못된 토큰 - 401 에러")

    # 주문 상세 조회 - 본인 주문
    response = client.get("/orders/1", headers={"x-token": "token-user1"})
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 1
    assert data["item"] == "노트북"
    print("  [통과] 주문 상세 조회 (본인 주문)")

    # 주문 상세 조회 - 다른 사용자의 주문
    response = client.get("/orders/3", headers={"x-token": "token-user1"})
    assert response.status_code == 403
    print("  [통과] 다른 사용자의 주문 접근 - 403 에러")

    # 존재하지 않는 주문
    response = client.get("/orders/999", headers={"x-token": "token-user1"})
    assert response.status_code == 404
    print("  [통과] 존재하지 않는 주문 - 404 에러")

    # 문제 3 테스트: 라우터 수준 의존성
    print()
    print("=" * 50)
    print("문제 3: 라우터 수준 의존성 테스트")
    print("=" * 50)

    # 관리자 접근
    response = client.get("/admin/stats", headers={"x-token": "token-admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 5
    assert data["total_revenue"] == 7470000
    assert data["status_counts"]["배송중"] == 2
    assert data["status_counts"]["완료"] == 2
    assert data["status_counts"]["준비중"] == 1
    print("  [통과] 관리자 통계 조회")

    # 일반 사용자 접근 시도
    response = client.get("/admin/stats", headers={"x-token": "token-user1"})
    assert response.status_code == 403
    print("  [통과] 일반 사용자 관리자 페이지 접근 - 403 에러")

    # 미인증 접근 시도
    response = client.get("/admin/stats", headers={"x-token": "invalid"})
    assert response.status_code == 401
    print("  [통과] 미인증 관리자 페이지 접근 - 401 에러")

    print()
    print("모든 테스트를 통과했습니다!")
