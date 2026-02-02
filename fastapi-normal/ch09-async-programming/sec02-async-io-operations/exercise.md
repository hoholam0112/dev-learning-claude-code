# 연습 문제: 비동기 I/O 작업

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: 동시 데이터 수집 시뮬레이션

여러 데이터 소스에서 동시에 데이터를 수집하는 시스템을 구현하세요.

### 요구 사항

1. 3개의 데이터 소스 엔드포인트 (이미 제공됨):
   - `GET /source/users` - 사용자 데이터 (0.3초 소요)
   - `GET /source/products` - 상품 데이터 (0.2초 소요)
   - `GET /source/orders` - 주문 데이터 (0.4초 소요)

2. `fetch_source(source_name: str, delay: float)` 비동기 헬퍼 함수
   - `await asyncio.sleep(delay)`로 I/O를 시뮬레이션
   - `{"source": source_name, "items": [source_name에 따른 데이터]}`를 반환
   - source_name별 데이터:
     - `"users"` → `["홍길동", "김영희", "이철수"]`
     - `"products"` → `["노트북", "마우스", "키보드"]`
     - `"orders"` → `["주문001", "주문002"]`

3. `GET /aggregate` 동시 수집 엔드포인트
   - `asyncio.gather`로 3개 소스를 **동시에** 호출
   - `time.time()`으로 소요 시간 측정
   - 반환 형식:
     ```json
     {
       "users": {"source": "users", "items": [...]},
       "products": {"source": "products", "items": [...]},
       "orders": {"source": "orders", "items": [...]},
       "elapsed_seconds": 소요 시간
     }
     ```

### 힌트

- `asyncio.gather(fetch_source("users", 0.3), fetch_source("products", 0.2), fetch_source("orders", 0.4))`
- 동시 실행이므로 가장 긴 작업(0.4초) 기준으로 약 0.4초 소요

---

## 문제 2: 비동기 배치 처리

여러 아이템을 동시에 처리하는 배치 시스템을 구현하세요.

### 요구 사항

1. `process_single_item(item_id: int)` 비동기 헬퍼 함수
   - `await asyncio.sleep(0.1)`으로 처리 시뮬레이션
   - `{"item_id": item_id, "result": f"processed_{item_id}"}`를 반환

2. `POST /batch` 배치 처리 엔드포인트
   - 요청 본문: `{"item_ids": [1, 2, 3, 4, 5]}`
   - `asyncio.gather`로 모든 아이템을 동시에 처리
   - 소요 시간 측정
   - 반환 형식:
     ```json
     {
       "results": [처리 결과 리스트],
       "total_processed": 처리된 아이템 수,
       "elapsed_seconds": 소요 시간
     }
     ```

### 힌트

- Pydantic 모델: `class BatchRequest(BaseModel): item_ids: list[int]`
- `tasks = [process_single_item(item_id) for item_id in request.item_ids]`
- `results = await asyncio.gather(*tasks)`

---

## 테스트 기대 결과

```
문제 1: 동시 데이터 수집 시뮬레이션
  [통과] 개별 소스 엔드포인트 동작 확인
  [통과] 동시 수집 완료 - 3개 소스
  [통과] 동시 실행으로 0.8초 이내 완료

문제 2: 비동기 배치 처리
  [통과] 5개 아이템 배치 처리 완료
  [통과] 동시 처리로 0.5초 이내 완료

모든 테스트를 통과했습니다!
```
