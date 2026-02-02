# 섹션 01: SQLAlchemy 설정 - 연습 문제

> **난이도**: ⭐⭐⭐ (3/5)
> **파일**: `exercise.py`

---

## 문제 1: SQLAlchemy 데이터베이스 설정 파일 작성

### 목표

SQLAlchemy의 3가지 핵심 구성 요소(엔진, 세션 팩토리, Base)를 올바르게 설정합니다.

### 요구 사항

| 항목 | 설정 값 |
|------|---------|
| 데이터베이스 URL | `sqlite:///./test_exercise.db` |
| connect_args | `{"check_same_thread": False}` (SQLite 필수) |
| autocommit | `False` |
| autoflush | `False` |
| Base | `declarative_base()` 사용 |

### 힌트

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 엔진 생성
engine = create_engine("데이터베이스URL", connect_args={...})

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=..., autoflush=..., bind=...)

# Base 클래스 생성
Base = declarative_base()
```

---

## 문제 2: 사용자 테이블 모델 정의

### 목표

SQLAlchemy 모델을 사용하여 `users` 테이블을 정의합니다.

### 테이블 스키마

| 컬럼 | 타입 | 제약 조건 |
|------|------|----------|
| `id` | Integer | 기본키, 자동 증가, 인덱스 |
| `username` | String | 유일값, 인덱스, NOT NULL |
| `email` | String | 유일값, NOT NULL |
| `full_name` | String | NULL 허용 |

### 힌트

```python
class User(Base):
    __tablename__ = "테이블이름"

    id = Column(Integer, primary_key=True, index=True)
    # 나머지 컬럼을 정의하세요...
```

---

## 문제 3: get_db 의존성 함수 작성

### 목표

`yield` 패턴을 사용하여 데이터베이스 세션을 안전하게 관리하는 의존성 함수를 작성합니다.

### 요구 사항

1. `SessionLocal()`로 세션을 생성합니다.
2. `yield`로 세션을 전달합니다.
3. `finally` 블록에서 `db.close()`로 세션을 닫습니다.

### 힌트

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 실행 및 검증

```bash
python exercise.py
```

### 기대 출력

```
✓ 테이블 생성 성공
✓ 사용자 생성 성공: id=1
✓ 사용자 조회 성공: testuser

모든 테스트를 통과했습니다!
```

> SQLite 파일(`test_exercise.db`)은 테스트 완료 후 자동으로 삭제됩니다.

---

## 자주 하는 실수

1. **`connect_args`를 빼먹는 경우**: SQLite에서 `check_same_thread: False` 없이 멀티스레드 접근 시 에러가 발생합니다.
2. **`__tablename__`을 빼먹는 경우**: SQLAlchemy가 테이블 이름을 알 수 없어 에러가 발생합니다.
3. **`Base`를 상속하지 않는 경우**: 일반 Python 클래스는 테이블로 생성되지 않습니다.
4. **`finally`에서 `db.close()`를 빼먹는 경우**: 데이터베이스 연결이 누수됩니다.
