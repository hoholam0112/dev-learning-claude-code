# 섹션 01: API 연동 - 연습문제

## 실행 방법

```bash
node exercise.jsx
```

## 문제 목록

### 문제 1: 데이터 페칭 상태 관리 (기본)

API 호출의 상태(대기, 로딩, 성공, 에러)를 관리하는 `createFetchState()` 함수를 구현하세요.

**요구사항:**
- 초기 상태: `{ status: "idle", data: null, error: null }`
- `getState()`: 현재 상태 객체를 반환
- `startLoading()`: status를 "loading"으로 변경, data와 error를 null로 초기화
- `setData(data)`: status를 "success"로 변경, data를 저장, error를 null로 초기화
- `setError(error)`: status를 "error"로 변경, error를 저장, data를 null로 초기화

**힌트:**
- 클로저를 사용하여 내부 상태를 관리하세요
- 각 메서드에서 상태를 통째로 교체하면 일관성을 유지할 수 있습니다

---

### 문제 2: 비동기 데이터 페칭 (중급)

비동기 함수를 실행하고 결과를 상태 객체로 반환하는 `executeFetch(fetchFn)` 함수를 구현하세요.

**요구사항:**
- `fetchFn`이 성공하면 `{ status: "success", data: 결과값, error: null }` 반환
- `fetchFn`이 실패하면 `{ status: "error", data: null, error: 에러메시지 }` 반환
- `fetchFn`은 `async` 함수이며, 직접 호출하면 됩니다

**힌트:**
- try/catch를 사용하세요
- 에러 객체의 `message` 속성을 사용하세요

---

### 문제 3: 데이터 표시 로직 (기본)

상태 객체를 받아서 화면에 표시할 문자열을 반환하는 `renderFetchResult(state)` 함수를 구현하세요.

**요구사항:**
- `status === "idle"` → `"대기 중"` 반환
- `status === "loading"` → `"로딩 중..."` 반환
- `status === "error"` → `"오류: {error 메시지}"` 반환
- `status === "success"`, data가 빈 배열 → `"데이터가 없습니다"` 반환
- `status === "success"`, data가 있음 → `"총 {N}건의 데이터"` 반환

**힌트:**
- switch 문 또는 if/else를 사용하세요
- 빈 배열 확인: `Array.isArray(data) && data.length === 0`

---

## 기대 출력

```
=== 문제 1: 페칭 상태 관리 테스트 ===
문제 1: 모든 테스트 통과!

=== 문제 2: 비동기 페칭 테스트 ===
문제 2: 모든 테스트 통과!

=== 문제 3: 데이터 표시 테스트 ===
문제 3: 모든 테스트 통과!

🎉 모든 테스트를 통과했습니다!
```
