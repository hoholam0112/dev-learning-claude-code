# 실행 방법: uvicorn example-02:app --reload
# 판별 합집합(Discriminated Union)과 다형성 응답 예제
# 필요 패키지: pip install fastapi uvicorn pydantic

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Union, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator, TypeAdapter

app = FastAPI(title="고급 Pydantic 패턴 - 판별 합집합 & 다형성 응답")


# ============================================================
# 1. 판별 합집합 (Discriminated Union)
# ============================================================

# --- 알림 시스템: 다양한 타입의 알림을 하나의 엔드포인트로 처리 ---

class EmailNotification(BaseModel):
    """이메일 알림"""
    type: Literal["email"]
    recipient: str = Field(description="수신자 이메일")
    subject: str = Field(description="제목")
    body: str = Field(description="본문 (HTML 허용)")
    cc: list[str] = Field(default=[], description="참조")

    @model_validator(mode="after")
    def validate_email(self) -> "EmailNotification":
        if "@" not in self.recipient:
            raise ValueError("유효한 이메일 주소가 아닙니다")
        return self


class SMSNotification(BaseModel):
    """SMS 알림"""
    type: Literal["sms"]
    phone_number: str = Field(description="수신 전화번호")
    message: str = Field(max_length=160, description="메시지 (160자 제한)")


class PushNotification(BaseModel):
    """푸시 알림"""
    type: Literal["push"]
    device_token: str = Field(description="디바이스 토큰")
    title: str = Field(description="알림 제목")
    body: str = Field(description="알림 본문")
    badge_count: int = Field(default=0, ge=0, description="뱃지 수")
    data: dict = Field(default={}, description="추가 데이터")


class SlackNotification(BaseModel):
    """Slack 알림"""
    type: Literal["slack"]
    channel: str = Field(description="슬랙 채널 (#channel)")
    message: str = Field(description="메시지")
    attachments: list[dict] = Field(default=[], description="첨부")
    mention_users: list[str] = Field(default=[], description="멘션할 사용자")


# 판별 합집합: type 필드로 O(1) 타입 결정
Notification = Annotated[
    Union[EmailNotification, SMSNotification, PushNotification, SlackNotification],
    Field(discriminator="type"),
]


# ============================================================
# 2. 다형성 이벤트 시스템
# ============================================================

class EventType(str, Enum):
    """이벤트 타입 열거형"""
    USER_CREATED = "user_created"
    ORDER_PLACED = "order_placed"
    PAYMENT_COMPLETED = "payment_completed"
    ITEM_SHIPPED = "item_shipped"


