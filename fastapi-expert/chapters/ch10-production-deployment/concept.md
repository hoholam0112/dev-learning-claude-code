# 챕터 10: 프로덕션 배포와 운영

> **난이도**: ⭐⭐⭐⭐⭐ (5/5)
> **예상 학습 시간**: 5~6시간
> **사전 요구사항**: FastAPI 전반, Docker 기본, Linux 기본, CI/CD 개념

---

## 학습 목표

이 챕터를 완료하면 다음을 할 수 있습니다:

1. Docker 멀티 스테이지 빌드로 최적화된 이미지를 만든다
2. Gunicorn + Uvicorn 워커 설정을 최적화한다
3. pydantic-settings로 환경 변수를 체계적으로 관리한다
4. 구조화된 로깅(JSON)을 설정한다
5. Prometheus 메트릭을 구현한다
6. 프로덕션 수준의 헬스 체크 엔드포인트를 설계한다
7. GitHub Actions CI/CD 파이프라인을 구성한다
8. 무중단 배포 전략을 이해한다

---

## 1. Docker 최적화

### 1.1 멀티 스테이지 빌드

```mermaid
graph LR
    subgraph "스테이지 1: 빌더"
        B1[Python 3.12<br/>+ 빌드 도구] --> B2[의존성 설치<br/>pip install]
        B2 --> B3[.whl 파일<br/>생성]
    end

    subgraph "스테이지 2: 런타임"
        R1[Python 3.12-slim<br/>최소 이미지] --> R2[.whl 복사<br/>+ 설치]
        R2 --> R3[앱 코드<br/>복사]
        R3 --> R4[최종 이미지<br/>~150MB]
    end

    B3 -->|복사| R2
```

### 1.2 Dockerfile 최적화 원칙

```dockerfile
# ❌ 비최적화 Dockerfile (700MB+)
FROM python:3.12
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# ✅ 최적화 Dockerfile (~150MB)
# 스테이지 1: 의존성 빌드
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# 스테이지 2: 런타임
FROM python:3.12-slim
# 비root 사용자 생성
RUN adduser --disabled-password --no-create-home appuser
WORKDIR /app
# 의존성 복사
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages/
# 앱 코드 복사
COPY ./app /app
# 비root 사용자로 실행
USER appuser
EXPOSE 8000
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 1.3 이미지 크기 최적화 기법

| 기법 | 효과 |
|------|------|
| `python:3.12-slim` 사용 | 기본 ~1GB -> ~150MB |
| `--no-cache-dir` | pip 캐시 제거 |
| `.dockerignore` 활용 | 불필요한 파일 제외 |
| 멀티 스테이지 빌드 | 빌드 도구 제외 |
| 레이어 최소화 | RUN 명령 합치기 |
| 비root 사용자 | 보안 강화 |

---

## 2. Gunicorn + Uvicorn 워커 설정

### 2.1 아키텍처

```mermaid
graph TB
    Client[클라이언트] --> Nginx[Nginx<br/>리버스 프록시]
    Nginx --> Gunicorn[Gunicorn<br/>프로세스 매니저]

    subgraph "Gunicorn 워커 풀"
        W1[Uvicorn 워커 1]
        W2[Uvicorn 워커 2]
        W3[Uvicorn 워커 3]
        W4[Uvicorn 워커 4]
    end

    Gunicorn --> W1
    Gunicorn --> W2
    Gunicorn --> W3
    Gunicorn --> W4
```

### 2.2 워커 수 결정 공식

```python
# 공식: (2 * CPU 코어 수) + 1
# 예: 4코어 서버 -> 9 워커

# 또는 환경에 맞게 조정:
# CPU 바운드 작업이 많으면: CPU 코어 수
# I/O 바운드 작업이 많으면: (2~4) * CPU 코어 수
```

### 2.3 Gunicorn 설정 파일

```python
# gunicorn.conf.py
import multiprocessing

# 워커 설정
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# 타임아웃
timeout = 120            # 워커 응답 대기 시간
graceful_timeout = 30    # Graceful Shutdown 대기 시간
keepalive = 5            # Keep-Alive 연결 유지 시간

# 바인딩
bind = "0.0.0.0:8000"

