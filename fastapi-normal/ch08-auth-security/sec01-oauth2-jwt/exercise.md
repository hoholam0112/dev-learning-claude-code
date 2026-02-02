# 섹션 01: OAuth2와 JWT 기본 - 연습 문제

> **난이도**: ⭐⭐⭐ (3/5)
> **파일**: `exercise.py`

---

## 사전 준비

```bash
# 필요한 패키지 설치
pip install "python-jose[cryptography]"
```

---

## 문제 1: JWT 토큰 생성 함수 구현

### 목표
`create_access_token` 함수를 구현하여 JWT 토큰을 생성합니다.

### 요구 사항

| 항목 | 내용 |
|------|------|
| 함수명 | `create_access_token(data, expires_delta)` |
| 매개변수 | `data`: dict - 토큰에 담을 데이터 |
| 매개변수 | `expires_delta`: timedelta - 만료 시간 간격 (기본값: 30분) |
| 반환값 | `str` - 인코딩된 JWT 토큰 |

### 구현 단계

1. `data`를 복사합니다. (원본 딕셔너리 변경 방지)
2. 현재 시간에 `expires_delta`를 더하여 만료 시간(`exp`)을 계산합니다.
3. 복사된 데이터에 `"exp"` 키로 만료 시간을 추가합니다.
4. `jwt.encode()`로 JWT 토큰을 생성하여 반환합니다.

### 힌트

```python
from datetime import datetime, timezone

# 현재 UTC 시간 구하기
now = datetime.now(timezone.utc)

# 만료 시간 계산
expire = now + expires_delta

# JWT 인코딩
jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

---

## 문제 2: JWT 토큰 디코딩 및 검증 함수 구현

### 목표
`decode_access_token` 함수를 구현하여 JWT 토큰을 디코딩하고 검증합니다.

### 요구 사항

| 항목 | 내용 |
|------|------|
| 함수명 | `decode_access_token(token)` |
| 매개변수 | `token`: str - JWT 토큰 문자열 |
| 반환값 (성공) | `dict` - 디코딩된 페이로드 |
| 반환값 (실패) | `None` - 토큰이 유효하지 않은 경우 |

### 구현 단계

1. `jwt.decode()`로 토큰을 디코딩합니다.
2. 디코딩이 성공하면 페이로드(dict)를 반환합니다.
3. `JWTError` 예외가 발생하면 `None`을 반환합니다.
   - 만료된 토큰, 잘못된 서명, 잘못된 형식 등 모든 오류가 포함됩니다.

### 힌트

```python
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # algorithms는 리스트로 전달해야 합니다!
    return payload
except JWTError:
    return None
```

> **주의**: `jwt.decode()`의 `algorithms` 매개변수는 **리스트**입니다.
> `algorithm="HS256"` (단수)가 아니라 `algorithms=["HS256"]` (복수, 리스트)입니다.

---

## 실행 및 검증

```bash
python exercise.py
```

### 기대 출력

```
✓ 토큰 생성 성공: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzd...
✓ 토큰 디코딩 성공: sub=user@example.com
✓ 만료 토큰 검증 테스트 통과
✓ 잘못된 토큰 검증 테스트 통과

모든 테스트를 통과했습니다!
```

---

## 추가 도전 과제 (선택)

1. **토큰 파트 분석**: 생성된 토큰을 `.`으로 분리하고, 각 파트를 Base64로 디코딩하여 내용을 확인해보세요.
2. **커스텀 클레임 추가**: `data`에 `"role"`, `"permissions"` 등 다양한 커스텀 데이터를 추가하여 토큰을 생성해보세요.
3. **다른 만료 시간**: 1분, 1시간, 1일 등 다양한 만료 시간으로 토큰을 생성해보세요.
