# 실행: python exercise.py
# 필요 패키지: pip install fastapi sqlalchemy httpx

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, ConfigDict

# ============================================================
# 데이터베이스 설정 (수정하지 마세요)
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

# TODO: Post 모델을 정의하세요
# - Base를 상속
# - __tablename__ = "posts"
# - 컬럼:
#   id: Integer, 기본키, 인덱스
#   title: String, NOT NULL
#   content: String, NOT NULL
#   is_published: Boolean, 기본값 False

# class Post(Base):
#     여기에 모델을 정의하세요
#     pass


# ============================================================
# TODO 2: Pydantic 스키마 정의
# ============================================================

# TODO: PostCreate 스키마를 정의하세요 (요청용)
# - title: str
# - content: str

# class PostCreate(BaseModel):
#     pass

# TODO: PostResponse 스키마를 정의하세요 (응답용)
# - id: int
# - title: str
# - content: str
# - is_published: bool
# - model_config = ConfigDict(from_attributes=True)

# class PostResponse(BaseModel):
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
# TODO 3: CRUD API 엔드포인트 구현
# ============================================================

# TODO: POST /posts - 게시글 생성
# - response_model=PostResponse, status_code=201
# - PostCreate를 받아서 Post 객체 생성
# - db.add() → db.commit() → db.refresh() → return

# @app.post("/posts", response_model=PostResponse, status_code=201)
# def create_post(post: PostCreate, db: Session = Depends(get_db)):
#     pass


# TODO: GET /posts - 게시글 목록 조회
# - response_model=list[PostResponse]
# - skip(기본값 0)과 limit(기본값 10) 쿼리 파라미터 지원
# - db.query(Post).offset(skip).limit(limit).all()

# @app.get("/posts", response_model=list[PostResponse])
# def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     pass


# TODO: GET /posts/{post_id} - 게시글 상세 조회
# - response_model=PostResponse
# - 게시글이 없으면 HTTPException(status_code=404) 발생

# @app.get("/posts/{post_id}", response_model=PostResponse)
# def get_post(post_id: int, db: Session = Depends(get_db)):
#     pass


# TODO: PUT /posts/{post_id} - 게시글 수정
# - response_model=PostResponse
# - 게시글이 없으면 HTTPException(status_code=404) 발생
# - 기존 객체의 title, content를 업데이트

# @app.put("/posts/{post_id}", response_model=PostResponse)
# def update_post(post_id: int, post_update: PostCreate, db: Session = Depends(get_db)):
#     pass


# TODO: DELETE /posts/{post_id} - 게시글 삭제
# - status_code=204
# - 게시글이 없으면 HTTPException(status_code=404) 발생

# @app.delete("/posts/{post_id}", status_code=204)
# def delete_post(post_id: int, db: Session = Depends(get_db)):
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
