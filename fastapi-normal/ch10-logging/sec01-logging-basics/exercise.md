# 연습 문제: 로깅 기본

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: 기본 로거 설정

FastAPI 앱에 로거를 설정하고, 각 로그 레벨로 메시지를 기록하는 엔드포인트를 만드세요.

### 요구 사항

- `"app"` 이름의 로거를 생성하고 DEBUG 레벨로 설정
- `ListHandler`를 사용하여 로그 레코드를 리스트에 저장
- Formatter 포맷: `"%(levelname)s - %(message)s"`
- `GET /info` - INFO 레벨로 `"정보 메시지입니다"` 로그 기록 후 `{"level": "info", "message": "정보 메시지입니다"}` 반환
- `GET /warning` - WARNING 레벨로 `"경고 메시지입니다"` 로그 기록 후 `{"level": "warning", "message": "경고 메시지입니다"}` 반환
- `GET /error` - ERROR 레벨로 `"에러 메시지입니다"` 로그 기록 후 `{"level": "error", "message": "에러 메시지입니다"}` 반환

### 힌트

- `logging.getLogger("app")`으로 로거 생성
- `logger.setLevel(logging.DEBUG)`로 레벨 설정
- `ListHandler`는 이미 제공되어 있습니다

---

## 문제 2: 요청 로깅 미들웨어

모든 HTTP 요청을 자동으로 기록하는 미들웨어를 작성하세요.

### 요구 사항

- 미들웨어에서 각 요청의 메서드, 경로, 상태 코드를 `access_logs` 리스트에 딕셔너리로 기록
- 딕셔너리 형식: `{"method": "GET", "path": "/info", "status_code": 200}`
- `GET /logs` 엔드포인트에서 `access_logs` 리스트를 반환
- 단, `/logs` 경로에 대한 요청은 로그에 기록하지 않음

### 힌트

- `@app.middleware("http")`를 사용
- `request.method`, `request.url.path`, `response.status_code` 활용
- `call_next(request)` 호출 후 status_code를 가져올 수 있습니다

---

## 테스트 기대 결과

```
✓ GET /info - INFO 레벨 로그 기록 확인
✓ GET /warning - WARNING 레벨 로그 기록 확인
✓ GET /error - ERROR 레벨 로그 기록 확인
✓ 요청 로깅 미들웨어 - 요청이 access_logs에 기록됨
✓ /logs 경로는 access_logs에 기록되지 않음

모든 테스트를 통과했습니다!
```
