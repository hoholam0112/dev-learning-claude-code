# 섹션 02: 비밀번호 해싱

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 (OAuth2와 JWT 기본) 완료
> **학습 목표**: 비밀번호를 안전하게 해싱하고 검증할 수 있다

---

## 핵심 개념

### 1. 왜 비밀번호를 평문으로 저장하면 안 되는가?

비밀번호를 데이터베이스에 **그대로(평문) 저장하는 것은 가장 위험한 보안 실수**입니다.

```
[ 절대 하면 안 되는 것 ]

users 테이블:
| id | username | password      |
|----|----------|---------------|
| 1  | 홍길동    | mypassword123 |   ← 평문 저장! 위험!
| 2  | 김영희    | qwerty456     |   ← 누구나 읽을 수 있음!
```

#### 평문 저장의 위험성

1. **데이터베이스 유출**: DB가 해킹되면 모든 사용자의 비밀번호가 즉시 노출됩니다.
2. **내부자 위협**: DB 접근 권한이 있는 직원이 비밀번호를 볼 수 있습니다.
3. **비밀번호 재사용**: 많은 사용자가 여러 서비스에 같은 비밀번호를 사용합니다. 한 곳이 유출되면 다른 서비스도 위험합니다.
4. **법적 책임**: 개인정보보호법에 따라 비밀번호는 암호화하여 저장해야 합니다.

```
[ 올바른 방법 - 해시 저장 ]

users 테이블:
| id | username | hashed_password                              |
|----|----------|----------------------------------------------|
| 1  | 홍길동    | $2b$12$LJ3m4ys3Gz2k... (60자 해시값)           |
| 2  | 김영희    | $2b$12$Xk9vBn7Rp5qW... (원본 복원 불가)         |
```

---

### 2. 해시(Hash) vs 암호화(Encryption)

이 두 개념은 자주 혼동되지만 **근본적으로 다릅니다**.

| 항목 | 해시 (Hash) | 암호화 (Encryption) |
|------|------------|-------------------|
| 방향 | **단방향** (원본 복원 불가) | **양방향** (복호화 가능) |
| 용도 | 비밀번호 저장, 무결성 검증 | 데이터 전송, 파일 보호 |
| 키 필요 | 불필요 (솔트 사용) | 필요 (암호화 키) |
| 예시 | bcrypt, SHA-256 | AES, RSA |

```
[ 해시 - 단방향 ]
"mypassword" → bcrypt → "$2b$12$LJ3m4ys3..." (되돌릴 수 없음!)

[ 암호화 - 양방향 ]
"mypassword" → AES 암호화(키) → "x8f2k9..." → AES 복호화(키) → "mypassword"
```

비밀번호는 반드시 **해시**를 사용합니다. 서버도 원본 비밀번호를 알 필요가 없습니다.
로그인 시에는 입력된 비밀번호를 같은 방식으로 해시하여 저장된 해시값과 **비교**합니다.

---

### 3. 솔트(Salt)

솔트는 해시 전에 비밀번호에 추가하는 **무작위 문자열**입니다.

#### 솔트가 없으면?

```
같은 비밀번호 → 같은 해시값 (위험!)

"password123" → SHA256 → "ef92b778..."
"password123" → SHA256 → "ef92b778..."  ← 같은 해시! 누가 같은 비밀번호인지 알 수 있음
```

공격자는 미리 계산된 해시값 목록(레인보우 테이블)을 사용하여 원본을 추측할 수 있습니다.

#### 솔트가 있으면?

```
같은 비밀번호 → 다른 해시값 (안전!)

"password123" + salt_A → bcrypt → "$2b$12$LJ3m4ys3..."
"password123" + salt_B → bcrypt → "$2b$12$Xk9vBn7R..."  ← 완전히 다른 해시!
```

bcrypt는 솔트를 **자동으로 생성하고 해시값에 포함**시킵니다.
별도로 솔트를 관리할 필요가 없습니다.

```
bcrypt 해시값의 구조:
$2b$12$LJ3m4ys3Gz2kB5e8vX1qZOxYz1234567890abcdefghij
 │  │  │                    │
 │  │  │                    └── 해시된 비밀번호
 │  │  └── 솔트 (22자)
 │  └── 라운드 수 (12 = 2^12 = 4096번 해싱)
 └── 알고리즘 식별자 (2b = bcrypt)
```

---

### 4. bcrypt 알고리즘

bcrypt는 비밀번호 해싱을 위해 특별히 설계된 알고리즘입니다.

#### bcrypt의 장점

1. **느린 속도**: 의도적으로 느리게 설계되어 무차별 대입 공격(brute force)을 어렵게 만듭니다.
2. **자동 솔트**: 매번 다른 솔트를 자동으로 생성합니다.
3. **적응형 비용**: 라운드 수를 조절하여 하드웨어 성능 향상에 대응할 수 있습니다.
4. **검증된 알고리즘**: 1999년부터 사용된 검증된 표준입니다.

> **참고**: SHA-256 같은 일반 해시 함수는 비밀번호 저장에 적합하지 않습니다.
> 너무 빨라서 공격자가 초당 수십억 개의 비밀번호를 시도할 수 있기 때문입니다.

---

### 5. passlib 라이브러리

`passlib`은 Python에서 비밀번호 해싱을 쉽게 처리할 수 있게 해주는 라이브러리입니다.
bcrypt를 직접 사용하는 것보다 더 편리한 인터페이스를 제공합니다.

