# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn sqlalchemy[asyncio] aiosqlite
"""
리포지토리 패턴과 트랜잭션 관리 예제.

주요 학습 포인트:
- 제네릭 리포지토리 패턴으로 데이터 접근 계층 추상화
- 서비스 계층에서 비즈니스 로직과 트랜잭션 관리
- 중첩 트랜잭션(세이브포인트)을 사용한 부분 롤백
- 낙관적 잠금(Optimistic Locking) 기법
"""
from contextlib import asynccontextmanager
from typing import TypeVar, Generic, Type, Optional, Any
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy import select, ForeignKey, func, update
from pydantic import BaseModel

# ──────────────────────────────────────────────
# 1. 데이터베이스 설정
# ──────────────────────────────────────────────
DATABASE_URL = "sqlite+aiosqlite:///./repo_pattern_db.sqlite"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# ──────────────────────────────────────────────
# 2. ORM 모델 정의
# ──────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


class Product(Base):
    """상품 모델 (낙관적 잠금 지원)"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column(default=0.0)
    stock: Mapped[int] = mapped_column(default=0)
    version: Mapped[int] = mapped_column(default=1)  # 낙관적 잠금용 버전 필드

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    """주문 모델"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column()
    total_amount: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(default="pending")

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OrderItem(Base):
    """주문 항목 모델"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[float] = mapped_column()

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


# ──────────────────────────────────────────────
# 3. 제네릭 리포지토리 패턴
# ──────────────────────────────────────────────
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    제네릭 리포지토리 베이스 클래스.
    모든 엔티티에 공통되는 CRUD 연산을 제공합니다.

    사용법:
        class ProductRepository(BaseRepository[Product]):
            def __init__(self, session):
                super().__init__(Product, session)
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
        await self.session.flush()  # ID 할당을 위해 flush
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

    async def count(self) -> int:
        """전체 엔티티 수 조회"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0


class ProductRepository(BaseRepository[Product]):
    """
    상품 전용 리포지토리.
    낙관적 잠금과 재고 관리 등 도메인 특화 메서드를 제공합니다.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def decrease_stock_optimistic(
        self, product_id: int, quantity: int
    ) -> bool:
        """
        낙관적 잠금을 사용한 재고 감소.
        version 필드를 사용하여 동시 수정 충돌을 감지합니다.

        동작 원리:
        1. 현재 version과 함께 UPDATE 실행
        2. WHERE 조건에 version 포함
        3. 다른 트랜잭션이 먼저 수정했다면 UPDATE 대상이 0행 -> False 반환
        """
        product = await self.get_by_id(product_id)
        if not product or product.stock < quantity:
            return False

        current_version = product.version
        result = await self.session.execute(
            update(Product)
            .where(Product.id == product_id, Product.version == current_version)
            .values(
                stock=Product.stock - quantity,
                version=Product.version + 1,
            )
        )

        # rowcount가 0이면 다른 트랜잭션이 먼저 수정한 것 (충돌)
        if result.rowcount == 0:
            return False

        # 세션 캐시 갱신
        await self.session.refresh(product)
        return True

    async def search_by_name(self, keyword: str) -> list[Product]:
        """상품명으로 검색"""
        stmt = select(Product).where(Product.name.ilike(f"%{keyword}%"))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class OrderRepository(BaseRepository[Order]):
    """주문 전용 리포지토리"""

    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_with_items(self, order_id: int) -> Optional[Order]:
        """주문과 항목을 함께 조회 (N+1 방지)"""
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


# ──────────────────────────────────────────────
# 4. 서비스 계층 (비즈니스 로직 + 트랜잭션)
# ──────────────────────────────────────────────
class OrderService:
    """
    주문 서비스.
    비즈니스 로직과 트랜잭션 관리를 담당합니다.
    리포지토리를 조합하여 복잡한 비즈니스 연산을 수행합니다.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.order_repo = OrderRepository(session)

    async def create_order(
        self, customer_name: str, items: list[dict]
    ) -> Order:
        """
        주문 생성 (트랜잭션 + 세이브포인트).

        동작 과정:
        1. 주문 레코드 생성
        2. 각 항목에 대해 세이브포인트로 재고 차감 시도
        3. 재고 부족 항목은 건너뛰기 (부분 주문)
        4. 최종 주문 금액 계산
        """
        order = await self.order_repo.create(
            customer_name=customer_name,
            total_amount=0,
            status="processing",
        )

        total_amount = 0.0
        failed_items = []

        for item_data in items:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]

            # 중첩 트랜잭션 (세이브포인트): 개별 항목 실패가 전체에 영향 없음
            try:
                async with self.session.begin_nested():
                    product = await self.product_repo.get_by_id(product_id)
                    if not product:
                        raise ValueError(f"상품 {product_id}를 찾을 수 없습니다")

                    # 낙관적 잠금으로 재고 차감
                    success = await self.product_repo.decrease_stock_optimistic(
                        product_id, quantity
                    )
                    if not success:
                        raise ValueError(f"상품 {product_id}의 재고가 부족합니다")

                    # 주문 항목 생성
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product_id,
                        quantity=quantity,
                        unit_price=product.price,
                    )
                    self.session.add(order_item)
                    await self.session.flush()

                    total_amount += product.price * quantity

            except (ValueError, Exception) as e:
                # 이 항목만 롤백 (세이브포인트), 다른 항목에는 영향 없음
                failed_items.append({
                    "product_id": product_id,
                    "reason": str(e),
                })

        # 주문 최종 업데이트
        if total_amount > 0:
            order.total_amount = total_amount
            order.status = "confirmed"
        else:
            order.status = "failed"

        await self.session.flush()

        if failed_items:
            print(f"[경고] 일부 항목 처리 실패: {failed_items}")

        return order


