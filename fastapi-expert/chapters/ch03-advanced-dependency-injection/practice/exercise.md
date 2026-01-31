# 챕터 03 연습문제: 고급 의존성 주입과 생명주기

---

## 문제 1: 커넥션 풀 의존성 (yield + 에러 처리)

### 설명

비동기 커넥션 풀을 구현하고, yield 의존성으로 안전하게 연결을 관리하는 시스템을 만드세요.

### 요구사항

1. `AsyncConnectionPool` 클래스 구현:
   - `max_size`: 최대 연결 수
   - `acquire()`: 연결 획득 (풀이 가득 차면 대기, 타임아웃 5초)
   - `release()`: 연결 반환
   - `health_check()`: 모든 연결의 상태 확인
   - `stats`: 현재 상태 (총 연결, 사용 중, 대기 중, 대기 큐 길이)
2. yield 의존성 `get_connection()`:
   - 풀에서 연결을 획득하여 yield
   - 예외 발생 시 자동으로 연결의 진행 중인 작업을 롤백
   - 정상/비정상 모두 연결을 풀에 반환
   - 연결 상태가 비정상이면 새 연결로 교체 후 반환
3. 동시 요청 처리 테스트:
   - `asyncio.Semaphore` 없이 풀 크기만으로 동시성 제한
   - 풀이 가득 찼을 때의 대기 동작 확인
4. 에러 시나리오 테스트 엔드포인트:
   - `/success`: 정상 쿼리 후 연결 반환
   - `/error`: 쿼리 중 에러 발생 후 연결 반환 확인
   - `/timeout`: 연결 획득 타임아웃 시뮬레이션

### 예상 입출력

```bash
# 정상 동작
curl http://localhost:8000/success
# → {"result": "ok", "connection_id": 1}

# 에러 후 복구
curl http://localhost:8000/error
# → {"error": "쿼리 실행 실패", "connection_returned": true}

# 풀 상태
curl http://localhost:8000/pool/stats
# → {"total": 5, "available": 4, "in_use": 1, "waiting": 0}
```

<details>
<summary>힌트</summary>

- `asyncio.Queue`를 사용하면 풀의 가용 연결을 관리하기 좋습니다.
- `asyncio.wait_for(queue.get(), timeout=5.0)`으로 타임아웃을 구현합니다.
- yield 의존성의 `finally` 블록에서 연결 상태를 확인한 후 반환합니다.
- 연결이 비정상 상태면 새 연결을 생성하여 풀에 반환합니다.
- `@app.get("/concurrent-test")`에서 `asyncio.gather`로 동시 쿼리를 테스트합니다.

</details>

---

## 문제 2: lifespan으로 공유 리소스 초기화/정리

### 설명

lifespan 이벤트를 활용하여 여러 종류의 공유 리소스를 관리하는 시스템을 만드세요.

### 요구사항

1. lifespan에서 다음 리소스를 초기화/정리:
   - DB 커넥션 풀
   - 캐시 클라이언트 (시뮬레이션)
   - 백그라운드 태스크 스케줄러 (주기적 정리 작업)
   - 설정 파일 로더 (환경 변수 기반)
2. `app.state`에 모든 리소스를 저장
3. 리소스 간 의존 관계 관리:
   - 설정 → DB 풀 (설정이 먼저 로드되어야 함)
   - 설정 → 캐시 클라이언트
   - DB 풀 + 캐시 → 백그라운드 스케줄러
4. 종료 시 역순으로 리소스 정리
5. 초기화 실패 시 이미 생성된 리소스도 정리 (부분 실패 처리)
6. 헬스체크 엔드포인트 (`/health`):
   - 모든 리소스의 상태를 확인
   - 하나라도 비정상이면 503 응답

### 예상 입출력