```bash
pip install "passlib[bcrypt]"
pip install bcrypt
```

#### CryptContext 설정

```python
from passlib.context import CryptContext

# 비밀번호 해싱 컨텍스트 설정
# - schemes: 사용할 해싱 알고리즘 목록
# - deprecated: "auto"로 설정하면 새 알고리즘 추가 시 기존 알고리즘을 자동 비권장 처리
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

#### 비밀번호 해싱

```python
# 평문 비밀번호를 해싱합니다.
hashed = pwd_context.hash("mypassword123")
print(hashed)
# 출력: $2b$12$LJ3m4ys3Gz2kB5e8vX1qZOxYz...

# 같은 비밀번호를 다시 해싱하면 다른 결과가 나옵니다 (솔트가 다르므로)
hashed2 = pwd_context.hash("mypassword123")
print(hashed == hashed2)  # False!
```

#### 비밀번호 검증

```python
# 입력된 비밀번호가 저장된 해시와 일치하는지 확인합니다.
is_valid = pwd_context.verify("mypassword123", hashed)
print(is_valid)  # True

is_valid = pwd_context.verify("wrongpassword", hashed)
print(is_valid)  # False
```

---

## 전체 코드 예제

```python
"""비밀번호 해싱 유틸리티 예제"""
from passlib.context import CryptContext

# 해싱 컨텍스트 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    평문 비밀번호를 bcrypt로 해싱합니다.

    Args:
        plain_password: 평문 비밀번호

    Returns:
        해싱된 비밀번호 문자열
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교합니다.

    Args:
        plain_password: 사용자가 입력한 평문 비밀번호
        hashed_password: 데이터베이스에 저장된 해시된 비밀번호

    Returns:
        일치하면 True, 불일치하면 False
    """
    return pwd_context.verify(plain_password, hashed_password)


# --- 사용 예시 ---
if __name__ == "__main__":
    # 회원가입 시: 비밀번호를 해싱하여 DB에 저장
    password = "secure_password_123"
    hashed = hash_password(password)
    print(f"원본 비밀번호: {password}")
    print(f"해시된 비밀번호: {hashed}")

    # 로그인 시: 입력된 비밀번호와 DB의 해시를 비교
    login_password = "secure_password_123"
    is_correct = verify_password(login_password, hashed)
    print(f"비밀번호 일치: {is_correct}")  # True

    wrong_password = "wrong_password"
    is_correct = verify_password(wrong_password, hashed)
    print(f"잘못된 비밀번호: {is_correct}")  # False
```

---

## 실제 FastAPI에서의 사용

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 가상의 데이터베이스 (실제로는 DB를 사용합니다)
fake_users_db = {}


class UserCreate(BaseModel):
    username: str
    password: str


@app.post("/register")
async def register(user: UserCreate):
    """회원가입 엔드포인트"""
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다")

    # 비밀번호를 해싱하여 저장합니다 (평문 저장 금지!)
    hashed_password = hash_password(user.password)
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed_password  # 해시된 비밀번호만 저장
    }
    return {"message": "회원가입이 완료되었습니다"}
```

---

## 주의 사항

### 절대 하지 말아야 할 것들

```python
# 1. 평문 비밀번호를 DB에 저장하지 마세요
user["password"] = "mypassword"  # 절대 금지!

# 2. MD5나 SHA-1 같은 약한 해시를 사용하지 마세요
import hashlib
hashlib.md5("mypassword".encode()).hexdigest()  # 보안 취약!

# 3. 해시된 비밀번호를 로그에 출력하지 마세요
print(f"해시: {hashed_password}")  # 개발 중에만, 운영에서는 금지
```

### 권장 사항

```python
# 1. bcrypt를 사용하세요
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. passlib의 CryptContext를 사용하면 나중에 알고리즘을 쉽게 교체할 수 있습니다
# 예: bcrypt → argon2로 전환 시
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
# 기존 bcrypt 해시도 자동으로 검증되고, 새 해시는 argon2로 생성됩니다

# 3. 비밀번호 최소 길이를 강제하세요
if len(password) < 8:
    raise HTTPException(status_code=400, detail="비밀번호는 8자 이상이어야 합니다")
```

---

## 정리

| 개념 | 설명 |
|------|------|
| 평문 저장 | 절대 금지. DB 유출 시 모든 비밀번호 노출 |
| 해시 (Hash) | 단방향 변환. 원본 복원 불가 |
| 암호화 (Encryption) | 양방향 변환. 키로 복호화 가능 |
| 솔트 (Salt) | 해시 전 추가하는 무작위 문자열 |
| bcrypt | 비밀번호 전용 해시 알고리즘 (느린 속도가 장점) |
| passlib | Python 비밀번호 해싱 라이브러리 |
| CryptContext | passlib의 해싱 컨텍스트 관리 클래스 |
| `pwd_context.hash()` | 비밀번호 해싱 |
| `pwd_context.verify()` | 비밀번호 검증 |

---

## 다음 단계

비밀번호 해싱을 배웠으니, 다음 섹션에서는 JWT와 비밀번호 해싱을 결합하여
완전한 인증 시스템을 구현합니다.

> [sec03-protected-routes: 보호된 라우트](../sec03-protected-routes/concept.md)
