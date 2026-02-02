# 실행: python exercise.py
# 필요 패키지: pip install fastapi sqlalchemy httpx

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from pydantic import BaseModel, ConfigDict

# ============================================================
# 데이터베이스 설정 (수정하지 마세요)
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

# TODO: User 모델을 정의하세요
# - Base를 상속
# - __tablename__ = "users"
# - 컬럼:
#   id: Integer, 기본키, 인덱스
#   username: String, 유일값, 인덱스, NOT NULL
#   email: String, 유일값, NOT NULL
# - 관계:
#   posts = relationship("Post", back_populates="author")

# class User(Base):
#     여기에 모델을 정의하세요
#     pass


# TODO: Post 모델을 정의하세요
# - Base를 상속
# - __tablename__ = "posts"
# - 컬럼:
#   id: Integer, 기본키, 인덱스
#   title: String, NOT NULL
#   content: String, NOT NULL
#   author_id: Integer, ForeignKey("users.id"), NOT NULL
# - 관계:
#   author = relationship("User", back_populates="posts")

# class Post(Base):
#     여기에 모델을 정의하세요
#     pass


# ============================================================
# TODO 2: Pydantic 스키마 정의
# ============================================================

# TODO: UserCreate 스키마 (요청용)
# - username: str
# - email: str

# class UserCreate(BaseModel):
#     pass


# TODO: PostCreate 스키마 (요청용)
# - title: str
# - content: str

# class PostCreate(BaseModel):
#     pass


# TODO: PostResponse 스키마 (응답용)
# - id: int
# - title: str
# - content: str
# - author_id: int
# - model_config = ConfigDict(from_attributes=True)

# class PostResponse(BaseModel):
#     pass


# TODO: UserWithPosts 스키마 (응답용 - 관계 데이터 포함)
# - id: int
# - username: str
# - email: str
# - posts: list[PostResponse] = []  (게시글 목록, 기본값 빈 리스트)
# - model_config = ConfigDict(from_attributes=True)

# class UserWithPosts(BaseModel):
#     pass


# ============================================================
# 테이블 생성 및 의존성 (수정하지 마세요)
# ============================================================
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


# ============================================================
# TODO 3: API 엔드포인트 구현
# ============================================================

# TODO: POST /users - 사용자 생성
# - status_code=201
# - UserCreate를 받아서 User 객체 생성
# - db.add() → db.commit() → db.refresh() → return

# @app.post("/users", status_code=201)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     pass


# TODO: POST /users/{user_id}/posts - 특정 사용자의 게시글 생성
# - response_model=PostResponse, status_code=201
# - 먼저 user_id로 사용자가 존재하는지 확인 (없으면 404)
# - Post 객체 생성 시 author_id=user_id 설정
# - db.add() → db.commit() → db.refresh() → return

# @app.post("/users/{user_id}/posts", response_model=PostResponse, status_code=201)
# def create_post_for_user(user_id: int, post: PostCreate, db: Session = Depends(get_db)):
#     pass


# TODO: GET /users/{user_id} - 사용자 + 게시글 목록 조회
# - response_model=UserWithPosts
# - 사용자가 없으면 404 반환
# - user 객체를 반환하면 relationship이 자동으로 posts를 로드

# @app.get("/users/{user_id}", response_model=UserWithPosts)
# def get_user_with_posts(user_id: int, db: Session = Depends(get_db)):
#     pass


# ============================================================
# 테스트 코드 (수정하지 마세요)
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
