# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn sqlalchemy
# DB 파일: 실행하면 현재 디렉토리에 solution.db 파일이 생성됩니다

"""
챕터 07 모범 답안: 데이터베이스 연동 (SQLAlchemy)

문제 1~4의 통합 솔루션입니다.
메모장 + 카테고리/상품 + 페이지네이션 + 검색 기능을 포함합니다.
"""

from datetime import datetime
from enum import Enum
from math import ceil

from fastapi import FastAPI, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime,
    ForeignKey, create_engine, func, or_,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# ── 데이터베이스 설정 ──────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///./solution.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ══════════════════════════════════════════════════════════
# 문제 1: 메모장 모델
# ══════════════════════════════════════════════════════════
class Note(Base):
    """메모 테이블"""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ══════════════════════════════════════════════════════════
# 문제 2: 카테고리 + 상품 모델
# ══════════════════════════════════════════════════════════
class Category(Base):
    """카테고리 테이블"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), default="")

    # 관계: 카테고리에 속한 상품들
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    """상품 테이블"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 외래 키
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # 관계: 상품이 속한 카테고리
    category = relationship("Category", back_populates="products")


# 테이블 생성
Base.metadata.create_all(bind=engine)


# ── Pydantic 모델 ─────────────────────────────────────────

# 문제 1: 메모장 스키마
class NoteCreate(BaseModel):
    title: str
    content: str = ""


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    is_pinned: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotePinResponse(BaseModel):
    id: int
    title: str
    is_pinned: bool
    message: str


# 문제 2: 카테고리/상품 스키마
class CategoryCreate(BaseModel):
    name: str
    description: str = ""


class CategoryBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CategoryWithCount(BaseModel):
    id: int
    name: str
    description: str
    product_count: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0, description="가격 (0보다 커야 합니다)")
    stock: int = Field(ge=0, default=0, description="재고 수량")


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int
    created_at: datetime
    category: CategoryBase

    class Config:
        from_attributes = True


