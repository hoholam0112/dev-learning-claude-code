# 섹션 03: 관계 매핑 - 연습 문제

> **난이도**: ⭐⭐⭐ (3/5)
> **파일**: `exercise.py`

---

## 문제: 사용자(1) - 게시글(N) 관계 구현

### 목표

SQLAlchemy의 ForeignKey와 relationship을 사용하여 사용자와 게시글 간의 1:N 관계를 설정하고,
관계 데이터를 포함하는 API를 구현합니다.

---

### 구현할 항목

| 순번 | 항목 | 설명 |
|------|------|------|
| 1 | User 모델 | users 테이블 + posts relationship |
| 2 | Post 모델 | posts 테이블 + author_id 외래키 + author relationship |
| 3 | Pydantic 스키마 | UserCreate, PostCreate, PostResponse, UserWithPosts |
| 4 | POST /users | 사용자 생성 API |
| 5 | POST /users/{user_id}/posts | 특정 사용자의 게시글 생성 API |
| 6 | GET /users/{user_id} | 사용자 + 게시글 목록 조회 API |

---

### 테이블 스키마

#### users 테이블

| 컬럼 | 타입 | 제약 조건 |
|------|------|----------|
| `id` | Integer | 기본키, 인덱스 |
| `username` | String | 유일값, 인덱스, NOT NULL |
| `email` | String | 유일값, NOT NULL |

#### posts 테이블

| 컬럼 | 타입 | 제약 조건 |
|------|------|----------|
| `id` | Integer | 기본키, 인덱스 |
| `title` | String | NOT NULL |
| `content` | String | NOT NULL |
| `author_id` | Integer | ForeignKey("users.id"), NOT NULL |

---

### 관계 설정

```
User 모델:
  posts = relationship("Post", back_populates="author")

Post 모델:
  author_id = Column(Integer, ForeignKey("users.id"))
  author = relationship("User", back_populates="posts")
```

---

### Pydantic 스키마

#### UserCreate (요청용)
| 필드 | 타입 |
|------|------|
| `username` | str |
| `email` | str |

#### PostCreate (요청용)
| 필드 | 타입 |
|------|------|
| `title` | str |
| `content` | str |

#### PostResponse (응답용)
| 필드 | 타입 |
|------|------|
| `id` | int |
| `title` | str |
| `content` | str |
| `author_id` | int |

#### UserWithPosts (응답용 - 관계 데이터 포함)
| 필드 | 타입 |
|------|------|
| `id` | int |
| `username` | str |
| `email` | str |
| `posts` | list[PostResponse] (기본값: []) |

> 모든 응답 스키마에 `model_config = ConfigDict(from_attributes=True)`를 추가하세요.

---

### API 엔드포인트 상세

#### 1. POST /users (사용자 생성)
- **요청**: `UserCreate` 본문
- **응답**: 사용자 정보 (status_code=201)
- **동작**: 새 사용자를 생성하고 반환

#### 2. POST /users/{user_id}/posts (게시글 생성)
- **경로 파라미터**: `user_id` (int)
- **요청**: `PostCreate` 본문
- **응답**: `PostResponse` (status_code=201)
- **에러**: 사용자가 없으면 404 반환
- **동작**: 해당 사용자의 게시글을 생성 (author_id 설정)

#### 3. GET /users/{user_id} (사용자 + 게시글 조회)
- **경로 파라미터**: `user_id` (int)
- **응답**: `UserWithPosts` (사용자 정보 + 게시글 목록)
- **에러**: 사용자가 없으면 404 반환
- **동작**: 사용자 정보와 해당 사용자의 게시글 목록을 함께 반환

---

### 힌트

```python
# User 모델에서 relationship 정의
posts = relationship("Post", back_populates="author")

# Post 모델에서 외래키 + relationship 정의
author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
author = relationship("User", back_populates="posts")

# 특정 사용자의 게시글 생성
db_post = Post(title=post.title, content=post.content, author_id=user_id)

# 사용자 조회 시 user.posts가 자동으로 게시글 목록을 반환
user = db.query(User).filter(User.id == user_id).first()
# user.posts → [Post(...), Post(...), ...]
```

---

## 실행 및 검증

```bash
python exercise.py
```

### 기대 출력

```
✓ 사용자 생성 테스트 통과
✓ 게시글 생성 테스트 통과 (게시글 1)
✓ 게시글 생성 테스트 통과 (게시글 2)
✓ 존재하지 않는 사용자에게 게시글 생성 시 404 테스트 통과
✓ 사용자 + 게시글 조회 테스트 통과
✓ 게시글에 author_id가 올바르게 설정됨
✓ 존재하지 않는 사용자 조회 시 404 테스트 통과

모든 테스트를 통과했습니다!
```

---

## 자주 하는 실수

1. **`ForeignKey("users.id")`에서 테이블 이름 오타**: `__tablename__`과 정확히 일치해야 합니다.
2. **`back_populates` 이름 불일치**: 양쪽 모델의 속성명을 정확히 지정해야 합니다.
3. **게시글 생성 시 `author_id`를 빼먹는 경우**: 외래키 값을 설정하지 않으면 에러가 발생합니다.
4. **Pydantic 스키마에 `from_attributes=True`를 빼먹는 경우**: SQLAlchemy 객체를 변환할 수 없습니다.
