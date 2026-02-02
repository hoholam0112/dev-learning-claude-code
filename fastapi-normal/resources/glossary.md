# 용어 사전 (Glossary)

FastAPI 학습 과정에서 자주 등장하는 용어를 정리했습니다.
각 용어는 처음 등장하는 챕터를 함께 표기했습니다.

---

## A

### API (Application Programming Interface)
소프트웨어 간의 상호작용을 정의하는 인터페이스. 웹 API는 HTTP를 통해 데이터를 주고받는 방식을 정의합니다. (Ch01)

### ASGI (Asynchronous Server Gateway Interface)
Python 비동기 웹 서버와 프레임워크 간의 표준 인터페이스. FastAPI는 ASGI 기반 프레임워크입니다. (Ch01)

### async/await
Python의 비동기 프로그래밍 키워드. `async def`로 비동기 함수를 정의하고, `await`로 비동기 작업을 기다립니다. (Ch01)

---

## B

### BaseModel
Pydantic의 기본 모델 클래스. 데이터 검증과 직렬화를 자동으로 처리합니다. (Ch03)

### BaseHTTPMiddleware
Starlette에서 제공하는 클래스 기반 미들웨어의 부모 클래스. `dispatch` 메서드를 오버라이드하여 커스텀 미들웨어를 구현합니다. (Ch06)

### back_populates
SQLAlchemy에서 양방향 관계를 설정할 때 사용하는 매개변수. 양쪽 모델에서 서로를 참조할 수 있게 합니다. (Ch07)

---

## C

### CORS (Cross-Origin Resource Sharing)
웹 브라우저에서 서로 다른 출처(Origin) 간의 리소스 공유를 허용하는 HTTP 메커니즘. 프론트엔드-백엔드 통신에 필수적입니다. (Ch06)

### CRUD
데이터베이스의 4가지 기본 작업: Create(생성), Read(조회), Update(수정), Delete(삭제). (Ch07)

### call_next
FastAPI 미들웨어에서 요청을 다음 미들웨어 또는 라우트 핸들러로 전달하는 함수. (Ch06)

### Column
SQLAlchemy에서 데이터베이스 테이블의 컬럼(열)을 정의하는 클래스. (Ch07)

### ConfigDict
Pydantic V2에서 모델 설정을 정의하는 딕셔너리. `from_attributes=True` 등의 옵션을 설정합니다. (Ch04)

### commit()
SQLAlchemy 세션에서 트랜잭션을 확정하여 데이터베이스에 변경사항을 반영하는 메서드. (Ch07)

---

## D

### Depends
FastAPI의 의존성 주입 함수. 엔드포인트 함수의 매개변수에 `Depends(함수)`를 사용하여 의존성을 주입합니다. (Ch05)

### declarative_base()
SQLAlchemy에서 모든 ORM 모델의 부모 클래스를 생성하는 함수. (Ch07)

---

## E

### Endpoint (엔드포인트)
API에서 특정 URL 경로와 HTTP 메서드의 조합으로 정의되는 접근 지점. 예: `GET /users`, `POST /items`. (Ch01)

### Engine (엔진)
SQLAlchemy에서 데이터베이스와의 연결 풀(Connection Pool)을 관리하는 객체. `create_engine()`으로 생성합니다. (Ch07)

---

## F

### FastAPI
Python 기반의 고성능 웹 프레임워크. 타입 힌트를 활용하여 자동 문서 생성, 데이터 검증 등을 제공합니다. (Ch01)

### Field
Pydantic에서 모델 필드의 메타데이터와 검증 규칙을 정의하는 함수. `min_length`, `ge`, `description` 등을 설정합니다. (Ch03)

### File()
FastAPI에서 파일 업로드를 처리하기 위한 함수. `UploadFile`과 함께 사용합니다. (Ch03)

### Form()
FastAPI에서 HTML 폼 데이터를 수신하기 위한 함수. `application/x-www-form-urlencoded` 또는 `multipart/form-data` 형식을 처리합니다. (Ch03)

