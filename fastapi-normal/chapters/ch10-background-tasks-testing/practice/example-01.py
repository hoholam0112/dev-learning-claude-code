# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn

"""
챕터 10 예제 01: 백그라운드 작업 (이메일 알림 시뮬레이션)

이 예제에서는 다음을 학습합니다:
- BackgroundTasks의 기본 사용법
- 여러 백그라운드 작업 등록
- 로그 파일 기록 작업
- 이메일 발송 시뮬레이션
"""

import time
import logging
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

# ── 로깅 설정 ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("background")

# 로그 파일 디렉토리
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="백그라운드 작업 예제", description="BackgroundTasks를 활용한 비동기 작업 예제")


# ── Pydantic 모델 ─────────────────────────────────────────
class EmailRequest(BaseModel):
    """이메일 발송 요청"""
    to: str
    subject: str
    body: str


class UserRegistration(BaseModel):
    """사용자 등록 요청"""
    username: str
    email: str


class NotificationRequest(BaseModel):
    """알림 요청"""
    user_id: int
    message: str
    channels: list[str] = ["email"]  # email, sms, push


# ── 백그라운드 작업 함수들 ─────────────────────────────────

def send_email(to: str, subject: str, body: str):
    """
    이메일 발송 시뮬레이션
    실제로는 SMTP 서버를 통해 이메일을 보냅니다.
    """
    logger.info(f"이메일 발송 시작: {to}")
    # 이메일 발송에 2초 걸린다고 가정
    time.sleep(2)
    logger.info(f"이메일 발송 완료: {to} | 제목: {subject}")


def send_sms(phone: str, message: str):
    """SMS 발송 시뮬레이션"""
    logger.info(f"SMS 발송 시작: {phone}")
    time.sleep(1)
    logger.info(f"SMS 발송 완료: {phone}")


def send_push_notification(user_id: int, message: str):
    """푸시 알림 발송 시뮬레이션"""
    logger.info(f"푸시 알림 발송 시작: 사용자 {user_id}")
    time.sleep(0.5)
    logger.info(f"푸시 알림 발송 완료: 사용자 {user_id}")


def write_audit_log(action: str, details: dict):
    """감사 로그를 파일에 기록합니다."""
    log_file = LOG_DIR / f"audit_{datetime.utcnow().strftime('%Y%m%d')}.log"
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"[{timestamp}] {action}: {details}\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

    logger.info(f"감사 로그 기록: {action}")


def cleanup_temp_files(directory: str, max_age_hours: int = 24):
    """임시 파일을 정리합니다."""
    logger.info(f"임시 파일 정리 시작: {directory}")
    temp_dir = Path(directory)
    if not temp_dir.exists():
        return

    now = time.time()
    cleaned = 0
    for file_path in temp_dir.iterdir():
        if file_path.is_file():
            age_hours = (now - file_path.stat().st_mtime) / 3600
            if age_hours > max_age_hours:
                file_path.unlink()
                cleaned += 1

    logger.info(f"임시 파일 정리 완료: {cleaned}개 삭제")


def process_user_registration(username: str, email: str):
    """
    사용자 등록 후처리 작업
    여러 단계를 순차적으로 실행합니다.
    """
    logger.info(f"사용자 등록 후처리 시작: {username}")

    # 1단계: 환영 이메일 발송
    send_email(
        to=email,
        subject=f"환영합니다, {username}님!",
        body=f"{username}님, 회원가입을 축하합니다!",
    )

    # 2단계: 감사 로그 기록
    write_audit_log(
        action="USER_REGISTERED",
        details={"username": username, "email": email},
    )

    logger.info(f"사용자 등록 후처리 완료: {username}")


# ── 엔드포인트 ─────────────────────────────────────────────

