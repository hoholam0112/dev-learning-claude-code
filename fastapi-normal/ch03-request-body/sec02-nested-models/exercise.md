# sec02 연습 문제: 중첩 모델

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py` (테스트) 또는 `uvicorn exercise:app --reload` (서버)

---

## 문제: 주문 생성 API

온라인 쇼핑몰의 주문 생성 API를 구현하세요.
주문은 배송 주소, 상품 목록, 결제 정보를 포함하는 중첩 구조입니다.

### 요구 사항

**Address 모델 (배송 주소):**
| 필드 | 타입 | 필수 여부 | 검증 규칙 |
|------|------|-----------|-----------|
| `city` | `str` | 필수 | 최소 1자 |
| `street` | `str` | 필수 | 최소 1자 |
| `zip_code` | `str` | 필수 | 정확히 5자 (`min_length=5`, `max_length=5`) |

**OrderItem 모델 (주문 상품):**
| 필드 | 타입 | 필수 여부 | 검증 규칙 |
|------|------|-----------|-----------|
| `product_name` | `str` | 필수 | 최소 1자 |
| `quantity` | `int` | 필수 | 1 이상 |
| `unit_price` | `int` | 필수 | 100 이상 (최소 금액) |

**OrderCreate 모델 (주문 생성):**
| 필드 | 타입 | 필수 여부 | 검증 규칙 |
|------|------|-----------|-----------|
| `customer_name` | `str` | 필수 | 최소 2자 |
| `address` | `Address` | 필수 | (중첩 모델) |
| `items` | `list[OrderItem]` | 필수 | 최소 1개 |
| `note` | `Optional[str]` | 선택 | 기본값 `None`, 최대 300자 |

**POST /orders 엔드포인트:**
- `OrderCreate` 모델을 요청 본문으로 받습니다
- 총액(`total_amount`)을 계산합니다: 각 상품의 `quantity * unit_price`의 합
- 반환값:
```json
{
    "message": "주문이 생성되었습니다",
    "order": { ...받은 주문 데이터... },
    "total_amount": 계산된_총액
}
```

### 힌트

- 중첩 모델은 필드 타입에 모델 클래스를 직접 사용합니다: `address: Address`
- 모델 리스트는 `list[OrderItem]` 형태로 정의합니다
- `sum()` 함수와 제너레이터 표현식으로 총액을 계산할 수 있습니다:
  ```python
  total = sum(item.quantity * item.unit_price for item in order.items)
  ```

### 테스트 케이스

1. 정상 주문 (상품 2개) -> 200 OK, 총액 계산 확인
2. 배송 메모 포함 주문 -> 200 OK
3. 빈 상품 목록 -> 422 (최소 1개)
4. 잘못된 우편번호 -> 422 (5자리 필수)
5. 수량 0인 상품 -> 422 (1 이상 필수)

---

## 정답 확인

모든 테스트를 통과하면 완료입니다.
막히는 부분이 있다면 `solution.py`를 참고하세요.
