# 섹션 01: OAuth2와 JWT 기본

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: Ch05 (의존성 주입) 완료
> **학습 목표**: OAuth2 흐름과 JWT 토큰 구조를 이해할 수 있다

---

## 핵심 개념

### 1. OAuth2란?

OAuth2는 **인증 및 권한 부여를 위한 업계 표준 프로토콜**입니다.
"Open Authorization 2.0"의 약자로, 사용자가 비밀번호를 직접 전달하지 않고도
제3자 애플리케이션에 자원 접근 권한을 부여할 수 있게 합니다.

FastAPI에서는 OAuth2의 여러 방식 중 **Password Flow**를 가장 많이 사용합니다.
이 방식은 사용자가 ID와 비밀번호를 직접 서버에 보내고, 서버가 토큰을 발급하는 단순한 흐름입니다.

> **참고**: Google/GitHub 로그인 같은 소셜 로그인은 OAuth2의 "Authorization Code Flow"를 사용합니다.
> 이 챕터에서는 자체 인증 시스템에 적합한 "Password Flow"를 다룹니다.

---

### 2. OAuth2 Password Flow

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant S as FastAPI 서버

    C->>S: POST /token (username + password)
    Note over S: 1. 사용자 확인<br/>2. 비밀번호 검증<br/>3. JWT 토큰 생성
    S-->>C: {"access_token": "eyJ...", "token_type": "bearer"}

    C->>S: GET /users/me (Authorization: Bearer eyJ...)
    Note over S: 토큰 디코딩 및 검증
    S-->>C: {"username": "홍길동", "email": "hong@example.com"}

    C->>S: GET /admin (Authorization: Bearer eyJ...)
    Note over S: 토큰 검증 + 권한 확인
    S-->>C: 403 Forbidden (권한 없음)
```

**흐름 요약:**
1. 클라이언트가 사용자명과 비밀번호로 로그인 요청을 보냅니다.
2. 서버가 자격 증명을 확인하고 JWT 토큰을 발급합니다.
3. 클라이언트는 이후 모든 요청에 토큰을 `Authorization` 헤더에 포함합니다.
4. 서버는 토큰을 검증하고 요청을 처리합니다.

---

### 3. OAuth2PasswordBearer

FastAPI는 OAuth2 Password Flow를 위한 내장 클래스를 제공합니다.

```python
from fastapi.security import OAuth2PasswordBearer

# tokenUrl은 토큰을 발급하는 엔드포인트 경로입니다.
# Swagger UI에서 "Authorize" 버튼을 누르면 이 URL로 로그인 요청을 보냅니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

`OAuth2PasswordBearer`는 **의존성(Dependency)**으로 사용됩니다:
- 요청의 `Authorization: Bearer <토큰>` 헤더에서 토큰을 추출합니다.
- 헤더가 없으면 자동으로 **401 Unauthorized** 에러를 반환합니다.
- Swagger UI에 **자물쇠 아이콘(Authorize)**이 자동으로 추가됩니다.

```python
from fastapi import Depends

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # token에는 "Bearer" 뒤의 JWT 문자열이 들어옵니다.
    return {"token": token}
```

---

### 4. JWT (JSON Web Token)

JWT는 **당사자 간에 정보를 안전하게 전달하기 위한 토큰 형식**입니다.
자체적으로 필요한 정보를 담고 있어서 "자기 포함(self-contained) 토큰"이라고도 합니다.

#### JWT의 구조

JWT는 **점(.)으로 구분된 3개의 파트**로 구성됩니다:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA5MTIzNDU2fQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
 \___________ Header ____________/.\_____________ Payload ______________/.\__________ Signature __________/
```

| 파트 | 내용 | 설명 |
|------|------|------|
| **Header** | `{"alg": "HS256", "typ": "JWT"}` | 알고리즘과 토큰 타입 |
| **Payload** | `{"sub": "user@example.com", "exp": 1709123456}` | 사용자 정보와 메타데이터 |
| **Signature** | HMAC-SHA256(header + payload, secret_key) | 위변조 방지 서명 |

#### Header (헤더)
```json
{
  "alg": "HS256",  // 서명 알고리즘 (HMAC SHA-256)
  "typ": "JWT"     // 토큰 타입
}
```

#### Payload (페이로드)
```json
{
  "sub": "user@example.com",  // subject: 토큰의 주체 (보통 사용자 식별자)
  "exp": 1709123456,          // expiration: 만료 시간 (Unix timestamp)
  "iat": 1709119856,          // issued at: 발급 시간
  "role": "admin"             // 커스텀 클레임: 자유롭게 추가 가능
}
```

> **주의**: Payload는 Base64로 인코딩되어 있을 뿐, **암호화되지 않습니다**.
> 누구나 디코딩하여 내용을 볼 수 있으므로 비밀번호 같은 민감한 정보를 넣으면 안 됩니다.

#### Signature (서명)
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```
서명은 토큰이 변조되지 않았음을 보증합니다.
서버만 알고 있는 `secret_key`로 생성되므로, 토큰 내용을 변경하면 서명이 맞지 않게 됩니다.

---

### 5. python-jose 라이브러리

`python-jose`는 Python에서 JWT를 생성하고 검증하는 라이브러리입니다.

```bash
pip install "python-jose[cryptography]"
```

#### JWT 토큰 생성

