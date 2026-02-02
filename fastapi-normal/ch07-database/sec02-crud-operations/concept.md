# 섹션 02: CRUD 구현

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 (SQLAlchemy 설정) 완료
> **학습 목표**: FastAPI + SQLAlchemy로 CRUD API를 구현할 수 있다

---

## 핵심 개념

### 1. CRUD란?

CRUD는 데이터베이스 조작의 4가지 기본 작업을 의미합니다.

| 작업 | 의미 | HTTP 메서드 | SQL | SQLAlchemy |
|------|------|------------|-----|-----------|
| **C**reate | 생성 | POST | INSERT | `db.add()` |
| **R**ead | 조회 | GET | SELECT | `db.query()` |
| **U**pdate | 수정 | PUT / PATCH | UPDATE | 객체 속성 변경 + `db.commit()` |
| **D**elete | 삭제 | DELETE | DELETE | `db.delete()` |

```
클라이언트                    FastAPI                    데이터베이스
  │                            │                            │
  │  POST /posts               │                            │
  │ ─────────────────────────→ │  db.add(post)              │
  │                            │ ─────────────────────────→ │
  │                            │           INSERT           │
  │                            │                            │
  │  GET /posts                │                            │
  │ ─────────────────────────→ │  db.query(Post).all()      │
  │                            │ ─────────────────────────→ │
  │                            │           SELECT           │
  │                            │                            │
  │  PUT /posts/1              │                            │
  │ ─────────────────────────→ │  post.title = "새 제목"     │
  │                            │  db.commit()               │
  │                            │ ─────────────────────────→ │
  │                            │           UPDATE           │
  │                            │                            │
  │  DELETE /posts/1           │                            │
  │ ─────────────────────────→ │  db.delete(post)           │
  │                            │ ─────────────────────────→ │
  │                            │           DELETE           │
```

---

### 2. Pydantic 모델 vs SQLAlchemy 모델

FastAPI에서는 두 종류의 모델을 **분리하여** 사용합니다.

```
┌──────────────────┐      ┌──────────────────┐
│  Pydantic 모델    │      │  SQLAlchemy 모델  │
│  (schemas.py)    │      │  (models.py)     │
├──────────────────┤      ├──────────────────┤
│ API 요청/응답 검증│      │ DB 테이블 정의    │
│ 데이터 직렬화     │      │ 데이터 영속성     │
│ 문서 자동 생성    │      │ 관계 매핑         │
└──────────────────┘      └──────────────────┘
```

#### 왜 분리하는가?

```python
# --- SQLAlchemy 모델 (models.py) ---
# DB 테이블 구조를 정의. id, created_at 등 서버가 관리하는 필드 포함
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_published = Column(Boolean, default=False)

# --- Pydantic 모델 (schemas.py) ---
# API 요청용: 클라이언트가 보내야 하는 데이터만 정의
class PostCreate(BaseModel):
    title: str
    content: str

# API 응답용: 클라이언트에 반환할 데이터 정의
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool

    model_config = ConfigDict(from_attributes=True)
```

> **`model_config = ConfigDict(from_attributes=True)`**: SQLAlchemy 모델 객체를
> Pydantic 모델로 자동 변환할 수 있게 해줍니다. (이전 버전에서는 `class Config: orm_mode = True`)

---

### 3. Create - 데이터 생성

```python
@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """새 게시글을 생성합니다"""
    # 1. Pydantic 모델 → SQLAlchemy 모델로 변환
    db_post = Post(
        title=post.title,
        content=post.content
    )
    # 2. 세션에 추가
    db.add(db_post)
    # 3. 데이터베이스에 반영
    db.commit()
    # 4. 생성된 데이터(id 등)를 새로고침
    db.refresh(db_post)
    # 5. 반환
    return db_post
```

#### 동작 흐름

```
POST /posts  {"title": "첫 글", "content": "내용"}
    │
    ▼
PostCreate로 검증 (Pydantic)
    │
    ▼
Post() 객체 생성 (SQLAlchemy)
    │
    ▼
db.add(db_post)  → 세션에 등록 (아직 DB에 반영 안 됨)
    │
    ▼
db.commit()      → DB에 INSERT 실행
    │
    ▼
db.refresh(db_post) → DB에서 id, 기본값 등을 가져옴
    │
    ▼
return db_post   → PostResponse로 직렬화하여 응답
```

---

### 4. Read - 데이터 조회

#### 목록 조회 (List)