```bash
# 서버 시작 시 콘솔:
# [lifespan] 설정 로드 완료
# [lifespan] DB 풀 초기화 완료 (5개 연결)
# [lifespan] 캐시 연결 완료
# [lifespan] 스케줄러 시작 (정리 주기: 60초)
# [lifespan] 모든 리소스 준비 완료!

# 헬스체크
curl http://localhost:8000/health
# → {"status": "healthy", "resources": {"db": "ok", "cache": "ok", "scheduler": "running"}}

# 서버 종료 시:
# [lifespan] 스케줄러 중지
# [lifespan] 캐시 연결 해제
# [lifespan] DB 풀 종료
# [lifespan] 모든 리소스 정리 완료
```

<details>
<summary>힌트</summary>

- `@asynccontextmanager`로 lifespan을 정의합니다.
- 리소스 초기화 순서와 정리 순서가 역순이 되도록 합니다.
- 부분 실패 처리: `try/except`로 각 리소스의 초기화를 감싸고, 실패 시 이미 초기화된 것들을 정리합니다.
- 백그라운드 스케줄러는 `asyncio.create_task`로 만들고, `task.cancel()`로 정리합니다.
- `app.state`의 속성으로 리소스에 접근합니다.

</details>

---

## 문제 3: 의존성 오버라이드를 활용한 테스트 격리

### 설명

의존성 오버라이드를 활용하여 완전히 격리된 테스트 환경을 구축하세요.

### 요구사항

1. 프로덕션 의존성:
   - `get_db()`: 실제 데이터베이스 세션
   - `get_current_user()`: JWT 토큰에서 사용자 추출
   - `get_email_service()`: 실제 이메일 전송
   - `get_settings()`: 환경 변수에서 설정 로드
2. 테스트용 오버라이드 의존성:
   - `get_test_db()`: 인메모리 딕셔너리 기반 DB
   - `get_mock_user()`: 고정된 테스트 사용자 반환
   - `get_mock_email()`: 이메일 전송 기록만 저장 (실제 전송 안 함)
   - `get_test_settings()`: 테스트 전용 설정
3. pytest 픽스처로 구현:
   - `@pytest.fixture`로 테스트 클라이언트 생성
   - 테스트 간 데이터 격리 보장
   - 테스트 종료 후 오버라이드 자동 정리
4. 다음 테스트 시나리오 구현:
   - 사용자 생성 → 조회 테스트
   - 인증 필요 엔드포인트 테스트 (모의 사용자)
   - 이메일 전송 확인 (실제 전송 없이)
   - 에러 케이스 테스트

### 예상 입출력

```python
# 테스트 실행: pytest solution.py -v
# test_create_user PASSED
# test_get_user PASSED
# test_protected_endpoint_with_auth PASSED
# test_protected_endpoint_without_auth PASSED
# test_email_sent_on_registration PASSED
# test_data_isolation_between_tests PASSED
```

<details>
<summary>힌트</summary>

- `app.dependency_overrides[원래_함수] = 대체_함수`로 의존성을 교체합니다.
- pytest의 `yield` 픽스처를 사용하면 설정/정리를 자동화할 수 있습니다.
- `TestClient`를 `with` 문으로 사용하면 lifespan 이벤트도 실행됩니다.
- 인메모리 DB는 `dict`로 간단히 구현할 수 있습니다.
- 이메일 서비스 모의 객체는 전송 기록을 리스트에 저장합니다.
- 각 테스트 함수에서 데이터를 독립적으로 설정하여 격리를 보장합니다.

</details>

---

## 제출 가이드

- `solution.py` 파일에 세 문제의 답안을 모두 작성하세요
- 문제 1, 2는 `uvicorn solution:app --reload`로 실행 가능해야 합니다
- 문제 3의 테스트는 `pytest solution.py -v`로 실행 가능해야 합니다
  (또는 테스트를 별도 실행 불가능한 경우 주석으로 테스트 코드를 포함)
- 콘솔 출력으로 의존성 생명주기를 추적할 수 있어야 합니다