@app.post("/email/send", summary="이메일 발송 (백그라운드)")
async def send_email_endpoint(
    request: EmailRequest,
    background_tasks: BackgroundTasks,
):
    """
    이메일을 백그라운드에서 발송합니다.
    응답은 즉시 반환되고, 이메일은 백그라운드에서 발송됩니다.
    """
    background_tasks.add_task(send_email, request.to, request.subject, request.body)

    return {
        "message": "이메일 발송이 요청되었습니다",
        "to": request.to,
        "subject": request.subject,
        "note": "실제 발송은 백그라운드에서 진행됩니다. 서버 로그를 확인하세요.",
    }


@app.post("/users/register", summary="사용자 등록 (후처리 포함)")
async def register_user(
    user: UserRegistration,
    background_tasks: BackgroundTasks,
):
    """
    사용자를 등록하고 백그라운드에서 후처리 작업을 실행합니다.
    후처리: 환영 이메일 발송 + 감사 로그 기록
    """
    # 사용자 등록 (즉시 처리)
    # 실제로는 DB에 저장합니다
    user_data = {
        "username": user.username,
        "email": user.email,
        "registered_at": datetime.utcnow().isoformat(),
    }

    # 후처리 작업 등록 (백그라운드)
    background_tasks.add_task(
        process_user_registration,
        user.username,
        user.email,
    )

    return {
        "message": f"{user.username}님, 회원가입이 완료되었습니다!",
        "user": user_data,
        "note": "환영 이메일이 곧 발송됩니다.",
    }


@app.post("/notifications/send", summary="다중 채널 알림 발송")
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
):
    """
    여러 채널(이메일, SMS, 푸시)로 알림을 발송합니다.
    각 채널은 별도의 백그라운드 작업으로 실행됩니다.
    """
    registered_tasks = []

    for channel in request.channels:
        if channel == "email":
            background_tasks.add_task(
                send_email,
                f"user{request.user_id}@example.com",
                "알림",
                request.message,
            )
            registered_tasks.append("email")
        elif channel == "sms":
            background_tasks.add_task(
                send_sms,
                f"010-0000-{request.user_id:04d}",
                request.message,
            )
            registered_tasks.append("sms")
        elif channel == "push":
            background_tasks.add_task(
                send_push_notification,
                request.user_id,
                request.message,
            )
            registered_tasks.append("push")

    # 감사 로그도 함께 기록
    background_tasks.add_task(
        write_audit_log,
        "NOTIFICATION_SENT",
        {"user_id": request.user_id, "channels": registered_tasks},
    )

    return {
        "message": "알림이 요청되었습니다",
        "user_id": request.user_id,
        "channels": registered_tasks,
        "total_tasks": len(registered_tasks) + 1,  # +1 감사 로그
    }


@app.post("/maintenance/cleanup", summary="임시 파일 정리")
async def trigger_cleanup(background_tasks: BackgroundTasks):
    """
    임시 파일 정리 작업을 백그라운드에서 실행합니다.
    """
    background_tasks.add_task(cleanup_temp_files, "uploads/temp", 24)

    background_tasks.add_task(
        write_audit_log,
        "CLEANUP_TRIGGERED",
        {"directory": "uploads/temp", "max_age_hours": 24},
    )

    return {
        "message": "임시 파일 정리가 요청되었습니다",
        "target_directory": "uploads/temp",
        "max_age_hours": 24,
    }


@app.get("/logs/audit", summary="감사 로그 조회")
async def get_audit_logs(date: str | None = None):
    """
    감사 로그를 조회합니다.
    date 파라미터가 없으면 오늘 날짜의 로그를 반환합니다.
    """
    if date is None:
        date = datetime.utcnow().strftime("%Y%m%d")

    log_file = LOG_DIR / f"audit_{date}.log"
    if not log_file.exists():
        return {"date": date, "entries": [], "message": "해당 날짜의 로그가 없습니다"}

    with open(log_file, "r", encoding="utf-8") as f:
        entries = f.readlines()

    return {
        "date": date,
        "total_entries": len(entries),
        "entries": [entry.strip() for entry in entries],
    }
