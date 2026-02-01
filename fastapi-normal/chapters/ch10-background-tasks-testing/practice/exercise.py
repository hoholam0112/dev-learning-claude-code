# 실행 방법:
#   - 앱 실행: uvicorn exercise:app --reload
#   - 테스트 실행: pytest exercise.py -v
# 필요 패키지: pip install fastapi uvicorn pytest httpx sqlalchemy
# 챕터 10 연습 문제 - 직접 코드를 작성해보세요!

import time
import logging
from datetime import datetime
from math import ceil
from pathlib import Path

import pytest
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ── 로깅 설정 ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger("app")

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# ══════════════════════════════════════════════════════════
# 데이터베이스 설정
# ══════════════════════════════════════════════════════════

SQLALCHEMY_DATABASE_URL = "sqlite:///./exercise_ch10.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── SQLAlchemy 모델 ────────────────────────────────────────
class BookModel(Base):
    """도서 테이블"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)


# ── Pydantic 모델 ─────────────────────────────────────────
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0, description="가격은 0보다 커야 합니다")


class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    author: str | None = Field(None, min_length=1, max_length=100)
    price: int | None = Field(None, gt=0)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    price: int

    class Config:
        from_attributes = True


class CleanupRequest(BaseModel):
    directory: str = "uploads"
    max_age_hours: int = Field(default=48, gt=0)


# ── 상태 저장소 ────────────────────────────────────────────
cleanup_logs: list[dict] = []


# ── 의존성 함수 ────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="챕터 10 연습 문제", description="백그라운드 작업 + 테스트")


# ══════════════════════════════════════════════════════════
# 문제 1: 파일 정리 백그라운드 작업
# POST /cleanup — 정리 작업 시작 (백그라운드)
# GET /cleanup/log — 정리 로그 조회
# ══════════════════════════════════════════════════════════

def perform_cleanup(task_id: str, directory: str, max_age_hours: int):
    """파일 정리 백그라운드 작업"""
    # TODO: 구현하세요
    # 1. cleanup_logs에 작업 시작 기록
    # 2. 디렉토리 내 오래된 파일 삭제 (max_age_hours 초과)
    # 3. 빈 디렉토리 삭제
    # 4. 결과 로그 업데이트
    pass


@app.post("/cleanup", tags=["파일 정리"])
async def start_cleanup(
    request: CleanupRequest,
    background_tasks: BackgroundTasks,
):
    """파일 정리 백그라운드 작업을 시작합니다."""
    # TODO: background_tasks.add_task()로 perform_cleanup을 등록하세요
    pass


@app.get("/cleanup/log", tags=["파일 정리"])
async def get_cleanup_logs():
    """파일 정리 작업의 로그를 조회합니다."""
    # TODO: cleanup_logs를 반환하세요
    pass


# ══════════════════════════════════════════════════════════
# 문제 2: 도서 CRUD API (테스트 대상)
# POST /books — 도서 추가 (201, 중복 확인)
# GET /books — 도서 목록
# GET /books/{book_id} — 도서 상세 (404)
# PUT /books/{book_id} — 도서 수정 (404)
# DELETE /books/{book_id} — 도서 삭제 (204/404)
# ══════════════════════════════════════════════════════════


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["도서"])
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """새로운 도서를 추가합니다."""
    # TODO: 중복 확인 (같은 제목+저자) → 도서 생성
    pass


@app.get("/books", response_model=list[BookResponse], tags=["도서"])
def list_books(db: Session = Depends(get_db)):
    """전체 도서 목록을 조회합니다."""
    # TODO: 전체 도서 반환
    pass


@app.get("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    """특정 도서를 조회합니다."""
    # TODO: book_id로 조회, 없으면 404
    pass


@app.put("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """특정 도서를 수정합니다."""
    # TODO: exclude_unset=True로 전달된 필드만 업데이트
    pass


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["도서"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """특정 도서를 삭제합니다."""
    # TODO: book_id로 조회 후 삭제
    pass


# ══════════════════════════════════════════════════════════
# 테스트 코드 (pytest로 실행)
# ══════════════════════════════════════════════════════════

# ── 테스트용 인메모리 DB 설정 ─────────────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """각 테스트 전에 테이블 생성, 후에 삭제"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_book() -> dict:
    return {"title": "파이썬 완벽 가이드", "author": "홍길동", "price": 30000}


# ══════════════════════════════════════════════════════════
# 문제 3: 도서 API 테스트를 작성하세요
# ══════════════════════════════════════════════════════════


class TestCreateBook:
    """도서 생성 API 테스트"""

    def test_도서_생성_성공(self, sample_book):
        """정상적인 도서 생성"""
        # TODO: POST /books 요청 후 201 확인, 반환된 데이터 검증
        pass

    def test_중복_도서_생성_400(self, sample_book):
        """같은 제목+저자의 도서를 두 번 생성하면 400 에러"""
        # TODO: 동일 데이터로 두 번 POST → 두 번째는 400
        pass

    def test_제목_누락_422(self):
        """제목이 누락되면 422 에러"""
        # TODO: title 없이 POST → 422
        pass


class TestReadBook:
    """도서 조회 API 테스트"""

    def test_빈_목록_조회(self):
        """도서가 없을 때 빈 목록 반환"""
        # TODO: GET /books → 200, 빈 리스트
        pass

    def test_존재하지_않는_도서_404(self):
        """존재하지 않는 ID로 조회하면 404"""
        # TODO: GET /books/99999 → 404
        pass


class TestDeleteBook:
    """도서 삭제 API 테스트"""

    def test_도서_삭제_성공(self, sample_book):
        """도서 삭제 시 204 반환"""
        # TODO: POST로 생성 → DELETE → 204
        pass

    def test_삭제_후_조회_404(self, sample_book):
        """삭제 후 같은 ID로 조회하면 404"""
        # TODO: POST → DELETE → GET → 404
        pass


# ══════════════════════════════════════════════════════════
# 문제 4: 경계값 및 에러 케이스 테스트를 작성하세요
# ══════════════════════════════════════════════════════════


class TestValidationErrors:
    """422 유효성 검증 에러 테스트"""

    @pytest.mark.parametrize("missing_field", ["title", "author", "price"])
    def test_필수_필드_누락(self, missing_field):
        """각 필수 필드를 빠뜨리면 422 에러"""
        # TODO: 각 필드를 빠뜨린 데이터로 POST → 422
        pass

    def test_가격_음수_422(self):
        """가격이 0 이하이면 422 에러"""
        # TODO: price=-100으로 POST → 422
        pass


class TestBoundaryValues:
    """경계값 테스트"""

    def test_빈_제목(self):
        """빈 문자열 제목은 422 에러"""
        # TODO: title=""으로 POST → 422
        pass

    def test_최소_가격(self):
        """가격 1은 정상"""
        # TODO: price=1로 POST → 201
        pass
