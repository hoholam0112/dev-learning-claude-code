// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: useRef 시뮬레이션 =====
// React의 useRef는 놀랍도록 단순합니다.
// 내부적으로 { current: initialValue } 객체를 생성하고,
// 컴포넌트가 리렌더링되어도 동일한 객체 참조를 유지합니다.
//
// useState와의 핵심 차이:
// - useState: 값 변경 → 리렌더링 발생 → 화면 업데이트
// - useRef: 값 변경 → 아무 일도 안 일어남 → 값만 저장
//
// 실제 React에서의 사용 예:
//   const inputRef = useRef(null);
//   <input ref={inputRef} />
//   inputRef.current.focus(); // DOM에 직접 접근
function createRef(initialValue) {
  // useRef의 구현은 이것이 전부입니다!
  // 단순한 객체이지만, React가 렌더링 간에 같은 참조를 유지해주는 것이 핵심
  return { current: initialValue };
}

// ===== 문제 2: useMemo 시뮬레이션 =====
// useMemo는 "의존성이 같으면 이전에 계산한 값을 재사용"하는 Hook입니다.
// 비용이 높은 계산(대량 데이터 필터링, 복잡한 수학 연산 등)에 사용합니다.
//
// 실제 React에서의 사용 예:
//   const sorted = useMemo(() => {
//     return [...items].sort((a, b) => a.name.localeCompare(b.name));
//   }, [items]); // items가 바뀔 때만 정렬 수행
function createMemo(computeFn) {
  // 캐싱된 값과 의존성을 저장 (클로저로 유지)
  let cachedValue = undefined;
  let cachedDeps = null;

  return {
    get(deps) {
      // 의존성 변경 여부를 확인
      // React도 내부적으로 Object.is()를 사용하여 각 의존성을 비교합니다
      const depsChanged =
        cachedDeps === null || // 첫 호출
        deps.length !== cachedDeps.length || // 의존성 개수 변경
        deps.some((dep, i) => dep !== cachedDeps[i]); // 값 비교

      if (depsChanged) {
        // 의존성이 변경되었으면 다시 계산
        cachedValue = computeFn(...deps);
        cachedDeps = [...deps]; // 의존성 복사 저장
      }

      // 변경되지 않았으면 캐싱된 값 반환 (재계산 없음)
      return cachedValue;
    },
  };
}

