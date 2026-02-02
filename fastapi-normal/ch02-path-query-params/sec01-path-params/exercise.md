# 섹션 01: 경로 매개변수 - 연습 문제

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py` (테스트 자동 실행)
> **서버 실행**: `uvicorn exercise:app --reload`

---

## 문제 1: 사용자 프로필 조회 API

### 요구 사항

`GET /users/{user_id}` 엔드포인트를 작성하세요.

- `user_id`는 **정수(int)** 타입이어야 합니다.
- 반환값: `{"user_id": user_id, "name": f"사용자_{user_id}"}`

### 예시

```
GET /users/42
응답: {"user_id": 42, "name": "사용자_42"}

GET /users/abc
응답: 422 Unprocessable Entity (타입 검증 실패)
```

### 힌트

- 함수 매개변수에 타입 힌트를 추가하면 FastAPI가 자동으로 타입 변환과 검증을 수행합니다.
- `{user_id}`와 함수 매개변수 이름이 일치해야 합니다.

---

## 문제 2: Enum을 사용한 모델 선택 API

### 요구 사항

1. `ModelName` Enum 클래스를 정의하세요.
   - `str`과 `Enum`을 동시에 상속해야 합니다.
   - 값: `"alexnet"`, `"resnet"`, `"lenet"`

2. `GET /models/{model_name}` 엔드포인트를 작성하세요.
   - `model_name`은 `ModelName` Enum 타입이어야 합니다.
   - 반환값: `{"model_name": model_name.value, "message": f"{model_name.value} 모델이 선택되었습니다"}`

### 예시

```
GET /models/alexnet
응답: {"model_name": "alexnet", "message": "alexnet 모델이 선택되었습니다"}

GET /models/invalid
응답: 422 Unprocessable Entity (유효하지 않은 Enum 값)
```

### 힌트

- Enum 클래스는 `class ModelName(str, Enum):`으로 정의합니다.
- Enum 멤버의 실제 문자열 값은 `.value` 속성으로 접근합니다.

---

## 테스트 체크리스트

- [ ] `/users/42` 요청 시 `{"user_id": 42, "name": "사용자_42"}` 반환
- [ ] `/users/abc` 요청 시 422 에러 반환
- [ ] `/models/alexnet` 요청 시 올바른 응답 반환
- [ ] `/models/invalid` 요청 시 422 에러 반환