```python
@app.get("/posts", response_model=list[PostResponse])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """게시글 목록을 조회합니다 (페이지네이션 지원)"""
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts
```

#### 상세 조회 (Detail)

```python
@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """특정 게시글을 조회합니다"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    return post
```

#### 주요 쿼리 메서드

| 메서드 | 설명 | 예시 |
|--------|------|------|
| `.all()` | 모든 결과를 리스트로 반환 | `db.query(Post).all()` |
| `.first()` | 첫 번째 결과만 반환 (없으면 None) | `db.query(Post).first()` |
| `.filter()` | 조건으로 필터링 | `.filter(Post.id == 1)` |
| `.offset()` | 건너뛸 개수 | `.offset(10)` |
| `.limit()` | 가져올 최대 개수 | `.limit(5)` |
| `.count()` | 결과 개수 반환 | `db.query(Post).count()` |
| `.order_by()` | 정렬 | `.order_by(Post.id.desc())` |

---

### 5. Update - 데이터 수정

```python
@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostCreate,
    db: Session = Depends(get_db)
):
    """게시글을 수정합니다"""
    # 1. 기존 데이터 조회
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")

    # 2. 속성 업데이트
    db_post.title = post_update.title
    db_post.content = post_update.content

    # 3. 커밋
    db.commit()
    db.refresh(db_post)

    return db_post
```

> **주의**: SQLAlchemy는 객체의 속성을 변경한 후 `commit()`하면 자동으로 UPDATE 쿼리가 실행됩니다.
> `db.add()`를 다시 호출할 필요가 없습니다.

---

### 6. Delete - 데이터 삭제

```python
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """게시글을 삭제합니다"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")

    db.delete(db_post)
    db.commit()

    return None  # 204 No Content
```

---

### 7. CRUD 패턴 정리

```python
# Create: db.add() → db.commit() → db.refresh()
db.add(new_item)
db.commit()
db.refresh(new_item)

# Read: db.query().filter().first() 또는 .all()
item = db.query(Model).filter(Model.id == item_id).first()
items = db.query(Model).all()

# Update: 속성 변경 → db.commit()
item.name = "새 이름"
db.commit()

# Delete: db.delete() → db.commit()
db.delete(item)
db.commit()
```

---

## 전체 코드 예제: 게시글 CRUD API

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict

# --- 데이터베이스 설정 ---
engine = create_engine(
    "sqlite:///./posts.db",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy 모델 ---
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_published = Column(Boolean, default=False)

# --- Pydantic 스키마 ---
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    is_published: bool

    model_config = ConfigDict(from_attributes=True)

# --- 테이블 생성 ---
Base.metadata.create_all(bind=engine)

# --- 의존성 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FastAPI 앱 ---
app = FastAPI()

@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts", response_model=list[PostResponse])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Post).offset(skip).limit(limit).all()

@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    return post

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    db_post.title = post_update.title
    db_post.content = post_update.content
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    db.delete(db_post)
    db.commit()
    return None
```

---

## 주의 사항

### commit과 refresh의 순서

```python
# 올바른 순서
db.add(item)
db.commit()       # DB에 저장
db.refresh(item)  # DB에서 최신 데이터(id 등) 로드

# 잘못된 순서 (refresh를 commit 전에 호출)
db.add(item)
db.refresh(item)  # 아직 commit 안 했으므로 의미 없음
db.commit()
```

### 404 에러 처리를 잊지 마세요

조회, 수정, 삭제 시 해당 데이터가 없을 수 있으므로 반드시 존재 여부를 확인해야 합니다.

```python
post = db.query(Post).filter(Post.id == post_id).first()
if post is None:
    raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
```

---

## 정리

| 작업 | 엔드포인트 | SQLAlchemy 코드 | 상태 코드 |
|------|-----------|----------------|----------|
| 생성 | `POST /posts` | `db.add()` + `db.commit()` | 201 |
| 목록 조회 | `GET /posts` | `db.query().all()` | 200 |
| 상세 조회 | `GET /posts/{id}` | `db.query().filter().first()` | 200 / 404 |
| 수정 | `PUT /posts/{id}` | 속성 변경 + `db.commit()` | 200 / 404 |
| 삭제 | `DELETE /posts/{id}` | `db.delete()` + `db.commit()` | 204 / 404 |

---

## 다음 단계

CRUD API를 구현했다면, 다음 섹션에서 테이블 간 관계(1:N)를 설정해 보겠습니다!

> [sec03-relationships: 관계 매핑](../sec03-relationships/concept.md)
