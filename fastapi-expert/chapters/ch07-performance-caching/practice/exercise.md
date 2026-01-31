# 챕터 07 연습문제: 성능 최적화와 캐싱

---

## 문제 1: 캐시 무효화 전략 구현 (TTL + 이벤트 기반)

### 설명

TTL 기반 자동 만료와 이벤트 기반 즉시 무효화를 결합한 하이브리드 캐싱 시스템을 구현하세요. 데이터 변경 시 관련 캐시를 자동으로 무효화하는 이벤트 시스템을 포함합니다.

### 요구사항

1. `CacheManager` 클래스:
   - `get(key)`: 캐시 조회 (TTL 만료 검사 포함)
   - `set(key, value, ttl)`: 캐시 저장 (TTL 지원)
   - `invalidate(key)`: 단일 키 무효화
   - `invalidate_by_tag(tag)`: 태그 기반 일괄 무효화
   - `tag(key, *tags)`: 키에 태그 연결

2. `CacheEvent` 시스템:
   - `on_create(resource_type)`: 생성 이벤트 -> 목록 캐시 무효화
   - `on_update(resource_type, resource_id)`: 수정 이벤트 -> 단건 + 목록 캐시 무효화
   - `on_delete(resource_type, resource_id)`: 삭제 이벤트 -> 단건 + 목록 캐시 무효화

3. 캐시 통계:
   - 히트/미스 횟수
   - 평균 응답 시간 (캐시 히트 vs 미스)
   - 무효화 횟수

### 예상 입출력

```python
cache = CacheManager(default_ttl=300)

# 태그 기반 캐싱
await cache.set("items:list:1", data, ttl=60)
await cache.tag("items:list:1", "items", "items:list")

await cache.set("items:42", item_data, ttl=120)
await cache.tag("items:42", "items", "items:detail")

# 새 항목 생성 -> 목록 캐시 무효화
await cache.invalidate_by_tag("items:list")
# items:list:1 삭제됨, items:42는 유지됨

# 통계
stats = cache.get_stats()
# {"hits": 150, "misses": 30, "hit_rate": 83.3, "invalidations": 5}
```

<details>
<summary>힌트</summary>

- 태그와 키의 매핑을 별도 딕셔너리로 관리하세요: `{tag: set(keys)}`
- 키와 태그의 역매핑도 필요합니다: `{key: set(tags)}`
- `time.monotonic()`을 사용하면 시스템 시간 변경에 영향 받지 않습니다
- 이벤트 시스템은 함수 리스트를 관리하는 간단한 옵저버 패턴으로 구현하세요

</details>

---

## 문제 2: API 응답 시간 프로파일링과 최적화

### 설명

각 엔드포인트의 응답 시간을 자동으로 프로파일링하고, 느린 엔드포인트를 감지하여 경고하는 시스템을 구현하세요. 성능 통계를 실시간으로 조회할 수 있는 대시보드 엔드포인트도 포함합니다.

### 요구사항

1. `ProfilingMiddleware`:
   - 모든 요청의 응답 시간 기록
   - 엔드포인트별 통계: 평균, 최소, 최대, p50, p95, p99
   - 느린 요청 감지 (임계값 초과 시 WARNING 로그)
   - 응답 헤더에 `X-Response-Time` 추가

2. `/metrics` 엔드포인트:
   - 전체 엔드포인트별 성능 통계
   - 가장 느린 엔드포인트 Top 5
   - 초당 요청 수 (RPS)

3. 의도적으로 느린 엔드포인트 3개를 만들어 프로파일링 테스트:
   - `/slow/db-query`: 느린 DB 쿼리 시뮬레이션 (200ms)
   - `/slow/serialization`: 대용량 직렬화 (100ms)
   - `/slow/external-api`: 외부 API 호출 시뮬레이션 (500ms)

### 예상 입출력

```json
GET /metrics
{
  "endpoints": {
    "GET /items": {
      "count": 1500,
      "avg_ms": 12.3,
      "min_ms": 2.1,
      "max_ms": 89.5,
      "p50_ms": 10.2,
      "p95_ms": 35.7,
      "p99_ms": 78.1
    },
    "GET /slow/db-query": {
      "count": 50,
      "avg_ms": 215.8,
      ...
    }
  },
  "top_5_slowest": [
    {"endpoint": "GET /slow/external-api", "avg_ms": 512.3},
    ...
  ],
  "rps": 125.7
}
```

<details>
<summary>힌트</summary>

- 백분위수(percentile) 계산: `sorted_times[int(len(times) * 0.95)]`
- `collections.defaultdict(list)`로 엔드포인트별 응답 시간을 누적하세요
- 메모리 절약을 위해 최근 N건만 유지하세요 (`collections.deque(maxlen=1000)`)
- RPS 계산: 총 요청 수 / 경과 시간

</details>

---

## 문제 3: 대용량 CSV 스트리밍 다운로드 구현

### 설명

데이터베이스에서 대량의 데이터를 조회하여 CSV로 변환하면서 스트리밍 다운로드하는 시스템을 구현하세요. 메모리 사용량을 일정하게 유지하면서 수백만 건의 데이터를 처리할 수 있어야 합니다.

### 요구사항

1. `StreamingCSVExporter` 클래스:
   - 배치 단위로 DB 조회 (batch_size=1000)
   - CSV 행을 생성하면서 즉시 전송
   - UTF-8 BOM 포함 (Excel 호환)
   - 진행 상태를 로깅 (10% 단위)

2. 지원 형식:
   - CSV (기본)
   - TSV (탭 구분)
   - 사용자 정의 구분자

3. 엔드포인트:
   - `GET /export/orders?format=csv&start_date=2024-01-01&end_date=2024-12-31`
   - `GET /export/orders/count?start_date=...`: 총 건수 조회 (다운로드 전 확인)

4. 100만 건 테스트 시 메모리 사용량이 50MB를 초과하지 않아야 합니다

### 예상 입출력

```bash
# 총 건수 확인
curl http://localhost:8000/export/orders/count?year=2024
# {"count": 1250000, "estimated_size_mb": 145.2}

# CSV 다운로드
curl -o orders.csv http://localhost:8000/export/orders?format=csv&year=2024
# 파일 다운로드 완료 (145MB, 1,250,001행)

# 서버 로그
# [INFO] CSV 내보내기 시작: 총 1,250,000건
# [INFO] 진행: 10% (125,000/1,250,000)
# [INFO] 진행: 20% (250,000/1,250,000)
# ...
# [INFO] CSV 내보내기 완료: 1,250,000건, 소요 시간 12.3초
```

<details>
<summary>힌트</summary>

- UTF-8 BOM: `b'\xef\xbb\xbf'`를 첫 청크에 포함하세요
- `asyncio.sleep(0)`을 주기적으로 호출하여 이벤트 루프 차단을 방지하세요
- 배치 조회 시 `offset`보다 `WHERE id > last_id`가 대용량에서 더 효율적입니다 (커서 기반 페이징)
- 메모리 절약을 위해 각 배치 처리 후 참조를 해제하세요
- Content-Disposition 헤더에 파일명을 포함하여 브라우저 다운로드를 유도하세요

</details>

---

## 제출 기준

- 모든 코드가 비동기로 작성되어야 합니다
- StreamingResponse를 사용하여 메모리 효율적이어야 합니다
- 캐시 히트율, 응답 시간 등 성능 지표를 확인할 수 있어야 합니다
- `# 실행 방법:` 주석이 첫 줄에 포함되어야 합니다
