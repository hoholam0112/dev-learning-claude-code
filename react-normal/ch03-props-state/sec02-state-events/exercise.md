# 섹션 02 연습 문제: State와 이벤트 처리

> **관련 개념**: `concept.md` 참조
> **코드 템플릿**: `exercise.jsx`
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: useState 시뮬레이션 (⭐⭐)

### 설명
React의 `useState` 훅을 순수 JavaScript로 시뮬레이션하세요.
`createState(initialValue)` 함수는 `[getValue, setValue]`를 반환합니다.

### 요구 사항
- `getValue()`를 호출하면 현재 상태값을 반환합니다
- `setValue(newValue)`를 호출하면 상태를 업데이트합니다
- `setValue`에 함수를 전달하면 이전 상태를 인자로 받아 새 상태를 계산합니다 (함수형 업데이트)

---

## 문제 2: 범위 제한 카운터 (⭐⭐)

### 설명
최솟값과 최댓값이 있는 카운터를 만드세요. `createCounter(min, max, initial)` 함수는 카운터 조작 메서드를 반환합니다.

### 요구 사항
- `increment()`: 1 증가 (최댓값 초과 불가)
- `decrement()`: 1 감소 (최솟값 미만 불가)
- `reset()`: 초기값으로 복원
- `getValue()`: 현재 값 반환

---

## 문제 3: Todo 리스트 상태 관리 (⭐⭐)

### 설명
Todo 리스트를 불변(immutable) 방식으로 관리하는 함수들을 만드세요.
React의 배열 상태 업데이트 패턴을 순수 JavaScript로 연습합니다.

### 요구 사항
- `addTodo(todos, text)`: 새 할일을 추가한 **새 배열** 반환
- `toggleTodo(todos, id)`: 특정 할일의 done 값을 반전한 **새 배열** 반환
- `removeTodo(todos, id)`: 특정 할일을 제거한 **새 배열** 반환
- 원본 배열을 절대 수정하지 않아야 합니다

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 불변성 유지 | 25% |
| 코드 가독성 | 15% |
| 엣지 케이스 처리 | 20% |
