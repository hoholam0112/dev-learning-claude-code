// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: useToggle 시뮬레이션 =====
function createToggle(initialValue = false) {
  let value = initialValue;
  return {
    getValue: () => value,
    // 현재 값을 반전 (React의 setIsOpen(prev => !prev)과 동일)
    toggle: () => { value = !value; },
    // 명시적으로 켜기/끄기
    setOn: () => { value = true; },
    setOff: () => { value = false; },
  };
}

// ===== 문제 2: useCounter 시뮬레이션 =====
function createCounter({ initial = 0, min = -Infinity, max = Infinity, step = 1 } = {}) {
  let value = initial;
  return {
    getValue: () => value,
    increment: () => {
      // Math.min으로 최대값 초과 방지
      value = Math.min(value + step, max);
    },
    decrement: () => {
      // Math.max로 최소값 미만 방지
      value = Math.max(value - step, min);
    },
    reset: () => {
      // 초기값으로 복원
      value = initial;
    },
  };
}

// ===== 문제 3: useLocalStorage 시뮬레이션 =====
function createStoredState(key, initialValue, storage) {
  // 스토리지에서 기존 값 로드, 없으면 초기값 사용
  const existing = storage.getItem(key);
  let value = existing !== null ? existing : initialValue;

  return {
    getValue: () => value,
    setValue: (newValue) => {
      value = newValue;
      // 스토리지와 동기화 (React에서 useEffect로 localStorage 동기화하는 것과 유사)
      storage.setItem(key, newValue);
    },
    remove: () => {
      // 스토리지에서 삭제하고 초기값으로 복원
      storage.removeItem(key);
      value = initialValue;
    },
  };
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