class BaseEvent(BaseModel):
    """모든 이벤트의 기본 클래스"""
    event_id: str = Field(description="이벤트 고유 ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default={})


class UserCreatedEvent(BaseEvent):
    """사용자 생성 이벤트"""
    event_type: Literal[EventType.USER_CREATED]
    user_id: int
    username: str
    email: str


class OrderPlacedEvent(BaseEvent):
    """주문 생성 이벤트"""
    event_type: Literal[EventType.ORDER_PLACED]
    order_id: str
    user_id: int
    items: list[dict]
    total_amount: float = Field(gt=0)


class PaymentCompletedEvent(BaseEvent):
    """결제 완료 이벤트"""
    event_type: Literal[EventType.PAYMENT_COMPLETED]
    payment_id: str
    order_id: str
    amount: float = Field(gt=0)
    payment_method: str


class ItemShippedEvent(BaseEvent):
    """배송 시작 이벤트"""
    event_type: Literal[EventType.ITEM_SHIPPED]
    shipment_id: str
    order_id: str
    carrier: str
    tracking_number: str


# 이벤트 판별 합집합
DomainEvent = Annotated[
    Union[
        UserCreatedEvent,
        OrderPlacedEvent,
        PaymentCompletedEvent,
        ItemShippedEvent,
    ],
    Field(discriminator="event_type"),
]


# ============================================================
# 3. TypeAdapter를 사용한 고성능 검증
# ============================================================

# 모델 클래스 없이 TypeAdapter로 검증
notification_adapter = TypeAdapter(Notification)
event_adapter = TypeAdapter(DomainEvent)
event_list_adapter = TypeAdapter(list[DomainEvent])


# ============================================================
# 4. 응답 모델: 처리 결과도 다형성
# ============================================================

class NotificationResult(BaseModel):
    """알림 전송 결과"""
    notification_type: str
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    delivered_at: Optional[datetime] = None


# ============================================================
# 5. 엔드포인트 정의
# ============================================================

# 알림 저장소 (데모용)
sent_notifications: list[dict] = []
event_log: list[dict] = []


@app.post("/notifications/send", response_model=NotificationResult)
async def send_notification(notification: Notification):
    """
    알림 전송 엔드포인트.

    판별 합집합을 사용하여 type 필드에 따라 자동으로
    적절한 모델(Email, SMS, Push, Slack)이 선택된다.

    요청 예시:
    - {"type": "email", "recipient": "user@example.com", "subject": "제목", "body": "본문"}
    - {"type": "sms", "phone_number": "01012345678", "message": "안녕하세요"}
    - {"type": "push", "device_token": "abc123", "title": "알림", "body": "내용"}
    - {"type": "slack", "channel": "#general", "message": "메시지"}
    """
    # 타입별 처리 분기
    notification_data = notification.model_dump()
    sent_notifications.append(notification_data)

    # 타입별로 다른 처리 로직 시뮬레이션
    if isinstance(notification, EmailNotification):
        result_message = f"이메일을 {notification.recipient}에게 전송했습니다"
    elif isinstance(notification, SMSNotification):
        result_message = f"SMS를 {notification.phone_number}에 전송했습니다"
    elif isinstance(notification, PushNotification):
        result_message = f"푸시 알림을 디바이스에 전송했습니다"
    elif isinstance(notification, SlackNotification):
        result_message = f"Slack 메시지를 {notification.channel}에 전송했습니다"
    else:
        raise HTTPException(status_code=400, detail="알 수 없는 알림 타입")

    return NotificationResult(
        notification_type=notification.type,
        success=True,
        message_id=f"msg_{len(sent_notifications)}",
        delivered_at=datetime.now(),
    )


@app.post("/notifications/batch")
async def send_batch_notifications(notifications: list[Notification]):
    """
    배치 알림 전송.
    리스트 내에 서로 다른 타입의 알림이 혼합될 수 있다.
    """
    results = []
    for notification in notifications:
        sent_notifications.append(notification.model_dump())
        results.append({
            "type": notification.type,
            "success": True,
            "message_id": f"msg_{len(sent_notifications)}",
        })

    return {
        "total": len(notifications),
        "results": results,
        "타입별_수": {
            ntype: sum(1 for n in notifications if n.type == ntype)
            for ntype in set(n.type for n in notifications)
        },
    }


@app.post("/events/publish")
async def publish_event(event: DomainEvent):
    """
    도메인 이벤트 발행.
    event_type 필드로 적절한 이벤트 모델이 자동 선택된다.
    """
    event_data = event.model_dump()
    event_data["timestamp"] = event_data["timestamp"].isoformat()
    event_log.append(event_data)

    return {
        "event_id": event.event_id,
        "event_type": event.event_type.value,
        "처리_결과": "이벤트가 성공적으로 발행되었습니다",
        "현재_이벤트_수": len(event_log),
    }


@app.get("/events")
async def list_events():
    """발행된 이벤트 목록 조회"""
    return {
        "total": len(event_log),
        "events": event_log,
    }


@app.get("/notifications")
async def list_notifications():
    """전송된 알림 목록 조회"""
    return {
        "total": len(sent_notifications),
        "notifications": sent_notifications,
    }


# ============================================================
# 6. TypeAdapter 성능 비교 데모
# ============================================================

@app.get("/performance-demo")
async def performance_demo():
    """
    TypeAdapter vs BaseModel 검증 성능 비교.
    동일한 데이터에 대해 두 방식의 검증 시간을 측정한다.
    """
    import time

    test_data = {
        "type": "email",
        "recipient": "test@example.com",
        "subject": "성능 테스트",
        "body": "테스트 본문",
    }

    # 방법 1: TypeAdapter로 검증
    iterations = 10000
    start = time.perf_counter()
    for _ in range(iterations):
        notification_adapter.validate_python(test_data)
    adapter_time = time.perf_counter() - start

    # 방법 2: JSON 문자열에서 직접 검증 (Rust 내부 처리)
    import json
    json_data = json.dumps(test_data).encode()

    start = time.perf_counter()
    for _ in range(iterations):
        notification_adapter.validate_json(json_data)
    json_time = time.perf_counter() - start

    return {
        "반복_횟수": iterations,
        "TypeAdapter_validate_python": f"{adapter_time:.4f}초",
        "TypeAdapter_validate_json": f"{json_time:.4f}초",
        "JSON_방식_속도_향상": f"{adapter_time / json_time:.2f}배",
        "설명": (
            "validate_json은 Rust에서 JSON 파싱과 검증을 동시에 수행하므로 "
            "Python dict를 경유하는 validate_python보다 빠릅니다"
        ),
    }


@app.get("/schema-demo")
async def schema_demo():
    """
    판별 합집합의 JSON Schema를 확인하는 데모.
    OpenAPI 문서에 어떻게 반영되는지 보여준다.
    """
    return {
        "notification_schema": notification_adapter.json_schema(),
        "event_schema": event_adapter.json_schema(),
        "설명": (
            "판별 합집합은 JSON Schema의 oneOf + discriminator로 표현되어 "
            "OpenAPI 클라이언트가 올바른 타입을 자동 선택할 수 있습니다"
        ),
    }


if __name__ == "__main__":
    import uvicorn

    print("판별 합집합 & 다형성 응답 서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print("성능 비교: http://localhost:8000/performance-demo")
    print("스키마 확인: http://localhost:8000/schema-demo")
    uvicorn.run(app, host="0.0.0.0", port=8000)
