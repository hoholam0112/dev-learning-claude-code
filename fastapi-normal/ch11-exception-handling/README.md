# 챕터 11: 예외 처리 (Exception Handling)

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: Ch04, Ch05, Ch06 완료, Ch10 권장
> **예상 학습 시간**: 3~4시간

---

## 개요

웹 API에서 에러는 피할 수 없습니다. 중요한 것은 에러가 **어떻게 처리되고, 어떤 형태로 클라이언트에 전달되는가**입니다.
이 챕터에서는 애플리케이션 수준의 **예외 처리 아키텍처**를 설계하는 방법을 학습합니다.

### ch04-sec03과의 차이점

| 항목 | Ch04 (기본) | Ch11 (고급) |
|------|------------|------------|
| 범위 | `HTTPException` 사용법 | 애플리케이션 에러 아키텍처 |
| 예외 클래스 | FastAPI 기본 제공 | 커스텀 예외 계층 구조 |
| 에러 응답 | `detail` 문자열 | 구조화된 `ErrorResponse` 모델 |
| 핸들링 | 엔드포인트별 개별 처리 | 전역 핸들러 + 미들웨어 |
| 추적성 | 없음 | `trace_id` 기반 에러 추적 |

### 에러 처리 아키텍처

```
클라이언트 요청
    │
    ▼
┌──────────────────────┐
│  에러 캐칭 미들웨어     │ ← 3번째 방어선 (최외곽)
│  (trace_id 부여, 로깅) │
└──────┬───────────────┘
       ▼
┌──────────────────────┐
│  전역 예외 핸들러       │ ← 2번째 방어선
│  (AppException,       │
│   ValidationError,    │
│   catch-all)          │
└──────┬───────────────┘
       ▼
┌──────────────────────┐
│  엔드포인트 함수        │ ← 1번째 방어선 (비즈니스 로직)
│  (도메인 예외 발생)     │
└──────┬───────────────┘
       ▼
구조화된 에러 응답 반환
```

---

## 섹션 목록

| 섹션 | 제목 | 난이도 | 핵심 내용 |
|------|------|--------|----------|
| sec01 | [예외 계층 구조](./sec01-exception-hierarchy/concept.md) | ⭐⭐⭐ (3/5) | `AppException` 기반 클래스, 도메인별 예외, 에러 코드 Enum |
| sec02 | [전역 에러 핸들러](./sec02-global-error-handlers/concept.md) | ⭐⭐⭐ (3/5) | 표준 `ErrorResponse`, 전역 핸들러, `ValidationError` 변환 |
| sec03 | [에러 미들웨어](./sec03-error-middleware/concept.md) | ⭐⭐⭐ (3/5) | 에러 캐칭 미들웨어, `trace_id` 전파, 다중 방어선 |

---

## 학습 순서

```
sec01-exception-hierarchy → sec02-global-error-handlers → sec03-error-middleware
```

1. **sec01**: 커스텀 예외 계층 구조를 설계하고 도메인별 예외 클래스를 구현합니다.
2. **sec02**: 전역 핸들러를 등록하여 모든 에러가 일관된 형식으로 반환되게 만듭니다.
3. **sec03**: 미들웨어를 활용하여 `trace_id` 추적과 에러 로깅을 구현합니다.

각 섹션에서:
1. `concept.md`를 읽고 개념을 이해합니다.
2. `exercise.md`의 문제를 확인합니다.
3. `exercise.py`에서 TODO를 완성합니다.
4. `python exercise.py`로 테스트를 실행합니다.
5. 막히면 `solution.py`를 참고합니다.

---

## 사전 준비

```bash
# 필요한 패키지 설치 (FastAPI, Uvicorn은 이미 설치되어 있어야 합니다)
pip install fastapi uvicorn
```

> 이 챕터는 추가 외부 패키지 없이 FastAPI/Starlette/Pydantic만으로 구현됩니다.

---

## 이 챕터를 마치면 할 수 있는 것

- `AppException` 기반의 커스텀 예외 계층 구조를 설계할 수 있다
- 도메인별 예외 클래스(`NotFoundException`, `DuplicateError` 등)를 구현할 수 있다
- `ErrorCode` Enum을 사용하여 에러 코드를 체계적으로 관리할 수 있다
- `app.exception_handler()`를 사용하여 전역 에러 핸들러를 등록할 수 있다
- `RequestValidationError`를 커스텀 핸들러로 변환할 수 있다
- 모든 에러가 일관된 `ErrorResponse` 형식으로 반환되도록 구성할 수 있다
- `trace_id`를 생성하여 에러 응답과 로그에 전파할 수 있다
- 미들웨어 → 전역 핸들러 → 엔드포인트의 다중 방어선 아키텍처를 이해하고 구현할 수 있다