// ===== 문제 3: 이전 값 추적 =====
// React에서 useRef를 활용한 가장 흔한 패턴 중 하나입니다.
// 이전 props나 state 값을 기억하여 변경 전후를 비교할 때 사용합니다.
//
// 실제 React에서의 패턴:
//   function usePrevious(value) {
//     const ref = useRef();
//     useEffect(() => {
//       ref.current = value;  // 렌더링 후에 업데이트
//     });
//     return ref.current;     // 렌더링 시점에는 아직 이전 값
//   }
//
//   const prevCount = usePrevious(count);
//   // count가 3이면 prevCount는 2 (이전 렌더링의 값)
function createPrevious(initialValue) {
  // 현재 값을 저장 (React의 state에 해당)
  let currentValue = initialValue;
  // 이전 값을 저장 (React의 useRef에 해당)
  let previousValue = undefined;
  // 모든 값의 이력을 저장
  const history = [initialValue];

  return {
    // 새 값으로 업데이트 (이전 값을 자동으로 보존)
    update(newValue) {
      previousValue = currentValue; // 현재 값을 이전 값으로 이동
      currentValue = newValue; // 새 값을 현재 값으로 설정
      history.push(newValue); // 이력에 추가
    },

    // 현재 값 반환
    getCurrent() {
      return currentValue;
    },

    // 이전 값 반환 (update 전에는 undefined)
    getPrevious() {
      return previousValue;
    },

    // 모든 값의 이력 반환 (초기값 포함)
    // 원본 배열이 외부에서 변경되지 않도록 복사본을 반환
    getHistory() {
      return [...history];
    },
  };
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: useRef 시뮬레이션 테스트 ===");
const ref1 = createRef(0);
console.assert(ref1.current === 0, `초기값 실패: ${ref1.current}`);

ref1.current = 42;
console.assert(ref1.current === 42, `값 변경 실패: ${ref1.current}`);

ref1.current = "문자열";
console.assert(ref1.current === "문자열", `문자열 설정 실패: ${ref1.current}`);

// null 초기값
const ref2 = createRef(null);
console.assert(ref2.current === null, `null 초기값 실패: ${ref2.current}`);

ref2.current = { name: "김철수" };
console.assert(ref2.current.name === "김철수", `객체 설정 실패`);

// ref는 단순한 객체 - current 속성만 가짐
console.assert("current" in ref1, "current 속성이 있어야 합니다");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: useMemo 시뮬레이션 테스트 ===");
let computeCount = 0;
const memo = createMemo((...args) => {
  computeCount++;
  return args.reduce((sum, n) => sum + n, 0);
});

// 첫 호출: 계산 실행
const result1 = memo.get([1, 2, 3]);
console.assert(result1 === 6, `첫 계산 실패: ${result1}`);
console.assert(computeCount === 1, `계산 횟수 실패: ${computeCount}`);

// 같은 의존성: 캐시 반환 (계산 실행 안 함)
const result2 = memo.get([1, 2, 3]);
console.assert(result2 === 6, `캐시 반환 실패: ${result2}`);
console.assert(computeCount === 1, `같은 deps에서 재계산되면 안 됩니다: ${computeCount}`);

// 다른 의존성: 재계산
const result3 = memo.get([10, 20]);
console.assert(result3 === 30, `재계산 실패: ${result3}`);
console.assert(computeCount === 2, `재계산 횟수 실패: ${computeCount}`);

// 다시 같은 의존성: 캐시 반환
const result4 = memo.get([10, 20]);
console.assert(result4 === 30, `두 번째 캐시 실패: ${result4}`);
console.assert(computeCount === 2, `불필요한 재계산: ${computeCount}`);
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 이전 값 추적 테스트 ===");
const tracker = createPrevious("초기값");

// 초기 상태
console.assert(tracker.getCurrent() === "초기값", `초기 현재값 실패: ${tracker.getCurrent()}`);
console.assert(tracker.getPrevious() === undefined, `초기 이전값 실패: ${tracker.getPrevious()}`);
console.assert(tracker.getHistory().length === 1, `초기 히스토리 실패`);
console.assert(tracker.getHistory()[0] === "초기값", `히스토리 초기값 실패`);

// 첫 번째 업데이트
tracker.update("두번째");
console.assert(tracker.getCurrent() === "두번째", `업데이트 후 현재값 실패`);
console.assert(tracker.getPrevious() === "초기값", `업데이트 후 이전값 실패`);

// 두 번째 업데이트
tracker.update("세번째");
console.assert(tracker.getCurrent() === "세번째", `두번째 업데이트 현재값 실패`);
console.assert(tracker.getPrevious() === "두번째", `두번째 업데이트 이전값 실패`);

// 히스토리 확인
const history = tracker.getHistory();
console.assert(history.length === 3, `히스토리 길이 실패: ${history.length}`);
console.assert(history[0] === "초기값", "히스토리 첫 번째 값");
console.assert(history[1] === "두번째", "히스토리 두 번째 값");
console.assert(history[2] === "세번째", "히스토리 세 번째 값");

// 숫자로도 테스트
const numTracker = createPrevious(0);
numTracker.update(10);
numTracker.update(20);
numTracker.update(30);
console.assert(numTracker.getCurrent() === 30, "숫자 현재값");
console.assert(numTracker.getPrevious() === 20, "숫자 이전값");
console.assert(numTracker.getHistory().join(",") === "0,10,20,30", "숫자 히스토리");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n모든 테스트를 통과했습니다!");
