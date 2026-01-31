# 챕터 09 연습 문제: 파일 업로드와 폼 데이터

---

## 문제 1: 프로필 이미지 업로드 (이미지 타입만 허용)

### 설명
사용자 프로필 이미지를 업로드하는 API를 구현하세요. 이미지 파일만 허용하고, 크기 제한과 함께 서버에 저장합니다.

### 요구사항
1. `POST /profile/image` 엔드포인트를 만드세요
2. 허용 파일 형식: JPEG, PNG, WebP만 허용
3. 최대 파일 크기: 3MB
4. 저장 시 UUID 기반의 고유한 파일명 사용
5. `uploads/profiles/` 디렉토리에 저장
6. 기존 프로필 이미지가 있으면 삭제 후 교체
7. `GET /profile/image/{user_id}` - 프로필 이미지 다운로드

### 예상 입출력

**성공 응답 (200):**
```json
{
    "message": "프로필 이미지가 업로드되었습니다",
    "image": {
        "original_name": "my-photo.jpg",
        "saved_name": "a1b2c3d4-e5f6.jpg",
        "content_type": "image/jpeg",
        "size_kb": 245.3
    }
}
```

**잘못된 파일 형식 (400):**
```json
{
    "detail": "허용되지 않는 파일 형식입니다. JPEG, PNG, WebP만 업로드 가능합니다."
}
```

**파일 크기 초과 (400):**
```json
{
    "detail": "파일 크기가 3MB를 초과합니다. 현재 크기: 4.5MB"
}
```

<details>
<summary>힌트 보기</summary>

- `file.content_type`으로 MIME 타입을 확인하세요
- `await file.read()`로 내용을 읽은 후 `len(content)`로 크기를 확인하세요
- `Path.unlink()`으로 기존 파일을 삭제할 수 있습니다
- `FileResponse`를 사용하면 파일을 다운로드 응답으로 반환할 수 있습니다

</details>

---

## 문제 2: CSV 파일 업로드 후 데이터 파싱

### 설명
CSV 파일을 업로드받아 내용을 파싱하고, 데이터 요약 정보를 반환하는 API를 구현하세요.

### 요구사항
1. `POST /upload/csv` 엔드포인트를 만드세요
2. CSV 파일만 허용 (`text/csv` 또는 파일 확장자 `.csv`)
3. 파일 내용을 파싱하여 다음을 반환하세요:
   - 전체 행 수
   - 컬럼 이름 목록
   - 처음 5개 행의 데이터 (미리보기)
   - 각 컬럼의 데이터 타입 추정
4. 최대 파일 크기: 5MB
5. UTF-8 인코딩을 기본으로 처리

### 예상 입출력

**업로드할 CSV 예시:**
```csv
이름,나이,이메일,점수
홍길동,25,hong@example.com,85.5
김철수,30,kim@example.com,92.0
이영희,28,lee@example.com,78.3
```

**성공 응답:**
```json
{
    "filename": "students.csv",
    "total_rows": 3,
    "columns": ["이름", "나이", "이메일", "점수"],
    "column_types": {
        "이름": "text",
        "나이": "integer",
        "이메일": "text",
        "점수": "float"
    },
    "preview": [
        {"이름": "홍길동", "나이": "25", "이메일": "hong@example.com", "점수": "85.5"},
        {"이름": "김철수", "나이": "30", "이메일": "kim@example.com", "점수": "92.0"},
        {"이름": "이영희", "나이": "28", "이메일": "lee@example.com", "점수": "78.3"}
    ]
}
```

<details>
<summary>힌트 보기</summary>

- Python 표준 라이브러리의 `csv` 모듈을 사용하세요
- `import csv` 후 `csv.DictReader`로 컬럼명이 있는 CSV를 파싱할 수 있습니다
- 파일 내용을 문자열로 변환: `content.decode("utf-8")`
- `io.StringIO`를 사용하면 문자열을 파일 객체처럼 사용할 수 있습니다:
  ```python
  import io
  text = content.decode("utf-8")
  reader = csv.DictReader(io.StringIO(text))
  ```
- 데이터 타입 추정: `str.isdigit()`, `float()` 변환 시도 등으로 판별하세요

</details>

---

## 문제 3: 폼 기반 게시글 작성 (제목 + 본문 + 첨부파일)

### 설명
Form 데이터로 게시글을 작성하고, 첨부파일을 함께 업로드하는 API를 구현하세요.

### 요구사항
1. `POST /articles` 엔드포인트를 만드세요
2. 폼 필드:
   - `title` (필수, 최대 100자)
   - `content` (필수)
   - `author` (필수)
   - `category` (선택, 기본값: "general")
   - `is_public` (선택, 기본값: True)
3. 첨부파일:
   - `thumbnail` (선택, 이미지 1개)
   - `attachments` (선택, 파일 최대 3개)
4. 성공 시 게시글 정보를 반환하세요
5. `GET /articles` - 게시글 목록 조회
6. `GET /articles/{article_id}` - 게시글 상세 조회

### 예상 입출력

**게시글 작성 (폼 데이터):**
```
title: FastAPI 학습 후기
content: FastAPI는 정말 빠르고 편리합니다...
author: 홍길동
category: 개발
is_public: true
thumbnail: (이미지 파일)
attachments: (파일1, 파일2)
```

**성공 응답 (201):**
```json
{
    "message": "게시글이 작성되었습니다",
    "article": {
        "id": 1,
        "title": "FastAPI 학습 후기",
        "content": "FastAPI는 정말 빠르고 편리합니다...",
        "author": "홍길동",
        "category": "개발",
        "is_public": true,
        "thumbnail": "a1b2c3d4.jpg",
        "attachments": [
            {"name": "참고자료.pdf", "saved_name": "e5f6g7h8.pdf", "size": 102400},
            {"name": "코드.py", "saved_name": "i9j0k1l2.py", "size": 2048}
        ],
        "created_at": "2024-01-01T00:00:00"
    }
}
```

<details>
<summary>힌트 보기</summary>

- `Form()`과 `File()`을 동시에 사용하면 `multipart/form-data`로 전송됩니다
- 선택적 파일: `thumbnail: UploadFile | None = File(None)`
- 다중 파일: `attachments: list[UploadFile] = File(default=[])`
- 빈 파일 확인: `if file and file.filename`으로 실제 파일이 전송되었는지 확인하세요
- 게시글을 딕셔너리에 저장하면 간단하게 CRUD를 구현할 수 있습니다

</details>
