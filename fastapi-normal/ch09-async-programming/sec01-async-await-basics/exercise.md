# 연습 문제: async/await 기본

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: async def와 def 엔드포인트 비교

`async def`와 `def`로 각각 엔드포인트를 작성하여 두 방식의 차이를 체감해보세요.

### 요구 사항

1. `GET /sync` 엔드포인트 (동기)
   - 일반 `def`로 정의
   - `{"message": "동기 응답", "type": "sync"}`를 반환

2. `GET /async` 엔드포인트 (비동기)
   - `async def`로 정의
   - `await asyncio.sleep(0)`을 호출하여 비동기 동작을 시연
   - `{"message": "비동기 응답", "type": "async"}`를 반환

### 힌트

- 동기 엔드포인트: `@app.get("/sync")` + `def sync_endpoint():`
- 비동기 엔드포인트: `@app.get("/async")` + `async def async_endpoint():`
- `asyncio.sleep(0)`은 이벤트 루프에 제어권을 양보하는 가장 간단한 방법

---

## 문제 2: 비동기 데이터 처리

여러 아이템을 비동기적으로 처리하는 엔드포인트를 작성하세요.

### 요구 사항

1. `process_item(item: str)` 비동기 헬퍼 함수
   - `await asyncio.sleep(0.1)`으로 I/O 작업을 시뮬레이션
   - `{"item": item, "status": "processed"}`를 반환

2. `GET /process` 엔드포인트 (비동기)
   - `items = ["아이템A", "아이템B", "아이템C"]` 리스트를 처리
   - `asyncio.gather`를 사용하여 모든 아이템을 **동시에** 처리
   - `time.time()`으로 처리 시간을 측정
   - 반환 형식:
     ```json
     {
       "results": [처리된 아이템 목록],
       "elapsed_seconds": 소요 시간 (소수점 2자리)
     }
     ```

### 힌트

- `asyncio.gather(*[process_item(item) for item in items])`
- 3개 아이템이 동시에 처리되므로 약 0.1초가 소요됩니다 (0.3초가 아닌)
- `round(elapsed, 2)`로 소수점 2자리까지 반올림

---

## 테스트 기대 결과

```
문제 1: async def와 def 엔드포인트 비교
  [통과] 동기 엔드포인트 - 200 응답
  [통과] 비동기 엔드포인트 - 200 응답

문제 2: 비동기 데이터 처리
  [통과] 3개 아이템 처리 완료
  [통과] 동시 처리로 0.5초 이내 완료

모든 테스트를 통과했습니다!
```
