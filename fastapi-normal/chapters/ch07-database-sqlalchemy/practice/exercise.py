# 실행 방법: uvicorn exercise:app --reload
# 필요 패키지: pip install fastapi uvicorn sqlalchemy
# 챕터 07 연습 문제 - 직접 코드를 작성해보세요!

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
SQLALCHEMY_DATABASE_URL = "sqlite:///./exercise.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ══════════════════════════════════════════════════════════
# 문제 1: 메모장 모델
# ══════════════════════════════════════════════════════════

# TODO: Note 모델을 정의하세요 (Base 상속)
# 테이블명: "notes"
# 컬럼: id(Integer, PK), title(String(200)), content(Text),
#       is_pinned(Boolean, 기본값 False), created_at(DateTime), updated_at(DateTime)


# ══════════════════════════════════════════════════════════
# 문제 2: 카테고리 + 상품 모델
# ══════════════════════════════════════════════════════════

# TODO: Category 모델을 정의하세요
# 테이블명: "categories"
# 컬럼: id(Integer, PK), name(String(100), unique), description(String(300))
# 관계: products (relationship, back_populates="category")


# TODO: Product 모델을 정의하세요
# 테이블명: "products"
# 컬럼: id(Integer, PK), name(String(200)), price(Integer),
#       stock(Integer, 기본값 0), created_at(DateTime),
#       category_id(Integer, ForeignKey)
# 관계: category (relationship, back_populates="products")


# 테이블 생성
Base.metadata.create_all(bind=engine)


# ── Pydantic 모델 ─────────────────────────────────────────

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


class CategoryCreate(BaseModel):
    name: str
    description: str = ""


class CategoryBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0)
    stock: int = Field(ge=0, default=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    stock: int
    created_at: datetime
    category: CategoryBase

    class Config:
        from_attributes = True


# ── 의존성 함수 ────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="챕터 07 연습 문제", description="데이터베이스 연동")


# ══════════════════════════════════════════════════════════
# 문제 1: 메모장 CRUD API
# POST /notes — 메모 생성 (201)
# GET /notes — 목록 조회 (고정 먼저, 최신순)
# GET /notes/{note_id} — 상세 조회
# PUT /notes/{note_id} — 수정
# DELETE /notes/{note_id} — 삭제 (204)
# PATCH /notes/{note_id}/pin — 고정/해제 토글
# ══════════════════════════════════════════════════════════


@app.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED, tags=["메모장"])
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    """새로운 메모를 생성합니다."""
    # TODO: Note 인스턴스 생성 → db.add → db.commit → db.refresh → 반환
    pass


@app.get("/notes", response_model=list[NoteResponse], tags=["메모장"])
def read_notes(db: Session = Depends(get_db)):
    """전체 메모 목록을 조회합니다. 고정 메모 먼저, 최신순 정렬."""
    # TODO: Note를 is_pinned 내림차순, created_at 내림차순으로 정렬하여 반환
    pass


@app.get("/notes/{note_id}", response_model=NoteResponse, tags=["메모장"])
def read_note(note_id: int, db: Session = Depends(get_db)):
    """특정 메모를 조회합니다."""
    # TODO: note_id로 조회, 없으면 404
    pass


@app.put("/notes/{note_id}", response_model=NoteResponse, tags=["메모장"])
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    """특정 메모를 수정합니다."""
    # TODO: exclude_unset=True로 전달된 필드만 업데이트
    pass


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["메모장"])
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """특정 메모를 삭제합니다."""
    # TODO: note_id로 조회 후 삭제
    pass


@app.patch("/notes/{note_id}/pin", tags=["메모장"])
def toggle_pin_note(note_id: int, db: Session = Depends(get_db)):
    """메모의 고정 상태를 토글합니다."""
    # TODO: is_pinned을 반전시키고 결과를 반환하세요
    pass


# ══════════════════════════════════════════════════════════
# 문제 2: 카테고리별 상품 조회
# POST /categories — 카테고리 생성 (201)
# GET /categories — 목록 조회 (상품 수 포함)
# POST /categories/{category_id}/products — 상품 추가 (201)
# GET /categories/{category_id}/products — 카테고리별 상품 조회
# ══════════════════════════════════════════════════════════


@app.post("/categories", status_code=status.HTTP_201_CREATED, tags=["카테고리/상품"])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """새로운 카테고리를 생성합니다."""
    # TODO: 중복 이름 확인 → Category 생성 → 반환
    pass


@app.get("/categories", tags=["카테고리/상품"])
def read_categories(db: Session = Depends(get_db)):
    """전체 카테고리 목록을 조회합니다. 각 카테고리의 상품 수를 포함합니다."""
    # TODO: 카테고리 목록을 상품 수와 함께 반환
    pass


@app.post("/categories/{category_id}/products", status_code=status.HTTP_201_CREATED, tags=["카테고리/상품"])
def create_product(category_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """특정 카테고리에 상품을 추가합니다."""
    # TODO: 카테고리 존재 확인 → Product 생성 → 반환
    pass


@app.get("/categories/{category_id}/products", tags=["카테고리/상품"])
def read_category_products(category_id: int, db: Session = Depends(get_db)):
    """특정 카테고리에 속한 상품 목록을 조회합니다."""
    # TODO: 카테고리 존재 확인 → 해당 카테고리의 상품 목록 반환
    pass
