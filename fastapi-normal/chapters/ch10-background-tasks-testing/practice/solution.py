# 실행 방법:
#   - 앱 실행: uvicorn solution:app --reload
#   - 테스트 실행: pytest solution.py -v
# 필요 패키지: pip install fastapi uvicorn pytest httpx sqlalchemy

"""
챕터 10 모범 답안: 백그라운드 작업과 테스트

문제 1~4의 통합 솔루션입니다.
파일 정리 백그라운드 작업 + API 테스트 + DB 테스트 + 에러 테스트를 포함합니다.

이 파일은 앱 코드와 테스트 코드를 함께 포함하고 있습니다.
"""

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
# 데이터베이스 설정 (프로덕션)
# ══════════════════════════════════════════════════════════

SQLALCHEMY_DATABASE_URL = "sqlite:///./solution_ch10.db"
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


class CleanupLog(BaseModel):
    task_id: str
    started_at: str
    completed_at: str | None = None
    files_deleted: int = 0
    dirs_deleted: int = 0
    space_freed: str = "0B"
    status: str = "running"


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
app = FastAPI(title="챕터 10 종합 솔루션", description="백그라운드 작업 + 테스트 종합 예제")


# ══════════════════════════════════════════════════════════
# 문제 1: 파일 정리 백그라운드 작업
# ══════════════════════════════════════════════════════════

def perform_cleanup(task_id: str, directory: str, max_age_hours: int):
    """파일 정리 백그라운드 작업"""
    log_entry = {
        "task_id": task_id,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "files_deleted": 0,
        "dirs_deleted": 0,
        "space_freed_bytes": 0,
        "space_freed": "0B",
        "status": "running",
    }
    cleanup_logs.append(log_entry)

    try:
        target_dir = Path(directory)
        if not target_dir.exists():
            log_entry["status"] = "completed"
            log_entry["completed_at"] = datetime.utcnow().isoformat()
            logger.info(f"[{task_id}] 디렉토리가 존재하지 않아 건너뜁니다: {directory}")
            return

        now = time.time()
        max_age_seconds = max_age_hours * 3600
        files_deleted = 0
        dirs_deleted = 0
        space_freed = 0

        # 파일 삭제 (재귀적으로 순회)
        for file_path in sorted(target_dir.rglob("*"), reverse=True):
            if file_path.is_file():
                age = now - file_path.stat().st_mtime
                if age > max_age_seconds:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    files_deleted += 1
                    space_freed += file_size
                    logger.info(f"[{task_id}] 파일 삭제: {file_path}")

        # 빈 디렉토리 삭제
        for dir_path in sorted(target_dir.rglob("*"), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                dir_path.rmdir()
                dirs_deleted += 1
                logger.info(f"[{task_id}] 빈 디렉토리 삭제: {dir_path}")

        # 용량 포맷팅
        if space_freed < 1024:
            space_str = f"{space_freed}B"
        elif space_freed < 1024 * 1024:
            space_str = f"{space_freed / 1024:.1f}KB"
        else:
            space_str = f"{space_freed / (1024 * 1024):.1f}MB"

        # 로그 업데이트
        log_entry["files_deleted"] = files_deleted
        log_entry["dirs_deleted"] = dirs_deleted
        log_entry["space_freed_bytes"] = space_freed
        log_entry["space_freed"] = space_str
        log_entry["status"] = "completed"
        log_entry["completed_at"] = datetime.utcnow().isoformat()

        logger.info(
            f"[{task_id}] 정리 완료: {files_deleted}개 파일, "
            f"{dirs_deleted}개 디렉토리 삭제, {space_str} 확보"
        )

    except Exception as e:
        log_entry["status"] = "failed"
        log_entry["completed_at"] = datetime.utcnow().isoformat()
        logger.error(f"[{task_id}] 정리 실패: {e}")


@app.post("/cleanup", tags=["파일 정리"], summary="파일 정리 시작")
async def start_cleanup(
    request: CleanupRequest,
    background_tasks: BackgroundTasks,
):
    """파일 정리 백그라운드 작업을 시작합니다."""
    task_id = f"cleanup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    background_tasks.add_task(
        perform_cleanup,
        task_id,
        request.directory,
        request.max_age_hours,
    )

    return {
        "message": "파일 정리가 시작되었습니다",
        "task_id": task_id,
        "target_directory": request.directory,
        "max_age_hours": request.max_age_hours,
    }


@app.get("/cleanup/log", tags=["파일 정리"], summary="정리 로그 조회")
async def get_cleanup_logs():
    """파일 정리 작업의 로그를 조회합니다."""
    return {"logs": cleanup_logs}


# ══════════════════════════════════════════════════════════
# 문제 2: 도서 API (테스트 대상)
# ══════════════════════════════════════════════════════════

