# 챕터 02 연습문제: 고급 Pydantic 패턴

---

## 문제 1: 재귀적 트리 구조 모델 설계

### 설명

파일 시스템이나 카테고리 구조처럼 재귀적인 트리 구조를 Pydantic 모델로 설계하세요.

### 요구사항

1. `TreeNode` 모델 정의:
   - `name`: 노드 이름 (문자열)
   - `node_type`: "file" 또는 "directory" (Literal 타입)
   - `size`: 파일 크기 (바이트, 파일인 경우만 필수)
   - `children`: 자식 노드 리스트 (디렉토리인 경우만)
   - `metadata`: 선택적 메타데이터 딕셔너리
2. 검증 규칙:
   - 파일 노드는 자식을 가질 수 없음
   - 디렉토리 노드는 size가 None이어야 함
   - 같은 부모 아래 중복 이름 불가
3. 트리 전체의 총 크기를 계산하는 메서드 추가
4. 트리를 들여쓰기된 문자열로 출력하는 메서드 추가

### 예상 입출력

```python
# 입력
tree_data = {
    "name": "root",
    "node_type": "directory",
    "children": [
        {"name": "docs", "node_type": "directory", "children": [
            {"name": "readme.md", "node_type": "file", "size": 1024},
            {"name": "guide.md", "node_type": "file", "size": 2048},
        ]},
        {"name": "app.py", "node_type": "file", "size": 4096},
    ]
}

tree = TreeNode.model_validate(tree_data)
print(tree.total_size())    # → 7168
print(tree.to_tree_string())
# root/
#   docs/
#     readme.md (1024 bytes)
#     guide.md (2048 bytes)
#   app.py (4096 bytes)
```

<details>
<summary>힌트</summary>

- Pydantic v2에서 재귀 모델은 `model_rebuild()`를 호출해야 할 수 있습니다.
- `from __future__ import annotations`를 사용하면 전방 참조가 자동 처리됩니다.
- `@model_validator(mode="after")`에서 node_type에 따른 일관성을 검증합니다.
- 총 크기 계산은 재귀 메서드로 구현하세요.

</details>

---

## 문제 2: 커스텀 타입과 Validator 체인

### 설명

한국 주민등록번호, 사업자등록번호, 은행 계좌번호 등 도메인 특화 타입을 Pydantic의 커스텀 타입으로 구현하세요.

### 요구사항

1. `KoreanPhoneNumber` 타입:
   - 다양한 형식 허용 (010-1234-5678, 01012345678, +82-10-1234-5678)
   - 정규화된 형식(010-XXXX-XXXX)으로 저장
   - JSON Schema에 pattern 제약 반영
2. `BusinessRegistrationNumber` 타입:
   - 형식: XXX-XX-XXXXX (10자리)
   - 체크 디지트 검증 알고리즘 구현
3. `Money` 타입:
   - 통화 코드(KRW, USD 등)와 금액을 함께 관리
   - 음수 금액 불허
   - 직렬화 시 "1,000 KRW" 형식
4. 위 타입들을 사용하는 `BusinessProfile` 모델 정의

### 예상 입출력

```python
profile = BusinessProfile(
    company_name="테스트 회사",
    business_number="123-45-67890",
    phone="01012345678",
    capital={"amount": 50000000, "currency": "KRW"},
)
print(profile.model_dump())
# {
#   "company_name": "테스트 회사",
#   "business_number": "123-45-67890",
#   "phone": "010-1234-5678",
#   "capital": "50,000,000 KRW"
# }
```

<details>
<summary>힌트</summary>

- `Annotated[str, ...]`과 `BeforeValidator`, `AfterValidator`를 조합하여 커스텀 타입을 만듭니다.
- `__get_pydantic_core_schema__` 클래스 메서드로 CoreSchema를 직접 정의할 수도 있습니다.
- 사업자등록번호 체크 디지트: 가중치 [1,3,7,1,3,7,1,3,5]를 곱한 합의 검증
- `PlainSerializer`로 직렬화 형태를 커스터마이징합니다.

</details>

---

## 문제 3: 제네릭 페이지네이션 응답 모델

### 설명

커서 기반(Cursor-based)과 오프셋 기반(Offset-based) 두 가지 페이지네이션 전략을 지원하는 제네릭 응답 모델을 설계하세요.

### 요구사항

