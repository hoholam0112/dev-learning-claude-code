// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: useToggle 시뮬레이션 =====
// true/false를 토글하는 커스텀 훅을 시뮬레이션하세요.
// createToggle(initialValue) → { getValue, toggle, setOn, setOff }

function createToggle(initialValue = false) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: useCounter 시뮬레이션 =====
// 증가/감소/리셋이 가능한 카운터 훅을 시뮬레이션하세요.
// createCounter({ initial, min, max, step }) → { getValue, increment, decrement, reset }

function createCounter({ initial = 0, min = -Infinity, max = Infinity, step = 1 } = {}) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: useLocalStorage 시뮬레이션 =====
// localStorage와 동기화되는 상태를 시뮬레이션하세요.
// createStoredState(key, initialValue, storage) → { getValue, setValue, remove }
// storage 객체는 getItem, setItem, removeItem 메서드를 가집니다.

function createStoredState(key, initialValue, storage) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: useToggle 테스트 ===");
const toggle = createToggle(false);
console.assert(toggle.getValue() === false, "초기값 테스트 실패");
toggle.toggle();
console.assert(toggle.getValue() === true, "토글 테스트 실패");
toggle.toggle();
console.assert(toggle.getValue() === false, "재토글 테스트 실패");
toggle.setOn();
console.assert(toggle.getValue() === true, "setOn 테스트 실패");
toggle.setOff();
console.assert(toggle.getValue() === false, "setOff 테스트 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: useCounter 테스트 ===");
const counter = createCounter({ initial: 5, min: 0, max: 10, step: 2 });
console.assert(counter.getValue() === 5, "초기값 테스트 실패");
counter.increment();
console.assert(counter.getValue() === 7, "증가 테스트 실패");
counter.increment();
console.assert(counter.getValue() === 9, "증가2 테스트 실패");
counter.increment();
console.assert(counter.getValue() === 10, "최대값 테스트 실패");
counter.decrement();
console.assert(counter.getValue() === 8, "감소 테스트 실패");
counter.reset();
console.assert(counter.getValue() === 5, "리셋 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: useLocalStorage 테스트 ===");
const mockStorage = {};
const fakeStorage = {
  getItem: (key) => (key in mockStorage ? mockStorage[key] : null),
  setItem: (key, value) => { mockStorage[key] = value; },
  removeItem: (key) => { delete mockStorage[key]; },
};
const stored = createStoredState("theme", "light", fakeStorage);
console.assert(stored.getValue() === "light", "초기값 테스트 실패");
stored.setValue("dark");
console.assert(stored.getValue() === "dark", "값 변경 테스트 실패");
console.assert(fakeStorage.getItem("theme") === "dark", "스토리지 동기화 테스트 실패");
stored.remove();
console.assert(stored.getValue() === "light", "삭제 후 초기값 테스트 실패");
console.assert(fakeStorage.getItem("theme") === null, "스토리지 삭제 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
