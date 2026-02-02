# 실습: HTTP 상태 코드 (Status Codes)

> `exercise.py`를 열어 TODO 부분을 완성하세요.

---

## 문제: 올바른 상태 코드를 가진 할일(Todo) CRUD API

할일 관리 API를 구현하면서, 각 동작에 적절한 HTTP 상태 코드를 설정합니다.

### 요구 사항

1. **POST /todos** - 할일 생성
   - 상태 코드: `201 Created`
   - `response_model=TodoResponse` 지정

2. **GET /todos** - 전체 할일 목록 조회
   - 상태 코드: `200 OK` (기본값이므로 생략 가능)
   - `response_model=list[TodoResponse]` 지정

3. **GET /todos/{todo_id}** - 특정 할일 조회
   - 상태 코드: `200 OK`
   - `response_model=TodoResponse` 지정

4. **PUT /todos/{todo_id}** - 할일 수정
   - 상태 코드: `200 OK`
   - `response_model=TodoResponse` 지정

5. **DELETE /todos/{todo_id}** - 할일 삭제
   - 상태 코드: `204 No Content`
   - 응답 본문 없음 (아무것도 반환하지 않음)

### 사용할 모델

- `TodoCreate`: `title`(str), `description`(Optional[str])
- `TodoResponse`: `id`(int), `title`(str), `description`(Optional[str]), `completed`(bool)
- `TodoUpdate`: `title`(Optional[str]), `description`(Optional[str]), `completed`(Optional[bool])

### 힌트

- `status` 모듈에서 `HTTP_201_CREATED`, `HTTP_204_NO_CONTENT`를 사용하세요.
- DELETE 엔드포인트에서는 `return` 없이 함수를 종료하세요.
- PUT에서는 `model_dump(exclude_unset=True)`를 활용하여 전달된 필드만 업데이트하세요.

---

## 실행 방법

```bash
# 테스트 실행
python exercise.py

# 서버로 실행하여 Swagger UI에서 상태 코드 확인
uvicorn exercise:app --reload
```

---

## 확인 포인트

- POST 응답의 상태 코드가 201인가?
- DELETE 응답의 상태 코드가 204인가?
- DELETE 응답에 본문이 없는가?
- GET, PUT 응답의 상태 코드가 200인가?
