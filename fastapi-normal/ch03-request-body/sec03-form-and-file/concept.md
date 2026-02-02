# sec03: 폼 데이터와 파일 업로드

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: sec01 (Pydantic 기본 모델) 완료
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

이 섹션을 완료하면 다음을 할 수 있습니다:

1. `Form()`을 사용하여 HTML 폼에서 전송된 데이터를 수신할 수 있다
2. `File()`과 `UploadFile`을 사용하여 파일 업로드를 처리할 수 있다
3. 폼 데이터와 파일을 동시에 받는 엔드포인트를 구현할 수 있다
4. JSON 본문과 폼 데이터의 차이를 이해하고 적절히 선택할 수 있다

---

## 핵심 개념

### 1. JSON vs 폼 데이터

지금까지 학습한 Pydantic 모델은 JSON 형식의 요청 본문을 처리했습니다.
하지만 HTML 폼에서 데이터를 전송하거나 파일을 업로드할 때는 다른 형식을 사용합니다.

| 구분 | JSON 본문 | 폼 데이터 |
|------|-----------|-----------|
| Content-Type | `application/json` | `application/x-www-form-urlencoded` |
| 파일 포함 시 | 불가 (Base64 인코딩 필요) | `multipart/form-data` |
| 사용 시나리오 | API 클라이언트, SPA | HTML 폼 전송, 파일 업로드 |
| FastAPI 처리 | `BaseModel` 매개변수 | `Form()`, `File()` 매개변수 |

### 2. python-multipart 설치

폼 데이터를 처리하려면 `python-multipart` 패키지가 필요합니다.

```bash
pip install python-multipart
```

> **참고**: FastAPI와 함께 설치하면 자동으로 포함되는 경우가 많지만,
> 명시적으로 설치하는 것을 권장합니다.

### 3. Form() - 폼 데이터 수신

`Form()`은 HTML 폼의 각 필드를 개별 매개변수로 받습니다.

```python
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/login")
async def login(
    username: str = Form(..., description="사용자명"),
    password: str = Form(..., description="비밀번호")
):
    """
    HTML 폼에서 전송된 로그인 데이터를 처리합니다.

    이 엔드포인트는 Content-Type: application/x-www-form-urlencoded
    형식의 요청을 받습니다.
    """
    # 실제로는 DB에서 사용자를 확인하고 비밀번호를 검증합니다
    # (여기서는 단순 예시)
    return {
        "message": "로그인 성공",
        "username": username
    }
```

**HTML 폼 예시:**
```html
<form action="/login" method="post">
    <input type="text" name="username" />
    <input type="password" name="password" />
    <button type="submit">로그인</button>
</form>
```

**curl로 테스트:**
```bash
curl -X POST http://localhost:8000/login \
  -d "username=hong&password=secret123"
```

> **주의**: `Form()`을 사용하는 매개변수와 Pydantic `BaseModel`을 사용하는 매개변수는
> 같은 엔드포인트에서 **동시에 사용할 수 없습니다**.
> 폼 데이터와 JSON 본문은 서로 다른 Content-Type이기 때문입니다.

### 4. File()과 UploadFile - 파일 업로드

#### 기본 파일 업로드

```python
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    파일을 업로드합니다.

    UploadFile은 다음 속성과 메서드를 제공합니다:
    - filename: 원본 파일명
    - content_type: MIME 타입 (예: image/png)
    - size: 파일 크기 (바이트)
    - read(): 파일 내용 읽기 (비동기)
    - write(): 파일에 쓰기 (비동기)
    - seek(): 파일 포인터 이동 (비동기)
    - close(): 파일 닫기 (비동기)
    """
    # 파일 내용 읽기
    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }
```

#### File() vs UploadFile

| 방식 | 설명 | 사용 시점 |
|------|------|-----------|
| `file: bytes = File(...)` | 파일 전체를 메모리에 로드 | 작은 파일 |
| `file: UploadFile = File(...)` | 스풀 파일 사용 (메모리 효율적) | 큰 파일, 권장 |

```python
# bytes로 받기 (작은 파일)
@app.post("/upload-bytes")
async def upload_bytes(file: bytes = File(...)):
    return {"size": len(file)}

# UploadFile로 받기 (권장)
@app.post("/upload-file")
async def upload_uploadfile(file: UploadFile = File(...)):
    return {"filename": file.filename}
```

