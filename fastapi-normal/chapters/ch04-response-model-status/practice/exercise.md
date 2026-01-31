# 챕터 04 연습 문제

---

## 문제 1: 게시글 API (비밀번호 숨기기) (기초~보통)

### 설명
비밀번호가 있는 게시글 API를 만드세요. 비밀번호는 수정/삭제 시 검증용이며, 조회 응답에는 절대 포함되지 않아야 합니다.

### 요구사항
- 모델 정의:
  - `PostCreate`: 생성용 (title, content, author, password)
  - `PostResponse`: 응답용 (id, title, content, author, created_at) - **password 제외**
  - `PostListResponse`: 목록 응답용 (total, posts)
- 엔드포인트:
  - `POST /posts` — 게시글 생성 (201 반환, response_model=PostResponse)
  - `GET /posts` — 목록 조회 (response_model=PostListResponse)
  - `GET /posts/{post_id}` — 단건 조회 (없으면 404 에러)
  - `DELETE /posts/{post_id}` — 삭제 (비밀번호 확인, 204 반환)

### 예상 입출력

```
POST /posts
요청: {"title": "첫 글", "content": "안녕하세요", "author": "홍길동", "password": "1234"}
응답 (201): {"id": 1, "title": "첫 글", "content": "안녕하세요", "author": "홍길동", "created_at": "..."}

GET /posts/1
응답 (200): {"id": 1, "title": "첫 글", "content": "안녕하세요", "author": "홍길동", "created_at": "..."}
→ password 필드가 절대 포함되지 않음!

DELETE /posts/1?password=wrong
응답 (403): {"detail": "비밀번호가 일치하지 않습니다"}

DELETE /posts/1?password=1234
응답 (204): 본문 없음
```

<details>
<summary>힌트 보기</summary>

- `response_model=PostResponse`를 사용하면 password 필드가 자동 필터링됩니다
- 삭제 시 비밀번호는 쿼리 파라미터 `password: str`로 받습니다
- `HTTPException(status_code=403, detail="...")`으로 비밀번호 불일치를 처리하세요
- `datetime.now().isoformat()`으로 생성 시간을 기록하세요

</details>

---

## 문제 2: 다양한 상태 코드 반환 API (보통)

### 설명
파일 업로드 메타데이터 관리 API를 만드세요. 각 상황에 맞는 적절한 상태 코드를 반환해야 합니다.

### 요구사항
- `FileMetadata` 모델: name, size_bytes, content_type, uploaded_at
- 엔드포인트:
  - `POST /files` — 파일 메타데이터 등록 (**201** Created)
  - `GET /files/{file_id}` — 조회 (200 또는 **404**)
  - `PUT /files/{file_id}` — 전체 수정 (200 또는 **404**)
  - `DELETE /files/{file_id}` — 삭제 (**204** 또는 **404**)
  - `POST /files/{file_id}/duplicate` — 복제 (**201** 또는 **404**)
- 각 엔드포인트에 `responses` 파라미터로 가능한 응답을 문서화하세요

### 예상 입출력

```
POST /files
요청: {"name": "report.pdf", "size_bytes": 1024000, "content_type": "application/pdf"}
응답 (201): {"id": 1, "name": "report.pdf", "size_bytes": 1024000, ...}

POST /files/1/duplicate
응답 (201): {"id": 2, "name": "report_copy.pdf", ...}

GET /files/999
응답 (404): {"detail": "파일을 찾을 수 없습니다"}
```

<details>
<summary>힌트 보기</summary>

- `status_code=status.HTTP_201_CREATED`로 201 반환을 설정하세요
- 복제 시 이름에 "_copy"를 추가하고 새 ID를 부여하세요
- `responses={404: {"description": "파일을 찾을 수 없음"}}`으로 문서화하세요
- `HTTPException`을 사용하여 404 에러를 발생시키세요

</details>

---

## 문제 3: 목록 조회 (페이지네이션 응답 모델) (보통)

### 설명
페이지네이션을 포함한 응답 모델을 설계하고, 기사(Article) 목록 API를 만드세요.

### 요구사항
- 모델:
  - `ArticleCreate`: title, content, author
  - `ArticleResponse`: id, title, content, author, created_at
  - `PaginatedResponse`: total, page, page_size, total_pages, has_next, has_prev, items (List[ArticleResponse])
- 엔드포인트:
  - `POST /articles` — 기사 작성 (201)
  - `GET /articles` — 목록 조회 (페이지네이션)
    - 쿼리: page (기본 1), page_size (기본 10, 최대 50)
  - `GET /articles/{article_id}` — 단건 조회

### 예상 입출력

```
GET /articles?page=2&page_size=2
응답:
{
    "total": 5,
    "page": 2,
    "page_size": 2,
    "total_pages": 3,
    "has_next": true,
    "has_prev": true,
    "items": [
        {"id": 3, "title": "세 번째 기사", ...},
        {"id": 4, "title": "네 번째 기사", ...}
    ]
}
```

<details>
<summary>힌트 보기</summary>

- 전체 페이지 수: `math.ceil(total / page_size)` (`import math` 필요)
- has_next: `page < total_pages`
- has_prev: `page > 1`
- 슬라이싱: `start = (page - 1) * page_size`, `items[start:start + page_size]`
- `response_model=PaginatedResponse`를 사용하세요

</details>

---

## 제출 방법

1. `solution.py` 파일에 3개 문제의 답안을 모두 작성하세요
2. `uvicorn solution:app --reload`로 실행하세요
3. 각 엔드포인트에서 올바른 상태 코드가 반환되는지 확인하세요
4. `http://localhost:8000/docs`에서 응답 스키마가 올바르게 표시되는지 확인하세요
5. 비밀번호 등 민감 정보가 응답에 포함되지 않는지 검증하세요
