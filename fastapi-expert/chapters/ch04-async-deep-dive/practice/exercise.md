# 챕터 04 연습문제: 비동기 프로그래밍 심화

---

## 문제 1: 여러 외부 서비스 동시 호출 최적화

### 설명

전자상거래 시스템의 주문 처리 과정에서 여러 외부 서비스를 동시에 호출하는 API를 구현하세요.

### 요구사항

1. 주문 처리 시 다음 5개 외부 서비스를 호출:
   - 사용자 서비스 (0.5초) - 사용자 정보 조회
   - 재고 서비스 (0.3초) - 재고 확인
   - 가격 서비스 (0.4초) - 할인 계산
   - 배송 서비스 (0.6초) - 배송비 계산
   - 결제 서비스 (0.8초) - 결제 검증
2. 의존 관계가 있는 호출 순서:
   - 1단계: 사용자 + 재고 + 가격 (동시 호출)
   - 2단계: 배송 (1단계의 사용자/재고 결과 필요)
   - 3단계: 결제 (2단계까지의 모든 결과 필요)
3. 각 단계별 타이밍을 기록하고 결과에 포함
4. 개별 서비스 실패 시 적절한 에러 처리
5. 순차 실행과 최적화된 실행의 소요 시간 비교

### 예상 입출력

```bash
POST /orders/process
{
  "순차_실행_예상시간": "2.6초",
  "최적화_실행_시간": "1.7초 (1단계 0.5초 + 2단계 0.6초 + 3단계 0.8초)",
  "단계별_결과": {
    "1단계": {"사용자": {...}, "재고": {...}, "가격": {...}, "소요시간": "0.5초"},
    "2단계": {"배송": {...}, "소요시간": "0.6초"},
    "3단계": {"결제": {...}, "소요시간": "0.8초"}
  }
}
```

<details>
<summary>힌트</summary>

- 1단계의 독립적인 호출은 `asyncio.gather`로 동시 실행합니다.
- 2단계는 1단계가 완료된 후 실행하되, 1단계 결과를 인자로 전달합니다.
- `time.perf_counter()`로 각 단계의 시작/종료 시간을 기록합니다.
- `return_exceptions=True`를 사용하여 개별 실패를 처리합니다.
- 총 소요 시간이 단계별 최대값의 합에 근접해야 합니다.

</details>

---

## 문제 2: 동기 라이브러리를 비동기로 래핑

### 설명

이미지 처리, 파일 I/O, 암호화 등 동기 라이브러리를 FastAPI의 비동기 환경에서 안전하게 사용하는 래퍼를 구현하세요.

### 요구사항

1. `AsyncExecutor` 클래스 구현:
   - I/O 바운드용 스레드풀과 CPU 바운드용 프로세스풀을 관리
   - `run_io(func, *args)`: 스레드풀에서 실행
   - `run_cpu(func, *args)`: 프로세스풀에서 실행
   - 풀 크기를 설정 가능
   - shutdown 메서드로 정리
2. 다음 동기 함수들을 비동기로 래핑:
   - 파일 읽기/쓰기 (`open().read()` 래핑)
   - 비밀번호 해싱 (PBKDF2)
   - JSON 대용량 파싱
   - 정규식 대량 매칭
3. FastAPI lifespan에서 `AsyncExecutor` 초기화/정리
4. 래핑된 함수들을 사용하는 엔드포인트 구현

### 예상 입출력

```bash
# 파일 비동기 읽기
GET /files/read?path=./test.txt
# → {"content": "파일 내용...", "size": 1234, "async": true}

# 비밀번호 해싱
POST /auth/hash
{"password": "mypassword"}
# → {"hash": "abc123...", "method": "pbkdf2", "async": true}

# 대량 JSON 파싱
POST /parse/json
# → {"parsed_items": 10000, "parse_time": "0.05초"}
```

<details>
<summary>힌트</summary>

- `ThreadPoolExecutor`와 `ProcessPoolExecutor`를 별도로 생성합니다.
- `functools.partial`로 키워드 인자를 포함한 함수 호출을 래핑합니다.
- `asyncio.get_event_loop().run_in_executor()`를 사용합니다.
- 프로세스풀에 전달하는 함수와 인자는 pickle 가능해야 합니다.
- lifespan의 yield 이후에 `executor.shutdown(wait=True)`를 호출합니다.

</details>

---

## 문제 3: 세마포어로 동시 요청 제한

### 설명

외부 API의 Rate Limit에 맞추어 동시 요청 수를 제한하는 비동기 Rate Limiter를 구현하세요.

### 요구사항

