# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn sqlalchemy[asyncio] aiosqlite
"""
챕터 06 연습문제 모범 답안.

문제 1: 비동기 리포지토리 패턴 완전 구현
문제 2: 커넥션 풀 모니터링 미들웨어
문제 3: 낙관적 잠금(Optimistic Locking)
문제 4: 읽기/쓰기 분리 의존성
"""
import asyncio
import itertools
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import TypeVar, Generic, Type, Optional, Any

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select, ForeignKey, func, update, String
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터베이스 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATABASE_URL = "sqlite+aiosqlite:///./solution_db.sqlite"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ORM 모델 정의
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Base(DeclarativeBase):
    pass


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )


class Post(Base):
    """게시글 모델"""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column(default="")
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")


class Account(Base):
    """계좌 모델 (낙관적 잠금 지원)"""
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column()
    balance: Mapped[float] = mapped_column(default=0.0)
    version: Mapped[int] = mapped_column(default=1)
    updated_at: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 1: 비동기 리포지토리 패턴 완전 구현
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    제네릭 리포지토리 베이스 클래스.
    모든 엔티티에 공통되는 CRUD + 유틸리티 메서드를 제공합니다.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """ID로 엔티티 조회"""
        return await self.session.get(self.model, id)

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """전체 엔티티 목록 조회 (페이징)"""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelType:
        """새 엔티티 생성"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: int, **kwargs: Any) -> Optional[ModelType]:
        """엔티티 수정"""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.session.flush()
        return instance

    async def delete(self, id: int) -> bool:
        """엔티티 삭제"""
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False

    async def exists(self, id: int) -> bool:
        """엔티티 존재 여부 확인 (효율적: 전체 로딩 없이 확인)"""
        stmt = select(func.count()).select_from(self.model).where(
            self.model.id == id  # type: ignore
        )
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def count(self) -> int:
        """전체 엔티티 수"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0


