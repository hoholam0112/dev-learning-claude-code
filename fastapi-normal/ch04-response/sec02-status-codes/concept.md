# 섹션 02: HTTP 상태 코드 (Status Codes)

> **난이도**: ⭐⭐ (2/5) | **선수 지식**: sec01 완료

---

## 학습 목표

- CRUD 각 동작에 적절한 HTTP 상태 코드를 설정할 수 있다
- `status_code` 매개변수와 `status` 모듈을 활용할 수 있다
- 201 Created, 204 No Content 등 상황에 맞는 상태 코드를 이해한다

---

## 핵심 개념

### 1. HTTP 상태 코드란?

HTTP 상태 코드는 서버가 클라이언트의 요청에 대해 **처리 결과를 숫자로 알려주는 코드**입니다.
웹 브라우저에서 "404 Not Found"를 본 적이 있을 것입니다.
이처럼 상태 코드는 요청이 성공했는지, 실패했는지, 어떤 종류의 문제인지를 나타냅니다.

### 2. 주요 상태 코드 정리

#### 2xx: 성공 (Success)

| 코드 | 이름 | 의미 | 사용 예 |
|------|------|------|---------|
| 200 | OK | 요청 성공 (기본값) | GET 조회, PUT 수정 |
| 201 | Created | 새로운 리소스 생성 완료 | POST 생성 |
| 204 | No Content | 성공했지만 응답 본문 없음 | DELETE 삭제 |

#### 4xx: 클라이언트 오류 (Client Error)

| 코드 | 이름 | 의미 | 사용 예 |
|------|------|------|---------|
| 400 | Bad Request | 잘못된 요청 | 유효하지 않은 데이터 |
| 401 | Unauthorized | 인증 필요 | 로그인하지 않은 사용자 |
| 403 | Forbidden | 권한 없음 | 접근 권한이 없는 리소스 |
| 404 | Not Found | 리소스 없음 | 존재하지 않는 ID |
| 422 | Unprocessable Entity | 처리 불가 | Pydantic 유효성 검사 실패 |

#### 5xx: 서버 오류 (Server Error)

| 코드 | 이름 | 의미 | 사용 예 |
|------|------|------|---------|
| 500 | Internal Server Error | 서버 내부 오류 | 예상하지 못한 에러 |
| 503 | Service Unavailable | 서비스 이용 불가 | 서버 점검 중 |

---

### 3. FastAPI에서 상태 코드 설정하기

#### 방법 1: 숫자 직접 지정

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


@app.post("/items", status_code=201)
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

#### 방법 2: status 모듈 사용 (권장)

숫자를 직접 쓰면 무슨 의미인지 알기 어렵습니다.
`status` 모듈을 사용하면 코드의 의미를 명확하게 표현할 수 있습니다.

```python
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


# 201 Created - 새로운 리소스가 생성되었음을 나타냄
@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

`status.HTTP_201_CREATED`는 `201`과 동일하지만,
코드를 읽는 사람이 의미를 바로 파악할 수 있습니다.

---

### 4. CRUD 동작별 적절한 상태 코드

```python
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 가상 데이터베이스
items_db = {}
item_id_counter = 0


class ItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None


# ── CREATE: 201 Created ──
@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global item_id_counter
    item_id_counter += 1
    item_data = item.model_dump()
    item_data["id"] = item_id_counter
    items_db[item_id_counter] = item_data
    return item_data


# ── READ: 200 OK (기본값) ──
@app.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int):
    return items_db[item_id]


# ── READ ALL: 200 OK (기본값) ──
@app.get("/items", response_model=list[ItemResponse])
async def read_items():
    return list(items_db.values())


# ── UPDATE: 200 OK ──
@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemUpdate):
    stored_item = items_db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    stored_item.update(update_data)
    return stored_item


# ── DELETE: 204 No Content ──
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    del items_db[item_id]
    # 204는 응답 본문이 없으므로 아무것도 반환하지 않음
```

**정리:**
| 동작 | HTTP 메서드 | 상태 코드 | 이유 |
|------|------------|----------|------|
| 생성 | POST | 201 Created | 새로운 리소스가 만들어졌음 |
| 조회 | GET | 200 OK | 요청이 정상 처리됨 (기본값) |
| 수정 | PUT/PATCH | 200 OK | 수정된 결과를 응답에 포함 |
| 삭제 | DELETE | 204 No Content | 삭제 완료, 반환할 데이터 없음 |

---

### 5. 204 No Content 주의사항

`status_code=204`를 사용할 때는 **응답 본문을 반환하면 안 됩니다**.
HTTP 표준에서 204는 "응답에 본문이 없음"을 의미합니다.

```python
# 올바른 예: 아무것도 반환하지 않음
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    del items_db[item_id]
    # return 없음 (또는 return None)


# 잘못된 예: 204인데 응답 본문을 반환
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_wrong(item_id: int):
    del items_db[item_id]
    return {"message": "삭제됨"}  # 204와 맞지 않음!
```

---

### 6. Swagger UI에서 확인하기

`status_code`를 지정하면 Swagger UI에서 다음과 같이 표시됩니다:

- 엔드포인트별로 예상되는 응답 코드가 표시됨
- 기본 성공 응답 코드가 `200` 대신 `201` 등으로 변경됨
- 프론트엔드 개발자가 어떤 상태 코드를 기대해야 하는지 문서로 확인 가능

`uvicorn`으로 서버를 실행하고 `http://localhost:8000/docs`에 접속하면
각 엔드포인트의 상태 코드를 확인할 수 있습니다.

---

## 요약

1. HTTP 상태 코드는 요청 처리 결과를 숫자로 나타냅니다.
2. `status_code` 매개변수로 엔드포인트의 기본 상태 코드를 설정합니다.
3. `status` 모듈을 사용하면 코드의 의미가 명확해집니다 (`status.HTTP_201_CREATED`).
4. 생성은 201, 조회/수정은 200, 삭제는 204를 사용하는 것이 일반적입니다.
5. 204 No Content는 응답 본문을 반환하지 않습니다.

---

## 다음 섹션

[sec03-error-handling: 에러 처리](../sec03-error-handling/concept.md)에서
HTTPException과 커스텀 예외 핸들러를 사용하여 에러를 처리하는 방법을 학습합니다.