### ForeignKey (외래키)
데이터베이스에서 다른 테이블의 기본키를 참조하는 컬럼. 테이블 간 관계를 설정하는 데 사용합니다. (Ch07)

### from_attributes
Pydantic V2의 설정 옵션. `True`로 설정하면 SQLAlchemy 모델 객체를 Pydantic 모델로 자동 변환할 수 있습니다. (Ch04)

---

## G

### get_db
FastAPI에서 데이터베이스 세션을 관리하는 의존성 함수. `yield` 패턴을 사용하여 세션의 생성과 종료를 안전하게 처리합니다. (Ch07)

---

## H

### HTTP 메서드
웹 요청의 종류를 나타내는 동사. GET(조회), POST(생성), PUT(전체 수정), PATCH(부분 수정), DELETE(삭제) 등이 있습니다. (Ch01)

### HTTPException
FastAPI에서 HTTP 에러 응답을 반환하기 위한 예외 클래스. `status_code`와 `detail`을 지정합니다. (Ch04)

---

## J

### JSON (JavaScript Object Notation)
경량 데이터 교환 형식. API 요청/응답의 표준 데이터 형식으로 사용됩니다. (Ch01)

### JWT (JSON Web Token)
사용자 인증 정보를 안전하게 전달하기 위한 토큰 형식. Header, Payload, Signature로 구성됩니다. (Ch08)

### joinedload
SQLAlchemy에서 관계 데이터를 미리 함께 로드(Eager Loading)하는 방법. N+1 쿼리 문제를 방지합니다. (Ch07)

---

## L

### Lazy Loading (지연 로딩)
SQLAlchemy의 기본 관계 데이터 로딩 방식. 관계 속성에 실제로 접근할 때 쿼리가 실행됩니다. (Ch07)

---

## M

### Middleware (미들웨어)
요청이 라우트 핸들러에 도달하기 전과 응답이 반환되기 전에 공통 로직을 수행하는 메커니즘. 로깅, 인증, CORS 등에 사용됩니다. (Ch06)

### model_dump()
Pydantic V2에서 모델 객체를 딕셔너리로 변환하는 메서드. V1의 `.dict()`를 대체합니다. (Ch03)

### multipart/form-data
파일 업로드 시 사용되는 HTTP Content-Type. Form 데이터와 파일을 동시에 전송할 수 있습니다. (Ch03)

---

## O

### ORM (Object-Relational Mapping)
데이터베이스 테이블을 프로그래밍 언어의 객체로 매핑하는 기술. SQL을 직접 작성하지 않고 객체를 통해 데이터베이스를 조작합니다. (Ch07)

### OAuth2
인증과 인가를 위한 산업 표준 프로토콜. FastAPI는 OAuth2 Password Bearer 방식을 지원합니다. (Ch08)

### Origin (출처)
URL의 프로토콜 + 호스트 + 포트의 조합. CORS에서 출처가 같은지 다른지를 판단하는 기준입니다. (Ch06)

---

## P

### Path Parameter (경로 매개변수)
URL 경로의 일부로 전달되는 변수. 예: `/users/{user_id}`에서 `user_id`. (Ch02)

### Path()
FastAPI에서 경로 매개변수의 검증 규칙과 메타데이터를 정의하는 함수. (Ch02)

### Pydantic
Python의 데이터 검증 라이브러리. 타입 힌트를 기반으로 데이터 유효성 검사와 직렬화를 수행합니다. (Ch03)

### Preflight 요청
브라우저가 실제 요청을 보내기 전에 OPTIONS 메서드로 서버에 사전 확인하는 CORS 메커니즘. (Ch06)

---

## Q

### Query Parameter (쿼리 매개변수)
URL의 `?` 뒤에 `key=value` 형식으로 전달되는 변수. 예: `/items?skip=0&limit=10`. (Ch02)

