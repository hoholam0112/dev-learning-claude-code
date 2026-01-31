# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn sqlalchemy[asyncio] aiosqlite
"""
비동기 SQLAlchemy 2.0을 사용한 고성능 데이터베이스 연동 예제
커넥션 풀 설정과 N+1 문제 해결을 포함합니다.

주요 학습 포인트:
- AsyncEngine과 커넥션 풀 최적화
- selectinload로 N+1 문제 해결
- 비동기 세션 의존성 주입
- lifespan 이벤트로 테이블 생성/엔진 정리
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy import select, ForeignKey, func, event
from pydantic import BaseModel
from typing import Optional
import time

# ──────────────────────────────────────────────
# 1. 비동기 엔진 설정 (커넥션 풀 최적화)
# ──────────────────────────────────────────────
DATABASE_URL = "sqlite+aiosqlite:///./expert_db.sqlite"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,          # 기본 풀 크기: 동시에 유지할 연결 수
    max_overflow=10,      # 최대 추가 연결 수 (풀 초과 시)
    pool_timeout=30,      # 연결 대기 타임아웃 (초)
    pool_recycle=1800,    # 연결 재활용 주기 (30분)
    echo=False,           # SQL 로깅 비활성화 (프로덕션 권장)
)

# async_sessionmaker: 비동기 세션 팩토리
# expire_on_commit=False: 커밋 후 속성 만료 방지 (비동기 필수)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# ──────────────────────────────────────────────
# 2. 쿼리 카운터 (N+1 문제 감지용)
# ──────────────────────────────────────────────
class QueryCounter:
    """요청당 실행된 SQL 쿼리 수를 추적하는 유틸리티"""

    def __init__(self):
        self.count = 0

    def reset(self):
        self.count = 0

    def increment(self):
        self.count += 1


query_counter = QueryCounter()


# SQLAlchemy 이벤트 리스너: 쿼리 실행마다 카운터 증가
@event.listens_for(engine.sync_engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    query_counter.increment()


# ──────────────────────────────────────────────
# 3. ORM 모델 정의
# ──────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class Author(Base):
    """저자 모델"""
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[Optional[str]] = mapped_column(default=None)

    # selectin 로딩: N+1 문제 해결의 핵심
    # lazy="selectin"은 Author 조회 시 books를 IN 쿼리로 자동 로딩
    books: Mapped[list["Book"]] = relationship(
        back_populates="author",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Author(id={self.id}, name={self.name})"


class Book(Base):
    """도서 모델"""
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    isbn: Mapped[Optional[str]] = mapped_column(default=None)
    price: Mapped[float] = mapped_column(default=0.0)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    author: Mapped["Author"] = relationship(back_populates="books")

    def __repr__(self) -> str:
        return f"Book(id={self.id}, title={self.title})"


# ──────────────────────────────────────────────
# 4. Pydantic 스키마
# ──────────────────────────────────────────────
class BookCreate(BaseModel):
    title: str
    isbn: Optional[str] = None
    price: float = 0.0


class BookResponse(BaseModel):
    id: int
    title: str
    isbn: Optional[str]
    price: float
    model_config = {"from_attributes": True}


class AuthorCreate(BaseModel):
    name: str
    email: Optional[str] = None


class AuthorResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    books: list[BookResponse] = []
    model_config = {"from_attributes": True}


class QueryStatsResponse(BaseModel):
    """쿼리 성능 통계 응답"""
    query_count: int
    execution_time_ms: float
    data: list[AuthorResponse]


# ──────────────────────────────────────────────
# 5. 의존성 주입
# ──────────────────────────────────────────────
async def get_db():
    """
    비동기 데이터베이스 세션 의존성.
    - 정상 완료 시 자동 커밋
    - 예외 발생 시 자동 롤백
    - 항상 세션 종료 보장
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ──────────────────────────────────────────────
# 6. 앱 생성 및 lifespan
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 관리:
    - 시작: 테이블 생성 + 샘플 데이터 삽입
    - 종료: 엔진 정리 (커넥션 풀 해제)
    """
    # 시작: 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 샘플 데이터 삽입
    async with async_session() as session:
        result = await session.execute(select(func.count(Author.id)))
        if result.scalar() == 0:
            authors_data = [
                Author(
                    name="김영한",
                    email="kim@example.com",
                    books=[
                        Book(title="스프링 입문", isbn="978-1", price=35000),
                        Book(title="JPA 프로그래밍", isbn="978-2", price=42000),
                    ],
                ),
                Author(
                    name="이일민",
                    email="lee@example.com",
                    books=[
                        Book(title="토비의 스프링", isbn="978-3", price=55000),
                    ],
                ),
                Author(
                    name="조영호",
                    email="cho@example.com",
                    books=[
                        Book(title="오브젝트", isbn="978-4", price=38000),
                        Book(title="객체지향의 사실과 오해", isbn="978-5", price=22000),
                    ],
                ),
            ]
            session.add_all(authors_data)
            await session.commit()

    yield

    # 종료: 엔진 정리
    await engine.dispose()


app = FastAPI(
    title="비동기 DB 최적화 예제",
    description="SQLAlchemy 2.0 비동기 엔진과 커넥션 풀 최적화",
    lifespan=lifespan,
)


# ──────────────────────────────────────────────
# 7. API 엔드포인트
# ──────────────────────────────────────────────
@app.get("/authors", response_model=list[AuthorResponse])
async def get_authors(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=100, description="최대 반환 수"),
    db: AsyncSession = Depends(get_db),
):
    """
    저자 목록 조회 (N+1 문제 해결 버전).
    selectinload로 books를 효율적으로 함께 로딩합니다.
    """
    result = await db.execute(
        select(Author)
        .options(selectinload(Author.books))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@app.get("/authors/stats", response_model=QueryStatsResponse)
async def get_authors_with_stats(db: AsyncSession = Depends(get_db)):
    """
    저자 목록 조회 + 쿼리 성능 통계.
    실행된 SQL 쿼리 수와 실행 시간을 함께 반환합니다.
    N+1 문제 감지에 유용합니다.
    """
    query_counter.reset()
    start_time = time.perf_counter()

    result = await db.execute(
        select(Author).options(selectinload(Author.books))
    )
    authors = result.scalars().all()

    execution_time = (time.perf_counter() - start_time) * 1000  # ms 변환

    return QueryStatsResponse(
        query_count=query_counter.count,
        execution_time_ms=round(execution_time, 2),
        data=[AuthorResponse.model_validate(a) for a in authors],
    )


@app.get("/authors/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int, db: AsyncSession = Depends(get_db)):
    """저자 상세 조회"""
    author = await db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="저자를 찾을 수 없습니다")
    return author


@app.post("/authors", response_model=AuthorResponse, status_code=201)
async def create_author(data: AuthorCreate, db: AsyncSession = Depends(get_db)):
    """새 저자 생성"""
    author = Author(name=data.name, email=data.email)
    db.add(author)
    await db.flush()  # ID 생성을 위해 flush (커밋은 의존성에서)
    return author


@app.post("/authors/{author_id}/books", response_model=BookResponse, status_code=201)
async def create_book(
    author_id: int,
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
):
    """저자에게 도서 추가"""
    # 저자 존재 확인
    author = await db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="저자를 찾을 수 없습니다")

    book = Book(
        title=data.title,
        isbn=data.isbn,
        price=data.price,
        author_id=author_id,
    )
    db.add(book)
    await db.flush()
    return book


@app.delete("/authors/{author_id}", status_code=204)
async def delete_author(author_id: int, db: AsyncSession = Depends(get_db)):
    """저자 삭제 (연관 도서도 함께 삭제)"""
    author = await db.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="저자를 찾을 수 없습니다")
    await db.delete(author)


@app.get("/pool-status")
async def get_pool_status():
    """
    커넥션 풀 상태 조회.
    현재 풀의 연결 사용 현황을 실시간으로 확인할 수 있습니다.
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),    # 유휴 연결 수
        "checked_out": pool.checkedout(),  # 사용 중인 연결 수
        "overflow": pool.overflow(),       # 오버플로우 연결 수
        "total": pool.checkedin() + pool.checkedout(),
    }