1. `AsyncRateLimiter` 클래스 구현:
   - `max_concurrent`: 최대 동시 요청 수
   - `max_per_second`: 초당 최대 요청 수
   - async context manager로 사용 가능 (`async with limiter:`)
   - 현재 상태(대기 중, 실행 중, 초당 요청 수) 조회 가능
2. 토큰 버킷(Token Bucket) 알고리즘 구현:
   - 초당 `max_per_second`개의 토큰이 생성
   - 요청 시 토큰 1개 소비
   - 토큰이 없으면 대기
3. 세마포어와 토큰 버킷을 결합하여 이중 제한
4. 10개의 요청을 동시에 보내는 테스트 엔드포인트
5. 실시간으로 Rate Limiter 상태를 확인하는 엔드포인트

### 예상 입출력

```bash
# 10개 동시 요청 (최대 동시 3개, 초당 5개)
GET /rate-limit-test?requests=10
{
  "total_requests": 10,
  "max_concurrent": 3,
  "max_per_second": 5,
  "results": [...],
  "total_time": "2.5초",
  "설명": "동시 3개 제한 + 초당 5개 제한으로 약 2초 소요"
}

# Rate Limiter 상태
GET /rate-limiter/status
{
  "concurrent": {"current": 2, "max": 3},
  "rate": {"current_rps": 4.5, "max_rps": 5},
  "waiting": 3
}
```

<details>
<summary>힌트</summary>

- `asyncio.Semaphore(max_concurrent)`로 동시 실행 수를 제한합니다.
- 토큰 버킷은 `asyncio.Queue`로 구현할 수 있습니다.
- 토큰 리필은 백그라운드 태스크(`asyncio.create_task`)로 주기적 실행합니다.
- `async with` 프로토콜은 `__aenter__`와 `__aexit__`를 구현합니다.
- `time.monotonic()`으로 초당 요청 수를 추적합니다.

</details>

---

## 문제 4: async generator를 사용한 스트리밍 응답

### 설명

대량 데이터를 점진적으로 처리하면서 결과를 실시간으로 스트리밍하는 API를 구현하세요.

### 요구사항

1. SSE(Server-Sent Events) 기반 스트리밍 엔드포인트:
   - `/stream/search`: 대량 데이터에서 키워드 검색하면서 결과를 실시간 전송
   - `/stream/transform`: 데이터를 변환하면서 진행 상황을 스트리밍
   - `/stream/aggregate`: 집계 작업을 단계별로 스트리밍
2. 각 스트리밍에서 CPU 바운드 작업은 `run_in_executor`로 처리
3. 중간 진행 상황(progress) 이벤트 포함
4. 클라이언트 연결 해제 감지 (graceful shutdown)
5. 스트리밍 도중 에러 발생 시 에러 이벤트 전송

### 예상 입출력

```bash
# 스트리밍 검색
curl -N http://localhost:8000/stream/search?keyword=python&data_size=10000
# data: {"type": "progress", "processed": 1000, "total": 10000, "matches": 5}
# data: {"type": "progress", "processed": 2000, "total": 10000, "matches": 12}
# ...
# data: {"type": "match", "item": {"id": 42, "content": "...python..."}}
# ...
# data: {"type": "complete", "total_matches": 47, "total_time": "1.23초"}

# 데이터 변환 스트리밍
curl -N http://localhost:8000/stream/transform?batch_size=100
# data: {"type": "batch", "batch_num": 1, "items_processed": 100}
# data: {"type": "batch", "batch_num": 2, "items_processed": 200}
# ...
# data: {"type": "complete", "total_processed": 1000}
```

<details>
<summary>힌트</summary>

- `StreamingResponse`와 `async generator`를 사용합니다.
- SSE 형식: `data: {json}\n\n` (줄바꿈 2개 필요)
- `media_type="text/event-stream"` 설정이 필요합니다.
- CPU 바운드 작업은 `asyncio.get_event_loop().run_in_executor()`로 오프로드합니다.
- 데이터를 배치로 나누어 각 배치 완료 시마다 진행 상황을 전송합니다.
- 에러 발생 시 `data: {"type": "error", "message": "..."}\n\n`을 전송합니다.
- `asyncio.sleep(0)`을 사용하면 CPU 집약 루프에서도 이벤트 루프에 양보할 수 있습니다.

</details>

---

## 제출 가이드

- `solution.py` 파일에 네 문제의 답안을 모두 작성하세요
- `uvicorn solution:app --reload`로 실행 가능해야 합니다
- 스트리밍 응답은 `curl -N http://localhost:8000/stream/...`로 테스트하세요
- 각 엔드포인트의 소요 시간이 예상과 일치하는지 확인하세요
