# 실습: 응답 모델 (Response Model)

> `exercise.py`를 열어 TODO 부분을 완성하세요.

---

## 문제 1: 입력/출력 모델 분리하기

사용자 생성 API를 구현합니다.

**요구 사항:**
- `UserCreate` 모델 (요청용): `username`, `email`, `password`, `full_name`(선택)
- `UserResponse` 모델 (응답용): `id`, `username`, `email`, `full_name`(선택)
- `POST /users` 엔드포인트에서 `response_model=UserResponse`를 지정
- 응답에 `password`가 **절대 포함되지 않아야** 합니다

**힌트:**
- `UserResponse`에는 `password` 필드를 정의하지 마세요.
- `response_model`을 지정하면 FastAPI가 자동으로 필터링합니다.

---

## 문제 2: 사용자 조회 엔드포인트

사용자 정보를 조회하는 API를 구현합니다.

**요구 사항:**
- `GET /users/{user_id}` 엔드포인트 작성
- `response_model=UserResponse` 지정
- `fake_db`에서 해당 `user_id`의 사용자 데이터를 조회하여 반환

---

## 실행 방법

```bash
# 테스트 실행
python exercise.py

# 서버로 실행하여 Swagger UI 확인
uvicorn exercise:app --reload
# 브라우저에서 http://localhost:8000/docs 접속
```

---

## 확인 포인트

- `POST /users` 응답에 `password`가 포함되지 않는가?
- `GET /users/{user_id}` 응답에 `id`, `username`, `email`이 포함되는가?
- Swagger UI에서 응답 스키마가 `UserResponse` 형태로 표시되는가?
