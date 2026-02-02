# sec03: 백그라운드 작업 (Background Tasks)

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: sec01 async/await 기본 완료
> **예상 학습 시간**: 40~50분

---

## 학습 목표

- `BackgroundTasks`를 사용하여 응답 후 실행되는 작업을 구현할 수 있다
- 하나의 엔드포인트에 여러 백그라운드 작업을 추가할 수 있다
- 의존성에서 백그라운드 작업을 추가하는 패턴을 활용할 수 있다

---

## 핵심 개념

### 1. BackgroundTasks란?

`BackgroundTasks`는 **응답을 먼저 반환한 후** 백그라운드에서 실행되는 작업을 정의하는 클래스입니다.
사용자에게 빠르게 응답하면서도, 시간이 걸리는 작업(이메일 발송, 로그 기록 등)을 처리할 수 있습니다.

```
일반 처리:
요청 → [이메일 발송 (3초)] → 응답 반환 (총 3초 대기)

BackgroundTasks 사용:
요청 → 응답 반환 (즉시!) → [백그라운드에서 이메일 발송]
```

### 2. 기본 사용법

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


def write_log(message: str):
    """백그라운드에서 실행될 함수"""
    # 파일 쓰기, DB 저장, 이메일 발송 등
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")


@app.post("/items")
async def create_item(name: str, background_tasks: BackgroundTasks):
    """아이템 생성 후, 백그라운드에서 로그를 기록합니다."""
    # 백그라운드 작업 등록
    background_tasks.add_task(write_log, f"아이템 생성: {name}")

    # 즉시 응답 반환 (로그 기록은 백그라운드에서 진행)
    return {"message": f"아이템 '{name}' 생성됨", "status": "ok"}
```

### 3. BackgroundTasks.add_task()

`add_task(func, *args, **kwargs)` 메서드로 백그라운드 작업을 등록합니다.

| 매개변수 | 설명 |
|---------|------|
| `func` | 실행할 함수 (일반 함수 또는 async 함수) |
| `*args` | 함수에 전달할 위치 인자 |
| `**kwargs` | 함수에 전달할 키워드 인자 |

```python
# 일반 함수 등록
background_tasks.add_task(write_log, "메시지")

# async 함수도 등록 가능
async def send_email(to: str, subject: str):
    await asyncio.sleep(2)  # 이메일 발송 시뮬레이션

background_tasks.add_task(send_email, "user@example.com", subject="가입 환영")
```

### 4. 여러 백그라운드 작업 추가

하나의 엔드포인트에서 여러 백그라운드 작업을 등록할 수 있습니다.
작업들은 **등록된 순서대로** 실행됩니다.

```python
@app.post("/register")
async def register_user(name: str, background_tasks: BackgroundTasks):
    """사용자 등록 후, 여러 백그라운드 작업을 실행합니다."""

    # 작업 1: 환영 이메일 발송
    background_tasks.add_task(send_welcome_email, name)

    # 작업 2: 관리자 알림
    background_tasks.add_task(notify_admin, f"신규 가입: {name}")

    # 작업 3: 로그 기록
    background_tasks.add_task(write_log, f"사용자 등록: {name}")

    return {"message": f"'{name}' 등록 완료"}
    # 응답 후 작업 1 → 작업 2 → 작업 3 순서대로 실행
```

### 5. 의존성에서 백그라운드 작업 추가

`BackgroundTasks`는 의존성 함수에서도 사용할 수 있습니다.
이를 통해 공통 백그라운드 로직을 여러 엔드포인트에서 재사용할 수 있습니다.

```python
from fastapi import Depends

def audit_logger(background_tasks: BackgroundTasks):
    """감사 로그를 기록하는 의존성"""
    def log(action: str):
        background_tasks.add_task(write_log, f"[감사] {action}")
    return log

@app.post("/items")
async def create_item(
    name: str,
    logger = Depends(audit_logger),
    background_tasks: BackgroundTasks = None,
):
    logger(f"아이템 생성: {name}")
    return {"message": f"아이템 '{name}' 생성됨"}
```

> **핵심**: FastAPI는 엔드포인트와 의존성에서 **같은 `BackgroundTasks` 인스턴스**를 공유합니다.
> 따라서 의존성에서 추가한 작업과 엔드포인트에서 추가한 작업이 모두 실행됩니다.

---

## 코드 예제 1: 기본 백그라운드 작업

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

# 로그 저장용 리스트 (실제로는 파일이나 DB 사용)
task_log = []


def write_log(message: str):
    """로그를 기록하는 백그라운드 함수"""
    task_log.append(message)


@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks,
):
    """알림 발송 후 로그를 백그라운드에서 기록"""
    background_tasks.add_task(write_log, f"알림 발송: {email}")
    return {"message": f"'{email}'에 알림 발송 예정"}
```

---

## 코드 예제 2: 다중 백그라운드 작업

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

task_log = []


def log_step(step: str):
    task_log.append(step)


@app.post("/order")
async def create_order(
    item: str,
    background_tasks: BackgroundTasks,
):
    """주문 생성 후 여러 후처리를 백그라운드에서 실행"""
    background_tasks.add_task(log_step, f"주문 확인: {item}")
    background_tasks.add_task(log_step, f"재고 차감: {item}")
    background_tasks.add_task(log_step, f"알림 발송: {item}")

    return {"message": f"주문 완료: {item}"}
    # 응답 후: 주문 확인 → 재고 차감 → 알림 발송 순서로 실행
```

---

## BackgroundTasks 사용 시 주의사항

### 1. 가벼운 작업에 적합

`BackgroundTasks`는 같은 프로세스 내에서 실행됩니다.
CPU 집약적이거나 매우 오래 걸리는 작업에는 **Celery** 같은 별도 작업 큐를 사용하세요.

| 사용 사례 | 적합한 도구 |
|-----------|------------|
| 이메일 발송, 로그 기록 | `BackgroundTasks` |
| 파일 업로드 후처리 | `BackgroundTasks` |
| 대용량 데이터 처리 | Celery, RQ |
| 정기 스케줄 작업 | Celery Beat, APScheduler |

### 2. 에러 처리

백그라운드 작업에서 발생한 예외는 클라이언트에게 전달되지 않습니다.
중요한 작업은 try/except로 감싸고, 실패 로그를 남기세요.

```python
def important_task(data: str):
    try:
        # 중요한 처리...
        pass
    except Exception as e:
        # 에러 로깅 (클라이언트에게는 전달되지 않음)
        print(f"백그라운드 작업 실패: {e}")
```

### 3. 응답 상태와 무관

백그라운드 작업의 성공/실패는 HTTP 응답 상태 코드에 영향을 주지 않습니다.
응답은 이미 클라이언트에게 전송된 후이기 때문입니다.

---

## 핵심 정리

1. `BackgroundTasks`는 응답을 먼저 반환하고 이후에 작업을 실행한다
2. `add_task(func, *args, **kwargs)`로 백그라운드 작업을 등록한다
3. 여러 작업을 등록하면 **등록 순서대로** 실행된다
4. 의존성에서도 `BackgroundTasks`를 사용할 수 있다
5. 가벼운 I/O 작업에 적합하며, 무거운 작업은 Celery 등을 사용한다

---

## 다음 단계

- `exercise.md`를 확인하고 연습 문제를 풀어보세요.
- 다음 챕터: Ch10 로깅
