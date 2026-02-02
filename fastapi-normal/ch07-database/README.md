# Ch07: 데이터베이스 연동

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: Ch05 의존성 주입 완료
> **예상 학습 시간**: 4~5시간

---

## 개요

이 챕터에서는 **FastAPI와 SQLAlchemy를 사용하여 데이터베이스를 연동**하는 방법을 학습합니다.
SQLite를 사용하므로 별도의 데이터베이스 서버를 설치할 필요가 없습니다.

### 왜 데이터베이스가 필요한가?

지금까지의 챕터에서는 데이터를 메모리(리스트, 딕셔너리)에 저장했습니다.
하지만 서버가 재시작되면 데이터가 모두 사라집니다.

```
메모리 저장 방식:                   데이터베이스 저장 방식:
┌─────────────┐                   ┌─────────────┐
│  FastAPI 앱  │                   │  FastAPI 앱  │
│ ┌─────────┐ │  서버 재시작 시    │             │
│ │ 데이터   │ │  ─→ 데이터 소멸   │  ↕ SQLAlchemy│
│ └─────────┘ │                   └──────┬──────┘
└─────────────┘                          │
                                   ┌─────┴──────┐
                                   │  SQLite DB  │  ─→ 데이터 영구 보존
                                   │  (파일)     │
                                   └────────────┘
```

### 기술 스택

| 기술 | 역할 | 설명 |
|------|------|------|
| **SQLAlchemy** | ORM | Python 객체로 데이터베이스를 조작 |
| **SQLite** | 데이터베이스 | 파일 기반 경량 DB (설치 불필요) |
| **Pydantic** | 스키마 | API 요청/응답 데이터 검증 |

> **ORM (Object-Relational Mapping)**: SQL 쿼리를 직접 작성하지 않고,
> Python 클래스와 객체를 통해 데이터베이스를 조작하는 기술입니다.

---

## 설치

```bash
# SQLAlchemy 설치
pip install sqlalchemy

# FastAPI 테스트 클라이언트 (이미 설치되어 있을 수 있음)
pip install httpx
```

---

## 섹션 목록

| 섹션 | 제목 | 난이도 | 핵심 내용 |
|------|------|--------|----------|
| sec01 | [SQLAlchemy 설정](./sec01-sqlalchemy-setup/concept.md) | ⭐⭐⭐ (3/5) | 엔진, 세션, 모델 설정 |
| sec02 | [CRUD 구현](./sec02-crud-operations/concept.md) | ⭐⭐⭐ (3/5) | 생성, 조회, 수정, 삭제 API |
| sec03 | [관계 매핑](./sec03-relationships/concept.md) | ⭐⭐⭐ (3/5) | ForeignKey, relationship, 1:N |

---

## 학습 순서

```
sec01-sqlalchemy-setup → sec02-crud-operations → sec03-relationships
```

1. **sec01**: SQLAlchemy 엔진, 세션, 모델을 설정하고 get_db 의존성을 만듭니다.
2. **sec02**: FastAPI + SQLAlchemy로 CRUD API를 구현합니다.
3. **sec03**: 테이블 간 관계(1:N)를 설정하고 연관된 데이터를 조회합니다.

각 섹션에서:
1. `concept.md`를 읽고 개념을 이해합니다.
2. `exercise.md`의 문제를 확인합니다.
3. `exercise.py`에서 TODO를 완성합니다.
4. `python exercise.py`로 테스트를 실행합니다.
5. 막히면 `solution.py`를 참고합니다.

---

## 사전 준비

- Ch05 (의존성 주입)까지 학습 완료
- SQLAlchemy 패키지 설치: `pip install sqlalchemy`
- Python 3.8 이상

```bash
# SQLAlchemy 설치 확인
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

---

## 이 챕터를 마치면 할 수 있는 것

- SQLAlchemy를 사용하여 데이터베이스 연결을 설정할 수 있다
- SQLAlchemy 모델로 테이블을 정의할 수 있다
- FastAPI에서 CRUD API를 구현할 수 있다
- Pydantic 모델과 SQLAlchemy 모델을 분리하여 사용할 수 있다
- 테이블 간 1:N 관계를 설정하고 조회할 수 있다