```python
from datetime import datetime, timedelta, timezone
from jose import jwt

# 비밀 키 (실제 운영에서는 환경 변수로 관리해야 합니다)
SECRET_KEY = "your-secret-key-keep-it-safe"
ALGORITHM = "HS256"

# 페이로드 구성
payload = {
    "sub": "user@example.com",           # 사용자 식별자
    "role": "admin",                     # 커스텀 데이터
    "exp": datetime.now(timezone.utc) + timedelta(minutes=30)  # 만료 시간
}

# JWT 토큰 생성
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(token)
# 출력: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWI...
```

#### JWT 토큰 디코딩

```python
from jose import jwt, JWTError

try:
    # 토큰 디코딩 (서명 검증 + 만료 확인이 자동으로 수행됩니다)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(payload)
    # 출력: {"sub": "user@example.com", "role": "admin", "exp": 1709123456}

    username = payload.get("sub")
    print(f"사용자: {username}")
except JWTError as e:
    # 서명이 잘못되었거나, 토큰이 만료되었거나, 형식이 잘못된 경우
    print(f"토큰 검증 실패: {e}")
```

---

## JWT vs 세션 비교

| 항목 | JWT (토큰 기반) | 세션 (서버 기반) |
|------|----------------|-----------------|
| 저장 위치 | 클라이언트 (쿠키/로컬스토리지) | 서버 (메모리/DB) |
| 서버 부하 | 낮음 (상태 없음) | 높음 (세션 저장 필요) |
| 확장성 | 우수 (서버 간 공유 불필요) | 제한적 (세션 공유 필요) |
| 만료 관리 | 토큰 자체에 만료 시간 포함 | 서버에서 세션 만료 관리 |
| 보안 | 토큰 탈취 시 만료까지 유효 | 서버에서 즉시 무효화 가능 |
| 적합한 경우 | REST API, 마이크로서비스 | 전통적인 웹 애플리케이션 |

---

## 전체 코드 예제

아래는 JWT 토큰 생성과 디코딩의 전체 예제입니다.

```python
"""JWT 토큰 생성 및 검증 예제"""
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# --- 설정 ---
SECRET_KEY = "학습용-비밀키-실제-운영에서는-환경변수를-사용하세요"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    JWT 액세스 토큰을 생성합니다.

    Args:
        data: 토큰에 담을 데이터 (예: {"sub": "user@example.com"})
        expires_delta: 만료 시간 간격 (기본값: 30분)

    Returns:
        인코딩된 JWT 토큰 문자열
    """
    # 원본 데이터를 변경하지 않기 위해 복사합니다.
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 페이로드에 만료 시간 추가
    to_encode.update({"exp": expire})

    # JWT 토큰 인코딩
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    JWT 토큰을 디코딩하고 검증합니다.

    Args:
        token: JWT 토큰 문자열

    Returns:
        디코딩된 페이로드 딕셔너리, 실패 시 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# --- 사용 예시 ---
if __name__ == "__main__":
    # 1. 토큰 생성
    token = create_access_token({"sub": "hong@example.com", "role": "user"})
    print(f"생성된 토큰: {token}")
    print(f"토큰 파트 수: {len(token.split('.'))}")  # 3

    # 2. 토큰 디코딩
    payload = decode_access_token(token)
    print(f"디코딩된 페이로드: {payload}")
    print(f"사용자: {payload['sub']}")
    print(f"역할: {payload['role']}")

    # 3. 잘못된 토큰 테스트
    result = decode_access_token("잘못된.토큰.문자열")
    print(f"잘못된 토큰 결과: {result}")  # None
```

---

## 주의 사항

### SECRET_KEY 관리
```python
# 나쁜 예: 코드에 직접 하드코딩
SECRET_KEY = "my-secret-key"

# 좋은 예: 환경 변수에서 읽기
import os
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-for-development-only")
```

### 토큰에 민감한 정보를 넣지 마세요
```python
# 나쁜 예: 비밀번호를 토큰에 포함
payload = {"sub": "user@example.com", "password": "1234"}  # 절대 금지!

# 좋은 예: 식별 정보만 포함
payload = {"sub": "user@example.com", "role": "admin"}
```

### 만료 시간을 반드시 설정하세요
```python
# 나쁜 예: 만료 시간 없는 토큰
payload = {"sub": "user@example.com"}  # 영원히 유효한 토큰은 위험!

# 좋은 예: 적절한 만료 시간 설정
payload = {
    "sub": "user@example.com",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
}
```

---

## 정리

| 개념 | 설명 |
|------|------|
| OAuth2 | 인증/인가를 위한 표준 프로토콜 |
| Password Flow | ID/PW로 토큰을 발급받는 OAuth2 방식 |
| OAuth2PasswordBearer | FastAPI의 토큰 추출 의존성 |
| JWT | 자기 포함(self-contained) 토큰 형식 |
| Header | 알고리즘과 토큰 타입 정보 |
| Payload | 사용자 데이터와 만료 시간 |
| Signature | 토큰 위변조 방지 서명 |
| python-jose | Python JWT 라이브러리 |
| `jwt.encode()` | JWT 토큰 생성 |
| `jwt.decode()` | JWT 토큰 디코딩 및 검증 |

---

## 다음 단계

JWT 토큰을 이해했으니, 다음 섹션에서는 비밀번호를 안전하게 해싱하는 방법을 배웁니다.

> [sec02-password-hashing: 비밀번호 해싱](../sec02-password-hashing/concept.md)
