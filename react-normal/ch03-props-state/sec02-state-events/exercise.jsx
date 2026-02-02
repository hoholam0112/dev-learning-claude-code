// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: useState 시뮬레이션 =====
// React의 useState를 순수 JavaScript로 시뮬레이션합니다.
// createState(initialValue) → [getValue, setValue]
//
// getValue()는 현재 상태를 반환합니다.
// setValue(newValue)는 상태를 업데이트합니다.
// setValue(함수)를 전달하면 이전 상태를 인자로 받아 새 상태를 계산합니다 (함수형 업데이트).
//
// 예시:
//   const [getCount, setCount] = createState(0);
//   getCount()       → 0
//   setCount(5)
//   getCount()       → 5
//   setCount(prev => prev + 1)
//   getCount()       → 6

function createState(initialValue) {
  // TODO: 여기에 코드를 작성하세요
  // 클로저를 활용하여 상태를 관리합니다
}

// ===== 문제 2: 범위 제한 카운터 =====
// 최솟값과 최댓값이 있는 카운터를 만듭니다.
// createCounter(min, max, initial) → { getValue, increment, decrement, reset }
//
// increment(): 1 증가 (max를 초과하면 max에서 멈춤)
// decrement(): 1 감소 (min 미만이면 min에서 멈춤)
// reset(): initial 값으로 복원
// getValue(): 현재 값 반환
//
// 예시:
//   const counter = createCounter(0, 5, 3);
//   counter.getValue()   → 3
//   counter.increment()
//   counter.getValue()   → 4

function createCounter(min, max, initial) {
  // TODO: 여기에 코드를 작성하세요
  // createState를 활용해도 좋고, 직접 클로저를 만들어도 됩니다
}

// ===== 문제 3: Todo 리스트 상태 관리 =====
// React에서 배열 상태를 업데이트하는 패턴을 순수 JavaScript로 연습합니다.
// 원본 배열을 절대 수정하지 않고, 항상 새 배열을 반환해야 합니다.
//
// addTodo(todos, text) → 새 할일이 추가된 새 배열
//   - 새 할일 형식: { id: (현재 최대 id + 1), text, done: false }
//   - todos가 비어 있으면 id는 1부터 시작
//
// toggleTodo(todos, id) → done이 반전된 새 배열
//   - 해당 id가 없으면 원본과 동일한 새 배열 반환
//
// removeTodo(todos, id) → 해당 할일이 제거된 새 배열

function addTodo(todos, text) {
  // TODO: 여기에 코드를 작성하세요
}

function toggleTodo(todos, id) {
  // TODO: 여기에 코드를 작성하세요
}

function removeTodo(todos, id) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: useState 시뮬레이션 테스트 ===");

const [getCount, setCount] = createState(0);
console.assert(getCount() === 0, "초기값 테스트 실패");

setCount(10);
console.assert(getCount() === 10, "직접 값 설정 테스트 실패");

setCount((prev) => prev + 5);
console.assert(getCount() === 15, "함수형 업데이트 테스트 실패");

setCount((prev) => prev * 2);
console.assert(getCount() === 30, "함수형 업데이트 곱셈 테스트 실패");

// 문자열 상태 테스트
const [getName, setName] = createState("초기값");
console.assert(getName() === "초기값", "문자열 초기값 테스트 실패");
setName("변경됨");
console.assert(getName() === "변경됨", "문자열 변경 테스트 실패");

console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 범위 제한 카운터 테스트 ===");

const counter = createCounter(0, 5, 3);
console.assert(counter.getValue() === 3, "초기값 테스트 실패");

counter.increment();
console.assert(counter.getValue() === 4, "증가 테스트 실패");

counter.increment();
counter.increment();
console.assert(counter.getValue() === 5, "최댓값 제한 테스트 실패 (5를 초과하면 안 됨)");

counter.increment();
console.assert(counter.getValue() === 5, "최댓값 초과 방지 테스트 실패");

counter.decrement();
console.assert(counter.getValue() === 4, "감소 테스트 실패");

counter.reset();
console.assert(counter.getValue() === 3, "리셋 테스트 실패");

// 최솟값 테스트
const counter2 = createCounter(-2, 2, 0);
counter2.decrement();
counter2.decrement();
counter2.decrement();
console.assert(counter2.getValue() === -2, "최솟값 제한 테스트 실패");

console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: Todo 리스트 테스트 ===");

// 추가 테스트
let todos = [];
const todos1 = addTodo(todos, "React 공부");
console.assert(todos1.length === 1, "추가 후 길이 테스트 실패");
console.assert(todos1[0].text === "React 공부", "추가된 항목 텍스트 테스트 실패");
console.assert(todos1[0].done === false, "추가된 항목 done 테스트 실패");
console.assert(todos1[0].id === 1, "첫 번째 항목 id 테스트 실패");

// 원본 불변성 테스트
console.assert(todos.length === 0, "원본 배열이 수정되지 않아야 합니다");

const todos2 = addTodo(todos1, "운동하기");
console.assert(todos2.length === 2, "두 번째 추가 후 길이 테스트 실패");
console.assert(todos2[1].id === 2, "두 번째 항목 id 테스트 실패");

// 토글 테스트
const todos3 = toggleTodo(todos2, 1);
console.assert(todos3[0].done === true, "토글 테스트 실패");
console.assert(todos3[1].done === false, "다른 항목은 변경되지 않아야 합니다");

// 토글 불변성 테스트
console.assert(todos2[0].done === false, "토글 시 원본이 수정되지 않아야 합니다");

// 삭제 테스트
const todos4 = removeTodo(todos3, 1);
console.assert(todos4.length === 1, "삭제 후 길이 테스트 실패");
console.assert(todos4[0].id === 2, "남은 항목 확인 테스트 실패");

// 삭제 불변성 테스트
console.assert(todos3.length === 2, "삭제 시 원본이 수정되지 않아야 합니다");

// 존재하지 않는 id 토글 테스트
const todos5 = toggleTodo(todos4, 999);
console.assert(todos5.length === 1, "존재하지 않는 id 토글 시 길이 유지");
console.assert(todos5 !== todos4, "존재하지 않는 id여도 새 배열을 반환해야 합니다");

console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