1. `OffsetPagination[T]` 모델:
   - items, total, page, page_size, total_pages, has_next, has_prev
   - 자동 계산 validator (total_pages, has_next, has_prev)
2. `CursorPagination[T]` 모델:
   - items, cursor (현재 커서), next_cursor, prev_cursor, has_more, page_size
3. 판별 합집합으로 두 가지 페이지네이션을 통합:
   - `PaginatedResult[T]` = OffsetPagination[T] | CursorPagination[T]
   - pagination_type 필드로 판별
4. FastAPI 엔드포인트에서 쿼리 파라미터로 페이지네이션 방식 선택
5. 각 모델에 팩토리 클래스 메서드 제공 (`from_queryset` 등)

### 예상 입출력

```bash
# 오프셋 기반
GET /items?pagination=offset&page=2&size=10
{
  "pagination_type": "offset",
  "items": [...],
  "total": 100,
  "page": 2,
  "page_size": 10,
  "total_pages": 10,
  "has_next": true,
  "has_prev": true
}

# 커서 기반
GET /items?pagination=cursor&cursor=abc123&size=10
{
  "pagination_type": "cursor",
  "items": [...],
  "cursor": "abc123",
  "next_cursor": "def456",
  "prev_cursor": null,
  "has_more": true,
  "page_size": 10
}
```

<details>
<summary>힌트</summary>

- `TypeVar("T")`와 `Generic[T]`로 제네릭 모델을 정의합니다.
- 판별 합집합을 제네릭과 함께 사용할 때는 구체적 타입으로 인스턴스화해야 합니다.
- 오프셋 페이지네이션에서 `total_pages`는 `@model_validator`에서 자동 계산할 수 있습니다.
- 커서는 보통 base64로 인코딩된 정렬 키입니다.
- `@classmethod`로 팩토리 메서드를 제공하면 사용이 편리합니다.

</details>

---

## 문제 4: Pydantic 직렬화 성능 비교

### 설명

다양한 Pydantic 직렬화/역직렬화 방법의 성능을 측정하고 비교하는 벤치마크를 작성하세요.

### 요구사항

1. 테스트용 복잡한 모델 정의 (중첩 모델, 리스트, 선택적 필드 포함)
2. 다음 방법들의 성능을 각각 10,000회 측정:
   - `Model(**data)` (생성자)
   - `Model.model_validate(data)` (딕셔너리 검증)
   - `Model.model_validate_json(json_bytes)` (JSON 직접 검증)
   - `Model.model_construct(**data)` (검증 건너뛰기)
   - `TypeAdapter.validate_python(data)` (TypeAdapter 사용)
3. 직렬화 성능도 비교:
   - `model.model_dump()`
   - `model.model_dump_json()`
   - `model.model_dump(exclude_none=True)`
4. 결과를 표 형태로 출력
5. FastAPI 엔드포인트로 벤치마크 실행 가능

### 예상 입출력

```bash
GET /benchmark?iterations=10000
{
  "역직렬화": {
    "Model(**data)": "0.1234초 (기준)",
    "model_validate": "0.1200초 (1.03배)",
    "model_validate_json": "0.0800초 (1.54배)",
    "model_construct": "0.0200초 (6.17배)",
    "TypeAdapter": "0.1100초 (1.12배)"
  },
  "직렬화": {
    "model_dump": "0.0900초 (기준)",
    "model_dump_json": "0.0700초 (1.29배)",
    "model_dump(exclude_none)": "0.1000초 (0.90배)"
  }
}
```

<details>
<summary>힌트</summary>

- `time.perf_counter()`로 정밀 시간 측정을 합니다.
- `model_construct`는 검증을 건너뛰므로 가장 빠르지만, 외부 입력에는 사용 금지입니다.
- `model_validate_json`은 Rust에서 JSON 파싱과 검증을 동시에 수행하므로 빠릅니다.
- GC(가비지 컬렉션)의 영향을 최소화하려면 `gc.disable()`을 고려하세요.
- 워밍업 실행을 먼저 수행하면 더 정확한 결과를 얻을 수 있습니다.

</details>

---

## 제출 가이드

- `solution.py` 파일에 네 문제의 답안을 모두 작성하세요
- 각 문제의 답안은 섹션별로 명확히 구분하세요
- `uvicorn solution:app --reload` 명령으로 실행 가능해야 합니다
- 벤치마크 결과는 API 엔드포인트로 확인할 수 있어야 합니다