@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["도서"],
    summary="도서 추가",
)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """새로운 도서를 추가합니다."""
    # 중복 확인
    existing = (
        db.query(BookModel)
        .filter(BookModel.title == book.title, BookModel.author == book.author)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="동일한 제목과 저자의 도서가 이미 존재합니다",
        )

    db_book = BookModel(title=book.title, author=book.author, price=book.price)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/books", response_model=list[BookResponse], tags=["도서"], summary="도서 목록")
def list_books(db: Session = Depends(get_db)):
    """전체 도서 목록을 조회합니다."""
    return db.query(BookModel).all()


@app.get("/books/{book_id}", response_model=BookResponse, tags=["도서"], summary="도서 상세")
def get_book(book_id: int, db: Session = Depends(get_db)):
    """특정 도서를 조회합니다."""
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    return book


@app.put("/books/{book_id}", response_model=BookResponse, tags=["도서"], summary="도서 수정")
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """특정 도서를 수정합니다."""
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")

    update_data = book.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)

    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["도서"],
    summary="도서 삭제",
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """특정 도서를 삭제합니다."""
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다")
    db.delete(db_book)
    db.commit()


# ══════════════════════════════════════════════════════════
# 테스트 코드 (pytest로 실행)
# ══════════════════════════════════════════════════════════

# ── 문제 3: 테스트용 인메모리 DB 설정 ─────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """테스트용 인메모리 DB 세션"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 의존성 오버라이드 적용
app.dependency_overrides[get_db] = override_get_db

# 테스트 클라이언트 생성
client = TestClient(app)


