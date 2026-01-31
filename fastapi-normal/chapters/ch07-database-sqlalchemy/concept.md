# 챕터 07: 데이터베이스 연동 (SQLAlchemy)

## 학습 목표

이 챕터를 완료하면 다음을 할 수 있습니다:

1. SQLAlchemy ORM의 핵심 개념을 이해한다
2. 데이터베이스 엔진과 세션을 설정할 수 있다
3. 테이블 모델을 정의하고 관계를 설정할 수 있다
4. FastAPI의 의존성 주입으로 DB 세션을 관리할 수 있다
5. CRUD 작업(생성, 조회, 수정, 삭제)을 구현할 수 있다

---

## 1. SQLAlchemy 소개 (ORM 개념)

**ORM(Object-Relational Mapping)**은 데이터베이스 테이블을 Python 클래스로 매핑하는 기술입니다. SQL을 직접 작성하는 대신 Python 객체를 조작하여 데이터베이스를 다룹니다.

### ORM 구조 다이어그램

```mermaid
graph LR
    A[Python 객체] -->|ORM| B[SQL 쿼리]
    B --> C[(데이터베이스)]
    C -->|ORM| D[Python 객체]

    subgraph "SQLAlchemy ORM"
        E[모델 클래스] --> F[세션]
        F --> G[엔진]
        G --> C
    end
```

### ORM vs Raw SQL 비교

| 방식 | 코드 예시 | 장점 |
|------|----------|------|
| Raw SQL | `SELECT * FROM users WHERE id = 1` | 직관적, 성능 최적화 가능 |
| ORM | `db.query(User).filter(User.id == 1).first()` | 타입 안전, 코드 재사용 |

---

## 2. 데이터베이스 세션 설정

SQLAlchemy를 사용하려면 세 가지 핵심 요소가 필요합니다.

### 핵심 구성 요소

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 엔진: 데이터베이스 연결을 관리
# SQLite는 파일 기반 DB로, 로컬 개발에 적합합니다
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 전용 옵션
)

# 2. 세션: 데이터베이스 트랜잭션을 관리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base: 모든 모델의 부모 클래스
Base = declarative_base()
```

### 구성 요소 관계

```mermaid
graph TD
    A[Engine<br/>데이터베이스 연결] --> B[SessionLocal<br/>세션 팩토리]
    B --> C[Session 인스턴스<br/>트랜잭션 관리]
    D[Base<br/>모델 기반 클래스] --> E[User 모델]
    D --> F[Post 모델]
    C --> G[CRUD 작업]
    E --> G
    F --> G
```

---

## 3. 모델 정의 (declarative_base)

데이터베이스 테이블은 Python 클래스로 표현합니다.

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"  # 테이블 이름

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 정의: 사용자가 작성한 게시글들
    posts = relationship("Post", back_populates="author")
```

### 주요 컬럼 타입

| SQLAlchemy 타입 | Python 타입 | SQL 타입 |
|----------------|-------------|----------|
| `Integer` | `int` | `INTEGER` |
| `String` | `str` | `VARCHAR` |
| `Boolean` | `bool` | `BOOLEAN` |
| `Float` | `float` | `FLOAT` |
| `DateTime` | `datetime` | `DATETIME` |
| `Text` | `str` | `TEXT` |

### 컬럼 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `primary_key` | 기본 키 | `Column(Integer, primary_key=True)` |
| `unique` | 고유 값 | `Column(String, unique=True)` |
| `index` | 인덱스 생성 | `Column(String, index=True)` |
| `default` | 기본값 | `Column(Boolean, default=True)` |
| `nullable` | NULL 허용 | `Column(String, nullable=False)` |
| `ForeignKey` | 외래 키 | `Column(Integer, ForeignKey("users.id"))` |

---

## 4. CRUD 작업 구현

### Create (생성)

