# sec03 연습 문제: 폼 데이터와 파일 업로드

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py` (테스트) 또는 `uvicorn exercise:app --reload` (서버)
> **사전 설치**: `pip install python-multipart`

---

## 문제 1: 로그인 폼 API

HTML 폼에서 전송된 로그인 데이터를 처리하는 API를 구현하세요.

### 요구 사항

**POST /login 엔드포인트:**
- `username`: `str` (Form, 필수, 최소 3자)
- `password`: `str` (Form, 필수, 최소 6자)
- 반환값: `{"message": "로그인 성공", "username": 사용자명}`

---

## 문제 2: 파일 업로드 API

파일을 업로드하고 파일 정보를 반환하는 API를 구현하세요.

### 요구 사항

**POST /upload 엔드포인트:**
- `file`: `UploadFile` (File, 필수)
- 반환값:
```json
{
    "filename": "파일명",
    "content_type": "MIME 타입",
    "size": 파일크기(바이트)
}
```

---

## 문제 3: 게시글 생성 API (폼 + 파일)

폼 데이터와 파일을 동시에 받는 게시글 생성 API를 구현하세요.

### 요구 사항

**POST /posts 엔드포인트:**
- `title`: `str` (Form, 필수, 최소 2자)
- `content`: `str` (Form, 선택, 기본값 `""`)
- `image`: `Optional[UploadFile]` (File, 선택, 기본값 `None`)
- 반환값:
```json
{
    "message": "게시글이 생성되었습니다",
    "post": {
        "title": "제목",
        "content": "내용",
        "image_filename": "파일명 또는 null",
        "image_size": 파일크기_또는_0
    }
}
```

### 힌트

- `Form()`은 `from fastapi import Form`으로 임포트합니다
- `File()`과 `UploadFile`은 `from fastapi import File, UploadFile`로 임포트합니다
- 파일 내용을 읽으려면 `contents = await file.read()`를 사용합니다
- 선택적 파일은 `Optional[UploadFile] = File(default=None)`으로 정의합니다

### 테스트 케이스

1. 정상 로그인 -> 200 OK
2. 짧은 사용자명 (2자) -> 422
3. 짧은 비밀번호 (5자) -> 422
4. 파일 업로드 -> 200 OK, 파일 정보 확인
5. 게시글 (이미지 포함) -> 200 OK
6. 게시글 (이미지 없이) -> 200 OK, image_filename이 None

---

## 정답 확인

모든 테스트를 통과하면 완료입니다.
막히는 부분이 있다면 `solution.py`를 참고하세요.
