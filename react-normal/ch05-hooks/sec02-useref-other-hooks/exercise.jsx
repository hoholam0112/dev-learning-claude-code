// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과
// 참고: 이 연습은 React의 useRef와 useMemo 패턴을 JavaScript로 연습합니다.

// ===== 문제 1: useRef 시뮬레이션 =====
// React의 useRef와 동일하게 { current: initialValue } 객체를 생성하세요.
// current 속성을 자유롭게 읽고 쓸 수 있어야 합니다.

function createRef(initialValue) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: useMemo 시뮬레이션 =====
// computeFn을 받아 메모이제이션 객체를 생성하세요.
// get(deps): 의존성 배열을 받아 값을 반환
//   - 첫 호출 시 항상 computeFn 실행
//   - 이후 호출 시 deps가 같으면 캐시 반환, 다르면 재계산
// computeFn은 get() 호출 시 전달된 deps를 인자로 받습니다.
// 예: computeFn = (a, b) => a + b; memo.get([1, 2]) → computeFn(1, 2)

function createMemo(computeFn) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 이전 값 추적 =====
// useRef를 활용한 "이전 값 추적" 패턴을 구현하세요.
// update(newValue): 새 값 설정 (이전 값은 자동으로 저장)
// getCurrent(): 현재 값 반환
// getPrevious(): 이전 값 반환 (첫 번째 update 전에는 undefined)
// getHistory(): 모든 값의 이력을 배열로 반환 (초기값 포함)

function createPrevious(initialValue) {
  // TODO: 여기에 코드를 작성하세요
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
