# 챕터 09: 비동기 프로그래밍 (Async Programming)

> **난이도**: ⭐⭐ ~ ⭐⭐⭐ (2~3/5) | **예상 학습 시간**: 3~4시간

---

## 개요

이 챕터에서는 FastAPI의 핵심 강점인 **비동기 프로그래밍(Async Programming)**을 학습합니다.
FastAPI는 Python의 `async`/`await` 문법을 기반으로 설계되어, 높은 동시성을 지원하는 고성능 API를 구축할 수 있습니다.
비동기 프로그래밍의 기본 개념부터 동시 실행, 백그라운드 작업까지 실전에서 필요한 패턴을 다룹니다.

---

## 왜 비동기 프로그래밍인가?

### 1. 높은 동시성 (High Concurrency)
- 동기 방식에서는 I/O 작업(DB 조회, 외부 API 호출) 중 스레드가 **대기 상태**에 놓입니다.
- 비동기 방식에서는 I/O 대기 시간에 **다른 요청을 처리**할 수 있어 처리량이 비약적으로 증가합니다.
- 같은 서버 자원으로 더 많은 동시 요청을 처리할 수 있습니다.

### 2. 리소스 효율성 (Resource Efficiency)
- 스레드 기반 동시성은 메모리 사용량이 높고 컨텍스트 전환 비용이 큽니다.
- 비동기 방식은 단일 스레드 이벤트 루프로 수천 개의 동시 연결을 처리할 수 있습니다.
- 서버 비용을 절감하면서 성능을 극대화할 수 있습니다.

### 3. FastAPI와의 시너지
- FastAPI는 내부적으로 **Starlette** + **uvicorn(ASGI 서버)**를 사용합니다.
- `async def`로 정의한 엔드포인트는 이벤트 루프에서 직접 실행됩니다.
- 일반 `def`로 정의한 엔드포인트는 자동으로 스레드 풀에서 실행됩니다.

```
동기 처리 vs 비동기 처리:

[동기] 요청1 처리 ████████ 완료 → 요청2 처리 ████████ 완료 → 요청3 처리 ████████ 완료
       (대기...)           (대기...)           (대기...)

[비동기] 요청1 시작 ██        요청1 완료 ██
         요청2 시작   ██      요청2 완료   ██
         요청3 시작     ██    요청3 완료     ██
         (I/O 대기 중 다른 요청 처리!)
```

---

## 포함된 섹션

| 섹션 | 제목 | 핵심 내용 |
|------|------|-----------|
| [sec01-async-await-basics](./sec01-async-await-basics/) | async/await 기본 | async def vs def, asyncio.sleep, 이벤트 루프 |
| [sec02-async-io-operations](./sec02-async-io-operations/) | 비동기 I/O 작업 | asyncio.gather, 동시 실행, 순차 vs 동시 비교 |
| [sec03-background-tasks](./sec03-background-tasks/) | 백그라운드 작업 | BackgroundTasks, 응답 후 처리, 의존성 연계 |

---

## 학습 순서

```
sec01-async-await-basics → sec02-async-io-operations → sec03-background-tasks
```

1. **sec01**: `async`/`await`의 기본 문법과 FastAPI에서의 동작 차이를 이해합니다.
2. **sec02**: `asyncio.gather`를 활용한 동시 실행과 성능 최적화를 배웁니다.
3. **sec03**: `BackgroundTasks`를 사용하여 응답 후 실행되는 작업을 구현합니다.

각 섹션에서:
1. `concept.md`를 읽고 개념을 이해합니다.
2. `exercise.md`의 문제를 확인합니다.
3. `exercise.py`에서 TODO를 완성합니다.
4. `python exercise.py`로 테스트를 실행합니다.
5. 막히면 `solution.py`를 참고합니다.

---

## 사전 준비

- **Ch05 (의존성 주입)** 챕터를 완료해야 합니다.
- Python 3.10 이상을 권장합니다.
- `asyncio` 모듈은 Python 표준 라이브러리에 포함되어 있어 별도 설치가 필요 없습니다.

```bash
# 필요한 패키지 설치
pip install "fastapi[standard]"
```

---

## 이 챕터를 마치면

- `async def`와 `def`의 차이를 FastAPI 맥락에서 설명할 수 있습니다.
- `asyncio.sleep`과 `time.sleep`의 차이를 이해하고 올바르게 사용할 수 있습니다.
- `asyncio.gather`를 활용하여 여러 비동기 작업을 동시에 실행할 수 있습니다.
- 순차 실행과 동시 실행의 성능 차이를 측정하고 비교할 수 있습니다.
- `BackgroundTasks`를 사용하여 응답 후 실행되는 작업을 구현할 수 있습니다.
- 의존성에서 백그라운드 작업을 추가하는 패턴을 활용할 수 있습니다.
