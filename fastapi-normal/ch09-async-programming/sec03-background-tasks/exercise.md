# 연습 문제: 백그라운드 작업

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: 기본 백그라운드 작업

알림을 발송하고, 백그라운드에서 로그를 기록하는 시스템을 구현하세요.

### 요구 사항

1. `write_log(message: str)` 함수
   - `task_log` 리스트에 `message`를 추가
   - 일반 함수 (async 아님)

2. `POST /send-notification/{email}` 엔드포인트
   - `BackgroundTasks`를 매개변수로 받음
   - 백그라운드 작업 등록: `write_log(f"알림 발송: {email}")`
   - 즉시 반환: `{"message": f"알림이 {email}에 발송됩니다", "status": "accepted"}`

### 힌트

- `background_tasks.add_task(write_log, f"알림 발송: {email}")`
- `BackgroundTasks`는 FastAPI가 자동으로 주입합니다

---

## 문제 2: 다중 백그라운드 작업과 의존성

주문을 생성하고, 여러 후처리를 백그라운드에서 실행하는 시스템을 구현하세요.

### 요구 사항

1. `log_activity(activity: str)` 함수
   - `task_log` 리스트에 `activity`를 추가

2. `write_notification(email: str, message: str)` 함수
   - `task_log` 리스트에 `f"알림: {email} - {message}"`를 추가

3. `verify_request(background_tasks: BackgroundTasks)` 의존성 함수
   - 백그라운드 작업 등록: `log_activity("요청 검증 완료")`
   - 문자열 `"verified"`를 반환

4. `POST /orders` 엔드포인트
   - 요청 본문: `{"item": str, "email": str}`
   - `verify_request` 의존성 사용 (`Depends`)
   - 백그라운드 작업 2개 추가:
     - `log_activity(f"주문 생성: {order.item}")`
     - `write_notification(order.email, f"주문 확인: {order.item}")`
   - 반환: `{"message": f"주문 완료: {order.item}", "verification": verification}`

### 힌트

- `BackgroundTasks`는 의존성과 엔드포인트에서 **같은 인스턴스**를 공유합니다
- 의존성에서 추가한 작업이 먼저 실행되고, 엔드포인트에서 추가한 작업이 이어서 실행됩니다
- Pydantic 모델: `class OrderRequest(BaseModel): item: str; email: str`

---

## 테스트 기대 결과

```
문제 1: 기본 백그라운드 작업
  [통과] 알림 발송 응답 확인
  [통과] 백그라운드 로그 기록 확인

문제 2: 다중 백그라운드 작업과 의존성
  [통과] 주문 생성 응답 확인
  [통과] 의존성 백그라운드 작업 실행 확인
  [통과] 다중 백그라운드 작업 순서 확인

모든 테스트를 통과했습니다!
```
