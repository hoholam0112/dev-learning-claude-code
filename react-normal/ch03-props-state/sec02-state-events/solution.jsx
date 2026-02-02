// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: useState 시뮬레이션 =====
function createState(initialValue) {
  // 클로저를 활용하여 상태를 캡슐화합니다.
  // React의 useState도 내부적으로 클로저를 활용하여 상태를 관리합니다.
  let state = initialValue;

  const getValue = () => state;

  const setValue = (newValue) => {
    // 함수가 전달되면 이전 상태를 인자로 호출 (함수형 업데이트)
    // React의 setState(prev => prev + 1) 패턴과 동일
    if (typeof newValue === "function") {
      state = newValue(state);
    } else {
      state = newValue;
    }
  };

  return [getValue, setValue];
}

// ===== 문제 2: 범위 제한 카운터 =====
function createCounter(min, max, initial) {
  // createState를 활용하여 카운터 상태를 관리합니다.
  // React에서 useState와 핸들러 함수 조합으로 카운터를 만드는 것과 동일한 패턴입니다.
  const [getValue, setValue] = createState(initial);

  return {
    getValue,

    increment() {
      // Math.min으로 최댓값 제한
      // React에서: setCount(prev => Math.min(prev + 1, max))
      setValue((prev) => Math.min(prev + 1, max));
    },

    decrement() {
      // Math.max로 최솟값 제한
      // React에서: setCount(prev => Math.max(prev - 1, min))
      setValue((prev) => Math.max(prev - 1, min));
    },

    reset() {
      // 초기값으로 복원
      // React에서: setCount(initial)
      setValue(initial);
    },
  };
}

// ===== 문제 3: Todo 리스트 상태 관리 =====

// 새 할일 추가 — React에서 setTodos([...todos, newTodo]) 패턴
function addTodo(todos, text) {
  // 현재 최대 id를 구하고 +1 (비어 있으면 1부터 시작)
  const maxId = todos.length > 0 ? Math.max(...todos.map((t) => t.id)) : 0;
  const newTodo = { id: maxId + 1, text, done: false };

  // 스프레드 연산자로 새 배열 생성 (원본 불변)
  return [...todos, newTodo];
}

// 할일 토글 — React에서 setTodos(todos.map(...)) 패턴
function toggleTodo(todos, id) {
  // map으로 새 배열 생성, 해당 id의 done만 반전
  // 해당 id가 없어도 map은 새 배열을 반환하므로 불변성 유지
  return todos.map((todo) =>
    todo.id === id ? { ...todo, done: !todo.done } : todo
  );
}

// 할일 삭제 — React에서 setTodos(todos.filter(...)) 패턴
function removeTodo(todos, id) {
  // filter로 새 배열 생성, 해당 id 제외
  return todos.filter((todo) => todo.id !== id);
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