```python
def create_user(db: Session, username: str, email: str):
    db_user = User(username=username, email=email)
    db.add(db_user)       # 세션에 추가
    db.commit()           # DB에 반영
    db.refresh(db_user)   # 최신 데이터로 갱신 (id 등 자동 생성된 값)
    return db_user
```

### Read (조회)

```python
# 단일 조회 (ID로)
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# 목록 조회 (페이지네이션)
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# 조건 조회
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
```

### Update (수정)

```python
def update_user(db: Session, user_id: int, new_email: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.email = new_email  # 속성 변경
        db.commit()                # DB에 반영
        db.refresh(db_user)        # 최신 데이터로 갱신
    return db_user
```

### Delete (삭제)

```python
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)  # 삭제 표시
        db.commit()          # DB에 반영
    return db_user
```

---

## 5. 의존성 주입으로 세션 관리 (get_db)

FastAPI의 의존성 주입 시스템과 `yield`를 활용하면, 요청마다 DB 세션을 안전하게 관리할 수 있습니다.

```python
def get_db():
    """
    요청마다 새로운 DB 세션을 생성하고,
    요청이 완료되면 자동으로 세션을 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db  # 세션을 엔드포인트에 전달
    finally:
        db.close()  # 요청 완료 후 세션 닫기

# 엔드포인트에서 사용
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user
```

### 세션 생명주기

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant F as FastAPI
    participant D as get_db()
    participant DB as 데이터베이스

    C->>F: HTTP 요청
    F->>D: 의존성 호출
    D->>DB: 세션 생성 (SessionLocal())
    D-->>F: 세션 yield
    F->>DB: CRUD 작업
    DB-->>F: 결과 반환
    F-->>C: HTTP 응답
    F->>D: 요청 완료
    D->>DB: 세션 종료 (db.close())
```

---

## 6. SQLite를 활용한 로컬 개발

SQLite는 별도의 서버 설치 없이 파일 하나로 동작하는 데이터베이스입니다.

### SQLite 장점 (개발용)

- 설치 불필요 (Python 기본 내장)
- 파일 기반으로 간편한 관리
- 소규모 프로젝트에 충분한 성능

### 프로덕션 전환 시

```python
# 개발 환경 (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# 프로덕션 환경 (PostgreSQL)
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

# 프로덕션 환경 (MySQL)
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

> **주의:** SQLite에서 다른 DB로 전환할 때, `connect_args={"check_same_thread": False}`는 SQLite 전용 옵션이므로 제거해야 합니다.

---

## 주의사항

| 항목 | 설명 |
|------|------|
| 세션 관리 | 반드시 `try/finally`로 세션을 닫아야 합니다 |
| N+1 문제 | `relationship`에 `lazy="joined"`를 사용하거나 `joinedload`로 해결 |
| 마이그레이션 | 프로덕션에서는 Alembic으로 스키마 변경을 관리하세요 |
| Pydantic 변환 | ORM 모델과 Pydantic 모델은 별도이므로 변환이 필요합니다 |
| 트랜잭션 | `commit()` 전에 오류가 발생하면 `rollback()`이 필요합니다 |

---

## 핵심 정리표

| 개념 | 설명 | 코드 |
|------|------|------|
| Engine | DB 연결 관리 | `create_engine(url)` |
| Session | 트랜잭션 관리 | `SessionLocal()` |
| Base | 모델 기반 클래스 | `declarative_base()` |
| Column | 테이블 컬럼 정의 | `Column(Integer, primary_key=True)` |
| relationship | 테이블 관계 | `relationship("Post", back_populates="author")` |
| get_db | 세션 의존성 | `db: Session = Depends(get_db)` |

---

## 필요 패키지

```bash
pip install fastapi uvicorn sqlalchemy
```

---

## 다음 단계

챕터 08에서는 **에러 처리와 미들웨어**를 학습합니다. 데이터베이스 작업 중 발생할 수 있는 다양한 에러를 체계적으로 처리하고, 미들웨어를 활용하여 요청/응답을 가로채는 방법을 배웁니다.
