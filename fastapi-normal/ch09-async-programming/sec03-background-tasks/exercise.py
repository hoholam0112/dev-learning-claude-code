# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

# 백그라운드 작업 실행 결과를 추적하는 리스트
task_log: list[str] = []


# ============================================================
# 문제 1: 기본 백그라운드 작업
# ============================================================

# TODO: write_log 함수를 작성하세요
# - 매개변수: message (str)
# - task_log 리스트에 message를 추가
# - 일반 함수 (async 아님)


# TODO: POST /send-notification/{email} 엔드포인트를 작성하세요
# - 매개변수: email (str, 경로 매개변수), background_tasks (BackgroundTasks)
# - 백그라운드 작업 등록: write_log(f"알림 발송: {email}")
#   힌트: background_tasks.add_task(write_log, f"알림 발송: {email}")
# - 반환값: {"message": f"알림이 {email}에 발송됩니다", "status": "accepted"}


# ============================================================
# 문제 2: 다중 백그라운드 작업과 의존성
# ============================================================

class OrderRequest(BaseModel):
    item: str
    email: str


# TODO: log_activity 함수를 작성하세요
# - 매개변수: activity (str)
# - task_log 리스트에 activity를 추가


# TODO: write_notification 함수를 작성하세요
# - 매개변수: email (str), message (str)
# - task_log 리스트에 f"알림: {email} - {message}"를 추가


# TODO: verify_request 의존성 함수를 작성하세요
# - 매개변수: background_tasks (BackgroundTasks)
# - 백그라운드 작업 등록: log_activity("요청 검증 완료")
# - 반환값: "verified"


# TODO: POST /orders 엔드포인트를 작성하세요
# - 매개변수:
#   - order (OrderRequest)
#   - background_tasks (BackgroundTasks)
#   - verification (str, Depends(verify_request))
# - 백그라운드 작업 2개 등록:
#   1. log_activity(f"주문 생성: {order.item}")
#   2. write_notification(order.email, f"주문 확인: {order.item}")
# - 반환값: {"message": f"주문 완료: {order.item}", "verification": verification}


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
    assert response.status_code == 200, (
        "POST /send-notification/{email} 엔드포인트가 없습니다. 엔드포인트를 작성하세요."
    )
    data = response.json()
    assert data["message"] == "알림이 user@example.com에 발송됩니다", (
        f"message가 올바르지 않습니다. 현재: {data.get('message')}"
    )
    assert data["status"] == "accepted", (
        f"status가 'accepted'여야 합니다. 현재: {data.get('status')}"
    )
    print("  [통과] 알림 발송 응답 확인")

    # 백그라운드 작업 실행 확인
    assert len(task_log) == 1, (
        f"task_log에 1개의 항목이 있어야 합니다. 현재: {len(task_log)}개. "
        "write_log 함수와 background_tasks.add_task를 확인하세요."
    )
    assert task_log[0] == "알림 발송: user@example.com", (
        f"로그 내용이 올바르지 않습니다. 현재: {task_log[0]}"
    )
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
    assert response.status_code == 200, (
        "POST /orders 엔드포인트가 없습니다. 엔드포인트를 작성하세요."
    )
    data = response.json()
    assert data["message"] == "주문 완료: 노트북", (
        f"message가 올바르지 않습니다. 현재: {data.get('message')}"
    )
    assert data["verification"] == "verified", (
        f"verification이 'verified'여야 합니다. 현재: {data.get('verification')}. "
        "verify_request 의존성을 확인하세요."
    )
    print("  [통과] 주문 생성 응답 확인")

    # 의존성의 백그라운드 작업이 실행되었는지 확인
    assert "요청 검증 완료" in task_log, (
        f"의존성 백그라운드 작업이 실행되지 않았습니다. task_log: {task_log}. "
        "verify_request에서 background_tasks.add_task를 호출했는지 확인하세요."
    )
    print("  [통과] 의존성 백그라운드 작업 실행 확인")

    # 다중 백그라운드 작업 순서 확인
    assert len(task_log) == 3, (
        f"task_log에 3개의 항목이 있어야 합니다. 현재: {len(task_log)}개 - {task_log}. "
        "의존성(1개) + 엔드포인트(2개) = 3개의 백그라운드 작업이 필요합니다."
    )
    assert task_log[0] == "요청 검증 완료", (
        f"첫 번째 로그가 '요청 검증 완료'여야 합니다. 현재: {task_log[0]}"
    )
    assert task_log[1] == "주문 생성: 노트북", (
        f"두 번째 로그가 '주문 생성: 노트북'이어야 합니다. 현재: {task_log[1]}"
    )
    assert task_log[2] == "알림: buyer@example.com - 주문 확인: 노트북", (
        f"세 번째 로그가 올바르지 않습니다. 현재: {task_log[2]}"
    )
    print(f"  [통과] 다중 백그라운드 작업 순서 확인: {task_log}")

    print()
    print("모든 테스트를 통과했습니다!")
