# 섹션 01: SQLAlchemy 설정 - 모범 답안
# 실행: python solution.py

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================
# 문제 1: 데이터베이스 설정
# ============================================================

# SQLite 데이터베이스 엔진 생성
# - "sqlite:///./test_exercise.db": 현재 디렉토리에 test_exercise.db 파일 생성
# - check_same_thread=False: SQLite의 단일 스레드 제한을 해제 (FastAPI는 멀티스레드)
engine = create_engine(
    "sqlite:///./test_exercise.db",
    connect_args={"check_same_thread": False}
)

# 세션 팩토리 생성
# - autocommit=False: 명시적으로 commit()을 호출해야 변경사항 반영
# - autoflush=False: 쿼리 전에 자동으로 flush하지 않음
# - bind=engine: 위에서 만든 엔진에 바인딩
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base 클래스 생성
# 모든 SQLAlchemy 모델의 부모 클래스
Base = declarative_base()


# ============================================================
# 문제 2: User 모델 정의
# ============================================================

class User(Base):
    """사용자 테이블 모델"""
    __tablename__ = "users"  # 실제 DB 테이블 이름

    # 기본키: 자동 증가하는 정수형 ID
    id = Column(Integer, primary_key=True, index=True)

    # 사용자명: 유일해야 하며, 검색을 위해 인덱스 설정
    username = Column(String, unique=True, index=True, nullable=False)

    # 이메일: 유일해야 하며, 필수 입력
    email = Column(String, unique=True, nullable=False)

    # 이름: 선택 입력 (NULL 허용)
    full_name = Column(String, nullable=True)


# ============================================================
# 문제 3: get_db 의존성 함수
# ============================================================

def get_db():
    """
    데이터베이스 세션을 생성하고 요청 완료 후 닫는 의존성 함수.

    yield 패턴을 사용하여:
    1. SessionLocal()로 세션을 생성
    2. yield로 세션을 엔드포인트에 전달
    3. finally에서 세션을 반드시 닫음 (에러 발생 시에도)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 테스트 코드
# ============================================================
if __name__ == "__main__":
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("✓ 테이블 생성 성공")

    # 세션 테스트
    db = next(get_db())

    # 사용자 추가
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="테스트 사용자"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None, "사용자 id가 생성되지 않았습니다"
    print(f"✓ 사용자 생성 성공: id={user.id}")

    # 사용자 조회
    found = db.query(User).filter(User.username == "testuser").first()
    assert found is not None, "사용자를 찾을 수 없습니다"
    assert found.email == "test@example.com", "이메일이 일치하지 않습니다"
    print(f"✓ 사용자 조회 성공: {found.username}")

    db.close()

    # 정리: 테스트용 DB 파일 삭제
    import os
    os.remove("./test_exercise.db")
    print("\n모든 테스트를 통과했습니다!")
