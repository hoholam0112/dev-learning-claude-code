# 실습: 에러 처리 (Error Handling)

> `exercise.py`를 열어 TODO 부분을 완성하세요.

---

## 문제: 에러 처리가 포함된 도서 관리 API

도서 관리 API를 구현하면서, 다양한 에러 상황을 처리합니다.

### 요구 사항

1. **GET /books/{book_id}** - 도서 조회
   - 존재하지 않는 `book_id`이면 **404 에러** 발생
   - `detail`: "ID {book_id}인 도서를 찾을 수 없습니다"

2. **POST /books** - 도서 등록
   - 이미 같은 `title`의 도서가 있으면 **400 에러** 발생
   - `detail`: "'{title}' 제목의 도서가 이미 존재합니다"
   - 성공 시 **201 Created** 반환

3. **DELETE /books/{book_id}** - 도서 삭제
   - 존재하지 않는 `book_id`이면 **404 에러** 발생
   - `user_role` 쿼리 매개변수가 "admin"이 아니면 **403 에러** 발생
   - `detail`: "도서 삭제 권한이 없습니다. 관리자만 삭제할 수 있습니다"
   - 성공 시 **204 No Content** 반환

4. **커스텀 예외 핸들러** (선택 과제)
   - `BookNotFoundException` 커스텀 예외 클래스를 만들고
   - `exception_handler`를 등록하여 통일된 에러 응답 형식을 사용

### 힌트

- `HTTPException`을 `raise`하면 즉시 에러 응답이 반환됩니다.
- `any()` 함수로 중복 제목을 확인할 수 있습니다.
- DELETE에서는 404를 먼저 확인하고, 그 다음 권한을 확인하세요.

---

## 실행 방법

```bash
# 테스트 실행
python exercise.py

# 서버로 실행
uvicorn exercise:app --reload
```

---

## 확인 포인트

- 존재하지 않는 도서를 조회하면 404가 반환되는가?
- 중복 제목으로 등록하면 400이 반환되는가?
- 관리자가 아닌 사용자가 삭제하면 403이 반환되는가?
- 에러 메시지가 구체적이고 명확한가?
