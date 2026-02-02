# 실행: python exercise.py
# SQLite를 사용하므로 별도 DB 설치 불필요
# 필요 패키지: pip install sqlalchemy

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================
# 문제 1: 데이터베이스 설정
# ============================================================

# TODO: SQLite 데이터베이스 엔진을 생성하세요
# URL: "sqlite:///./test_exercise.db"
# connect_args={"check_same_thread": False}
engine = None  # 이 줄을 수정하세요

# TODO: SessionLocal을 생성하세요
# autocommit=False, autoflush=False, bind=engine
SessionLocal = None  # 이 줄을 수정하세요

# TODO: Base를 생성하세요 (declarative_base 사용)
Base = None  # 이 줄을 수정하세요


# ============================================================
# 문제 2: User 모델 정의
# ============================================================

# TODO: User 모델을 정의하세요
# - Base를 상속받아야 합니다
# - __tablename__ = "users"
# - 컬럼:
#   id: Integer, 기본키(primary_key), 인덱스(index)
#   username: String, 유일값(unique), 인덱스(index), NOT NULL(nullable=False)
#   email: String, 유일값(unique), NOT NULL(nullable=False)
#   full_name: String, NULL 허용(nullable=True)

# class User(...):
#     여기에 모델을 정의하세요
#     pass


# ============================================================
# 문제 3: get_db 의존성 함수
# ============================================================

# TODO: get_db 제너레이터 함수를 작성하세요
# 1. SessionLocal()으로 세션(db)을 생성
# 2. try 블록에서 yield db
# 3. finally 블록에서 db.close()

# def get_db():
#     여기에 함수를 작성하세요
#     pass


# ============================================================
# 테스트 코드 (수정하지 마세요)
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
