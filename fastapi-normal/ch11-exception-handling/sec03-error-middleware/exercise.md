# sec03: 에러 미들웨어 - 연습 문제

> `exercise.py` 파일을 열고 TODO 부분을 완성하세요.
> 테스트 실행: `python exercise.py`

---

## 문제 1: trace_id 미들웨어

### 요구사항

모든 요청에 `trace_id`를 부여하는 미들웨어를 구현하세요.

- `uuid.uuid4()`로 `trace_id` 생성
- `request.state.trace_id`에 저장
- 응답 헤더 `X-Trace-ID`에 추가
- 에러 발생 시에도 `trace_id`가 응답에 포함되도록 에러 핸들러 수정

### 동작 흐름

```
1. 미들웨어: trace_id 생성 → request.state.trace_id에 저장
2. 엔드포인트: 정상 처리 또는 예외 발생
3-a. 정상: 응답 헤더에 X-Trace-ID 추가
3-b. 에러: 전역 핸들러가 ErrorResponse에 trace_id 포함 + 응답 헤더에도 추가
```

### 테스트 케이스

```
GET /health          -> 200, 응답 헤더에 X-Trace-ID 포함
GET /users/999       -> 404, 에러 응답에 trace_id 포함, 헤더에도 X-Trace-ID 포함
```

---

## 문제 2: 에러 로깅 미들웨어

### 요구사항

에러를 자동으로 로깅하는 미들웨어를 구현하세요.

- `error_log` 리스트에 에러 정보를 기록
- 기록할 정보: `trace_id`, `method`, `path`, `error_type`, `error_message`
- 예외를 잡아서 로깅한 후 **다시 발생**시킴 (전역 핸들러가 처리)
- 테스트용 엔드포인트로 다양한 에러 발생 후 로그 확인

### 테스트 케이스

```
GET /error/not-found  -> 404, error_log에 "NotFoundException" 기록
GET /error/runtime    -> 500, error_log에 "RuntimeError" 기록

error_log에 trace_id, method, path, error_type, error_message 포함 확인
```

---

## 힌트

1. trace_id 미들웨어에서는 `call_next` 호출 전에 `request.state.trace_id`를 설정합니다.
2. 에러 로깅 미들웨어에서는 `try-except`로 예외를 잡고, 로그를 기록한 후 `raise`합니다.
3. 미들웨어 등록 순서에 주의하세요. trace_id가 먼저 설정되어야 로깅에서 사용할 수 있습니다.

```python
# 미들웨어 등록 (안쪽부터 등록, 나중에 등록한 것이 바깥쪽)
app.add_middleware(TraceIDMiddleware)         # 안쪽
app.add_middleware(ErrorLoggingMiddleware)    # 바깥쪽 (먼저 실행)
```

4. `getattr(request.state, "trace_id", "unknown")`으로 안전하게 접근하세요.