# ── fixture ────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_database():
    """
    각 테스트 전에 인메모리 DB 테이블을 생성하고,
    테스트 후에 테이블을 삭제합니다.
    이렇게 하면 각 테스트가 깨끗한 DB에서 시작합니다.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_book() -> dict:
    """테스트용 도서 데이터"""
    return {"title": "파이썬 완벽 가이드", "author": "홍길동", "price": 30000}


@pytest.fixture
def another_book() -> dict:
    """추가 테스트용 도서 데이터"""
    return {"title": "FastAPI 실전", "author": "김철수", "price": 28000}


@pytest.fixture
def created_book(sample_book) -> dict:
    """DB에 미리 생성된 도서"""
    response = client.post("/books", json=sample_book)
    return response.json()


# ══════════════════════════════════════════════════════════
# 문제 2: API 통합 테스트
# ══════════════════════════════════════════════════════════

class TestCreateBook:
    """도서 생성 API 테스트"""

    def test_도서_생성_성공(self, sample_book):
        """정상적인 도서 생성"""
        response = client.post("/books", json=sample_book)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_book["title"]
        assert data["author"] == sample_book["author"]
        assert data["price"] == sample_book["price"]
        assert "id" in data

    def test_중복_도서_생성_400(self, sample_book):
        """같은 제목+저자의 도서를 두 번 생성하면 400 에러"""
        client.post("/books", json=sample_book)
        response = client.post("/books", json=sample_book)

        assert response.status_code == 400
        assert "이미 존재" in response.json()["detail"]

    def test_제목_누락_422(self):
        """제목이 누락되면 422 에러"""
        response = client.post("/books", json={"author": "작가", "price": 1000})
        assert response.status_code == 422

    def test_가격_음수_422(self):
        """가격이 0 이하이면 422 에러"""
        response = client.post(
            "/books",
            json={"title": "테스트", "author": "작가", "price": -1000},
        )
        assert response.status_code == 422


class TestReadBook:
    """도서 조회 API 테스트"""

    def test_빈_목록_조회(self):
        """도서가 없을 때 빈 목록 반환"""
        response = client.get("/books")
        assert response.status_code == 200
        assert response.json() == []

    def test_도서_목록_조회(self, created_book, another_book):
        """여러 도서가 있을 때 목록 조회"""
        client.post("/books", json=another_book)
        response = client.get("/books")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_도서_상세_조회(self, created_book):
        """ID로 도서 상세 조회"""
        response = client.get(f"/books/{created_book['id']}")

        assert response.status_code == 200
        assert response.json()["title"] == created_book["title"]

    def test_존재하지_않는_도서_404(self):
        """존재하지 않는 ID로 조회하면 404"""
        response = client.get("/books/99999")
        assert response.status_code == 404


class TestUpdateBook:
    """도서 수정 API 테스트"""

    def test_도서_제목_수정(self, created_book):
        """도서 제목 수정 성공"""
        response = client.put(
            f"/books/{created_book['id']}",
            json={"title": "수정된 제목"},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "수정된 제목"
        # 다른 필드는 그대로
        assert response.json()["author"] == created_book["author"]

    def test_도서_가격_수정(self, created_book):
        """도서 가격 수정 성공"""
        response = client.put(
            f"/books/{created_book['id']}",
            json={"price": 99000},
        )

        assert response.status_code == 200
        assert response.json()["price"] == 99000

    def test_존재하지_않는_도서_수정_404(self):
        """존재하지 않는 도서 수정 시 404"""
        response = client.put("/books/99999", json={"title": "없는 책"})
        assert response.status_code == 404


class TestDeleteBook:
    """도서 삭제 API 테스트"""

    def test_도서_삭제_성공(self, created_book):
        """도서 삭제 시 204 반환"""
        response = client.delete(f"/books/{created_book['id']}")
        assert response.status_code == 204

    def test_삭제_후_조회_404(self, created_book):
        """삭제 후 같은 ID로 조회하면 404"""
        client.delete(f"/books/{created_book['id']}")
        response = client.get(f"/books/{created_book['id']}")
        assert response.status_code == 404

    def test_삭제_후_목록에서_제거(self, created_book):
        """삭제 후 목록에서도 제거됨"""
        assert len(client.get("/books").json()) == 1
        client.delete(f"/books/{created_book['id']}")
        assert len(client.get("/books").json()) == 0

    def test_존재하지_않는_도서_삭제_404(self):
        """존재하지 않는 도서 삭제 시 404"""
        response = client.delete("/books/99999")
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════
# 문제 3: DB 격리 테스트
# ══════════════════════════════════════════════════════════

class TestDatabaseIsolation:
    """테스트 간 데이터베이스 격리 확인"""

    def test_첫번째_테스트_데이터_생성(self):
        """첫 번째 테스트에서 데이터를 생성합니다."""
        response = client.post(
            "/books",
            json={"title": "격리 테스트 1", "author": "작가", "price": 1000},
        )
        assert response.status_code == 201
        assert len(client.get("/books").json()) == 1

    def test_두번째_테스트_데이터_없음(self):
        """두 번째 테스트에서는 첫 번째 테스트의 데이터가 없어야 합니다."""
        response = client.get("/books")
        # autouse fixture가 DB를 초기화하므로 비어있어야 합니다
        assert response.status_code == 200
        assert len(response.json()) == 0


# ══════════════════════════════════════════════════════════
# 문제 4: 에러 케이스 테스트
# ══════════════════════════════════════════════════════════

class TestNotFoundErrors:
    """404 에러 테스트"""

    @pytest.mark.parametrize("book_id", [0, -1, 99999, 1000000])
    def test_존재하지_않는_ID_조회(self, book_id):
        """다양한 존재하지 않는 ID로 조회"""
        response = client.get(f"/books/{book_id}")
        assert response.status_code == 404
        assert "detail" in response.json()


class TestValidationErrors:
    """422 유효성 검증 에러 테스트"""

    @pytest.mark.parametrize("missing_field", ["title", "author", "price"])
    def test_필수_필드_누락(self, missing_field):
        """각 필수 필드를 빠뜨리면 422 에러"""
        data = {"title": "테스트", "author": "작가", "price": 1000}
        del data[missing_field]
        response = client.post("/books", json=data)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "field, value, description",
        [
            ("price", "문자열입니다", "가격에 문자열"),
            ("price", -100, "음수 가격"),
            ("price", 0, "가격 0"),
        ],
    )
    def test_잘못된_값(self, field, value, description):
        """잘못된 값이 들어오면 422 에러"""
        data = {"title": "테스트", "author": "작가", "price": 1000}
        data[field] = value
        response = client.post("/books", json=data)
        assert response.status_code == 422, f"실패: {description}"


class TestBoundaryValues:
    """경계값 테스트"""

    def test_빈_제목(self):
        """빈 문자열 제목은 422 에러"""
        response = client.post(
            "/books",
            json={"title": "", "author": "작가", "price": 1000},
        )
        assert response.status_code == 422

    def test_매우_긴_제목(self):
        """201자 이상의 제목은 422 에러"""
        long_title = "가" * 201
        response = client.post(
            "/books",
            json={"title": long_title, "author": "작가", "price": 1000},
        )
        assert response.status_code == 422

    def test_최대_길이_제목_성공(self):
        """200자 제목은 정상 생성"""
        max_title = "가" * 200
        response = client.post(
            "/books",
            json={"title": max_title, "author": "작가", "price": 1000},
        )
        assert response.status_code == 201

    def test_최소_가격(self):
        """가격 1은 정상"""
        response = client.post(
            "/books",
            json={"title": "최소 가격 책", "author": "작가", "price": 1},
        )
        assert response.status_code == 201
        assert response.json()["price"] == 1

    @pytest.mark.parametrize("invalid_price", [0, -1, -100])
    def test_유효하지_않은_가격(self, invalid_price):
        """0 이하 가격은 422 에러"""
        response = client.post(
            "/books",
            json={"title": "테스트", "author": "작가", "price": invalid_price},
        )
        assert response.status_code == 422

    def test_빈_JSON_전송(self):
        """빈 JSON은 422 에러"""
        response = client.post("/books", json={})
        assert response.status_code == 422

    def test_JSON_아닌_본문(self):
        """JSON이 아닌 본문은 422 에러"""
        response = client.post(
            "/books",
            content=b"이것은 JSON이 아닙니다",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
