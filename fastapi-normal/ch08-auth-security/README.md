# 챕터 08: 인증과 보안

> **난이도**: ⭐⭐⭐ (3/5) | **예상 학습 시간**: 3~4시간

---

## 개요

이 챕터에서는 FastAPI에서 **JWT(JSON Web Token) 토큰 기반 인증 시스템**을 구현하는 방법을 학습합니다.
사용자 로그인부터 토큰 발급, 보호된 엔드포인트 접근까지 실제 운영 환경에서 사용하는 인증 흐름 전체를 다룹니다.

---

## 왜 인증이 중요한가?

웹 API를 만들 때 인증(Authentication)은 선택이 아니라 **필수**입니다.
인증 없이 API를 공개하면 다음과 같은 심각한 문제가 발생합니다.

### 1. 보안 (Security)
- 인증이 없으면 누구나 데이터를 조회, 수정, 삭제할 수 있습니다.
- 악의적인 사용자가 민감한 정보에 접근하거나 시스템을 파괴할 수 있습니다.
- 인증은 **"당신은 누구인가?"**를 확인하는 첫 번째 방어선입니다.

### 2. 사용자 식별 (User Identification)
- 요청을 보낸 사람이 누구인지 식별해야 맞춤형 서비스를 제공할 수 있습니다.
- 예: "내 주문 내역 조회"는 로그인한 사용자 본인의 데이터만 반환해야 합니다.
- 사용자 식별 없이는 개인화된 기능을 구현할 수 없습니다.

### 3. 권한 관리 (Authorization)
- 인증된 사용자라도 모든 자원에 접근할 수 있어서는 안 됩니다.
- 일반 사용자는 자신의 데이터만, 관리자는 모든 데이터를 관리할 수 있어야 합니다.
- 인증(Authentication)을 기반으로 **인가(Authorization)**를 수행합니다.

```
인증의 3단계:

[클라이언트] ---(1) 로그인 요청 (ID/PW)---> [서버]
[클라이언트] <--(2) JWT 토큰 발급----------- [서버]
[클라이언트] ---(3) 토큰과 함께 API 요청---> [서버] ---> 토큰 검증 후 응답
```

---

## 이 챕터에서 사용하는 패키지

```bash
# 필요한 패키지 설치
pip install "fastapi[standard]"
pip install "python-jose[cryptography]"   # JWT 토큰 생성/검증
pip install "passlib[bcrypt]"             # 비밀번호 해싱
pip install bcrypt                         # bcrypt 알고리즘
```

| 패키지 | 역할 |
|--------|------|
| `python-jose` | JWT 토큰 생성, 디코딩, 검증 |
| `passlib` | 비밀번호 해싱 유틸리티 (bcrypt 래퍼) |
| `bcrypt` | 안전한 비밀번호 해싱 알고리즘 |

---

## 포함된 섹션

| 섹션 | 제목 | 핵심 내용 |
|------|------|-----------|
| [sec01-oauth2-jwt](./sec01-oauth2-jwt/) | OAuth2와 JWT 기본 | OAuth2PasswordBearer, JWT 구조, 토큰 생성/검증 |
| [sec02-password-hashing](./sec02-password-hashing/) | 비밀번호 해싱 | bcrypt, passlib, 해시 vs 암호화, 솔트(salt) |
| [sec03-protected-routes](./sec03-protected-routes/) | 보호된 라우트 | 로그인 → 토큰 발급 → 보호된 엔드포인트 접근 |

---

## 학습 순서

```
sec01-oauth2-jwt → sec02-password-hashing → sec03-protected-routes
```

1. **sec01**: JWT 토큰의 구조를 이해하고, 토큰을 생성/검증하는 방법을 배웁니다.
2. **sec02**: 비밀번호를 안전하게 해싱하고 검증하는 방법을 배웁니다.
3. **sec03**: sec01과 sec02를 통합하여 완전한 인증 시스템을 구현합니다.

---

## 사전 준비

- **Ch05 (의존성 주입)** 챕터를 완료해야 합니다.
  - `Depends`를 사용한 의존성 주입 개념이 인증 시스템의 핵심입니다.
- Python 3.10 이상을 권장합니다. (`dict | None` 문법 사용)
- 위에 명시된 패키지들이 설치되어 있어야 합니다.

```bash
# 한 번에 설치
pip install "fastapi[standard]" "python-jose[cryptography]" "passlib[bcrypt]" bcrypt
```

---

## 이 챕터를 마치면

- JWT 토큰의 구조(header.payload.signature)를 설명할 수 있습니다.
- 비밀번호를 bcrypt로 안전하게 해싱하고 검증할 수 있습니다.
- FastAPI에서 OAuth2 Password Flow 기반 인증 시스템을 구현할 수 있습니다.
- `Depends`를 활용하여 보호된 API 엔드포인트를 만들 수 있습니다.
- 인증(Authentication)과 인가(Authorization)의 차이를 설명할 수 있습니다.
