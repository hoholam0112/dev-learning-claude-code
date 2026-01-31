# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn sqlalchemy
# DB 파일: 실행하면 현재 디렉토리에 blog.db 파일이 생성됩니다

"""
챕터 07 예제 02: 관계형 모델 (사용자 - 게시글)

이 예제에서는 다음을 학습합니다:
- 일대다(One-to-Many) 관계 설정
- relationship과 ForeignKey 사용
- 관련 데이터를 함께 조회하기
- 여러 테이블에 걸친 CRUD 작업
"""

from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# ── 데이터베이스 설정 ──────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── SQLAlchemy 모델 ────────────────────────────────────────
class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계: 사용자가 작성한 게시글들 (일대다)
    # back_populates는 양방향 관계를 설정합니다
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")


class Post(Base):
    """게시글 테이블"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 외래 키: 작성자 ID (users 테이블의 id 참조)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 관계: 게시글의 작성자 (다대일)
    author = relationship("User", back_populates="posts")


# 테이블 생성
Base.metadata.create_all(bind=engine)


# ── Pydantic 모델 ─────────────────────────────────────────
# 게시글 관련 스키마
class PostCreate(BaseModel):
    """게시글 생성 요청"""
    title: str
    content: str


class PostResponse(BaseModel):
    """게시글 응답 (작성자 정보 미포함)"""
    id: int
    title: str
    content: str
    created_at: datetime
    author_id: int

    class Config:
        from_attributes = True


class PostWithAuthor(BaseModel):
    """게시글 응답 (작성자 정보 포함)"""
    id: int
    title: str
    content: str
    created_at: datetime
    author: "UserBase"

    class Config:
        from_attributes = True


# 사용자 관련 스키마
class UserBase(BaseModel):
    """사용자 기본 정보"""
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """사용자 생성 요청"""
    username: str
    email: str


class UserResponse(BaseModel):
    """사용자 응답 (게시글 목록 미포함)"""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithPosts(BaseModel):
    """사용자 응답 (게시글 목록 포함)"""
    id: int
    username: str
    email: str
    created_at: datetime
    posts: list[PostResponse] = []

    class Config:
        from_attributes = True


# PostWithAuthor에서 UserBase를 참조하므로 모델 업데이트 필요
PostWithAuthor.model_rebuild()


# ── 의존성 함수 ────────────────────────────────────────────
def get_db():
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="블로그 API", description="관계형 모델 (사용자-게시글) 예제")


# ── 사용자 엔드포인트 ──────────────────────────────────────

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """새로운 사용자를 생성합니다."""
    # 중복 확인
    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명 또는 이메일입니다",
        )

    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=list[UserResponse], summary="사용자 목록 조회")
def read_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """전체 사용자 목록을 조회합니다."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserWithPosts, summary="사용자 상세 조회")
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 상세 정보를 조회합니다.
    해당 사용자가 작성한 게시글 목록도 함께 반환됩니다.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    return db_user


# ── 게시글 엔드포인트 ──────────────────────────────────────

@app.post(
    "/users/{user_id}/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성",
)
def create_post(user_id: int, post: PostCreate, db: Session = Depends(get_db)):
    """특정 사용자가 새로운 게시글을 작성합니다."""
    # 사용자 존재 확인
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )

    db_post = Post(title=post.title, content=post.content, author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/posts", response_model=list[PostWithAuthor], summary="전체 게시글 조회")
def read_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    전체 게시글 목록을 조회합니다.
    각 게시글에 작성자 정보가 포함됩니다.
    """
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posts


@app.get("/posts/{post_id}", response_model=PostWithAuthor, summary="게시글 상세 조회")
def read_post(post_id: int, db: Session = Depends(get_db)):
    """특정 게시글의 상세 정보와 작성자 정보를 조회합니다."""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )
    return db_post


@app.get(
    "/users/{user_id}/posts",
    response_model=list[PostResponse],
    summary="사용자별 게시글 조회",
)
def read_user_posts(user_id: int, db: Session = Depends(get_db)):
    """특정 사용자가 작성한 게시글 목록을 조회합니다."""
    # 사용자 존재 확인
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )

    posts = (
        db.query(Post)
        .filter(Post.author_id == user_id)
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts


@app.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="게시글 삭제",
)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """특정 게시글을 삭제합니다."""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )

    db.delete(db_post)
    db.commit()
