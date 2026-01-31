# FastAPI 참고 자료 (Expert - 고급)

## 공식 문서

| 자료 | URL | 설명 |
|------|-----|------|
| FastAPI 공식 문서 | https://fastapi.tiangolo.com | 공식 튜토리얼 및 레퍼런스 |
| FastAPI 고급 가이드 | https://fastapi.tiangolo.com/advanced/ | 심화 기능 가이드 |
| FastAPI 배포 가이드 | https://fastapi.tiangolo.com/deployment/ | 프로덕션 배포 가이드 |
| FastAPI GitHub | https://github.com/fastapi/fastapi | 소스 코드 및 이슈 |
| Starlette 공식 문서 | https://www.starlette.io/ | ASGI 프레임워크 (FastAPI 기반) |
| Pydantic v2 문서 | https://docs.pydantic.dev/latest/ | 데이터 검증 (v2 심화) |
| SQLAlchemy 2.0 문서 | https://docs.sqlalchemy.org/en/20/ | 비동기 ORM |
| ASGI 명세 | https://asgi.readthedocs.io/ | ASGI 프로토콜 공식 명세 |

## 모범 사례 및 아키텍처

| 자료 | URL | 설명 |
|------|-----|------|
| FastAPI Best Practices | https://github.com/zhanymkanov/fastapi-best-practices | 커뮤니티 모범 사례 모음 |
| FastAPI 프로덕션 배포 | https://render.com/articles/fastapi-production-deployment-best-practices | 프로덕션 배포 모범 사례 |
| FastAPI 성능 최적화 | https://leapcell.io/blog/fastapi-performance-hacks | 성능 최적화 10가지 방법 |
| FastAPI 풀스택 템플릿 | https://github.com/fastapi/full-stack-fastapi-template | 공식 풀스택 프로젝트 템플릿 |

## 심화 라이브러리 문서

| 라이브러리 | 용도 | URL |
|-----------|------|-----|
| asyncio | 비동기 프로그래밍 | https://docs.python.org/3/library/asyncio.html |
| httpx | 비동기 HTTP 클라이언트 | https://www.python-httpx.org/ |
| Redis (aioredis) | 비동기 Redis 클라이언트 | https://redis.readthedocs.io/ |
| Alembic | DB 마이그레이션 | https://alembic.sqlalchemy.org/ |
| OpenTelemetry | 분산 트레이싱 | https://opentelemetry.io/docs/ |
| Prometheus | 모니터링 메트릭 | https://prometheus.io/docs/ |
| structlog | 구조화된 로깅 | https://www.structlog.org/ |
| orjson | 고성능 JSON 직렬화 | https://github.com/ijl/orjson |
| Gunicorn | WSGI/ASGI 프로세스 매니저 | https://gunicorn.org/ |
| Docker | 컨테이너화 | https://docs.docker.com/ |

## 성능 벤치마킹 도구

| 도구 | 용도 | URL |
|------|------|-----|
| wrk | HTTP 벤치마킹 | https://github.com/wg/wrk |
| k6 | 부하 테스트 | https://k6.io/ |
| Locust | Python 기반 부하 테스트 | https://locust.io/ |
| py-spy | Python 프로파일러 | https://github.com/benfred/py-spy |

## 아키텍처 참고

| 자료 | URL | 설명 |
|------|-----|------|
| The Twelve-Factor App | https://12factor.net/ | 클라우드 네이티브 앱 설계 원칙 |
| Martin Fowler - Microservices | https://martinfowler.com/articles/microservices.html | 마이크로서비스 아키텍처 |
| Circuit Breaker Pattern | https://martinfowler.com/bliki/CircuitBreaker.html | 서킷 브레이커 패턴 |

## 추천 학습 순서

1. FastAPI 공식 Advanced User Guide 정독
2. 각 챕터의 `concept.md` → `example` → `exercise` 순서로 학습
3. FastAPI Best Practices 저장소 분석
4. 실제 프로덕션 프로젝트에 적용하며 학습
5. 성능 벤치마킹과 프로파일링 실습
