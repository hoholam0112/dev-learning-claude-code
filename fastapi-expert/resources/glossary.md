# FastAPI 용어 사전 (Expert - 고급)

## A

| 영어 | 한국어 | 설명 |
|------|--------|------|
| ASGI (Asynchronous Server Gateway Interface) | 비동기 서버 게이트웨이 인터페이스 | Python 비동기 웹 서버와 앱 사이의 표준 인터페이스. scope, receive, send 3개의 호출 규약으로 구성 |
| AsyncEngine | 비동기 엔진 | SQLAlchemy 2.0의 비동기 데이터베이스 엔진 |
| AsyncSession | 비동기 세션 | SQLAlchemy의 비동기 데이터베이스 세션 객체 |
| API Gateway | API 게이트웨이 | 마이크로서비스 앞단에서 라우팅, 인증, 속도 제한 등을 처리하는 진입점 |

## B

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Backpressure | 백프레셔 | 수신측이 처리 속도를 초과하는 데이터 유입을 제어하는 메커니즘 |
| Blue-Green Deployment | 블루-그린 배포 | 두 개의 동일한 환경을 교대로 사용하는 무중단 배포 전략 |
| Broadcast | 브로드캐스트 | 연결된 모든 클라이언트에게 동시에 메시지를 전송하는 방식 |

## C

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Cache-Aside Pattern | 캐시 어사이드 패턴 | 애플리케이션이 캐시와 DB를 직접 관리하는 캐싱 전략 |
| Circuit Breaker | 서킷 브레이커 | 연쇄 장애를 방지하기 위해 실패한 서비스 호출을 차단하는 패턴 |
| Connection Pool | 커넥션 풀 | 데이터베이스 연결을 재사용하기 위해 미리 생성해 둔 연결 집합 |
| Context Manager | 컨텍스트 매니저 | 리소스의 획득과 해제를 자동 관리하는 Python 프로토콜 (with/async with) |
| Coroutine | 코루틴 | async def로 정의된 비동기 함수, await로 실행을 양보할 수 있음 |
| CSRF (Cross-Site Request Forgery) | 사이트 간 요청 위조 | 인증된 사용자의 권한을 도용하여 악의적 요청을 보내는 공격 |

## D

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Discriminated Union | 판별 합집합 | 특정 필드 값으로 타입을 구분하는 Pydantic의 다형성 모델 패턴 |
| Distributed Tracing | 분산 트레이싱 | 마이크로서비스 간 요청 흐름을 추적하는 기법 (OpenTelemetry) |

## E

| 영어 | 한국어 | 설명 |
|------|--------|------|
| ETag | 엔티티 태그 | 리소스 버전을 식별하는 HTTP 헤더, 캐시 무효화에 사용 |
| Event Loop | 이벤트 루프 | asyncio의 핵심, 비동기 작업을 스케줄링하고 실행하는 루프 |
| Event-Driven Architecture | 이벤트 기반 아키텍처 | 이벤트의 발행과 구독으로 서비스 간 통신하는 설계 방식 |

## G

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Generic Model | 제네릭 모델 | 타입 파라미터를 받아 재사용 가능한 Pydantic 모델 (Generic[T]) |
| Graceful Shutdown | 정상 종료 | 진행 중인 요청을 모두 처리한 후 서버를 안전하게 종료하는 방식 |
| Gunicorn | Gunicorn | Python WSGI/ASGI 프로세스 매니저, 멀티 워커 관리 |

## H

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Heartbeat | 하트비트 | WebSocket 연결의 생존을 확인하기 위해 주기적으로 보내는 신호 |
| Health Check | 헬스 체크 | 서비스의 정상 동작 여부를 확인하는 엔드포인트 |
| Horizontal Scaling | 수평 확장 | 서버 인스턴스 수를 늘려 처리 용량을 확장하는 방식 |

## J

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Joinedload | 조인 로딩 | SQLAlchemy에서 JOIN으로 관련 데이터를 한 번에 로딩하는 전략 |

## L

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Lifespan Event | 수명 주기 이벤트 | FastAPI 앱의 시작/종료 시 실행되는 이벤트 (리소스 초기화/정리) |
| Load Balancer | 로드 밸런서 | 여러 서버 인스턴스에 트래픽을 분배하는 장치/소프트웨어 |

