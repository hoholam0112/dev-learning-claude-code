# 섹션 02: CRUD 구현 - 모범 답안
# 실행: python solution.py
# 필요 패키지: pip install fastapi sqlalchemy httpx

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict

# ============================================================
# 데이터베이스 설정
# ============================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_crud.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# TODO 1: SQLAlchemy 모델 정의
# ============================================================

class Post(Base):
    """게시글 테이블 모델"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    is_published = Column(Boolean, default=False)


# ============================================================
# TODO 2: Pydantic 스키마 정의
# ============================================================

class PostCreate(BaseModel):
    """게시글 생성/수정 요청 스키마"""
    title: str
    content: str


class PostResponse(BaseModel):
    """게시글 응답 스키마"""
    id: int
    title: str
    content: str
    is_published: bool

    # SQLAlchemy 모델 객체를 Pydantic 모델로 변환 허용
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
# TODO 3: CRUD API 엔드포인트 구현
# ============================================================

@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """새 게시글을 생성합니다"""
    # Pydantic 모델의 데이터로 SQLAlchemy 모델 객체를 생성
    db_post = Post(
        title=post.title,
        content=post.content
    )
    # 세션에 추가하고 DB에 반영
    db.add(db_post)
    db.commit()
    # DB에서 자동 생성된 값(id 등)을 새로고침
    db.refresh(db_post)
    return db_post


@app.get("/posts", response_model=list[PostResponse])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """게시글 목록을 조회합니다 (페이지네이션 지원)"""
    # offset: 건너뛸 개수, limit: 가져올 최대 개수
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts


@app.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """특정 게시글을 조회합니다"""
    post = db.query(Post).filter(Post.id == post_id).first()
    # 게시글이 없으면 404 에러
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")
    return post


@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostCreate,
    db: Session = Depends(get_db)
):
    """게시글을 수정합니다"""
    # 기존 게시글 조회
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")

    # 속성 업데이트 (SQLAlchemy가 변경을 자동 추적)
    db_post.title = post_update.title
    db_post.content = post_update.content

    # 변경사항을 DB에 반영
    db.commit()
    db.refresh(db_post)
    return db_post


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """게시글을 삭제합니다"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다")

    # 세션에서 객체를 삭제하고 DB에 반영
    db.delete(db_post)
    db.commit()
    return None


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

    # 테스트 1: 게시글 생성
    response = client.post(
        "/posts",
        json={"title": "첫 번째 글", "content": "안녕하세요!"}
    )
    assert response.status_code == 201, f"기대: 201, 실제: {response.status_code}"
    data = response.json()
    assert data["title"] == "첫 번째 글"
    assert data["id"] is not None
    assert data["is_published"] == False
    print("✓ 게시글 생성 테스트 통과")

    # 추가 게시글 생성
    client.post("/posts", json={"title": "두 번째 글", "content": "반갑습니다!"})

    # 테스트 2: 게시글 목록 조회
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2, f"기대: 2개, 실제: {len(data)}개"
    print("✓ 게시글 목록 조회 테스트 통과")

    # 테스트 3: 게시글 상세 조회
    response = client.get("/posts/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "첫 번째 글"
    print("✓ 게시글 상세 조회 테스트 통과")

    # 테스트 4: 존재하지 않는 게시글 조회
    response = client.get("/posts/999")
    assert response.status_code == 404, f"기대: 404, 실제: {response.status_code}"
    print("✓ 존재하지 않는 게시글 조회 시 404 테스트 통과")

    # 테스트 5: 게시글 수정
    response = client.put(
        "/posts/1",
        json={"title": "수정된 제목", "content": "수정된 내용"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "수정된 제목"
    assert data["content"] == "수정된 내용"
    print("✓ 게시글 수정 테스트 통과")

    # 테스트 6: 게시글 삭제
    response = client.delete("/posts/1")
    assert response.status_code == 204, f"기대: 204, 실제: {response.status_code}"
    print("✓ 게시글 삭제 테스트 통과")

    # 테스트 7: 삭제된 게시글 조회
    response = client.get("/posts/1")
    assert response.status_code == 404
    print("✓ 삭제된 게시글 조회 시 404 테스트 통과")

    # 정리
    import os
    if os.path.exists("./test_crud.db"):
        os.remove("./test_crud.db")

    print("\n모든 테스트를 통과했습니다!")
