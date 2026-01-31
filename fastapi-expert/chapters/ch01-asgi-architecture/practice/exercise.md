# 챕터 01 연습문제: ASGI 아키텍처와 FastAPI 내부 구조

---

## 문제 1: 순수 ASGI 앱에서 라우팅 구현하기

### 설명

순수 ASGI 프로토콜만을 사용하여 간단한 라우터를 구현하세요. FastAPI나 Starlette의 라우터를 사용하지 않고, `scope`, `receive`, `send` 만으로 요청을 처리해야 합니다.

### 요구사항

1. `GET /` - `{"message": "홈페이지"}` 반환
2. `GET /health` - `{"status": "healthy", "timestamp": <현재시간>}` 반환
3. `POST /echo` - 요청 본문을 그대로 JSON 응답으로 반환
4. 존재하지 않는 경로 - `404` 상태 코드와 `{"error": "경로를 찾을 수 없습니다"}` 반환
5. 허용되지 않은 메서드 - `405` 상태 코드와 `{"error": "허용되지 않은 메서드"}` 반환
6. 모든 응답에 `Content-Type: application/json` 헤더 포함

### 예상 입출력

```bash
# GET /
curl http://localhost:8000/
# → {"message": "홈페이지"}

# GET /health
curl http://localhost:8000/health
# → {"status": "healthy", "timestamp": "2024-01-01T12:00:00"}

# POST /echo
curl -X POST http://localhost:8000/echo -d '{"key": "value"}'
# → {"received_body": "{\"key\": \"value\"}", "body_length": 16}

# 잘못된 경로
curl http://localhost:8000/unknown
# → {"error": "경로를 찾을 수 없습니다"} (404)

# 잘못된 메서드
curl -X POST http://localhost:8000/health
# → {"error": "허용되지 않은 메서드"} (405)
```

<details>
<summary>힌트</summary>

- `scope["path"]`로 경로를, `scope["method"]`로 HTTP 메서드를 확인할 수 있습니다.
- 응답 전송은 반드시 `http.response.start` → `http.response.body` 순서로 해야 합니다.
- 요청 본문은 `receive()`를 반복 호출하여 `more_body`가 `False`가 될 때까지 수집합니다.
- `json.dumps(data, ensure_ascii=False).encode("utf-8")`로 JSON 바이트를 생성합니다.
- 라우팅 테이블을 `dict`로 구성하면 깔끔합니다: `{(method, path): handler}`

</details>

---

## 문제 2: 요청/응답 본문을 기록하는 미들웨어 작성

### 설명

요청과 응답의 본문(body)을 모두 캡처하여 로깅하는 미들웨어를 두 가지 방식으로 구현하세요:
1. `BaseHTTPMiddleware` 기반 (고수준)
2. 순수 ASGI 미들웨어 (저수준)

### 요구사항

1. 요청 본문을 캡처하여 콘솔에 로깅 (최대 1KB까지만)
2. 응답 본문을 캡처하여 콘솔에 로깅 (최대 1KB까지만)
3. 요청/응답 정보를 구조화된 형태로 로깅:
   ```
   [요청] POST /api/users | 본문: {"name": "홍길동"} (23 bytes)
   [응답] POST /api/users | 상태: 201 | 본문: {"id": 1, ...} (45 bytes) | 소요: 0.0023s
   ```
4. 이미지나 바이너리 응답은 본문 내용 대신 `<바이너리 데이터>` 로 표시
5. 순수 ASGI 버전에서는 스트리밍 응답도 올바르게 처리해야 함

### 예상 입출력

```bash
# POST 요청 시 콘솔 출력:
# [요청] POST /api/data | 본문: {"key": "value"} (16 bytes)
# [응답] POST /api/data | 상태: 200 | 본문: {"result": "ok"} (15 bytes) | 소요: 0.0012s

# GET 요청 시 (본문 없음):
# [요청] GET /api/data | 본문: (없음)
# [응답] GET /api/data | 상태: 200 | 본문: {"items": [...]} (234 bytes) | 소요: 0.0008s
```

<details>
<summary>힌트</summary>

- `BaseHTTPMiddleware`에서 요청 본문은 `await request.body()`로 읽을 수 있습니다.
- `BaseHTTPMiddleware`에서 응답 본문 접근은 까다롭습니다. `response.body`가 없을 수 있어 `response.body_iterator`를 소비해야 합니다.
- 순수 ASGI 미들웨어에서는 `receive`를 래핑하여 요청 본문을 캡처하고, `send`를 래핑하여 응답 본문을 캡처합니다.
- `Content-Type` 헤더를 확인하여 바이너리 데이터 여부를 판단합니다.
- `time.perf_counter()`로 처리 시간을 측정합니다.

</details>

---

## 문제 3: Starlette의 라우팅 동작을 직접 사용해보기

### 설명

FastAPI의 라우터를 사용하지 않고, Starlette의 `Route`, `Router`, `Mount`를 직접 조합하여 다음 요구사항을 만족하는 애플리케이션을 만드세요.

### 요구사항

1. Starlette의 `Route`와 `Router`를 직접 사용하여 라우팅을 구성
2. 다음 엔드포인트 구현:
   - `GET /` - 홈페이지
   - `GET /users/{user_id:int}` - 사용자 상세 (타입 변환 포함)
   - `POST /users` - 사용자 생성
3. `Mount`를 사용하여 서브 애플리케이션 구성:
   - `/admin` 하위에 별도 라우터 마운트
   - `GET /admin/dashboard` - 관리자 대시보드
   - `GET /admin/users` - 사용자 관리
4. 404 처리 커스터마이징
5. 경로 매칭의 우선순위를 실험하고 결과를 주석으로 기록

### 예상 입출력

```bash
# GET /
curl http://localhost:8000/
# → {"message": "Starlette 라우터 직접 사용"}

# GET /users/42
curl http://localhost:8000/users/42
# → {"user_id": 42, "타입": "int"}

# GET /users/abc (타입 불일치)
curl http://localhost:8000/users/abc
# → 404 또는 적절한 에러 응답

# GET /admin/dashboard
curl http://localhost:8000/admin/dashboard
# → {"page": "관리자 대시보드"}
```

<details>
<summary>힌트</summary>

- `from starlette.routing import Route, Router, Mount`를 사용합니다.
- `Route`의 첫 번째 인자는 경로 패턴, 두 번째는 핸들러 함수입니다.
- Starlette 핸들러는 `async def handler(request: Request) -> Response` 시그니처를 따릅니다.
- `{user_id:int}` 문법으로 경로 파라미터의 타입을 지정할 수 있습니다.
- `Mount("/admin", routes=[...])` 로 서브 라우터를 구성합니다.
- `Router(routes=[...])`로 라우터를 생성하고, 이를 ASGI 앱으로 직접 사용할 수 있습니다.

</details>

---

## 제출 가이드

- `solution.py` 파일에 세 문제의 답안을 모두 작성하세요
- 각 문제의 답안은 명확히 구분하세요 (주석이나 클래스로)
- `uvicorn solution:app --reload` 명령으로 실행 가능해야 합니다
- 콘솔 출력을 통해 각 기능의 동작을 확인할 수 있어야 합니다
