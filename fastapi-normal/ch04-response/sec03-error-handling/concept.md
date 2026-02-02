# 섹션 03: 에러 처리 (Error Handling)

> **난이도**: ⭐⭐ (2/5) | **선수 지식**: sec02 완료

---

## 학습 목표

- `HTTPException`을 사용하여 적절한 에러 응답을 반환할 수 있다
- `detail` 매개변수로 에러 메시지를 전달할 수 있다
- 커스텀 `exception_handler`를 등록하여 일관된 에러 응답 형식을 만들 수 있다
- `RequestValidationError`를 커스터마이징할 수 있다

---

## 핵심 개념

### 1. HTTPException이란?

`HTTPException`은 FastAPI가 제공하는 **에러를 발생시키는 예외 클래스**입니다.
Python의 `raise`문과 함께 사용하면, 즉시 에러 응답을 클라이언트에게 반환합니다.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

items = {"item1": "노트북", "item2": "마우스"}


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        # 존재하지 않는 아이템 → 404 에러 발생
        raise HTTPException(
            status_code=404,
            detail="해당 아이템을 찾을 수 없습니다"
        )
    return {"item_id": item_id, "name": items[item_id]}
```

**응답 예시 (item_id가 존재하지 않을 때):**
```json
{
    "detail": "해당 아이템을 찾을 수 없습니다"
}
```

`HTTPException`의 주요 매개변수:
- `status_code`: HTTP 상태 코드 (404, 403, 400 등)
- `detail`: 에러 메시지 (문자열 또는 딕셔너리)
- `headers`: 추가 HTTP 헤더 (선택)

---

### 2. 다양한 에러 상황 처리

실제 API에서 자주 발생하는 에러 상황들을 살펴보겠습니다.

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

# 가상 데이터
users_db = {
    1: {"id": 1, "username": "admin", "role": "admin"},
    2: {"id": 2, "username": "hong", "role": "user"},
}

posts_db = {
    1: {"id": 1, "title": "첫 번째 게시글", "author_id": 2},
}


# ── 404 Not Found: 리소스가 존재하지 않을 때 ──
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id}인 사용자를 찾을 수 없습니다"
        )
    return users_db[user_id]


# ── 403 Forbidden: 권한이 없을 때 ──
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, user_id: int):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다"
        )

    post = posts_db[post_id]

    # 작성자만 삭제 가능
    if post["author_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인이 작성한 게시글만 삭제할 수 있습니다"
        )

    del posts_db[post_id]
    return {"message": "삭제되었습니다"}


# ── 400 Bad Request: 잘못된 요청일 때 ──
@app.post("/users/{user_id}/follow/{target_id}")
async def follow_user(user_id: int, target_id: int):
    if user_id == target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 팔로우할 수 없습니다"
        )
    return {"message": f"사용자 {user_id}가 {target_id}를 팔로우했습니다"}
```

---

### 3. detail에 딕셔너리 전달하기

`detail`에 문자열 대신 **딕셔너리**를 전달하면, 더 구조화된 에러 정보를 제공할 수 있습니다.

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ITEM_NOT_FOUND",
                "message": "해당 아이템을 찾을 수 없습니다",
                "item_id": item_id
            }
        )
    return items[item_id]
```

**응답 예시:**
```json
{
    "detail": {
        "error": "ITEM_NOT_FOUND",
        "message": "해당 아이템을 찾을 수 없습니다",
        "item_id": "item999"
    }
}
```

---

### 4. 커스텀 예외 핸들러 (Exception Handler)

모든 에러 응답의 형식을 통일하고 싶다면, **커스텀 예외 핸들러**를 등록합니다.

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()


# ── 커스텀 예외 클래스 정의 ──
class ItemNotFoundException(Exception):
    """아이템을 찾을 수 없을 때 발생하는 예외"""
    def __init__(self, item_id: str):
        self.item_id = item_id


# ── 예외 핸들러 등록 ──
@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": {
                "code": "ITEM_NOT_FOUND",
                "message": f"아이템 '{exc.item_id}'을(를) 찾을 수 없습니다"
            }
        }
    )


items = {"item1": "노트북", "item2": "마우스"}


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        # HTTPException 대신 커스텀 예외를 발생시킴
        raise ItemNotFoundException(item_id)
    return {"success": True, "data": {"item_id": item_id, "name": items[item_id]}}
```