#### 다중 파일 업로드

```python
@app.post("/upload-multiple")
async def upload_multiple_files(
    files: list[UploadFile] = File(..., description="여러 파일 업로드")
):
    """여러 파일을 동시에 업로드합니다."""
    file_info = []
    for f in files:
        contents = await f.read()
        file_info.append({
            "filename": f.filename,
            "content_type": f.content_type,
            "size": len(contents)
        })
    return {"files": file_info, "count": len(file_info)}
```

### 5. 폼 데이터 + 파일 동시 수신

실제 서비스에서는 파일과 함께 추가 정보(설명, 카테고리 등)를 받는 경우가 많습니다.

```python
@app.post("/profile")
async def update_profile(
    username: str = Form(..., description="사용자명"),
    bio: str = Form(default="", description="자기소개"),
    avatar: UploadFile = File(..., description="프로필 이미지")
):
    """
    프로필 정보와 이미지를 함께 수신합니다.

    Form()과 File()은 같은 엔드포인트에서 함께 사용할 수 있습니다.
    (둘 다 multipart/form-data로 전송되기 때문)
    """
    avatar_contents = await avatar.read()

    return {
        "username": username,
        "bio": bio,
        "avatar_filename": avatar.filename,
        "avatar_size": len(avatar_contents)
    }
```

**curl로 테스트:**
```bash
curl -X POST http://localhost:8000/profile \
  -F "username=hong" \
  -F "bio=안녕하세요" \
  -F "avatar=@./my_photo.jpg"
```

### 6. 파일 업로드 검증

FastAPI에서 파일의 타입이나 크기를 검증하는 방법입니다:

```python
from fastapi import FastAPI, File, UploadFile, HTTPException

# 허용되는 이미지 MIME 타입
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    이미지 파일만 허용하며, 최대 5MB까지 업로드 가능합니다.
    """
    # 파일 타입 검증
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 파일 형식입니다: {file.content_type}. "
                   f"허용 형식: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )

    # 파일 크기 검증
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # 파일 저장 (예시)
    # with open(f"uploads/{file.filename}", "wb") as f:
    #     f.write(contents)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }
```

---

## 전체 흐름 다이어그램

```
[JSON 요청]                          [폼/파일 요청]
     │                                     │
     │ Content-Type:                       │ Content-Type:
     │ application/json                    │ multipart/form-data
     │                                     │
     ▼                                     ▼
┌──────────────┐              ┌──────────────────────┐
│   Pydantic   │              │   Form() + File()    │
│   BaseModel  │              │                      │
│              │              │  username = Form(...) │
│  class Item: │              │  avatar = File(...)   │
│    name: str │              │                      │
│    price: int│              │                      │
└──────┬───────┘              └──────────┬───────────┘
       │                                 │
       ▼                                 ▼
┌──────────────────────────────────────────┐
│          FastAPI 엔드포인트 함수           │
│                                          │
│  async def handler(item/form/file):      │
│      # 검증된 데이터를 사용               │
│      ...                                 │
└──────────────────────────────────────────┘
```

---

## 실전 코드 예제: 프로필 관리 API

