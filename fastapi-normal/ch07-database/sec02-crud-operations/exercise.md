# 섹션 02: CRUD 구현 - 연습 문제

> **난이도**: ⭐⭐⭐ (3/5)
> **파일**: `exercise.py`

---

## 문제: 게시글(Post) CRUD API 구현

### 목표

FastAPI와 SQLAlchemy를 사용하여 게시글의 생성, 조회, 수정, 삭제 API를 구현합니다.

### 구현할 항목

| 순번 | 항목 | 설명 |
|------|------|------|
| 1 | SQLAlchemy 모델 | `Post` 모델 정의 (posts 테이블) |
| 2 | Pydantic 스키마 | `PostCreate`, `PostResponse` 정의 |
| 3 | POST /posts | 게시글 생성 API |
| 4 | GET /posts | 게시글 목록 조회 API (페이지네이션) |
| 5 | GET /posts/{post_id} | 게시글 상세 조회 API |
| 6 | PUT /posts/{post_id} | 게시글 수정 API |
| 7 | DELETE /posts/{post_id} | 게시글 삭제 API |

---

### 테이블 스키마: posts

| 컬럼 | 타입 | 제약 조건 |
|------|------|----------|
| `id` | Integer | 기본키, 인덱스 |
| `title` | String | NOT NULL |
| `content` | String | NOT NULL |
| `is_published` | Boolean | 기본값 False |

---

### Pydantic 스키마

#### PostCreate (요청용)
| 필드 | 타입 | 설명 |
|------|------|------|
| `title` | str | 게시글 제목 |
| `content` | str | 게시글 내용 |

#### PostResponse (응답용)
| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | int | 게시글 ID |
| `title` | str | 게시글 제목 |
| `content` | str | 게시글 내용 |
| `is_published` | bool | 게시 여부 |

> `PostResponse`에는 `model_config = ConfigDict(from_attributes=True)`를 설정해야 합니다.

---

### API 엔드포인트 상세

#### 1. POST /posts (게시글 생성)
- **요청**: `PostCreate` 본문
- **응답**: `PostResponse` (status_code=201)
- **동작**: 새 게시글을 생성하고 반환

#### 2. GET /posts (목록 조회)
- **쿼리 파라미터**: `skip` (기본값 0), `limit` (기본값 10)
- **응답**: `list[PostResponse]`
- **동작**: 페이지네이션을 적용하여 게시글 목록 반환

#### 3. GET /posts/{post_id} (상세 조회)
- **경로 파라미터**: `post_id` (int)
- **응답**: `PostResponse`
- **에러**: 게시글이 없으면 404 반환

#### 4. PUT /posts/{post_id} (수정)
- **경로 파라미터**: `post_id` (int)
- **요청**: `PostCreate` 본문
- **응답**: `PostResponse`
- **에러**: 게시글이 없으면 404 반환

#### 5. DELETE /posts/{post_id} (삭제)
- **경로 파라미터**: `post_id` (int)
- **응답**: 없음 (status_code=204)
- **에러**: 게시글이 없으면 404 반환

---

### 힌트

```python
# Create
db_post = Post(title=post.title, content=post.content)
db.add(db_post)
db.commit()
db.refresh(db_post)

# Read
posts = db.query(Post).offset(skip).limit(limit).all()
post = db.query(Post).filter(Post.id == post_id).first()

# Update (조회 후 속성 변경)
db_post.title = post_update.title
db.commit()
db.refresh(db_post)

# Delete (조회 후 삭제)
db.delete(db_post)
db.commit()
```

---

## 실행 및 검증

```bash
python exercise.py
```

### 기대 출력

```
✓ 게시글 생성 테스트 통과
✓ 게시글 목록 조회 테스트 통과
✓ 게시글 상세 조회 테스트 통과
✓ 존재하지 않는 게시글 조회 시 404 테스트 통과
✓ 게시글 수정 테스트 통과
✓ 게시글 삭제 테스트 통과
✓ 삭제된 게시글 조회 시 404 테스트 통과

모든 테스트를 통과했습니다!
```

> 테스트는 SQLite 인메모리 데이터베이스를 사용하므로 파일이 생성되지 않습니다.

---

## 자주 하는 실수

1. **`db.commit()`을 빼먹는 경우**: 데이터가 DB에 저장되지 않습니다.
2. **`db.refresh()`를 빼먹는 경우**: `id` 등 DB가 자동 생성한 값이 객체에 반영되지 않습니다.
3. **404 처리를 빼먹는 경우**: 존재하지 않는 데이터에 접근할 때 서버 에러(500)가 발생합니다.
4. **`from_attributes=True`를 빼먹는 경우**: SQLAlchemy 모델을 Pydantic 모델로 변환할 수 없습니다.
