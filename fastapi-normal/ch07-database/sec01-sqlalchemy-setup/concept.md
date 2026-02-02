# 섹션 01: SQLAlchemy 설정

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: Ch05 (의존성 주입) 완료
> **학습 목표**: SQLAlchemy 엔진, 세션, 모델을 설정할 수 있다

---

## 핵심 개념

### 1. SQLAlchemy란?

SQLAlchemy는 Python에서 가장 널리 사용되는 **ORM(Object-Relational Mapping)** 라이브러리입니다.
SQL 쿼리를 직접 작성하지 않고, Python 클래스와 객체를 통해 데이터베이스를 조작할 수 있습니다.

```python
# SQL을 직접 작성하는 방식
cursor.execute("INSERT INTO users (username, email) VALUES ('hong', 'hong@example.com')")

# SQLAlchemy ORM 방식 (Python 객체로 조작)
user = User(username="hong", email="hong@example.com")
db.add(user)
db.commit()
```

---

### 2. SQLAlchemy 구성 요소

SQLAlchemy를 FastAPI에서 사용하려면 3가지 핵심 요소를 설정해야 합니다.

```
┌───────────────────────────────────────────────┐
│                   FastAPI 앱                    │
│                                               │
│   @app.get("/users")                          │
│   def get_users(db: Session = Depends(get_db))│
│       └──────────────┬───────────────┘        │
│                      │ Depends(get_db)         │
│                      ▼                         │
│              ┌──────────────┐                  │
│              │  Session      │  ← sessionmaker │
│              │  (세션)       │                  │
│              └──────┬───────┘                  │
│                     │                          │
│              ┌──────┴───────┐                  │
│              │  Engine       │  ← create_engine│
│              │  (엔진)       │                  │
│              └──────┬───────┘                  │
│                     │                          │
└─────────────────────┼─────────────────────────┘
                      │
               ┌──────┴───────┐
               │  SQLite DB    │
               │  (파일)       │
               └──────────────┘
```

| 구성 요소 | 역할 | 생성 함수 |
|-----------|------|----------|
| **Engine** | 데이터베이스와의 연결을 관리 | `create_engine()` |
| **Session** | 데이터베이스 작업의 단위 (트랜잭션) | `sessionmaker()` |
| **Base** | 모든 모델 클래스의 부모 클래스 | `declarative_base()` |

---

### 3. database.py - 데이터베이스 설정 파일

모든 데이터베이스 설정을 하나의 파일에 모아서 관리합니다.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- 1. 엔진 생성 ---
# SQLite 데이터베이스 파일 경로 지정
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 전용 옵션
)

# --- 2. 세션 팩토리 생성 ---
SessionLocal = sessionmaker(
    autocommit=False,  # 자동 커밋 비활성화 (명시적 commit 필요)
    autoflush=False,   # 자동 플러시 비활성화
    bind=engine        # 위에서 만든 엔진에 바인딩
)

# --- 3. Base 클래스 생성 ---
Base = declarative_base()
```

#### 각 설정의 의미

**`create_engine()`**
- 데이터베이스와의 연결 풀(Connection Pool)을 생성합니다.
- `connect_args={"check_same_thread": False}`: SQLite는 기본적으로 하나의 스레드에서만 접근할 수 있습니다. FastAPI는 멀티스레드로 동작하므로 이 제한을 해제해야 합니다.

**`sessionmaker()`**
- 세션 객체를 생성하는 팩토리(공장)를 만듭니다.
- `autocommit=False`: 변경사항을 명시적으로 `commit()`해야 반영됩니다.
- `autoflush=False`: 쿼리 전에 자동으로 flush하지 않습니다.

**`declarative_base()`**
- 모든 SQLAlchemy 모델의 부모 클래스를 생성합니다.
- 이 Base를 상속받아 테이블을 정의합니다.

---

### 4. models.py - 테이블 정의

SQLAlchemy 모델은 데이터베이스 테이블을 Python 클래스로 표현합니다.

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"  # 실제 테이블 이름

    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

#### 주요 컬럼 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `primary_key=True` | 기본키 (자동 증가) | `id` 컬럼 |
| `unique=True` | 중복 값 불허 | `username`, `email` |
| `index=True` | 검색 성능 향상을 위한 인덱스 | 자주 검색하는 컬럼 |
| `nullable=False` | NULL 값 불허 (필수 필드) | `username` |
| `nullable=True` | NULL 값 허용 (선택 필드) | `full_name` |
| `server_default` | DB 서버 수준의 기본값 | `func.now()` |

#### SQLAlchemy 모델 vs Python 클래스 비교

```python
# 일반 Python 클래스
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