```python
"""
프로필 관리 API - 폼 데이터와 파일 업로드 예제
실행: uvicorn example_profile:app --reload
주의: pip install python-multipart 필요
"""
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from typing import Optional

app = FastAPI(title="프로필 관리 API", version="1.0.0")

# --- 인메모리 저장소 ---
profiles_db: dict[str, dict] = {}


# --- 엔드포인트 ---

@app.post("/login")
async def login(
    username: str = Form(..., min_length=3, description="사용자명 (3자 이상)"),
    password: str = Form(..., min_length=6, description="비밀번호 (6자 이상)")
):
    """
    로그인 폼을 처리합니다.
    실제 서비스에서는 DB 조회와 비밀번호 해싱이 필요합니다.
    """
    # 간단한 예시 (실제로는 이렇게 하면 안 됩니다!)
    return {
        "message": "로그인 성공",
        "username": username,
        "token": "fake-jwt-token"
    }


@app.post("/profile/avatar")
async def upload_avatar(
    username: str = Form(..., description="사용자명"),
    avatar: UploadFile = File(..., description="프로필 이미지")
):
    """
    프로필 이미지를 업로드합니다.
    """
    # 파일 내용 읽기
    contents = await avatar.read()

    # 프로필 정보 저장 (실제로는 파일을 디스크/S3에 저장)
    profiles_db[username] = {
        "username": username,
        "avatar_filename": avatar.filename,
        "avatar_content_type": avatar.content_type,
        "avatar_size": len(contents)
    }

    return {
        "message": "프로필 이미지가 업로드되었습니다",
        "profile": profiles_db[username]
    }


@app.post("/posts")
async def create_post(
    title: str = Form(..., min_length=1, description="게시글 제목"),
    content: str = Form(default="", description="게시글 내용"),
    image: Optional[UploadFile] = File(default=None, description="첨부 이미지 (선택)")
):
    """
    게시글을 생성합니다. 이미지는 선택적으로 첨부할 수 있습니다.
    """
    post_data = {
        "title": title,
        "content": content,
        "has_image": image is not None
    }

    if image:
        image_contents = await image.read()
        post_data["image_filename"] = image.filename
        post_data["image_size"] = len(image_contents)

    return {
        "message": "게시글이 생성되었습니다",
        "post": post_data
    }
```

---

## 주의 사항

### 1. Form()과 BaseModel을 동시에 사용할 수 없음

```python
# 불가능: Form()과 BaseModel 매개변수를 같이 사용
@app.post("/wrong")
async def wrong_endpoint(
    username: str = Form(...),
    item: Item  # BaseModel - JSON 본문 기대
):
    pass  # 동작하지 않습니다!
```

이유: `Form()`은 `multipart/form-data` 또는 `application/x-www-form-urlencoded`를 기대하고,
`BaseModel`은 `application/json`을 기대하기 때문입니다. 하나의 요청에서 두 가지 Content-Type을
동시에 사용할 수 없습니다.

### 2. 파일 읽기 후 포인터 위치

```python
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # 첫 번째 read() - 전체 내용을 읽음
    contents = await file.read()
    print(len(contents))  # 예: 1024

    # 두 번째 read() - 이미 끝까지 읽었으므로 빈 바이트
    contents_again = await file.read()
    print(len(contents_again))  # 0!

    # 다시 읽으려면 seek(0)으로 포인터를 처음으로 이동
    await file.seek(0)
    contents_again = await file.read()
    print(len(contents_again))  # 1024
```

### 3. 선택적 파일 업로드

파일을 필수가 아닌 선택으로 만들려면 `Optional`과 `default=None`을 사용합니다:

```python
from typing import Optional

@app.post("/optional-file")
async def optional_file_upload(
    title: str = Form(...),
    file: Optional[UploadFile] = File(default=None)
):
    if file:
        contents = await file.read()
        return {"title": title, "file_size": len(contents)}
    return {"title": title, "file_size": 0}
```

---

## 요약

| 개념 | 설명 | 사용 예 |
|------|------|---------|
| `Form()` | 폼 필드 데이터 수신 | 로그인 폼, 검색 폼 |
| `File()` | 파일 데이터를 bytes로 수신 | 작은 파일 업로드 |
| `UploadFile` | 파일 데이터를 스풀 파일로 수신 | 대용량 파일 업로드 (권장) |
| `multipart/form-data` | 폼 + 파일을 동시에 전송하는 인코딩 | 프로필 업데이트 |
| `python-multipart` | 폼/파일 처리에 필요한 패키지 | `pip install python-multipart` |

---

## 챕터 마무리

이것으로 Ch03의 모든 섹션을 완료했습니다.

**학습 내용 정리:**
- sec01: Pydantic BaseModel과 Field를 사용한 JSON 요청 본문 처리
- sec02: 중첩 모델과 리스트/딕셔너리 타입 활용
- sec03: 폼 데이터와 파일 업로드 처리

다음 챕터 [Ch04: 응답 모델과 상태 코드](../../ch04-response-models/)에서 응답 데이터를 체계적으로 관리하는 방법을 학습합니다.
