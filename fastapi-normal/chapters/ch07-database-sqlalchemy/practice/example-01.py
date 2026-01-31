# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn sqlalchemy
# DB 파일: 실행하면 현재 디렉토리에 todos.db 파일이 생성됩니다

"""
챕터 07 예제 01: SQLAlchemy + FastAPI 기본 CRUD (Todo 앱)

이 예제에서는 다음을 학습합니다:
- SQLAlchemy 엔진, 세션, 모델 설정
- 의존성 주입으로 DB 세션 관리
- 기본적인 CRUD (생성, 조회, 수정, 삭제) 구현
"""

from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ── 데이터베이스 설정 ──────────────────────────────────────
# SQLite 파일 기반 데이터베이스 (로컬 개발용)
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

# 엔진 생성 (check_same_thread는 SQLite 전용 옵션)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 기반 클래스
Base = declarative_base()


# ── SQLAlchemy 모델 (DB 테이블) ────────────────────────────
class Todo(Base):
    """할 일 테이블"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 테이블 생성 (앱 시작 시 자동 실행)
Base.metadata.create_all(bind=engine)


# ── Pydantic 모델 (API 스키마) ─────────────────────────────
class TodoCreate(BaseModel):
    """할 일 생성 요청 모델"""
    title: str
    description: str = ""


class TodoUpdate(BaseModel):
    """할 일 수정 요청 모델"""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    """할 일 응답 모델"""
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime

    class Config:
        # ORM 모델에서 Pydantic 모델로 자동 변환 허용
        from_attributes = True


# ── 의존성 함수 ────────────────────────────────────────────
def get_db():
    """
    요청마다 DB 세션을 생성하고, 완료 후 자동으로 닫습니다.
    yield를 사용하여 세션의 생명주기를 관리합니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="Todo API", description="SQLAlchemy를 활용한 기본 CRUD 예제")


# ── CRUD 엔드포인트 ────────────────────────────────────────

# Create: 할 일 생성
@app.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="할 일 생성",
)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """새로운 할 일을 생성합니다."""
    db_todo = Todo(title=todo.title, description=todo.description)
    db.add(db_todo)        # 세션에 추가
    db.commit()            # DB에 반영
    db.refresh(db_todo)    # 자동 생성된 값(id, created_at) 가져오기
    return db_todo


# Read: 전체 목록 조회
@app.get("/todos", response_model=list[TodoResponse], summary="할 일 목록 조회")
def read_todos(
    skip: int = 0,
    limit: int = 20,
    completed: bool | None = None,
    db: Session = Depends(get_db),
):
    """
    할 일 목록을 조회합니다.

    - skip: 건너뛸 항목 수 (기본값: 0)
    - limit: 조회할 항목 수 (기본값: 20)
    - completed: 완료 여부로 필터링 (선택)
    """
    query = db.query(Todo)

    # 완료 여부 필터
    if completed is not None:
        query = query.filter(Todo.completed == completed)

    # 최신순 정렬 + 페이지네이션
    todos = query.order_by(Todo.created_at.desc()).offset(skip).limit(limit).all()
    return todos


# Read: 단일 조회
@app.get("/todos/{todo_id}", response_model=TodoResponse, summary="할 일 상세 조회")
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    """ID로 특정 할 일을 조회합니다."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {todo_id}인 할 일을 찾을 수 없습니다",
        )
    return db_todo


# Update: 수정
@app.patch("/todos/{todo_id}", response_model=TodoResponse, summary="할 일 수정")
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    """
    특정 할 일을 수정합니다.
    전달된 필드만 업데이트됩니다 (부분 수정 지원).
    """
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {todo_id}인 할 일을 찾을 수 없습니다",
        )

    # 전달된 필드만 업데이트
    update_data = todo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


# Delete: 삭제
@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="할 일 삭제")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """특정 할 일을 삭제합니다."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {todo_id}인 할 일을 찾을 수 없습니다",
        )

    db.delete(db_todo)
    db.commit()


# 통계 조회
@app.get("/todos/stats/summary", summary="할 일 통계")
def get_todo_stats(db: Session = Depends(get_db)):
    """할 일의 전체 통계를 반환합니다."""
    total = db.query(Todo).count()
    completed = db.query(Todo).filter(Todo.completed == True).count()
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "0%",
    }
