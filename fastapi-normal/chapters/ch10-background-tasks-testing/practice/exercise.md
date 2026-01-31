# 챕터 10 연습 문제: 백그라운드 작업과 테스트

---

## 문제 1: 파일 정리 백그라운드 작업

### 설명
업로드 디렉토리에서 오래된 파일을 자동으로 정리하는 백그라운드 작업을 구현하세요.

### 요구사항
1. `POST /cleanup` 엔드포인트를 만드세요
2. 백그라운드에서 다음 작업을 수행하세요:
   - 지정된 디렉토리에서 N시간 이상 된 파일 삭제
   - 빈 하위 디렉토리 삭제
   - 정리 결과를 로그 파일에 기록
3. 요청 시 즉시 응답을 반환하세요
4. `GET /cleanup/log` - 최근 정리 로그 조회
5. 정리 작업의 진행 상태를 추적할 수 있도록 구현하세요

### 예상 입출력

**정리 요청:**
```json
POST /cleanup
{
    "directory": "uploads",
    "max_age_hours": 48
}
```

**즉시 응답:**
```json
{
    "message": "파일 정리가 시작되었습니다",
    "task_id": "cleanup-20240101-120000",
    "target_directory": "uploads",
    "max_age_hours": 48
}
```

**정리 로그 조회:**
```json
GET /cleanup/log

{
    "logs": [
        {
            "task_id": "cleanup-20240101-120000",
            "started_at": "2024-01-01T12:00:00",
            "completed_at": "2024-01-01T12:00:03",
            "files_deleted": 15,
            "dirs_deleted": 2,
            "space_freed": "45.3MB",
            "status": "completed"
        }
    ]
}
```

<details>
<summary>힌트 보기</summary>

- `pathlib.Path.stat().st_mtime`으로 파일의 수정 시간을 확인할 수 있습니다
- `time.time() - mtime`으로 경과 시간(초)을 계산하세요
- 진행 상태 추적: 딕셔너리에 task_id별 상태를 저장하세요
- `Path.iterdir()`로 디렉토리 내 파일을 순회할 수 있습니다
- `Path.rmdir()`로 빈 디렉토리를 삭제할 수 있습니다 (비어있지 않으면 에러)

</details>

---

## 문제 2: API 통합 테스트 작성

### 설명
간단한 도서 관리 API에 대한 통합 테스트를 작성하세요.

### 요구사항
1. 도서 API:
   - `POST /books` - 도서 추가 (title, author, price)
   - `GET /books` - 도서 목록 조회
   - `GET /books/{book_id}` - 도서 상세 조회
   - `PUT /books/{book_id}` - 도서 수정
   - `DELETE /books/{book_id}` - 도서 삭제
2. 다음 테스트를 작성하세요:
   - 도서 생성 성공 테스트
   - 중복 도서 생성 시 에러 테스트
   - 존재하지 않는 도서 조회 시 404 테스트
   - 도서 수정 후 변경 확인 테스트
   - 도서 삭제 후 목록 확인 테스트
   - 유효하지 않은 데이터 전송 시 422 테스트
3. `pytest.fixture`를 활용하여 테스트 데이터를 관리하세요
4. 각 테스트는 독립적으로 실행 가능해야 합니다

### 예상 테스트 결과

```
$ pytest test_books.py -v

test_books.py::TestCreateBook::test_도서_생성_성공 PASSED
test_books.py::TestCreateBook::test_제목_누락_시_422 PASSED
test_books.py::TestCreateBook::test_가격_음수_시_422 PASSED
test_books.py::TestReadBook::test_도서_목록_조회 PASSED
test_books.py::TestReadBook::test_존재하지_않는_도서_404 PASSED
test_books.py::TestUpdateBook::test_도서_수정_성공 PASSED
test_books.py::TestDeleteBook::test_도서_삭제_성공 PASSED
test_books.py::TestDeleteBook::test_삭제_후_목록에서_제거 PASSED
```

<details>
<summary>힌트 보기</summary>

- `@pytest.fixture(autouse=True)`로 매 테스트마다 데이터를 초기화하세요
- `TestClient(app)`으로 테스트 클라이언트를 생성하세요
- `response.json()`으로 응답 본문을 파싱할 수 있습니다
- `assert response.status_code == 200`으로 상태 코드를 검증하세요
- fixture를 체이닝하여 미리 생성된 데이터를 활용하세요:
  ```python
  @pytest.fixture
  def created_book(sample_book):
      response = client.post("/books", json=sample_book)
      return response.json()
  ```

