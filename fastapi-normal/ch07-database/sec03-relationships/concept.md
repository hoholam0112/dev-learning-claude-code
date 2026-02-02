# 섹션 03: 관계 매핑

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec02 (CRUD 구현) 완료
> **학습 목표**: SQLAlchemy의 relationship을 사용하여 테이블 간 관계를 설정할 수 있다

---

## 핵심 개념

### 1. 테이블 간 관계란?

현실 세계에서 데이터는 서로 연결되어 있습니다.
예를 들어, "사용자"는 여러 개의 "게시글"을 작성할 수 있습니다.

```
사용자(User)                      게시글(Post)
┌────────────────┐               ┌────────────────────────┐
│ id: 1          │──────────────→│ id: 1                  │
│ username: hong │               │ title: "첫 글"          │
│                │──────────────→│ author_id: 1 (FK)      │
│                │               ├────────────────────────┤
│                │               │ id: 2                  │
│                │──────────────→│ title: "두 번째 글"      │
│                │               │ author_id: 1 (FK)      │
└────────────────┘               └────────────────────────┘

사용자(User)                      게시글(Post)
┌────────────────┐               ┌────────────────────────┐
│ id: 2          │──────────────→│ id: 3                  │
│ username: kim  │               │ title: "김씨의 글"       │
│                │               │ author_id: 2 (FK)      │
└────────────────┘               └────────────────────────┘
```

이런 관계를 **1:N(일대다) 관계**라고 합니다.
- 하나의 사용자(1)는 여러 개의 게시글(N)을 가질 수 있습니다.
- 각 게시글은 한 명의 작성자(사용자)에게 속합니다.

---

### 2. 관계의 종류

| 관계 | 설명 | 예시 |
|------|------|------|
| **1:N (일대다)** | 하나가 여러 개를 가짐 | 사용자 → 게시글들 |
| **N:1 (다대일)** | 여러 개가 하나에 속함 | 게시글들 → 사용자 |
| **1:1 (일대일)** | 하나가 하나를 가짐 | 사용자 → 프로필 |
| **N:M (다대다)** | 여러 개가 여러 개와 연결 | 게시글 ↔ 태그 |

> 이 섹션에서는 가장 기본적이고 자주 사용되는 **1:N 관계**를 다룹니다.

---

### 3. ForeignKey (외래키)

외래키는 다른 테이블의 기본키를 참조하는 컬럼입니다.
**N 쪽(자식 테이블)**에 외래키를 추가합니다.

```python
from sqlalchemy import Column, Integer, String, ForeignKey

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

    # 외래키: users 테이블의 id 컬럼을 참조
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
```

#### ForeignKey 문법

```python
# ForeignKey("테이블이름.컬럼이름")
author_id = Column(Integer, ForeignKey("users.id"))
```

- `"users.id"`: `users` 테이블의 `id` 컬럼을 참조한다는 의미
- 외래키 컬럼의 타입은 참조하는 컬럼의 타입과 동일해야 합니다 (여기서는 Integer)

---

### 4. relationship (관계 정의)

`ForeignKey`는 DB 레벨의 제약 조건이고,
`relationship`은 **Python 코드 레벨**에서 관련 객체에 접근할 수 있게 해줍니다.

```python
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # 관계 정의: User.posts로 이 사용자의 게시글 목록에 접근 가능
    posts = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 관계 정의: Post.author로 이 게시글의 작성자에 접근 가능
    author = relationship("User", back_populates="posts")
```

#### relationship 동작 원리

```python
# 사용자의 게시글 목록 조회
user = db.query(User).first()
print(user.posts)        # [Post(id=1, ...), Post(id=2, ...)]
                         # → 자동으로 SELECT * FROM posts WHERE author_id = user.id 실행

# 게시글의 작성자 조회
post = db.query(Post).first()
print(post.author)       # User(id=1, username="hong", ...)
                         # → 자동으로 SELECT * FROM users WHERE id = post.author_id 실행
```

#### back_populates의 역할

`back_populates`는 양방향 관계를 설정합니다.
양쪽 모델에서 서로를 참조할 수 있게 해줍니다.

```
User 모델                              Post 모델
┌─────────────────────────┐           ┌──────────────────────────┐
│ posts = relationship(   │           │ author = relationship(   │
│   "Post",               │←─────────→│   "User",                │
│   back_populates="author"│          │   back_populates="posts" │
│ )                       │           │ )                        │
└─────────────────────────┘           └──────────────────────────┘

user.posts ──→ [Post1, Post2, ...]    (1 → N 방향)
post.author ──→ User                   (N → 1 방향)
```

> **주의**: `back_populates`의 값은 상대방 모델에 정의한 `relationship` 속성의 이름과
> 정확히 일치해야 합니다.

---

### 5. Pydantic 스키마에서 관계 데이터 포함하기

관계가 있는 데이터를 API 응답에 포함하려면 Pydantic 스키마를 중첩합니다.

```python
from pydantic import BaseModel, ConfigDict

# --- 기본 스키마 ---
class PostBase(BaseModel):
    title: str
    content: str

class PostResponse(PostBase):
    id: int
    author_id: int
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    email: str

# --- 관계가 포함된 스키마 ---
class UserWithPosts(UserBase):
    """사용자 정보 + 게시글 목록"""
    id: int
    posts: list[PostResponse] = []  # 게시글 목록 포함

    model_config = ConfigDict(from_attributes=True)

class PostWithAuthor(PostBase):
    """게시글 정보 + 작성자 정보"""
    id: int
    author: UserBase  # 작성자 정보 포함

    model_config = ConfigDict(from_attributes=True)
```

