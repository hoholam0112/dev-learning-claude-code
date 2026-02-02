# 참고 자료 (References)

FastAPI 학습에 도움이 되는 공식 문서와 참고 자료를 정리했습니다.

---

## 공식 문서

### FastAPI

| 자료 | URL | 설명 |
|------|-----|------|
| FastAPI 공식 문서 | https://fastapi.tiangolo.com/ | 튜토리얼, API 레퍼런스, 고급 사용법 |
| FastAPI GitHub | https://github.com/tiangolo/fastapi | 소스 코드, 이슈, 릴리스 노트 |
| FastAPI 튜토리얼 (한국어) | https://fastapi.tiangolo.com/ko/ | 공식 한국어 번역 문서 |

### Pydantic

| 자료 | URL | 설명 |
|------|-----|------|
| Pydantic 공식 문서 | https://docs.pydantic.dev/ | 모델 정의, 유효성 검사, 설정 관리 |
| Pydantic V2 마이그레이션 | https://docs.pydantic.dev/latest/migration/ | V1에서 V2로의 변경 사항 |

### SQLAlchemy

| 자료 | URL | 설명 |
|------|-----|------|
| SQLAlchemy 공식 문서 | https://docs.sqlalchemy.org/ | ORM 튜토리얼, 엔진, 세션, 관계 매핑 |
| SQLAlchemy 2.0 스타일 | https://docs.sqlalchemy.org/en/20/changelog/migration_20.html | 2.0 스타일 쿼리 가이드 |

### Starlette

| 자료 | URL | 설명 |
|------|-----|------|
| Starlette 공식 문서 | https://www.starlette.io/ | FastAPI의 기반 프레임워크 |

### Uvicorn

| 자료 | URL | 설명 |
|------|-----|------|
| Uvicorn 공식 문서 | https://www.uvicorn.org/ | ASGI 서버 설정 및 배포 |

---

## 챕터별 참고 자료

### Ch01: FastAPI 시작하기

- [FastAPI 첫 번째 단계](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [Python 타입 힌트 소개](https://fastapi.tiangolo.com/python-types/)
- [Uvicorn 실행 옵션](https://www.uvicorn.org/settings/)

### Ch02: 경로 매개변수와 쿼리 매개변수

- [경로 매개변수](https://fastapi.tiangolo.com/tutorial/path-params/)
- [쿼리 매개변수](https://fastapi.tiangolo.com/tutorial/query-params/)
- [경로 매개변수와 수치 검증](https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/)
- [쿼리 매개변수와 문자열 검증](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)

### Ch03: 요청 본문

- [요청 본문](https://fastapi.tiangolo.com/tutorial/body/)
- [본문 - 중첩 모델](https://fastapi.tiangolo.com/tutorial/body-nested-models/)
- [요청 폼과 파일](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/)
- [Pydantic Field](https://docs.pydantic.dev/latest/concepts/fields/)

### Ch04: 응답 모델과 상태 코드

- [응답 모델](https://fastapi.tiangolo.com/tutorial/response-model/)
- [응답 상태 코드](https://fastapi.tiangolo.com/tutorial/response-status-code/)
- [추가 응답](https://fastapi.tiangolo.com/advanced/additional-responses/)

### Ch05: 의존성 주입

- [의존성 주입 - 첫 번째 단계](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [의존성 주입 - yield를 사용한 의존성](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [하위 의존성](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/)

### Ch06: 미들웨어와 CORS

- [미들웨어](https://fastapi.tiangolo.com/tutorial/middleware/)
- [CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [고급 미들웨어](https://fastapi.tiangolo.com/advanced/middleware/)
- [Starlette BaseHTTPMiddleware](https://www.starlette.io/middleware/#basehttpmiddleware)
- [MDN - CORS](https://developer.mozilla.org/ko/docs/Web/HTTP/CORS)

### Ch07: 데이터베이스 연동

- [FastAPI SQL 데이터베이스](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy ORM 튜토리얼](https://docs.sqlalchemy.org/en/20/tutorial/)
- [SQLAlchemy 관계 매핑](https://docs.sqlalchemy.org/en/20/orm/relationships.html)

### Ch08: 인증과 보안

- [보안 - 첫 번째 단계](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 with Password](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [python-jose (JWT)](https://github.com/mpdavis/python-jose)
- [passlib (비밀번호 해싱)](https://passlib.readthedocs.io/)

---

## 추가 학습 자료

### Python 기초

| 자료 | URL | 설명 |
|------|-----|------|
| Python 공식 튜토리얼 | https://docs.python.org/ko/3/tutorial/ | Python 기초 문법 |
| Python 타입 힌트 (PEP 484) | https://peps.python.org/pep-0484/ | 타입 어노테이션 명세 |
| async/await 이해하기 | https://docs.python.org/ko/3/library/asyncio.html | 비동기 프로그래밍 |

### HTTP 기초

| 자료 | URL | 설명 |
|------|-----|------|
| MDN HTTP 개요 | https://developer.mozilla.org/ko/docs/Web/HTTP/Overview | HTTP 프로토콜 기초 |
| HTTP 상태 코드 | https://developer.mozilla.org/ko/docs/Web/HTTP/Status | 상태 코드 레퍼런스 |
| REST API 디자인 | https://restfulapi.net/ | RESTful API 설계 원칙 |

### 도구

| 도구 | URL | 설명 |
|------|-----|------|
| Swagger UI | https://swagger.io/tools/swagger-ui/ | API 문서 및 테스트 UI |
| Postman | https://www.postman.com/ | API 테스트 클라이언트 |
| httpie | https://httpie.io/ | 커맨드라인 HTTP 클라이언트 |
| DB Browser for SQLite | https://sqlitebrowser.org/ | SQLite 데이터베이스 뷰어 |

---

## 커뮤니티

| 커뮤니티 | URL | 설명 |
|----------|-----|------|
| FastAPI GitHub Discussions | https://github.com/tiangolo/fastapi/discussions | 공식 Q&A |
| Stack Overflow [fastapi] | https://stackoverflow.com/questions/tagged/fastapi | Q&A |
| FastAPI Discord | https://discord.gg/fastapi | 실시간 채팅 커뮤니티 |