# 로깅
accesslog = "-"          # stdout으로 출력
errorlog = "-"
loglevel = "info"

# 프리로딩 (메모리 절약)
preload_app = True

# 프로세스 이름
proc_name = "fastapi-app"
```

---

## 3. 환경 변수 관리 (pydantic-settings)

### 3.1 설정 클래스

```python
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    """앱 설정 (환경 변수에서 자동 로딩)"""

    # 앱 기본
    app_name: str = "FastAPI App"
    debug: bool = False
    environment: str = "production"

    # 데이터베이스
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="데이터베이스 연결 문자열",
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300

    # 보안
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",         # .env 파일에서 로딩
        "env_prefix": "APP_",       # 환경 변수 접두사
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤 (캐싱으로 매번 파싱하지 않음)"""
    return Settings()
```

### 3.2 환경별 설정

```bash
# .env.development
APP_DEBUG=true
APP_ENVIRONMENT=development
APP_DATABASE_URL=sqlite:///./dev.db
APP_SECRET_KEY=dev-secret

# .env.production
APP_DEBUG=false
APP_ENVIRONMENT=production
APP_DATABASE_URL=postgresql+asyncpg://user:pass@db-host/prod
APP_SECRET_KEY=super-long-random-secret-key-here
```

---

## 4. 구조화된 로깅

### 4.1 왜 구조화된 로깅인가?

```
# ❌ 일반 로그 (파싱 어려움)
2024-01-15 10:30:00 INFO Request received from 192.168.1.1 for GET /api/users took 45ms

# ✅ JSON 구조화 로그 (머신 파서블)
{"timestamp":"2024-01-15T10:30:00Z","level":"info","message":"request_completed",
 "method":"GET","path":"/api/users","status":200,"duration_ms":45,"client_ip":"192.168.1.1",
 "trace_id":"abc123","request_id":"req-456"}
```

### 4.2 structlog 설정

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),  # JSON 출력
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
```

### 4.3 로그 레벨 가이드라인

| 레벨 | 사용 시기 | 예시 |
|------|----------|------|
| DEBUG | 개발 시 상세 정보 | 쿼리 파라미터, 변수 값 |
| INFO | 정상 동작 기록 | 요청 처리 완료, 사용자 로그인 |
| WARNING | 잠재적 문제 | 느린 쿼리, 재시도 발생 |
| ERROR | 오류 발생 | 외부 서비스 실패, 예외 |
| CRITICAL | 시스템 장애 | DB 연결 불가, 메모리 부족 |

---

## 5. 모니터링 (Prometheus 메트릭)

### 5.1 핵심 메트릭 (RED 방법론)

```mermaid
graph LR
    subgraph "RED 메트릭"
        R[Rate<br/>초당 요청 수]
        E[Errors<br/>에러 비율]
        D[Duration<br/>응답 시간]
    end

    subgraph "USE 메트릭 (리소스)"
        U[Utilization<br/>사용률]
        S[Saturation<br/>포화도]
        ER[Errors<br/>에러 수]
    end
```

### 5.2 Prometheus 메트릭 타입

| 타입 | 설명 | 예시 |
|------|------|------|
| Counter | 단조 증가 | 총 요청 수, 총 에러 수 |
| Gauge | 증가/감소 | 현재 연결 수, 메모리 사용량 |
| Histogram | 분포 측정 | 응답 시간 분포 |
| Summary | 분위수 측정 | p50, p95, p99 응답 시간 |

---

## 6. 헬스 체크 엔드포인트

### 6.1 계층별 헬스 체크

```python
@app.get("/health/live")
async def liveness():
    """Liveness: 프로세스 생존 확인 (쿠버네티스)"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Readiness: 서비스 준비 상태 (의존성 확인)"""
    checks = {}
    checks["database"] = await check_database()
    checks["redis"] = await check_redis()
    checks["disk_space"] = check_disk_space()

    all_healthy = all(v["healthy"] for v in checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
```

---

## 7. CI/CD 파이프라인

### 7.1 GitHub Actions 워크플로우

```mermaid
graph LR
    Push[코드 Push] --> Test[테스트 실행]
    Test --> Lint[린트/포맷팅]
    Lint --> Build[Docker 빌드]
    Build --> Scan[보안 스캔]
    Scan --> Push2[이미지 Push]
    Push2 --> Deploy[배포]
```

### 7.2 워크플로우 파일 구조

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest --cov=app tests/

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Docker 빌드 및 푸시
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push myapp:${{ github.sha }}
      - name: 배포
        run: |
          # kubectl, docker-compose, 또는 클라우드 CLI 사용
          echo "배포 실행"
```

---

## 8. 무중단 배포

### 8.1 배포 전략 비교

```mermaid
graph TB
    subgraph "Rolling Update"
        R1[v1 Pod] -->|순차 교체| R2[v2 Pod]
        R3[v1 Pod] -->|순차 교체| R4[v2 Pod]
        R5[v1 Pod] -->|순차 교체| R6[v2 Pod]
    end
```

| 전략 | 다운타임 | 리소스 | 롤백 속도 | 적합한 경우 |
|------|---------|--------|----------|------------|
| Rolling Update | 없음 | 1x | 느림 | 일반적 배포 |
| Blue-Green | 없음 | 2x | 즉시 | 높은 안정성 필요 |
| Canary | 없음 | 1.x | 빠름 | 점진적 검증 |

### 8.2 Graceful Shutdown

```python
import signal
import asyncio

class GracefulShutdown:
    """
    Graceful Shutdown 핸들러.
    SIGTERM 수신 시 진행 중인 요청을 완료한 후 종료합니다.
    """

    def __init__(self):
        self.is_shutting_down = False

    def setup(self):
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum, frame):
        self.is_shutting_down = True
```

---

## 프로덕션 배포 체크리스트

```
[보안]
  [ ] DEBUG=False
  [ ] SECRET_KEY를 환경 변수로 관리
  [ ] CORS 설정 최소화
  [ ] HTTPS 강제 (TLS)
  [ ] 비root 사용자로 실행
  [ ] 보안 헤더 설정 (HSTS, CSP 등)

[성능]
  [ ] Gunicorn + Uvicorn 워커 수 최적화
  [ ] 커넥션 풀 설정
  [ ] Redis 캐시 레이어
  [ ] 응답 압축 (GZip)
  [ ] 정적 파일은 CDN 또는 Nginx에서 서빙

[안정성]
  [ ] 헬스 체크 엔드포인트 (liveness + readiness)
  [ ] Graceful Shutdown 구현
  [ ] 서킷 브레이커 적용
  [ ] 재시도 + 백오프 전략

[모니터링]
  [ ] 구조화된 로깅 (JSON)
  [ ] Prometheus 메트릭 익스포터
  [ ] 분산 트레이싱
  [ ] 에러 추적 (Sentry 등)
  [ ] 알림 설정 (PagerDuty, Slack 등)

[배포]
  [ ] Docker 멀티 스테이지 빌드
  [ ] CI/CD 파이프라인
  [ ] 무중단 배포 전략
  [ ] 롤백 절차 문서화
  [ ] 환경별 설정 분리
```

---

## 정리

| 개념 | 핵심 포인트 |
|------|------------|
| Docker | 멀티 스테이지, slim 베이스, 비root 사용자, ~150MB 목표 |
| Gunicorn | 워커 수 = 코어*2+1, UvicornWorker, preload_app |
| 설정 관리 | pydantic-settings, .env 파일, lru_cache 싱글톤 |
| 로깅 | JSON 구조화, structlog, 로그 레벨 정책 |
| 메트릭 | RED (Rate/Error/Duration), Prometheus, Grafana |
| 헬스 체크 | liveness/readiness 분리, 의존성별 확인 |
| CI/CD | GitHub Actions, 테스트->빌드->배포 파이프라인 |
| 무중단 배포 | Rolling Update, Graceful Shutdown |

---

## 마무리

이 챕터로 FastAPI Expert 시리즈의 챕터 6~10을 완료했습니다. 데이터베이스 최적화부터 프로덕션 배포까지, 실무에서 필요한 핵심 기술을 다루었습니다.

다음 학습 추천:
- Kubernetes 환경에서 FastAPI 운영
- 서비스 메시(Istio, Linkerd) 적용
- Observability 심화 (Jaeger, Grafana, ELK)
- 로드 테스팅과 카오스 엔지니어링
- API 게이트웨이 (Kong, Traefik) 활용