**응답 예시:**
```json
{
    "success": false,
    "error": {
        "code": "ITEM_NOT_FOUND",
        "message": "아이템 'item999'을(를) 찾을 수 없습니다"
    }
}
```

이렇게 하면 모든 에러 응답이 `{"success": false, "error": {...}}` 형태로 통일됩니다.

---

### 5. RequestValidationError 커스터마이징

FastAPI는 Pydantic 유효성 검사가 실패하면 자동으로 422 에러를 반환합니다.
이 에러 응답의 형식을 커스터마이징할 수 있습니다.

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


# Pydantic 유효성 검사 에러를 커스터마이징
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    # 에러 메시지를 한국어로 가공
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "입력 데이터가 유효하지 않습니다",
                "details": errors
            }
        }
    )


class UserCreate(BaseModel):
    username: str
    email: str
    age: int


@app.post("/users")
async def create_user(user: UserCreate):
    return {"success": True, "data": user.model_dump()}
```

**잘못된 요청 시 응답 예시:**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "입력 데이터가 유효하지 않습니다",
        "details": [
            {
                "field": "body → age",
                "message": "Input should be a valid integer, unable to parse string as an integer",
                "type": "int_parsing"
            }
        ]
    }
}
```

---

### 6. HTTPException 핸들러 오버라이드

FastAPI의 기본 `HTTPException` 처리 방식도 커스터마이징할 수 있습니다.

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()


# HTTPException의 기본 처리 방식을 오버라이드
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id > 100:
        raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")
    return {"success": True, "data": {"id": item_id}}
```

이렇게 하면 `raise HTTPException(...)`을 사용할 때마다
자동으로 통일된 형식의 에러 응답이 반환됩니다.

---

## 에러 처리 모범 사례

### 1. 일관된 에러 응답 형식

```python
# 좋은 예: 모든 에러가 동일한 형식
{"success": False, "error": {"code": "NOT_FOUND", "message": "..."}}

# 나쁜 예: 에러마다 형식이 다름
{"detail": "..."}           # 어떤 곳에서는 이 형식
{"error": "..."}            # 다른 곳에서는 이 형식
{"message": "..."}          # 또 다른 곳에서는 이 형식
```

### 2. 구체적인 에러 메시지

```python
# 좋은 예: 무엇이 잘못되었는지 명확
raise HTTPException(status_code=404, detail="ID 42인 사용자를 찾을 수 없습니다")

# 나쁜 예: 너무 모호함
raise HTTPException(status_code=404, detail="찾을 수 없습니다")
```

### 3. 적절한 상태 코드 사용

```python
# 좋은 예: 상황에 맞는 상태 코드
raise HTTPException(status_code=404)  # 리소스 없음
raise HTTPException(status_code=403)  # 권한 없음
raise HTTPException(status_code=400)  # 잘못된 요청

# 나쁜 예: 모든 에러에 500 사용
raise HTTPException(status_code=500, detail="에러 발생")
```

---

## 요약

1. `HTTPException`은 에러 응답을 반환하는 가장 기본적인 방법입니다.
2. `status_code`와 `detail`로 에러의 종류와 메시지를 전달합니다.
3. `detail`에 딕셔너리를 전달하면 구조화된 에러 정보를 제공할 수 있습니다.
4. 커스텀 `exception_handler`로 에러 응답 형식을 통일할 수 있습니다.
5. `RequestValidationError` 핸들러로 유효성 검사 에러를 커스터마이징할 수 있습니다.
6. 에러 메시지는 구체적으로, 상태 코드는 상황에 맞게 사용합니다.