class UserRepository(BaseRepository[User]):
    """사용자 전용 리포지토리"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_posts(self, user_id: int) -> Optional[User]:
        """사용자와 게시글 함께 조회 (N+1 방지)"""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.posts))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PostRepository(BaseRepository[Post]):
    """게시글 전용 리포지토리"""

    def __init__(self, session: AsyncSession):
        super().__init__(Post, session)

    async def get_by_author(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """특정 저자의 게시글 조회"""
        stmt = (
            select(Post)
            .where(Post.author_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search(self, keyword: str) -> list[Post]:
        """제목 또는 내용에서 키워드 검색"""
        stmt = select(Post).where(
            Post.title.ilike(f"%{keyword}%")
            | Post.content.ilike(f"%{keyword}%")
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 2: 커넥션 풀 모니터링 미들웨어
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class PoolMonitorMiddleware(BaseHTTPMiddleware):
    """
    커넥션 풀 상태 모니터링 미들웨어.
    모든 요청에 대해 풀 사용률을 추적하고 로깅합니다.
    """

    def __init__(self, app, db_engine: AsyncEngine):
        super().__init__(app)
        self.db_engine = db_engine

    def _get_pool_usage(self) -> dict:
        """현재 풀 상태를 딕셔너리로 반환"""
        pool = self.db_engine.pool
        checked_out = pool.checkedout()
        pool_size = pool.size()
        overflow = pool.overflow()
        total_capacity = pool_size + max(overflow, 0)

        # 사용률 계산 (총 용량이 0이면 0%)
        usage_percent = (
            (checked_out / total_capacity * 100) if total_capacity > 0 else 0
        )

        return {
            "checked_in": pool.checkedin(),
            "checked_out": checked_out,
            "pool_size": pool_size,
            "overflow": overflow,
            "total_capacity": total_capacity,
            "usage_percent": round(usage_percent, 1),
        }

    async def dispatch(self, request: Request, call_next):
        """요청 전후 풀 상태를 로깅"""
        # 요청 시작 시 풀 상태
        before_stats = self._get_pool_usage()
        logger.info(
            f"[풀 모니터] 요청 시작 {request.method} {request.url.path} "
            f"- 풀 사용률: {before_stats['usage_percent']}%"
        )

        # 요청 처리
        response = await call_next(request)

        # 요청 완료 후 풀 상태
        after_stats = self._get_pool_usage()
        usage = after_stats["usage_percent"]

        # 경고 레벨 결정
        if usage >= 95:
            logger.critical(
                f"[풀 모니터] DB 커넥션 풀 사용률 {usage}% "
                f"(checked_out={after_stats['checked_out']}, "
                f"total={after_stats['total_capacity']})"
            )
        elif usage >= 80:
            logger.warning(
                f"[풀 모니터] DB 커넥션 풀 사용률 {usage}% "
                f"(checked_out={after_stats['checked_out']}, "
                f"total={after_stats['total_capacity']})"
            )

        # 응답 헤더에 풀 사용률 추가
        response.headers["X-DB-Pool-Usage"] = f"{usage}%"

        return response


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 3: 낙관적 잠금(Optimistic Locking)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class OptimisticLockError(Exception):
    """낙관적 잠금 충돌 시 발생하는 예외"""

    def __init__(self, entity_type: str, entity_id: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(
            f"{entity_type}(id={entity_id}) 수정 충돌: "
            f"다른 트랜잭션이 먼저 수정했습니다"
        )


async def optimistic_update(
    session: AsyncSession,
    entity_id: int,
    current_version: int,
    retry_count: int = 3,
    **update_values: Any,
) -> Account:
    """
    낙관적 잠금을 사용한 계좌 업데이트.
    version이 일치할 때만 UPDATE를 수행합니다.

    Args:
        session: 비동기 세션
        entity_id: 계좌 ID
        current_version: 현재 알고 있는 version
        retry_count: 충돌 시 최대 재시도 횟수
        **update_values: 업데이트할 필드와 값
    """
    for attempt in range(retry_count):
        # 최신 데이터 조회
        if attempt > 0:
            # 재시도 시 세션 캐시 무효화
            account = await session.get(Account, entity_id)
            if account:
                await session.refresh(account)
                current_version = account.version

        # version 조건부 UPDATE
        result = await session.execute(
            update(Account)
            .where(
                Account.id == entity_id,
                Account.version == current_version,
            )
            .values(
                version=Account.version + 1,
                updated_at=datetime.now(timezone.utc),
                **update_values,
            )
        )

        if result.rowcount > 0:
            # 성공: 세션 캐시 갱신
            account = await session.get(Account, entity_id)
            if account:
                await session.refresh(account)
            return account  # type: ignore

        # 충돌 감지: 지수 백오프 후 재시도
        logger.warning(
            f"낙관적 잠금 충돌 (시도 {attempt + 1}/{retry_count}): "
            f"Account(id={entity_id})"
        )
        await asyncio.sleep(0.1 * (attempt + 1))

    # 모든 재시도 실패
    raise OptimisticLockError("Account", entity_id)


async def transfer_funds(
    session: AsyncSession,
    from_id: int,
    to_id: int,
    amount: float,
) -> dict:
    """
    계좌 간 이체 (낙관적 잠금 적용).

    두 계좌 모두 낙관적 잠금으로 보호하며,
    잔액 부족 시 에러를 발생시킵니다.
    """
    # 출금 계좌 확인
    from_account = await session.get(Account, from_id)
    if not from_account:
        raise ValueError(f"출금 계좌(id={from_id})를 찾을 수 없습니다")

    if from_account.balance < amount:
        raise ValueError(
            f"잔액 부족: 현재 {from_account.balance}원, 이체 요청 {amount}원"
        )

    # 입금 계좌 확인
    to_account = await session.get(Account, to_id)
    if not to_account:
        raise ValueError(f"입금 계좌(id={to_id})를 찾을 수 없습니다")

    # 출금 (낙관적 잠금)
    await optimistic_update(
        session,
        from_id,
        from_account.version,
        balance=Account.balance - amount,
    )

    # 입금 (낙관적 잠금)
    await optimistic_update(
        session,
        to_id,
        to_account.version,
        balance=Account.balance + amount,
    )

    await session.flush()

    # 최종 상태 조회
    from_account = await session.get(Account, from_id)
    to_account = await session.get(Account, to_id)

    return {
        "from_account": {
            "id": from_id,
            "balance": from_account.balance if from_account else 0,
        },
        "to_account": {
            "id": to_id,
            "balance": to_account.balance if to_account else 0,
        },
        "amount": amount,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 문제 4: 읽기/쓰기 분리 의존성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class DatabaseSessionManager:
    """
    읽기/쓰기 분리 데이터베이스 세션 매니저.
    마스터(쓰기)와 레플리카(읽기) 엔진을 관리합니다.
    읽기 요청은 라운드 로빈으로 레플리카에 분산합니다.
    """

    def __init__(self, write_url: str, read_urls: list[str]):
        # 마스터 엔진 (쓰기)
        self.write_engine = create_async_engine(
            write_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        self.write_session_factory = async_sessionmaker(
            self.write_engine, expire_on_commit=False
        )

        # 레플리카 엔진 목록 (읽기)
        self.read_engines = [
            create_async_engine(url, pool_size=5, pool_pre_ping=True)
            for url in read_urls
        ]
        self.read_session_factories = [
            async_sessionmaker(eng, expire_on_commit=False)
            for eng in self.read_engines
        ]

        # 라운드 로빈 이터레이터
        self._read_cycle = itertools.cycle(
            range(len(self.read_session_factories))
        )

    async def get_write_session(self):
        """쓰기용 세션 (마스터)"""
        async with self.write_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def get_read_session(self):
        """읽기용 세션 (레플리카, 라운드 로빈)"""
        index = next(self._read_cycle)
        factory = self.read_session_factories[index]
        logger.info(f"[읽기/쓰기 분리] 레플리카 #{index} 사용")
        async with factory() as session:
            yield session  # 읽기 전용: 커밋 불필요

    async def dispose_all(self):
        """모든 엔진 정리"""
        await self.write_engine.dispose()
        for eng in self.read_engines:
            await eng.dispose()


# 데이터베이스 매니저 인스턴스
# (실제로는 레플리카 URL이 다르지만, 테스트를 위해 같은 DB 사용)
db_manager = DatabaseSessionManager(
    write_url=DATABASE_URL,
    read_urls=[DATABASE_URL, DATABASE_URL],  # 레플리카 2개 시뮬레이션
)


async def get_write_db():
    """쓰기용 세션 의존성"""
    async for session in db_manager.get_write_session():
        yield session


async def get_read_db():
    """읽기용 세션 의존성"""
    async for session in db_manager.get_read_session():
        yield session


async def get_auto_db(request: Request):
    """
    HTTP 메서드에 따라 자동으로 세션 선택.
    GET/HEAD/OPTIONS -> 읽기 레플리카
    POST/PUT/PATCH/DELETE -> 마스터
    """
    read_methods = {"GET", "HEAD", "OPTIONS"}
    if request.method in read_methods:
        logger.info(f"[자동 선택] {request.method} -> 읽기 레플리카")
        async for session in db_manager.get_read_session():
            yield session
    else:
        logger.info(f"[자동 선택] {request.method} -> 마스터 DB")
        async for session in db_manager.get_write_session():
            yield session


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pydantic 스키마
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class UserCreate(BaseModel):
    name: str
    email: str


class PostCreate(BaseModel):
    title: str
    content: str = ""


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = {"from_attributes": True}


class UserWithPostsResponse(UserResponse):
    posts: list[PostResponse] = []


class AccountCreate(BaseModel):
    owner: str
    balance: float = 0.0


class AccountResponse(BaseModel):
    id: int
    owner: str
    balance: float
    version: int
    model_config = {"from_attributes": True}


class TransferRequest(BaseModel):
    from_id: int
    to_id: int
    amount: float


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 의존성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 앱 생성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 샘플 데이터
    async with async_session() as session:
        result = await session.execute(select(func.count(User.id)))
        if result.scalar() == 0:
            user1 = User(name="홍길동", email="hong@test.com")
            user2 = User(name="김철수", email="kim@test.com")
            session.add_all([user1, user2])
            await session.flush()

            posts = [
                Post(title="첫 번째 글", content="내용입니다", author_id=user1.id),
                Post(title="두 번째 글", content="파이썬 학습", author_id=user1.id),
                Post(title="세 번째 글", content="FastAPI 심화", author_id=user2.id),
            ]
            session.add_all(posts)

            accounts = [
                Account(owner="홍길동", balance=1000000),
                Account(owner="김철수", balance=500000),
            ]
            session.add_all(accounts)
            await session.commit()

    yield

    await engine.dispose()
    await db_manager.dispose_all()


app = FastAPI(
    title="챕터 06 모범 답안",
    description="리포지토리 패턴, 풀 모니터링, 낙관적 잠금, 읽기/쓰기 분리",
    lifespan=lifespan,
)

# 미들웨어 등록
app.add_middleware(PoolMonitorMiddleware, db_engine=engine)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API 엔드포인트
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# --- 문제 1: 리포지토리 패턴 ---
@app.get("/users", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_read_db)):
    """사용자 목록 (읽기 레플리카 사용)"""
    repo = UserRepository(db)
    return await repo.get_all()


@app.get("/users/{user_id}", response_model=UserWithPostsResponse)
async def get_user_with_posts(user_id: int, db: AsyncSession = Depends(get_read_db)):
    """사용자 상세 + 게시글 (N+1 방지)"""
    repo = UserRepository(db)
    user = await repo.get_with_posts(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    return user


@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_write_db)):
    """사용자 생성 (마스터 DB 사용)"""
    repo = UserRepository(db)
    existing = await repo.find_by_email(data.email)
    if existing:
        raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다")
    return await repo.create(name=data.name, email=data.email)


@app.post("/users/{user_id}/posts", response_model=PostResponse, status_code=201)
async def create_post(
    user_id: int,
    data: PostCreate,
    db: AsyncSession = Depends(get_write_db),
):
    """게시글 작성"""
    user_repo = UserRepository(db)
    if not await user_repo.exists(user_id):
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    post_repo = PostRepository(db)
    return await post_repo.create(
        title=data.title,
        content=data.content,
        author_id=user_id,
    )


@app.get("/posts/search", response_model=list[PostResponse])
async def search_posts(keyword: str, db: AsyncSession = Depends(get_read_db)):
    """게시글 검색"""
    repo = PostRepository(db)
    return await repo.search(keyword)


# --- 문제 2: 풀 모니터링 ---
@app.get("/pool-metrics")
async def get_pool_metrics():
    """현재 커넥션 풀 상태"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.checkedin() + pool.checkedout(),
    }


# --- 문제 3: 낙관적 잠금 ---
@app.get("/accounts", response_model=list[AccountResponse])
async def list_accounts(db: AsyncSession = Depends(get_read_db)):
    """전체 계좌 목록"""
    result = await db.execute(select(Account))
    return result.scalars().all()


@app.post("/accounts", response_model=AccountResponse, status_code=201)
async def create_account(
    data: AccountCreate, db: AsyncSession = Depends(get_write_db)
):
    """계좌 생성"""
    account = Account(owner=data.owner, balance=data.balance)
    db.add(account)
    await db.flush()
    return account


@app.post("/accounts/transfer")
async def api_transfer_funds(
    data: TransferRequest,
    db: AsyncSession = Depends(get_write_db),
):
    """
    계좌 이체 (낙관적 잠금 적용).
    동시 수정 충돌 시 자동 재시도합니다.
    """
    try:
        result = await transfer_funds(
            db, data.from_id, data.to_id, data.amount
        )
        return {"status": "success", "detail": result}
    except OptimisticLockError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
