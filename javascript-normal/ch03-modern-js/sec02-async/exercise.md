# 섹션 02 연습 문제: 비동기 프로그래밍

> **관련 개념**: `concept.md` 참조
> **코드 템플릿**: `exercise.js`
> **모범 답안**: `solution.js` 참조

---

## 문제 1: delay 함수 (⭐⭐)

### 설명
지정된 밀리초 후에 resolve되는 Promise를 반환하는 함수를 작성하세요.

### 요구 사항
- `setTimeout`과 `Promise`를 사용합니다
- 지정된 시간 후 전달된 값으로 resolve합니다

### 힌트
<details>
<summary>힌트 보기</summary>

- `new Promise((resolve) => setTimeout(() => resolve(value), ms))`

</details>

---

## 문제 2: 순차 실행 (⭐⭐)

### 설명
비동기 함수 배열을 순서대로 실행하고 결과를 배열로 반환하세요.

### 요구 사항
- async/await를 사용합니다
- 각 함수는 이전 함수가 완료된 후 실행됩니다
- 모든 결과를 배열로 반환합니다

### 힌트
<details>
<summary>힌트 보기</summary>

- `for...of`로 순회하며 각 함수를 `await`합니다

</details>

---

## 문제 3: 에러 처리가 포함된 fetch (⭐⭐⭐)

### 설명
여러 URL에서 데이터를 가져오되, 실패한 요청은 null로 처리하세요.

### 요구 사항
- 각 요청은 독립적으로 에러 처리합니다
- 하나가 실패해도 나머지는 정상 반환합니다
- Promise.all을 활용합니다

### 힌트
<details>
<summary>힌트 보기</summary>

- 각 fetch를 try/catch로 감싸서 실패 시 null을 반환합니다
- `Promise.all([safeFetch(url1), safeFetch(url2)])`

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

---

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요.
> 모범 답안은 `solution.js`에 있지만, 먼저 스스로 풀어보는 것을 권장합니다.