</details>

---

## 문제 3: 의존성 오버라이드를 활용한 DB 테스트

### 설명
SQLAlchemy 데이터베이스 의존성을 오버라이드하여 테스트용 인메모리 DB로 교체하고 테스트를 작성하세요.

### 요구사항
1. 프로덕션 코드: SQLite 파일 DB (`app.db`)
2. 테스트 코드: 인메모리 SQLite DB (`sqlite:///:memory:`)
3. `app.dependency_overrides`를 사용하여 `get_db` 의존성을 교체하세요
4. 다음을 테스트하세요:
   - CRUD 작업이 인메모리 DB에서 정상 동작
   - 테스트 간 데이터 격리 확인
   - 트랜잭션 롤백 테스트
5. 테스트 완료 후 원래 의존성을 복원하세요

### 핵심 코드 구조

```python
# 테스트용 DB 설정
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine)

# 의존성 오버라이드
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
```

### 예상 테스트 결과

```
$ pytest test_db.py -v

test_db.py::test_인메모리_DB_생성 PASSED
test_db.py::test_아이템_CRUD PASSED
test_db.py::test_테스트_간_데이터_격리 PASSED
test_db.py::test_존재하지_않는_아이템_404 PASSED
```

<details>
<summary>힌트 보기</summary>

- 인메모리 DB: `create_engine("sqlite:///:memory:")`
- 테스트 시작 시 테이블 생성: `Base.metadata.create_all(bind=test_engine)`
- 테스트 종료 시 테이블 삭제: `Base.metadata.drop_all(bind=test_engine)`
- `@pytest.fixture(autouse=True)`로 매 테스트마다 DB를 초기화하세요
- `app.dependency_overrides.clear()`로 오버라이드를 해제하세요

</details>

---

## 문제 4: 에러 케이스 테스트 (404, 422 등)

### 설명
API의 다양한 에러 상황을 체계적으로 테스트하세요.

### 요구사항
1. 다음 에러 케이스를 테스트하세요:
   - **400 Bad Request**: 잘못된 요청 (예: 중복 데이터)
   - **404 Not Found**: 존재하지 않는 리소스
   - **422 Unprocessable Entity**: 유효성 검증 실패
2. 각 에러에 대해 확인할 사항:
   - 올바른 HTTP 상태 코드
   - 에러 메시지 내용
   - 응답 본문의 구조
3. 경계값 테스트:
   - 빈 문자열
   - 매우 긴 문자열 (최대 길이 초과)
   - 음수 값
   - 잘못된 타입 (문자열 → 숫자 필드)
4. `@pytest.mark.parametrize`를 사용하여 여러 케이스를 효율적으로 테스트하세요

### 예상 테스트 결과

```
$ pytest test_errors.py -v

test_errors.py::TestNotFoundErrors::test_존재하지_않는_아이템_404 PASSED
test_errors.py::TestNotFoundErrors::test_존재하지_않는_사용자_404 PASSED
test_errors.py::TestValidationErrors::test_필수_필드_누락[title] PASSED
test_errors.py::TestValidationErrors::test_필수_필드_누락[price] PASSED
test_errors.py::TestValidationErrors::test_잘못된_타입[price-문자열] PASSED
test_errors.py::TestValidationErrors::test_잘못된_타입[quantity-음수] PASSED
test_errors.py::TestBoundaryValues::test_빈_제목 PASSED
test_errors.py::TestBoundaryValues::test_매우_긴_제목 PASSED
test_errors.py::TestBoundaryValues::test_가격_경계값[0] PASSED
test_errors.py::TestBoundaryValues::test_가격_경계값[-1] PASSED
```

<details>
<summary>힌트 보기</summary>

- `@pytest.mark.parametrize`로 여러 입력값을 한 번에 테스트하세요:
  ```python
  @pytest.mark.parametrize("field", ["title", "price", "author"])
  def test_필수_필드_누락(self, field):
      data = {"title": "책", "price": 1000, "author": "작가"}
      del data[field]
      response = client.post("/books", json=data)
      assert response.status_code == 422
  ```
- `"detail"` 키에 에러 메시지가 포함되어 있는지 확인하세요
- `response.json()`의 구조를 `isinstance()`로 검증할 수 있습니다
- 경계값 테스트에서는 정확히 허용 범위의 경계를 테스트하세요

</details>
