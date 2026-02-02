# 섹션 03: 관계 매핑 - 모범 답안
# 실행: python solution.py
# 필요 패키지: pip install fastapi sqlalchemy httpx

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from pydantic import BaseModel, ConfigDict

# ============================================================
# 데이터베이스 설정
# ============================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_relations.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# TODO 1: SQLAlchemy 모델 정의
# ============================================================

class User(Base):
    """사용자 테이블 모델 (1 쪽)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # 관계 정의: User.posts로 이 사용자의 게시글 목록에 접근 가능
    # back_populates="author"는 Post 모델의 'author' 속성과 양방향으로 연결
    posts = relationship("Post", back_populates="author")


class Post(Base):
    """게시글 테이블 모델 (N 쪽)"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

    # 외래키: users 테이블의 id를 참조
    # 1:N 관계에서 외래키는 항상 N 쪽(자식)에 추가
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 관계 정의: Post.author로 이 게시글의 작성자에 접근 가능
    # back_populates="posts"는 User 모델의 'posts' 속성과 양방향으로 연결
    author = relationship("User", back_populates="posts")


# ============================================================
# TODO 2: Pydantic 스키마 정의
# ============================================================

class UserCreate(BaseModel):
    """사용자 생성 요청 스키마"""
    username: str
    email: str


class PostCreate(BaseModel):
    """게시글 생성 요청 스키마"""
    title: str
    content: str


class PostResponse(BaseModel):
    """게시글 응답 스키마"""
    id: int
    title: str
    content: str
    author_id: int

    # SQLAlchemy 모델 객체를 Pydantic 모델로 자동 변환
    model_config = ConfigDict(from_attributes=True)


class UserWithPosts(BaseModel):
    """사용자 + 게시글 목록 응답 스키마"""
    id: int
    username: str
    email: str
    # 관계 데이터: 이 사용자의 게시글 목록
    # 기본값 빈 리스트 → 게시글이 없어도 에러 없이 빈 리스트 반환
    posts: list[PostResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 테이블 생성 및 의존성
# ============================================================
Base.metadata.create_all(bind=engine)


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


# ============================================================
# TODO 3: API 엔드포인트 구현
# ============================================================

@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """새 사용자를 생성합니다"""
    db_user = User(
        username=user.username,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/users/{user_id}/posts", response_model=PostResponse, status_code=201)
def create_post_for_user(
    user_id: int,
    post: PostCreate,
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
        author_id=user_id  # 외래키 값 설정
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/users/{user_id}", response_model=UserWithPosts)
def get_user_with_posts(user_id: int, db: Session = Depends(get_db)):
    """사용자 정보와 해당 사용자의 게시글 목록을 함께 조회합니다"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    # user.posts는 relationship이 자동으로 로드합니다 (Lazy Loading)
    # UserWithPosts 스키마가 user.posts를 PostResponse 리스트로 변환합니다
    return user


# ============================================================
# 테스트 코드
# ============================================================
if __name__ == "__main__":
    from fastapi.testclient import TestClient

    # 인메모리 DB로 테스트
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # 테스트 1: 사용자 생성
    response = client.post(
        "/users",
        json={"username": "hong", "email": "hong@example.com"}
    )
    assert response.status_code == 201, f"기대: 201, 실제: {response.status_code}"
    user_data = response.json()
    assert user_data["username"] == "hong"
    assert user_data["id"] is not None
    user_id = user_data["id"]
    print("✓ 사용자 생성 테스트 통과")

    # 테스트 2: 게시글 생성 (사용자에게 연결)
    response = client.post(
        f"/users/{user_id}/posts",
        json={"title": "첫 번째 글", "content": "안녕하세요!"}
    )
    assert response.status_code == 201, f"기대: 201, 실제: {response.status_code}"
    post_data = response.json()
    assert post_data["title"] == "첫 번째 글"
    assert post_data["author_id"] == user_id
    print("✓ 게시글 생성 테스트 통과 (게시글 1)")

    # 테스트 3: 두 번째 게시글 생성
    response = client.post(
        f"/users/{user_id}/posts",
        json={"title": "두 번째 글", "content": "반갑습니다!"}
    )
    assert response.status_code == 201
    print("✓ 게시글 생성 테스트 통과 (게시글 2)")

    # 테스트 4: 존재하지 않는 사용자에게 게시글 생성
    response = client.post(
        "/users/999/posts",
        json={"title": "실패할 글", "content": "이 글은 생성되면 안 됩니다"}
    )
    assert response.status_code == 404, f"기대: 404, 실제: {response.status_code}"
    print("✓ 존재하지 않는 사용자에게 게시글 생성 시 404 테스트 통과")

    # 테스트 5: 사용자 + 게시글 목록 조회
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "hong"
    assert len(data["posts"]) == 2, f"기대: 2개, 실제: {len(data['posts'])}개"
    print("✓ 사용자 + 게시글 조회 테스트 통과")

    # 테스트 6: 게시글의 author_id 확인
    for post in data["posts"]:
        assert post["author_id"] == user_id, \
            f"기대: author_id={user_id}, 실제: {post['author_id']}"
    print("✓ 게시글에 author_id가 올바르게 설정됨")

    # 테스트 7: 존재하지 않는 사용자 조회
    response = client.get("/users/999")
    assert response.status_code == 404, f"기대: 404, 실제: {response.status_code}"
    print("✓ 존재하지 않는 사용자 조회 시 404 테스트 통과")

    # 정리
    import os
    if os.path.exists("./test_relations.db"):
        os.remove("./test_relations.db")

    print("\n모든 테스트를 통과했습니다!")
