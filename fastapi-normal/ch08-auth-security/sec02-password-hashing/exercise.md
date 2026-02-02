# 섹션 02: 비밀번호 해싱 - 연습 문제

> **난이도**: ⭐⭐⭐ (3/5)
> **파일**: `exercise.py`

---

## 사전 준비

```bash
# 필요한 패키지 설치
pip install "passlib[bcrypt]" bcrypt
```

---

## 문제 1: 비밀번호 해싱 함수 구현

### 목표
`hash_password` 함수를 구현하여 평문 비밀번호를 bcrypt로 해싱합니다.

### 요구 사항

| 항목 | 내용 |
|------|------|
| 함수명 | `hash_password(plain_password)` |
| 매개변수 | `plain_password`: str - 평문 비밀번호 |
| 반환값 | `str` - bcrypt로 해싱된 비밀번호 |

### 구현 단계

1. `pwd_context.hash()`를 사용하여 비밀번호를 해싱합니다.
2. 해싱된 문자열을 반환합니다.

### 힌트

```python
# CryptContext의 hash() 메서드를 사용합니다.
hashed = pwd_context.hash(plain_password)
```

---

## 문제 2: 비밀번호 검증 함수 구현

### 목표
`verify_password` 함수를 구현하여 평문 비밀번호와 해시된 비밀번호를 비교합니다.

### 요구 사항

| 항목 | 내용 |
|------|------|
| 함수명 | `verify_password(plain_password, hashed_password)` |
| 매개변수 | `plain_password`: str - 사용자가 입력한 평문 비밀번호 |
| 매개변수 | `hashed_password`: str - DB에 저장된 해시된 비밀번호 |
| 반환값 | `bool` - 일치하면 True, 불일치하면 False |

### 구현 단계

1. `pwd_context.verify()`를 사용하여 비밀번호를 비교합니다.
2. 비교 결과(True/False)를 반환합니다.

### 힌트

```python
# CryptContext의 verify() 메서드를 사용합니다.
# 첫 번째 인자: 평문 비밀번호
# 두 번째 인자: 해시된 비밀번호
is_match = pwd_context.verify(plain_password, hashed_password)
```

> **주의**: `==` 연산자로 해시를 비교하면 안 됩니다!
> 같은 비밀번호라도 솔트가 달라서 해시값이 다릅니다.
> 반드시 `verify()` 메서드를 사용해야 합니다.

---

## 실행 및 검증

```bash
python exercise.py
```

### 기대 출력

```
✓ 비밀번호 해싱 성공 (60자 해시 생성)
✓ 올바른 비밀번호 검증 통과
✓ 잘못된 비밀번호 검증 통과
✓ 같은 비밀번호, 다른 해시 확인
✓ 여러 비밀번호 해싱/검증 통과

모든 테스트를 통과했습니다!
```

---

## 추가 도전 과제 (선택)

1. **해시값 분석**: 생성된 bcrypt 해시값을 분석하여 알고리즘 식별자, 라운드 수, 솔트 부분을 구분해보세요.
2. **비밀번호 강도 검증**: 비밀번호 길이, 대소문자, 숫자, 특수문자 포함 여부를 확인하는 `validate_password_strength` 함수를 추가로 만들어보세요.
3. **성능 측정**: `time` 모듈을 사용하여 해싱에 걸리는 시간을 측정해보세요. bcrypt가 의도적으로 느린 이유를 체감할 수 있습니다.
