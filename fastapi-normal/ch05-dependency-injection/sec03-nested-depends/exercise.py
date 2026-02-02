# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI, Depends, Header, HTTPException, APIRouter
from fastapi.testclient import TestClient

app = FastAPI()


# ============================================================
# 가상 데이터 및 헬퍼 클래스 (수정하지 마세요)
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
    """가상 데이터베이스 클래스 (수정하지 마세요)"""

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
    """주문 리포지토리 (수정하지 마세요)"""

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
# 문제 1: yield를 사용한 DB 세션 의존성
# ============================================================

# TODO: get_db 의존성 함수를 작성하세요
# 1. FakeDB 인스턴스 생성
# 2. db.connect() 호출
# 3. yield db (DB 인스턴스 제공)
# 4. finally 블록에서 db.close() 호출


# ============================================================
# 문제 2: 중첩 의존성 체인
# ============================================================

# TODO: get_current_user 의존성 함수를 작성하세요
# 매개변수: x_token (str, Header()로 받음)
# - fake_users에서 x_token에 해당하는 사용자를 찾음
# - 사용자가 없으면 HTTPException(status_code=401, detail="유효하지 않은 토큰") 발생
# - 사용자 정보(dict)를 반환


# TODO: get_order_repository 의존성 함수를 작성하세요
# 매개변수: db (FakeDB, Depends(get_db)로 받음)
# - OrderRepository(db) 인스턴스를 반환


# TODO: GET /orders 엔드포인트를 작성하세요
# 의존성: get_current_user, get_order_repository
# - 현재 사용자의 user_id에 해당하는 주문만 조회 (find_by_user_id 사용)
# - 반환값: {"user": 사용자 username, "orders": 주문 목록}


# TODO: GET /orders/{order_id} 엔드포인트를 작성하세요
# 의존성: get_current_user, get_order_repository
# - 특정 주문 조회 (find_by_id 사용)
# - 주문이 없으면: HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
# - 주문의 user_id != 현재 사용자의 user_id이면:
#     HTTPException(status_code=403, detail="다른 사용자의 주문입니다")
# - 반환값: 주문 정보(dict)


# ============================================================
# 문제 3: 라우터 수준 의존성
# ============================================================

# TODO: require_admin 의존성 함수를 작성하세요
# 매개변수: user (dict, Depends(get_current_user)로 받음)
# - user["role"]이 "admin"이 아니면:
#     HTTPException(status_code=403, detail="관리자 권한이 필요합니다") 발생
# - 사용자 정보를 반환


# TODO: admin_router를 생성하세요
# - prefix="/admin"
# - tags=["관리자"]
# - dependencies=[Depends(require_admin)]


# TODO: GET /admin/stats 엔드포인트를 admin_router에 작성하세요
# 의존성: get_order_repository (라우터 수준에서 인증은 이미 처리됨)
# - 전체 주문 목록 조회 (find_all 사용)
# - 반환값: {
#     "total_orders": 전체 주문 수,
#     "total_revenue": 전체 주문 가격 합계,
#     "status_counts": {"배송중": 개수, "완료": 개수, "준비중": 개수}
#   }


# TODO: app.include_router(admin_router) 호출


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
