# 모범 답안: 백그라운드 작업
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

# 백그라운드 작업 실행 결과를 추적하는 리스트
task_log: list[str] = []


# ============================================================
# 문제 1 해답: 기본 백그라운드 작업
# ============================================================

def write_log(message: str):
    """백그라운드에서 로그를 기록하는 함수.

    실제 환경에서는 파일이나 DB에 기록하지만,
    테스트를 위해 리스트에 추가합니다.
    """
    task_log.append(message)


@app.post("/send-notification/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks,
):
    """알림 발송 엔드포인트.

    응답을 즉시 반환하고, 백그라운드에서 로그를 기록합니다.
    """
    background_tasks.add_task(write_log, f"알림 발송: {email}")
    return {"message": f"알림이 {email}에 발송됩니다", "status": "accepted"}


# ============================================================
# 문제 2 해답: 다중 백그라운드 작업과 의존성
# ============================================================

class OrderRequest(BaseModel):
    item: str
    email: str


def log_activity(activity: str):
    """활동 로그를 기록하는 함수."""
    task_log.append(activity)


def write_notification(email: str, message: str):
    """알림을 기록하는 함수."""
    task_log.append(f"알림: {email} - {message}")


def verify_request(background_tasks: BackgroundTasks) -> str:
    """요청 검증 의존성.

    검증 후 백그라운드 작업으로 검증 로그를 기록합니다.
    의존성에서 추가한 백그라운드 작업은 엔드포인트의 작업보다 먼저 실행됩니다.
    """
    background_tasks.add_task(log_activity, "요청 검증 완료")
    return "verified"


@app.post("/orders")
async def create_order(
    order: OrderRequest,
    background_tasks: BackgroundTasks,
    verification: str = Depends(verify_request),
):
    """주문 생성 엔드포인트.

    의존성(verify_request)에서 1개, 엔드포인트에서 2개,
    총 3개의 백그라운드 작업이 등록됩니다.

    실행 순서:
    1. "요청 검증 완료" (의존성에서 등록)
    2. "주문 생성: {item}" (엔드포인트에서 등록)
    3. "알림: {email} - 주문 확인: {item}" (엔드포인트에서 등록)
    """
    background_tasks.add_task(log_activity, f"주문 생성: {order.item}")
    background_tasks.add_task(
        write_notification, order.email, f"주문 확인: {order.item}"
    )

    return {
        "message": f"주문 완료: {order.item}",
        "verification": verification,
    }


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 테스트: 기본 백그라운드 작업
    print("=" * 50)
    print("문제 1: 기본 백그라운드 작업")
    print("=" * 50)

    # task_log 초기화
    task_log.clear()

    # 알림 발송 요청
    response = client.post("/send-notification/user@example.com")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "알림이 user@example.com에 발송됩니다"
    assert data["status"] == "accepted"
    print("  [통과] 알림 발송 응답 확인")

    # 백그라운드 작업 실행 확인
    # TestClient는 백그라운드 작업이 완료될 때까지 대기합니다
    assert len(task_log) == 1
    assert task_log[0] == "알림 발송: user@example.com"
    print(f"  [통과] 백그라운드 로그 기록 확인: {task_log}")

    # 문제 2 테스트: 다중 백그라운드 작업과 의존성
    print()
    print("=" * 50)
    print("문제 2: 다중 백그라운드 작업과 의존성")
    print("=" * 50)

    # task_log 초기화
    task_log.clear()

    # 주문 생성 요청
    response = client.post(
        "/orders",
        json={"item": "노트북", "email": "buyer@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "주문 완료: 노트북"
    assert data["verification"] == "verified"
    print("  [통과] 주문 생성 응답 확인")

    # 의존성의 백그라운드 작업이 실행되었는지 확인
    assert "요청 검증 완료" in task_log, (
        f"의존성 백그라운드 작업이 실행되지 않았습니다. task_log: {task_log}"
    )
    print("  [통과] 의존성 백그라운드 작업 실행 확인")

    # 다중 백그라운드 작업 순서 확인
    assert len(task_log) == 3, (
        f"task_log에 3개의 항목이 있어야 합니다. 현재: {len(task_log)}개 - {task_log}"
    )
    assert task_log[0] == "요청 검증 완료"
    assert task_log[1] == "주문 생성: 노트북"
    assert task_log[2] == "알림: buyer@example.com - 주문 확인: 노트북"
    print(f"  [통과] 다중 백그라운드 작업 순서 확인: {task_log}")

    print()
    print("모든 테스트를 통과했습니다!")