# ──────────────────────────────────────────────
# 5. Pydantic 스키마
# ──────────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int = 0


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    version: int
    model_config = {"from_attributes": True}


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_name: str
    items: list[OrderItemRequest]


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    total_amount: float
    status: str
    items: list[OrderItemResponse] = []
    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 6. 의존성 주입
# ──────────────────────────────────────────────
async def get_db():
    """비동기 세션 의존성"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_product_repo(
    db: AsyncSession = Depends(get_db),
) -> ProductRepository:
    """상품 리포지토리 의존성"""
    return ProductRepository(db)


async def get_order_service(
    db: AsyncSession = Depends(get_db),
) -> OrderService:
    """주문 서비스 의존성"""
    return OrderService(db)


# ──────────────────────────────────────────────
# 7. 앱 생성 및 lifespan
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 샘플 상품 데이터 삽입
    async with async_session() as session:
        result = await session.execute(select(func.count(Product.id)))
        if result.scalar() == 0:
            products = [
                Product(name="노트북", price=1500000, stock=10),
                Product(name="키보드", price=150000, stock=50),
                Product(name="마우스", price=80000, stock=100),
                Product(name="모니터", price=500000, stock=5),
            ]
            session.add_all(products)
            await session.commit()

    yield
    await engine.dispose()


app = FastAPI(
    title="리포지토리 패턴 예제",
    description="제네릭 리포지토리, 서비스 계층, 트랜잭션 관리",
    lifespan=lifespan,
)


# ──────────────────────────────────────────────
# 8. API 엔드포인트
# ──────────────────────────────────────────────
@app.get("/products", response_model=list[ProductResponse])
async def list_products(repo: ProductRepository = Depends(get_product_repo)):
    """전체 상품 목록 조회"""
    return await repo.get_all()


@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    repo: ProductRepository = Depends(get_product_repo),
):
    """새 상품 등록"""
    return await repo.create(
        name=data.name, price=data.price, stock=data.stock
    )


@app.get("/products/search", response_model=list[ProductResponse])
async def search_products(
    keyword: str,
    repo: ProductRepository = Depends(get_product_repo),
):
    """상품명 검색"""
    return await repo.search_by_name(keyword)


@app.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    """
    주문 생성.

    세이브포인트를 사용하여 일부 항목이 실패해도
    나머지 항목으로 부분 주문을 생성합니다.

    요청 예시:
    {
        "customer_name": "홍길동",
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    """
    items = [item.model_dump() for item in data.items]
    order = await service.create_order(data.customer_name, items)

    if order.status == "failed":
        raise HTTPException(
            status_code=400,
            detail="모든 주문 항목이 처리에 실패했습니다",
        )

    return order


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """주문 상세 조회"""
    repo = OrderRepository(db)
    order = await repo.get_with_items(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order