# 문제 3: 페이지네이션 스키마
class PaginationMeta(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedProducts(BaseModel):
    items: list[ProductResponse]
    pagination: PaginationMeta


# 문제 4: 검색 관련
class SearchField(str, Enum):
    title = "title"
    content = "content"
    all = "all"


class SearchResult(BaseModel):
    query: str
    field: str
    count: int
    results: list[NoteResponse]


# ── 의존성 함수 ────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="챕터 07 종합 솔루션", description="메모장 + 카테고리/상품 + 페이지네이션 + 검색")


# ══════════════════════════════════════════════════════════
# 문제 1: 메모장 API
# ══════════════════════════════════════════════════════════

@app.post(
    "/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["메모장"],
    summary="메모 생성",
)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """새로운 메모를 생성합니다."""
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@app.get("/notes", response_model=list[NoteResponse], tags=["메모장"], summary="메모 목록 조회")
def read_notes(db: Session = Depends(get_db)):
    """
    전체 메모 목록을 조회합니다.
    고정된 메모가 먼저 표시되고, 그 다음 최신순으로 정렬됩니다.
    """
    notes = (
        db.query(Note)
        .order_by(Note.is_pinned.desc(), Note.created_at.desc())
        .all()
    )
    return notes


@app.get("/notes/{note_id}", response_model=NoteResponse, tags=["메모장"], summary="메모 상세 조회")
def read_note(note_id: int, db: Session = Depends(get_db)):
    """특정 메모를 조회합니다."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
    return db_note


@app.put("/notes/{note_id}", response_model=NoteResponse, tags=["메모장"], summary="메모 수정")
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """특정 메모를 수정합니다."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")

    update_data = note.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)

    db.commit()
    db.refresh(db_note)
    return db_note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["메모장"], summary="메모 삭제")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """특정 메모를 삭제합니다."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
    db.delete(db_note)
    db.commit()


@app.patch("/notes/{note_id}/pin", response_model=NotePinResponse, tags=["메모장"], summary="메모 고정/해제")
def toggle_pin_note(note_id: int, db: Session = Depends(get_db)):
    """메모의 고정 상태를 토글합니다."""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")

    # 고정 상태 토글
    db_note.is_pinned = not db_note.is_pinned
    db.commit()
    db.refresh(db_note)

    message = "메모가 고정되었습니다" if db_note.is_pinned else "메모 고정이 해제되었습니다"
    return NotePinResponse(
        id=db_note.id,
        title=db_note.title,
        is_pinned=db_note.is_pinned,
        message=message,
    )


# ══════════════════════════════════════════════════════════
# 문제 2: 카테고리별 상품 조회
# ══════════════════════════════════════════════════════════

@app.post(
    "/categories",
    response_model=CategoryBase,
    status_code=status.HTTP_201_CREATED,
    tags=["카테고리/상품"],
    summary="카테고리 생성",
)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """새로운 카테고리를 생성합니다."""
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 카테고리명입니다")

    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get(
    "/categories",
    response_model=list[CategoryWithCount],
    tags=["카테고리/상품"],
    summary="카테고리 목록 (상품 수 포함)",
)
def read_categories(db: Session = Depends(get_db)):
    """전체 카테고리 목록을 조회합니다. 각 카테고리의 상품 수를 포함합니다."""
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        result.append(
            CategoryWithCount(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                product_count=len(cat.products),
            )
        )
    return result


@app.post(
    "/categories/{category_id}/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["카테고리/상품"],
    summary="상품 추가",
)
def create_product(
    category_id: int, product: ProductCreate, db: Session = Depends(get_db)
):
    """특정 카테고리에 상품을 추가합니다."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    db_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
        category_id=category_id,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get(
    "/categories/{category_id}/products",
    response_model=list[ProductResponse],
    tags=["카테고리/상품"],
    summary="카테고리별 상품 조회",
)
def read_category_products(category_id: int, db: Session = Depends(get_db)):
    """특정 카테고리에 속한 상품 목록을 조회합니다."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")

    products = (
        db.query(Product)
        .filter(Product.category_id == category_id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return products


@app.get(
    "/products",
    response_model=list[ProductResponse],
    tags=["카테고리/상품"],
    summary="전체 상품 조회",
)
def read_all_products(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """전체 상품 목록을 조회합니다. 카테고리 정보가 포함됩니다."""
    products = (
        db.query(Product)
        .order_by(Product.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return products


# ══════════════════════════════════════════════════════════
# 문제 3: 페이지네이션이 포함된 상품 목록
# ══════════════════════════════════════════════════════════

class SortBy(str, Enum):
    created_at = "created_at"
    name = "name"
    price = "price"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


@app.get(
    "/products/paginated",
    response_model=PaginatedProducts,
    tags=["페이지네이션"],
    summary="페이지네이션된 상품 목록",
)
def read_products_paginated(
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=10, ge=1, le=100, description="페이지 크기"),
    sort_by: SortBy = Query(default=SortBy.created_at, description="정렬 기준"),
    order: SortOrder = Query(default=SortOrder.desc, description="정렬 방향"),
    db: Session = Depends(get_db),
):
    """
    페이지네이션이 적용된 상품 목록을 조회합니다.

    - page: 페이지 번호 (1부터 시작)
    - size: 한 페이지에 표시할 항목 수
    - sort_by: 정렬 기준 (created_at, name, price)
    - order: 정렬 방향 (asc, desc)
    """
    # 전체 개수 조회
    total_items = db.query(Product).count()
    total_pages = ceil(total_items / size) if total_items > 0 else 1

    # 정렬 설정
    sort_column = getattr(Product, sort_by.value)
    if order == SortOrder.desc:
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    # 오프셋 계산 및 조회
    skip = (page - 1) * size
    products = (
        db.query(Product)
        .order_by(sort_column)
        .offset(skip)
        .limit(size)
        .all()
    )

    # 페이지네이션 메타데이터 구성
    pagination = PaginationMeta(
        page=page,
        size=size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedProducts(items=products, pagination=pagination)


# ══════════════════════════════════════════════════════════
# 문제 4: 검색 기능 (LIKE 쿼리)
# ══════════════════════════════════════════════════════════

@app.get("/search", response_model=SearchResult, tags=["검색"], summary="메모 검색")
def search_notes(
    q: str = Query(min_length=1, description="검색 키워드"),
    field: SearchField = Query(default=SearchField.all, description="검색 대상 필드"),
    db: Session = Depends(get_db),
):
    """
    메모를 검색합니다. 대소문자 구분 없이 부분 일치 검색을 수행합니다.

    - q: 검색 키워드
    - field: 검색 대상 (title, content, all)
    """
    keyword = f"%{q}%"

    query = db.query(Note)

    if field == SearchField.title:
        # 제목에서만 검색
        query = query.filter(Note.title.ilike(keyword))
    elif field == SearchField.content:
        # 내용에서만 검색
        query = query.filter(Note.content.ilike(keyword))
    else:
        # 제목 또는 내용에서 검색 (OR 조건)
        query = query.filter(
            or_(
                Note.title.ilike(keyword),
                Note.content.ilike(keyword),
            )
        )

    results = query.order_by(Note.created_at.desc()).all()

    return SearchResult(
        query=q,
        field=field.value,
        count=len(results),
        results=results,
    )


# ── 초기 데이터 생성 (시연용) ──────────────────────────────
@app.post("/seed", tags=["유틸리티"], summary="시연용 초기 데이터 생성")
def seed_data(db: Session = Depends(get_db)):
    """시연용 초기 데이터를 생성합니다. (개발/테스트 용도)"""
    # 메모 데이터
    sample_notes = [
        Note(title="파이썬 기초 정리", content="변수, 조건문, 반복문 등 기본 문법 정리"),
        Note(title="FastAPI 학습 노트", content="FastAPI 프레임워크의 핵심 기능 학습"),
        Note(title="파이썬 웹 개발", content="Django, Flask, FastAPI 비교"),
        Note(title="장보기 목록", content="우유, 빵, 계란, 과일", is_pinned=True),
        Note(title="회의 메모", content="프로젝트 진행 상황 공유"),
    ]

    # 카테고리 데이터
    electronics = Category(name="전자제품", description="전자 기기 카테고리")
    books = Category(name="도서", description="책 카테고리")

    db.add_all(sample_notes)
    db.add(electronics)
    db.add(books)
    db.commit()

    # 상품 데이터
    sample_products = [
        Product(name="무선 키보드", price=45000, stock=100, category_id=electronics.id),
        Product(name="무선 마우스", price=35000, stock=150, category_id=electronics.id),
        Product(name="모니터 거치대", price=28000, stock=80, category_id=electronics.id),
        Product(name="파이썬 완벽 가이드", price=32000, stock=50, category_id=books.id),
        Product(name="FastAPI 실전 가이드", price=28000, stock=30, category_id=books.id),
    ]

    db.add_all(sample_products)
    db.commit()

    return {"message": "초기 데이터가 생성되었습니다", "notes": 5, "categories": 2, "products": 5}
