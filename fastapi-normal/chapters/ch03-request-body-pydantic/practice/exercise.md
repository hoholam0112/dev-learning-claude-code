# 챕터 03 연습 문제

---

## 문제 1: 상품 등록 API (기초)

### 설명
Pydantic 모델을 사용하여 상품을 등록하고 조회하는 API를 만드세요.

### 요구사항
- `ProductCreate` 모델 정의:
  - `name` (str): 필수, 1~100자
  - `price` (int): 필수, 100 이상
  - `description` (str): 선택적, 최대 500자
  - `category` (str): 필수
  - `in_stock` (bool): 기본값 True
- `POST /products` — 상품 등록
- `GET /products` — 전체 상품 목록
- `GET /products/{product_id}` — 특정 상품 조회

### 예상 입출력

```
POST /products
요청 본문:
{
    "name": "무선 키보드",
    "price": 89000,
    "description": "블루투스 5.0 지원 무선 키보드",
    "category": "electronics"
}

응답:
{
    "message": "상품이 등록되었습니다",
    "product": {
        "id": 1,
        "name": "무선 키보드",
        "price": 89000,
        "description": "블루투스 5.0 지원 무선 키보드",
        "category": "electronics",
        "in_stock": true
    }
}
```

<details>
<summary>힌트 보기</summary>

- `Field(..., min_length=1, max_length=100)`으로 문자열 길이를 제한하세요
- `Field(..., ge=100)`으로 최소 가격을 설정하세요
- `Optional[str] = Field(default=None, max_length=500)`으로 선택적 필드를 만드세요
- 저장소는 딕셔너리를 사용하고, ID는 전역 변수로 관리하세요

</details>

---

## 문제 2: 주문 생성 API (보통)

### 설명
중첩 모델을 활용하여 주문을 생성하는 API를 만드세요. 주문 안에 여러 상품 항목이 포함됩니다.

### 요구사항
- `OrderItem` 모델:
  - `product_name` (str): 상품명
  - `quantity` (int): 수량, 1 이상
  - `unit_price` (int): 단가, 100 이상
- `OrderCreate` 모델:
  - `customer_name` (str): 고객명
  - `items` (List[OrderItem]): 주문 항목 리스트 (1개 이상)
  - `note` (str): 선택적, 배송 메모
- `POST /orders` — 주문 생성 (총 금액 자동 계산)
- `GET /orders` — 전체 주문 목록
- `GET /orders/{order_id}` — 특정 주문 조회

### 예상 입출력

```
POST /orders
요청 본문:
{
    "customer_name": "홍길동",
    "items": [
        {"product_name": "노트북", "quantity": 1, "unit_price": 1200000},
        {"product_name": "마우스", "quantity": 2, "unit_price": 45000}
    ],
    "note": "부재 시 경비실에 맡겨주세요"
}

응답:
{
    "message": "주문이 생성되었습니다",
    "order": {
        "id": 1,
        "customer_name": "홍길동",
        "items": [...],
        "note": "부재 시 경비실에 맡겨주세요",
        "total_price": 1290000
    }
}
```

<details>
<summary>힌트 보기</summary>

- `items: List[OrderItem] = Field(..., min_length=1)`로 최소 1개 항목을 강제하세요
- 총 금액 계산: `sum(item.quantity * item.unit_price for item in order.items)`
- `model_dump()`로 Pydantic 모델을 딕셔너리로 변환할 수 있습니다

</details>

---

## 문제 3: 필드 유효성 검증 (보통)

### 설명
다양한 Field 검증 규칙을 적용한 회원가입 API를 만드세요.

### 요구사항
- `SignupRequest` 모델:
  - `username` (str): 필수, 3~20자, 영문+숫자만 (`pattern` 사용)
  - `email` (str): 필수, 이메일 형식 (`pattern` 사용)
  - `password` (str): 필수, 8~100자
  - `age` (int): 필수, 14~120
  - `nickname` (str): 선택적, 2~30자
- `POST /signup` — 회원가입
- 유효성 검증에 실패하면 422 에러가 자동으로 반환되어야 합니다
- 성공 시 비밀번호를 제외한 정보를 반환합니다

### 예상 입출력

```
POST /signup
요청 본문:
{
    "username": "hong123",
    "email": "hong@example.com",
    "password": "securePass123",
    "age": 25,
    "nickname": "길동이"
}

응답:
{
    "message": "회원가입이 완료되었습니다",
    "user": {
        "id": 1,
        "username": "hong123",
        "email": "hong@example.com",
        "age": 25,
        "nickname": "길동이"
    }
}
```

<details>
<summary>힌트 보기</summary>

- 영문+숫자 패턴: `pattern=r"^[a-zA-Z0-9]+$"`
- 이메일 패턴: `pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"`
- 응답에서 비밀번호 제외: `user.model_dump(exclude={"password"})`
- 또는 `model_dump()`한 딕셔너리에서 `del` 또는 `pop`으로 제거

</details>

---

## 문제 4: 선택적 필드를 가진 프로필 업데이트 API (보통)

### 설명
PATCH 요청으로 사용자 프로필을 부분 업데이트하는 API를 만드세요.

### 요구사항
- `ProfileCreate` 모델: 생성용 (대부분 필수 필드)
  - `name` (str): 필수
  - `email` (str): 필수
  - `age` (int): 필수
  - `bio` (str): 선택적
  - `website` (str): 선택적
- `ProfileUpdate` 모델: 수정용 (모든 필드 선택적)
  - 위와 동일한 필드, 모두 `Optional`
- `POST /profiles` — 프로필 생성
- `PATCH /profiles/{profile_id}` — 프로필 부분 수정
- `GET /profiles/{profile_id}` — 프로필 조회
- PATCH에서는 전달된 필드만 수정되어야 합니다

### 예상 입출력

```
POST /profiles
{"name": "홍길동", "email": "hong@example.com", "age": 25}
→ {"id": 1, "name": "홍길동", "email": "hong@example.com", "age": 25, "bio": null, "website": null}

PATCH /profiles/1
{"bio": "백엔드 개발자입니다", "age": 26}
→ {"id": 1, "name": "홍길동", "email": "hong@example.com", "age": 26, "bio": "백엔드 개발자입니다", "website": null}
```

<details>
<summary>힌트 보기</summary>

- `model_dump(exclude_unset=True)`는 요청에서 실제로 전달된 필드만 포함합니다
- 이를 통해 "전달되지 않은 필드"와 "None으로 전달된 필드"를 구분할 수 있습니다
- 업데이트 로직: `for key, value in update_data.items(): profile[key] = value`

</details>

---

## 제출 방법

1. `solution.py` 파일에 4개 문제의 답안을 모두 작성하세요
2. `uvicorn solution:app --reload`로 실행하세요
3. `http://localhost:8000/docs`에서 POST 요청을 직접 테스트하세요
4. 잘못된 데이터를 보내 422 에러가 반환되는지 확인하세요
