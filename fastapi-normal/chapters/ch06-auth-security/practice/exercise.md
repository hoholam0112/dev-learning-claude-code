# 챕터 06 연습 문제: 인증과 보안 기초

---

## 문제 1: 회원가입 엔드포인트 추가

### 설명
기존 인증 시스템에 **회원가입(register)** 엔드포인트를 추가하세요.

### 요구사항
1. `POST /register` 엔드포인트를 만드세요
2. 요청 본문: `username`, `password`, `email`
3. 이미 존재하는 사용자명이면 `400` 에러를 반환하세요
4. 비밀번호는 반드시 해싱하여 저장하세요
5. 성공 시 생성된 사용자 정보(비밀번호 제외)를 반환하세요

### 예상 입출력

**요청:**
```json
POST /register
{
    "username": "newuser",
    "password": "securepass123",
    "email": "new@example.com"
}
```

**성공 응답 (201):**
```json
{
    "username": "newuser",
    "email": "new@example.com",
    "message": "회원가입이 완료되었습니다"
}
```

**중복 사용자 응답 (400):**
```json
{
    "detail": "이미 존재하는 사용자명입니다"
}
```

<details>
<summary>힌트 보기</summary>

- `UserCreate`라는 Pydantic 모델을 만들어 요청 본문을 검증하세요
- `pwd_context.hash(password)`로 비밀번호를 해싱하세요
- `status_code=status.HTTP_201_CREATED`를 사용하면 201 응답을 반환할 수 있습니다

</details>

---

## 문제 2: 토큰 만료 처리 로직 확인

### 설명
토큰 만료 시간을 **1분**으로 설정하고, 만료된 토큰으로 접근 시 적절한 에러 메시지를 반환하는 로직을 구현하세요.

### 요구사항
1. `ACCESS_TOKEN_EXPIRE_MINUTES`를 1분으로 변경하세요
2. `GET /token/verify` 엔드포인트를 추가하세요
3. 토큰이 유효하면 남은 만료 시간(초)을 반환하세요
4. 토큰이 만료되었으면 명확한 에러 메시지를 반환하세요

### 예상 입출력

**유효한 토큰 응답:**
```json
{
    "valid": true,
    "username": "testuser",
    "expires_in_seconds": 45
}
```

**만료된 토큰 응답 (401):**
```json
{
    "detail": "토큰이 만료되었습니다. 다시 로그인해주세요."
}
```

<details>
<summary>힌트 보기</summary>

- `jwt.decode()`는 만료된 토큰에 대해 `ExpiredSignatureError`를 발생시킵니다
- `from jose import ExpiredSignatureError`로 가져올 수 있습니다
- 페이로드의 `"exp"` 값과 현재 시간을 비교하여 남은 시간을 계산하세요
- `datetime.utcnow().timestamp()`로 현재 Unix 타임스탬프를 얻을 수 있습니다

</details>

---

## 문제 3: 역할(admin/user) 기반 접근 제어 기초

### 설명
사용자에게 역할(role)을 부여하고, 역할에 따라 접근을 제한하는 시스템을 구현하세요.

### 요구사항
1. 사용자 데이터에 `role` 필드를 추가하세요 (`"admin"` 또는 `"user"`)
2. `get_current_admin_user` 의존성 함수를 만드세요
3. `GET /admin/users` - 관리자만 접근 가능 (모든 사용자 목록 반환)
4. `GET /users/me` - 모든 인증된 사용자 접근 가능

### 예상 입출력

**관리자 접근 (200):**
```json
{
    "users": [
        {"username": "testuser", "email": "test@example.com", "role": "user"},
        {"username": "admin", "email": "admin@example.com", "role": "admin"}
    ]
}
```

**일반 사용자 접근 (403):**
```json
{
    "detail": "관리자 권한이 필요합니다"
}
```

<details>
<summary>힌트 보기</summary>

- JWT 토큰의 페이로드에 `role` 정보를 포함하세요: `{"sub": username, "role": role}`
- `get_current_admin_user`는 `get_current_user`를 의존성으로 사용하세요 (의존성 체이닝)
- `status.HTTP_403_FORBIDDEN`을 사용하면 403 응답을 반환할 수 있습니다

</details>

---

## 문제 4: 리프레시 토큰 구현

### 설명
액세스 토큰이 만료되었을 때 리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받는 시스템을 구현하세요.

### 요구사항
1. 로그인 시 `access_token`과 `refresh_token`을 함께 발급하세요
2. 액세스 토큰 만료 시간: 30분
3. 리프레시 토큰 만료 시간: 7일
4. `POST /token/refresh` 엔드포인트를 추가하세요
5. 리프레시 토큰의 페이로드에는 `"type": "refresh"`를 포함하세요
6. 액세스 토큰을 리프레시 토큰으로 사용하는 것을 방지하세요

### 예상 입출력

**로그인 응답:**
```json
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
}
```

**리프레시 요청:**
```json
POST /token/refresh
{
    "refresh_token": "eyJ..."
}
```

**리프레시 응답 (200):**
```json
{
    "access_token": "새로운-eyJ...",
    "token_type": "bearer"
}
```

**잘못된 리프레시 토큰 (401):**
```json
{
    "detail": "유효하지 않은 리프레시 토큰입니다"
}
```

<details>
<summary>힌트 보기</summary>

- 리프레시 토큰도 JWT로 생성하되, 페이로드에 `"type": "refresh"`를 추가하세요
- 리프레시 엔드포인트에서는 토큰의 `type`이 `"refresh"`인지 확인하세요
- `timedelta(days=7)`로 7일 만료 시간을 설정할 수 있습니다
- 리프레시 토큰 전용 시크릿 키를 사용하면 보안이 더 강화됩니다

</details>
