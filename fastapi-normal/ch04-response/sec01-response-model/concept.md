# 섹션 01: 응답 모델 (Response Model)

> **난이도**: ⭐⭐ (2/5) | **선수 지식**: Ch03 완료 (Pydantic 모델 기초)

---

## 학습 목표

- `response_model`을 사용하여 API 응답 형태를 정의할 수 있다
- 입력 모델과 출력 모델을 분리하여 민감한 정보를 필터링할 수 있다
- `response_model_exclude`를 활용하여 특정 필드를 응답에서 제외할 수 있다

---

## 핵심 개념

### 1. response_model이란?

FastAPI에서 `response_model`은 **API가 어떤 형태의 데이터를 응답으로 돌려줄지** 정의하는 매개변수입니다.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    description: str | None = None


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    return {"name": "노트북", "price": 1500000, "description": "고성능 노트북"}
```

`response_model=Item`을 지정하면 FastAPI가 자동으로 다음을 수행합니다:

1. **응답 데이터를 Item 모델에 맞게 변환** (직렬화)
2. **Swagger UI에 응답 스키마를 표시** (자동 문서화)
3. **모델에 정의되지 않은 필드를 자동으로 제거** (데이터 필터링)

---

### 2. 왜 응답 모델이 중요한가?

#### 보안: 민감한 정보 필터링

가장 대표적인 사례가 **비밀번호 필터링**입니다.

```python
# 잘못된 예: 비밀번호가 응답에 그대로 노출됨
@app.post("/users")
async def create_user(user_data: dict):
    # user_data에 password가 포함되어 있다면...
    return user_data  # password도 함께 응답에 포함됨!
```

이런 실수는 실제 서비스에서 심각한 보안 사고로 이어질 수 있습니다.
`response_model`을 사용하면 이를 구조적으로 방지할 수 있습니다.

#### 문서화: Swagger UI 자동 생성

`response_model`을 지정하면 Swagger UI(`/docs`)에서 응답 스키마를 확인할 수 있습니다.
프론트엔드 개발자가 별도의 문서 없이도 API 응답 형태를 파악할 수 있습니다.

#### 일관성: 응답 형태 보장

반환하는 데이터에 모델에 정의되지 않은 불필요한 필드가 있어도 자동으로 제거되어,
항상 일관된 형태의 응답을 보장합니다.

---

### 3. 입력 모델 vs 출력 모델 분리

실무에서 가장 많이 사용하는 패턴은 **요청용 모델**과 **응답용 모델을 분리**하는 것입니다.

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import Optional

app = FastAPI()

# 가상 데이터베이스
fake_db = {}
user_id_counter = 0


# ── 요청용 모델 (입력) ──
class UserCreate(BaseModel):
    """사용자 생성 요청 모델 - 클라이언트가 보내는 데이터"""
    username: str
    email: str
    password: str           # 입력에는 비밀번호 포함
    full_name: Optional[str] = None


# ── 응답용 모델 (출력) ──
class UserResponse(BaseModel):
    """사용자 응답 모델 - 서버가 돌려주는 데이터"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    # password는 포함하지 않음!


# ── 엔드포인트 ──
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    global user_id_counter
    user_id_counter += 1

    # 데이터베이스에 저장 (비밀번호 포함)
    user_data = user.model_dump()
    user_data["id"] = user_id_counter
    fake_db[user_id_counter] = user_data

    # 응답 반환 - response_model=UserResponse이므로
    # password가 자동으로 제거됨
    return user_data


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user_data = fake_db.get(user_id)
    if not user_data:
        return {"error": "사용자를 찾을 수 없습니다"}
    # user_data에 password가 있지만,
    # response_model=UserResponse이므로 응답에서 자동 제거
    return user_data
```

**핵심 포인트:**
- `UserCreate`에는 `password`가 있지만, `UserResponse`에는 없습니다.
- 엔드포인트에서 `user_data` (password 포함)를 그대로 반환해도,
  `response_model=UserResponse` 덕분에 password가 응답에서 **자동으로 제거**됩니다.
