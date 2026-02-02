# 섹션 03: 보호된 라우트 - 연습 문제

> **난이도**: ⭐⭐⭐ (3/5)
> **파일**: `exercise.py`

---

## 사전 준비

```bash
# 필요한 패키지 설치
pip install "fastapi[standard]" "python-jose[cryptography]" "passlib[bcrypt]" bcrypt httpx
```

---

## 문제: 전체 인증 시스템 통합 구현

### 목표

sec01에서 배운 JWT 토큰과 sec02에서 배운 비밀번호 해싱을 결합하여,
**회원가입 → 로그인 → 보호된 엔드포인트 접근**의 전체 흐름을 구현합니다.

### 구현해야 할 것들

총 5개의 함수/엔드포인트를 구현해야 합니다.

---

### TODO 1: `authenticate_user` 함수

사용자명과 비밀번호로 사용자를 인증합니다.

| 항목 | 내용 |
|------|------|
| 매개변수 | `username`: str, `password`: str |
| 반환값 (성공) | `dict` - 사용자 정보 |
| 반환값 (실패) | `None` |

**구현 단계:**
1. `fake_users_db`에서 username으로 사용자를 조회합니다.
2. 사용자가 없으면 `None`을 반환합니다.
3. `verify_password()`로 비밀번호를 검증합니다.
4. 비밀번호가 틀리면 `None`을 반환합니다.
5. 모든 검증이 통과하면 사용자 정보(dict)를 반환합니다.

---

### TODO 2: `get_current_user` 의존성 함수

JWT 토큰에서 현재 사용자를 추출합니다.

| 항목 | 내용 |
|------|------|
| 매개변수 | `token`: str (OAuth2PasswordBearer에서 자동 주입) |
| 반환값 (성공) | `dict` - 사용자 정보 |
| 반환값 (실패) | HTTPException 401 발생 |

**구현 단계:**
1. `decode_access_token()`으로 토큰을 디코딩합니다.
2. 디코딩 실패 시 401 에러를 발생시킵니다.
3. 페이로드에서 `"sub"` (사용자명)을 추출합니다.
4. `"sub"`가 없으면 401 에러를 발생시킵니다.
5. DB에서 사용자를 조회합니다.
6. 사용자가 없으면 401 에러를 발생시킵니다.
7. 사용자 정보를 반환합니다.

---

### TODO 3: `POST /register` 엔드포인트

회원가입 처리 엔드포인트입니다.

**구현 단계:**
1. `fake_users_db`에 이미 같은 username이 있으면 400 에러를 발생시킵니다.
2. 비밀번호를 `hash_password()`로 해싱합니다.
3. 사용자 정보를 `fake_users_db`에 저장합니다.
4. 성공 메시지를 반환합니다.

---

### TODO 4: `POST /token` 엔드포인트

로그인 후 JWT 토큰을 발급하는 엔드포인트입니다.

**구현 단계:**
1. `authenticate_user()`로 사용자를 인증합니다.
2. 인증 실패 시 401 에러를 발생시킵니다.
3. `create_access_token()`으로 JWT 토큰을 생성합니다.
   - `data`에 `{"sub": username}`을 전달합니다.
4. `{"access_token": token, "token_type": "bearer"}`를 반환합니다.

---

### TODO 5: `GET /users/me` 엔드포인트

현재 로그인한 사용자의 정보를 반환하는 보호된 엔드포인트입니다.

**구현 단계:**
1. `get_current_user`를 의존성으로 주입합니다.
2. 사용자의 username과 email을 반환합니다.

---

## 힌트 모음

### OAuth2PasswordRequestForm 사용법
```python
# 폼 데이터를 받는 엔드포인트
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
```

### HTTPException 사용법
```python
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="에러 메시지",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### TestClient에서 폼 데이터 전송
```python
# JSON이 아니라 data= 로 전송합니다
response = client.post("/token", data={"username": "...", "password": "..."})
```

---

## 실행 및 검증

```bash
python exercise.py
```

### 기대 출력

```
✓ 회원가입 성공
✓ 로그인 및 토큰 발급 성공
✓ 보호된 엔드포인트 접근 성공
✓ 인증 없이 접근 시 401 에러 확인
✓ 잘못된 비밀번호로 로그인 실패 확인
✓ 존재하지 않는 사용자 로그인 실패 확인
✓ 잘못된 토큰으로 접근 시 401 에러 확인

모든 테스트를 통과했습니다!
```

---

## 추가 도전 과제 (선택)

1. **역할 기반 접근 제어**: `get_current_admin_user` 의존성을 만들어 관리자만 접근할 수 있는 `/admin` 엔드포인트를 추가해보세요.
2. **중복 회원가입 방지**: 이메일도 중복 체크하도록 개선해보세요.
3. **토큰 갱신**: 토큰이 만료되기 전에 새 토큰을 발급하는 `/token/refresh` 엔드포인트를 만들어보세요.
