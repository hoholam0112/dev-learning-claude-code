# 연습 문제: 구조화된 로깅

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: JSON 포맷 로거

커스텀 JSON Formatter를 만들어 로그를 JSON 문자열로 출력하세요.

### 요구 사항

- `JSONFormatter` 클래스를 구현 (`logging.Formatter` 상속)
- `format` 메서드에서 로그 레코드를 JSON 문자열로 변환
- JSON에 포함할 필드: `timestamp`, `level`, `message`
- `record`에 `extra_data` 속성이 있으면 JSON에 병합
- `ListHandler`에 `JSONFormatter`를 적용하여 로그 캡처
- `GET /items` 엔드포인트에서 extra_data 포함 로그 기록

### 힌트

```python
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": ...,  # datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        return json.dumps(log_data, ensure_ascii=False)
```

---

## 문제 2: request_id 기반 요청 추적

모든 요청에 고유한 request_id를 부여하고, 로그에 request_id를 포함하세요.

### 요구 사항

- 미들웨어에서 `uuid.uuid4()`로 request_id 생성
- `request.state.request_id`에 저장
- 응답 헤더 `X-Request-ID`에 request_id 포함
- `GET /users/{user_id}` 엔드포인트에서 request_id를 포함하여 로그 기록
- 로그의 JSON에 `request_id` 필드가 존재하는지 테스트

### 힌트

```python
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

---

## 테스트 기대 결과

```
✓ JSON 포맷 로그에 timestamp 필드 존재
✓ JSON 포맷 로그에 level 필드 존재
✓ JSON 포맷 로그에 message 필드 존재
✓ JSON 포맷 로그에 extra_data 필드가 병합됨
✓ 응답 헤더에 X-Request-ID 포함
✓ 로그에 request_id 필드 존재
✓ 응답 본문에 request_id 포함

모든 테스트를 통과했습니다!
```