- 이렇게 하면 개발자가 실수로 민감한 정보를 노출하는 것을 구조적으로 방지합니다.

---

### 4. response_model_exclude와 response_model_include

모델을 별도로 만들지 않고도 특정 필드를 제외하거나 포함할 수 있습니다.

#### response_model_exclude: 특정 필드 제외

```python
class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


# password 필드를 응답에서 제외
@app.get("/users/{user_id}", response_model=User, response_model_exclude={"password"})
async def get_user(user_id: int):
    return fake_db.get(user_id)
```

#### response_model_include: 특정 필드만 포함

```python
# username과 email만 응답에 포함
@app.get(
    "/users/{user_id}/summary",
    response_model=User,
    response_model_include={"username", "email"}
)
async def get_user_summary(user_id: int):
    return fake_db.get(user_id)
```

> **참고**: `response_model_exclude`와 `response_model_include`는 간편하지만,
> 실무에서는 **별도의 응답 모델을 만드는 것이 더 권장**됩니다.
> 별도 모델을 사용하면 Swagger 문서에 정확한 스키마가 표시되기 때문입니다.

---

### 5. response_model_exclude_unset

기본값이 설정된 필드 중, 실제로 값이 할당되지 않은 필드를 응답에서 제외합니다.
이는 **PATCH (부분 업데이트)** 시 유용합니다.

```python
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 10.5


items = {
    "item1": {"name": "노트북", "price": 1500000},
    "item2": {"name": "마우스", "description": "무선 마우스", "price": 35000, "tax": 3500},
}


@app.get(
    "/items/{item_id}",
    response_model=Item,
    response_model_exclude_unset=True
)
async def read_item(item_id: str):
    return items[item_id]
```

**응답 결과:**
- `GET /items/item1` → `{"name": "노트북", "price": 1500000}`
  - `description`과 `tax`는 설정되지 않았으므로 응답에서 제외
- `GET /items/item2` → `{"name": "마우스", "description": "무선 마우스", "price": 35000, "tax": 3500}`
  - 모든 필드가 설정되었으므로 전부 포함

---

## 패턴 정리

| 방법 | 사용 시기 | 장점 | 단점 |
|------|----------|------|------|
| 별도 응답 모델 | 대부분의 경우 (권장) | 명확한 스키마, 좋은 문서화 | 모델 클래스가 늘어남 |
| `response_model_exclude` | 빠른 프로토타이핑 | 간편함 | 문서 스키마가 부정확 |
| `response_model_include` | 요약 응답 | 간편함 | 문서 스키마가 부정확 |
| `response_model_exclude_unset` | 부분 업데이트 (PATCH) | 유연한 응답 | 로직 이해가 필요 |

---

## 실전 팁

### 모델 상속을 활용한 코드 재사용

여러 모델에 공통 필드가 있다면 **기반 모델(Base)**을 만들고 상속합니다:

```python
from pydantic import BaseModel
from typing import Optional


# 공통 필드를 가진 기반 모델
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


# 생성 요청용 (password 추가)
class UserCreate(UserBase):
    password: str


# 응답용 (id 추가)
class UserResponse(UserBase):
    id: int


# 업데이트 요청용 (모든 필드 선택적)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
```

이렇게 하면 중복 코드를 줄이면서도 각 용도에 맞는 모델을 유지할 수 있습니다.

---

## 요약

1. `response_model`은 API 응답의 형태를 정의하고 자동으로 필터링합니다.
2. **입력 모델과 출력 모델을 분리**하면 민감한 정보 노출을 구조적으로 방지합니다.
3. `response_model_exclude`로 간단히 필드를 제외할 수 있지만, 별도 모델이 더 권장됩니다.
4. 모델 상속을 활용하면 공통 필드를 재사용할 수 있습니다.

---

## 다음 섹션

[sec02-status-codes: HTTP 상태 코드](../sec02-status-codes/concept.md)에서
API 응답에 적절한 HTTP 상태 코드를 설정하는 방법을 학습합니다.
