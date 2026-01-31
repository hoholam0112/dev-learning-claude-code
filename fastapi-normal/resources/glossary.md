# FastAPI 용어 사전 (Normal - 초중급)

## A

| 영어 | 한국어 | 설명 |
|------|--------|------|
| API (Application Programming Interface) | 응용 프로그래밍 인터페이스 | 소프트웨어 간 데이터를 주고받기 위한 인터페이스 |
| ASGI (Asynchronous Server Gateway Interface) | 비동기 서버 게이트웨이 인터페이스 | Python 비동기 웹 서버와 앱 사이의 표준 인터페이스 |
| Authentication | 인증 | 사용자의 신원을 확인하는 과정 |
| Authorization | 인가 | 인증된 사용자의 접근 권한을 확인하는 과정 |
| async/await | 비동기 키워드 | Python에서 비동기 코드를 작성하기 위한 키워드 |

## B

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Background Task | 백그라운드 작업 | 응답 후 서버에서 비동기로 실행되는 작업 |
| BaseModel | 기본 모델 | Pydantic의 데이터 모델 기본 클래스 |
| Bearer Token | 베어러 토큰 | HTTP 인증에서 사용하는 접근 토큰 형식 |

## C

| 영어 | 한국어 | 설명 |
|------|--------|------|
| CORS (Cross-Origin Resource Sharing) | 교차 출처 리소스 공유 | 다른 도메인에서의 API 접근을 제어하는 보안 메커니즘 |
| CRUD | 생성/조회/수정/삭제 | Create, Read, Update, Delete의 약자 |

## D

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Dependency Injection | 의존성 주입 | 객체가 필요로 하는 의존성을 외부에서 제공하는 설계 패턴 |
| Depends | 의존성 함수 | FastAPI에서 의존성을 선언하는 함수 |
| Decorator | 데코레이터 | 함수나 클래스를 수정하는 Python 문법 (@기호) |

## E

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Endpoint | 엔드포인트 | API에서 특정 URL 경로와 HTTP 메서드의 조합 |
| Exception Handler | 예외 핸들러 | 오류 발생 시 처리를 담당하는 함수 |

## F

| 영어 | 한국어 | 설명 |
|------|--------|------|
| FastAPI | FastAPI | Python 기반 고성능 웹 프레임워크 |
| Field | 필드 | Pydantic 모델의 속성을 정의하고 검증하는 함수 |
| Form Data | 폼 데이터 | HTML 폼에서 전송되는 데이터 (application/x-www-form-urlencoded) |

## H

| 영어 | 한국어 | 설명 |
|------|--------|------|
| HTTP Method | HTTP 메서드 | GET, POST, PUT, DELETE 등 요청의 종류 |
| HTTPException | HTTP 예외 | FastAPI에서 HTTP 에러 응답을 반환하기 위한 예외 클래스 |
| Hashing | 해싱 | 데이터를 고정 길이의 문자열로 변환하는 단방향 암호화 |

## J

| 영어 | 한국어 | 설명 |
|------|--------|------|
| JSON (JavaScript Object Notation) | JSON | 데이터 교환을 위한 경량 텍스트 형식 |
| JWT (JSON Web Token) | JWT 토큰 | JSON 기반의 인증 토큰 표준 |

## M

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Middleware | 미들웨어 | 요청과 응답 사이에서 동작하는 처리 계층 |
| Migration | 마이그레이션 | 데이터베이스 스키마를 버전 관리하며 변경하는 과정 |
| Model | 모델 | 데이터의 구조와 검증 규칙을 정의하는 클래스 |

## O

| 영어 | 한국어 | 설명 |
|------|--------|------|
| OAuth2 | OAuth2 | 인증/인가를 위한 개방형 표준 프로토콜 |
| OpenAPI | OpenAPI | REST API를 기술하기 위한 표준 명세 |
| ORM (Object-Relational Mapping) | 객체-관계 매핑 | 객체와 데이터베이스 테이블을 매핑하는 기술 |

## P

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Path Parameter | 경로 파라미터 | URL 경로에 포함되는 변수 (/items/{item_id}) |
| Pydantic | Pydantic | Python 데이터 검증 및 설정 관리 라이브러리 |
| Path Operation | 경로 작업 | 특정 HTTP 메서드와 경로의 조합으로 정의된 API 함수 |

## Q

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Query Parameter | 쿼리 파라미터 | URL의 ? 뒤에 오는 키=값 쌍 (?skip=0&limit=10) |

## R

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Request Body | 요청 본문 | HTTP 요청에 포함되는 데이터 (주로 JSON) |
| Response Model | 응답 모델 | API 응답 데이터의 구조를 정의하는 Pydantic 모델 |
| REST (Representational State Transfer) | REST | 웹 API 설계를 위한 아키텍처 스타일 |

## S

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Schema | 스키마 | 데이터의 구조와 규칙을 정의한 명세 |
| Session | 세션 | 데이터베이스와의 연결을 관리하는 객체 |
| SQLAlchemy | SQLAlchemy | Python SQL 도구킷 및 ORM 라이브러리 |
| Status Code | 상태 코드 | HTTP 응답의 처리 결과를 나타내는 숫자 (200, 404 등) |
| Swagger UI | Swagger UI | OpenAPI 기반의 대화형 API 문서 인터페이스 |

## T

| 영어 | 한국어 | 설명 |
|------|--------|------|
| TestClient | 테스트 클라이언트 | API를 테스트하기 위한 가상 HTTP 클라이언트 |
| Type Hint | 타입 힌트 | Python 변수의 타입을 명시하는 표기법 |
| Token | 토큰 | 인증 정보를 담은 문자열 |

## U

| 영어 | 한국어 | 설명 |
|------|--------|------|
| UploadFile | 업로드 파일 | FastAPI에서 파일 업로드를 처리하는 클래스 |
| Uvicorn | Uvicorn | Python ASGI 웹 서버 |

## V

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Validation | 유효성 검증 | 데이터가 정의된 규칙에 맞는지 확인하는 과정 |
| Validator | 검증기 | 데이터 유효성을 검사하는 함수 |

## W

| 영어 | 한국어 | 설명 |
|------|--------|------|
| WSGI (Web Server Gateway Interface) | 웹 서버 게이트웨이 인터페이스 | Python 동기 웹 서버와 앱 사이의 표준 인터페이스 |