## M

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Message Queue | 메시지 큐 | 서비스 간 비동기 메시지를 전달하는 큐 시스템 (RabbitMQ, Kafka 등) |
| Middleware Stack | 미들웨어 스택 | 요청/응답을 순차적으로 처리하는 미들웨어의 계층 구조 (양파 모델) |
| Multi-Stage Build | 멀티 스테이지 빌드 | Docker에서 빌드와 실행 환경을 분리하여 이미지 크기를 줄이는 기법 |

## N

| 영어 | 한국어 | 설명 |
|------|--------|------|
| N+1 Problem | N+1 문제 | 관련 데이터를 조회할 때 1개의 쿼리 후 N개의 추가 쿼리가 발생하는 성능 문제 |

## O

| 영어 | 한국어 | 설명 |
|------|--------|------|
| OAuth2 Scopes | OAuth2 스코프 | 접근 토큰의 권한 범위를 세분화하여 정의하는 메커니즘 |
| OpenTelemetry | 오픈텔레메트리 | 분산 트레이싱, 메트릭, 로깅을 위한 관측 가능성 프레임워크 |
| Optimistic Locking | 낙관적 잠금 | 버전 번호로 동시 수정 충돌을 감지하는 데이터베이스 동시성 제어 방식 |

## P

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Pool Size | 풀 크기 | 커넥션 풀에서 유지하는 기본 연결 수 |
| Prometheus | 프로메테우스 | 시계열 데이터 기반의 모니터링 및 알림 시스템 |
| Pub/Sub | 발행/구독 | 메시지를 발행하고 구독자가 수신하는 비동기 메시징 패턴 |

## R

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Rate Limiting | 속도 제한 | 일정 시간 내 요청 수를 제한하여 서비스를 보호하는 기법 |
| RBAC (Role-Based Access Control) | 역할 기반 접근 제어 | 사용자 역할에 따라 리소스 접근 권한을 관리하는 방식 |
| Repository Pattern | 리포지토리 패턴 | 데이터 접근 로직을 비즈니스 로직과 분리하는 설계 패턴 |
| Rolling Update | 롤링 업데이트 | 서버 인스턴스를 하나씩 순차적으로 업데이트하는 배포 전략 |
| run_in_executor | 실행기에서 실행 | 동기 블로킹 코드를 스레드풀에서 비동기로 실행하는 방법 |

## S

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Savepoint | 세이브포인트 | 트랜잭션 내에서 중간 복원 지점을 설정하는 기능 |
| Scope (ASGI) | 스코프 | ASGI 요청의 메타데이터를 담는 딕셔너리 (type, path, method 등) |
| Selectinload | 선택적 로딩 | SQLAlchemy에서 별도 SELECT로 관련 데이터를 효율적으로 로딩하는 전략 |
| Semaphore | 세마포어 | 동시 접근 수를 제한하는 동기화 프리미티브 |
| Service Discovery | 서비스 디스커버리 | 마이크로서비스의 네트워크 위치를 동적으로 찾는 메커니즘 |
| SSE (Server-Sent Events) | 서버 전송 이벤트 | 서버에서 클라이언트로 단방향 실시간 데이터를 전송하는 HTTP 기반 프로토콜 |
| Streaming Response | 스트리밍 응답 | 데이터를 청크 단위로 나누어 전송하는 응답 방식 |
| Structured Logging | 구조화된 로깅 | 로그를 JSON 등 구조화된 형식으로 기록하는 방식 |

## T

| 영어 | 한국어 | 설명 |
|------|--------|------|
| TypeAdapter | 타입 어댑터 | Pydantic v2에서 모델 없이 타입 검증/직렬화를 수행하는 도구 |
| Thread Pool Executor | 스레드풀 실행기 | 동기 코드를 별도 스레드에서 실행하는 asyncio 메커니즘 |

## W

| 영어 | 한국어 | 설명 |
|------|--------|------|
| WebSocket | 웹소켓 | 클라이언트와 서버 간 양방향 실시간 통신을 위한 프로토콜 |
| Worker | 워커 | Gunicorn/Uvicorn에서 요청을 처리하는 프로세스 단위 |
| Write-Through Cache | 쓰기 관통 캐시 | 데이터 쓰기 시 캐시와 DB에 동시에 반영하는 캐싱 전략 |