---

### 6. 관계 데이터 조회 API

```python
@app.get("/users/{user_id}", response_model=UserWithPosts)
def get_user_with_posts(user_id: int, db: Session = Depends(get_db)):
    """사용자 정보와 해당 사용자의 게시글 목록을 함께 조회합니다"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    # user.posts는 relationship이 자동으로 로드합니다
    return user
```

```python
@app.post("/users/{user_id}/posts", response_model=PostWithAuthor, status_code=201)
def create_post_for_user(
    user_id: int,
    post: PostBase,
    db: Session = Depends(get_db)
):
    """특정 사용자의 게시글을 생성합니다"""
    # 사용자 존재 확인
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    # author_id를 설정하여 게시글 생성
    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
```

---

### 7. Lazy Loading vs Eager Loading

기본적으로 SQLAlchemy는 **Lazy Loading**(지연 로딩)을 사용합니다.
관계 데이터는 실제로 접근할 때 DB에서 가져옵니다.

```python
# Lazy Loading (기본값): user.posts에 접근하는 순간 쿼리 실행
user = db.query(User).first()
# 이 시점에서는 posts 데이터를 아직 가져오지 않음
print(user.posts)  # 이때 SELECT * FROM posts WHERE author_id = ... 실행

# Eager Loading: 처음부터 관계 데이터를 함께 가져옴
from sqlalchemy.orm import joinedload
user = db.query(User).options(joinedload(User.posts)).first()
# JOIN으로 posts도 한 번에 가져옴 (쿼리 1회)
```

> **팁**: 데이터 양이 적을 때는 Lazy Loading으로 충분합니다.
> 성능이 중요할 때는 Eager Loading(`joinedload`)을 고려하세요.

---

## 전체 코드 예제: 사용자 - 게시글 관계

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from pydantic import BaseModel, ConfigDict

# --- DB 설정 ---
engine = create_engine("sqlite:///./blog.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy 모델 ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="posts")

# --- Pydantic 스키마 ---
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(PostCreate):
    id: int
    author_id: int
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserWithPosts(UserResponse):
    posts: list[PostResponse] = []

# --- 앱 ---
Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserWithPosts)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user

@app.post("/users/{user_id}/posts", response_model=PostResponse, status_code=201)
def create_post_for_user(user_id: int, post: PostCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    db_post = Post(title=post.title, content=post.content, author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
```

---

## 주의 사항

### back_populates 이름 불일치

양쪽의 `back_populates` 값이 상대방 속성명과 정확히 일치해야 합니다.

```python
# 올바른 예
class User(Base):
    posts = relationship("Post", back_populates="author")  # "author"

class Post(Base):
    author = relationship("User", back_populates="posts")  # "posts"

# 잘못된 예 (이름 불일치 → 에러)
class User(Base):
    posts = relationship("Post", back_populates="writer")  # "writer" != "author"

class Post(Base):
    author = relationship("User", back_populates="posts")
```

### ForeignKey는 N 쪽에 추가

1:N 관계에서 외래키는 항상 **N 쪽(자식)**에 추가합니다.

```python
# 올바른 예: Post(N 쪽)에 author_id 외래키 추가
class Post(Base):
    author_id = Column(Integer, ForeignKey("users.id"))

# 잘못된 예: User(1 쪽)에 외래키를 추가하면 안 됨
class User(Base):
    post_id = Column(Integer, ForeignKey("posts.id"))  # 잘못됨!
```

### 순환 참조 주의

Pydantic 모델에서 서로를 참조하면 순환 참조가 발생할 수 있습니다.
필요한 필드만 포함하는 별도의 스키마를 만들어 해결합니다.

```python
# 순환 참조가 발생하는 예 (피해야 함)
class UserResponse(BaseModel):
    posts: list[PostResponse]  # PostResponse가 UserResponse를 참조하면 순환!

# 해결: 중첩 깊이를 제한하는 별도 스키마 사용
class PostSimple(BaseModel):  # author 필드 없음
    id: int
    title: str

class UserWithPosts(BaseModel):
    id: int
    username: str
    posts: list[PostSimple]  # 순환 없음
```

---

## 정리

| 개념 | 설명 | 코드 |
|------|------|------|
| ForeignKey | 다른 테이블의 키를 참조 | `ForeignKey("users.id")` |
| relationship | Python에서 관계 객체에 접근 | `relationship("Post", back_populates="author")` |
| back_populates | 양방향 관계 설정 | 양쪽 모델에 서로의 이름 지정 |
| 1:N 관계 | 하나가 여러 개를 가짐 | User(1) → Post(N) |
| Lazy Loading | 접근 시 쿼리 실행 | 기본 동작 |
| Eager Loading | 미리 함께 로드 | `joinedload()` |

---

## 챕터 마무리

이 챕터에서 학습한 내용을 정리합니다:

1. **sec01**: SQLAlchemy 엔진, 세션, 모델 설정 방법
2. **sec02**: FastAPI + SQLAlchemy로 CRUD API 구현
3. **sec03**: ForeignKey와 relationship을 사용한 테이블 간 관계 매핑

다음 챕터에서는 **인증과 보안**(JWT, OAuth2)을 다룹니다!

> [Ch08: 인증과 보안](../../ch08-auth-security/README.md)