### Query()
FastAPI에서 쿼리 매개변수의 검증 규칙과 메타데이터를 정의하는 함수. (Ch02)

---

## R

### REST (Representational State Transfer)
웹 API 설계를 위한 아키텍처 스타일. 리소스를 URL로 표현하고 HTTP 메서드로 조작합니다. (Ch01)

### relationship()
SQLAlchemy에서 Python 코드 레벨에서 관련 객체에 접근할 수 있게 해주는 함수. ForeignKey와 함께 사용합니다. (Ch07)

### response_model
FastAPI 엔드포인트에서 응답 데이터의 형식을 지정하는 매개변수. Pydantic 모델을 사용하여 응답을 직렬화하고 문서를 생성합니다. (Ch04)

### Route (라우트)
URL 경로와 HTTP 메서드를 특정 함수에 매핑하는 것. `@app.get("/items")`과 같은 데코레이터로 정의합니다. (Ch01)

---

## S

### Session (세션)
SQLAlchemy에서 데이터베이스 작업의 단위. 트랜잭션을 관리하고, 객체의 상태를 추적합니다. (Ch07)

### sessionmaker
SQLAlchemy에서 세션 객체를 생성하는 팩토리 함수. (Ch07)

### SQLAlchemy
Python에서 가장 널리 사용되는 ORM 라이브러리. SQL을 직접 작성하지 않고 Python 객체로 데이터베이스를 조작합니다. (Ch07)

### SQLite
파일 기반의 경량 관계형 데이터베이스. 별도 서버 설치 없이 사용할 수 있어 학습과 프로토타이핑에 적합합니다. (Ch07)

### Starlette
FastAPI의 기반이 되는 Python ASGI 프레임워크. 라우팅, 미들웨어, 웹소켓 등의 기능을 제공합니다. (Ch01)

### status_code
HTTP 응답의 상태를 나타내는 숫자 코드. 200(성공), 201(생성됨), 404(찾을 수 없음), 422(유효성 검사 실패) 등이 있습니다. (Ch04)

### Swagger UI
FastAPI가 자동으로 생성하는 대화형 API 문서 UI. `/docs` 경로에서 접근할 수 있습니다. (Ch01)

---

## T

### TestClient
FastAPI 앱을 실제 서버 없이 테스트할 수 있게 해주는 클라이언트. `from fastapi.testclient import TestClient`로 사용합니다. (Ch01)

### Type Hint (타입 힌트)
Python에서 변수나 함수의 매개변수/반환값의 타입을 명시하는 문법. FastAPI는 타입 힌트를 기반으로 데이터 검증과 문서 생성을 수행합니다. (Ch01)

---

## U

### UploadFile
FastAPI에서 파일 업로드를 처리하는 클래스. `filename`, `content_type`, `read()` 등의 속성과 메서드를 제공합니다. (Ch03)

### Uvicorn
Python ASGI 서버. FastAPI 앱을 실행하는 데 사용됩니다. `uvicorn main:app --reload`로 실행합니다. (Ch01)

---

## V

### Validation (유효성 검사)
입력 데이터가 정의된 규칙에 맞는지 검증하는 과정. FastAPI는 Pydantic을 통해 자동으로 유효성 검사를 수행합니다. (Ch02)

---

## Y

### yield
Python 제너레이터 키워드. FastAPI에서 의존성 함수의 setup/teardown 패턴에 사용됩니다. `yield` 전 코드는 요청 시, `yield` 후 코드는 응답 후에 실행됩니다. (Ch05)

---

## 숫자

### 422 Unprocessable Entity
FastAPI에서 요청 데이터의 유효성 검사에 실패했을 때 반환하는 HTTP 상태 코드. Pydantic 검증 에러 시 자동으로 반환됩니다. (Ch02)

### 1:N 관계 (일대다 관계)
데이터베이스에서 하나의 레코드가 여러 개의 관련 레코드를 가지는 관계. 예: 사용자(1) - 게시글(N). (Ch07)