# SQLAlchemy 모델 (데이터베이스 테이블과 매핑)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
```

---

### 5. get_db 의존성 - 세션 관리

FastAPI의 `Depends`를 활용하여 각 요청마다 독립적인 데이터베이스 세션을 제공합니다.

```python
from database import SessionLocal

def get_db():
    """데이터베이스 세션을 생성하고 요청 완료 후 닫는 의존성 함수"""
    db = SessionLocal()
    try:
        yield db  # 세션을 엔드포인트에 전달
    finally:
        db.close()  # 요청 완료 후 반드시 세션 닫기
```

#### yield 패턴의 동작 흐름

```
요청 시작
    │
    ▼
db = SessionLocal()     ← 세션 생성
    │
    ▼
yield db                ← 엔드포인트에 세션 전달
    │                      (엔드포인트 함수 실행)
    ▼
db.close()              ← 세션 닫기 (finally 블록)
    │
    ▼
요청 종료
```

> **주의**: `yield` 패턴을 사용하면 `finally` 블록에서 세션이 반드시 닫힙니다.
> 이는 에러가 발생하더라도 세션이 안전하게 반환되도록 보장합니다.

#### 엔드포인트에서 사용하기

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    """db 파라미터에 세션이 자동으로 주입됩니다"""
    users = db.query(User).all()
    return users
```

---

### 6. 테이블 생성

모든 모델을 정의한 후, 실제 데이터베이스에 테이블을 생성해야 합니다.

```python
from database import engine, Base
import models  # 모델을 import해야 Base가 인식합니다

# 정의된 모든 모델에 대한 테이블을 생성
Base.metadata.create_all(bind=engine)
```

> `create_all()`은 이미 존재하는 테이블은 건너뛰고, 새로운 테이블만 생성합니다.

---

## 전체 흐름 요약

```
1. database.py 작성
   ├── create_engine() → 엔진 생성
   ├── sessionmaker()  → 세션 팩토리 생성
   └── declarative_base() → Base 클래스 생성

2. models.py 작성
   └── class User(Base) → 테이블 정의

3. 의존성 함수 작성
   └── get_db() → yield 패턴으로 세션 관리

4. main.py에서 테이블 생성
   └── Base.metadata.create_all(bind=engine)

5. 엔드포인트에서 사용
   └── def get_users(db: Session = Depends(get_db))
```

---

## 주의 사항

### 세션은 반드시 닫아야 합니다

세션을 닫지 않으면 데이터베이스 연결이 계속 쌓여 리소스가 고갈될 수 있습니다.
`yield` 패턴과 `finally` 블록을 사용하면 안전하게 관리할 수 있습니다.

```python
# 나쁜 예: 세션을 닫지 않음
def get_db():
    db = SessionLocal()
    return db  # 에러 발생 시 세션이 닫히지 않음!

# 좋은 예: yield + finally로 안전하게 관리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # 에러가 발생해도 반드시 실행됨
```

### SQLite의 check_same_thread

SQLite는 단일 스레드용 데이터베이스이므로, FastAPI(멀티스레드)에서 사용하려면
반드시 `connect_args={"check_same_thread": False}`를 설정해야 합니다.

```python
# SQLite에서 필수!
engine = create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False}
)
```

> PostgreSQL, MySQL 등 다른 데이터베이스를 사용할 때는 이 옵션이 필요하지 않습니다.

---

## 정리

| 개념 | 설명 | 코드 |
|------|------|------|
| 엔진 | DB 연결 관리 | `create_engine("sqlite:///./app.db")` |
| 세션 팩토리 | 세션 객체 생성기 | `sessionmaker(bind=engine)` |
| Base | 모델의 부모 클래스 | `declarative_base()` |
| 모델 | 테이블을 Python 클래스로 표현 | `class User(Base)` |
| get_db | 세션 의존성 함수 | `yield` 패턴 사용 |
| 테이블 생성 | 모델을 실제 DB 테이블로 변환 | `Base.metadata.create_all()` |

---

## 다음 단계

데이터베이스 설정이 완료되었다면, 다음 섹션에서 CRUD API를 구현해 보겠습니다!

> [sec02-crud-operations: CRUD 구현](../sec02-crud-operations/concept.md)
