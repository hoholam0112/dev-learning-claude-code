// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과
// 참고: 이 연습은 React useEffect의 동작 원리를 JavaScript로 연습합니다.

// ===== 문제 1: 이펙트 시뮬레이션 =====
// React의 useEffect 동작을 시뮬레이션하세요.
// run(callback, deps): 의존성이 변경되었을 때만 콜백 실행
// cleanup(): 현재 클린업 함수를 수동으로 실행
//
// 동작 규칙:
// - 첫 번째 run() 호출 시 항상 콜백 실행
// - 이후 호출 시 deps 배열의 값이 하나라도 바뀌었으면 콜백 실행
// - 콜백이 함수를 반환하면 클린업 함수로 저장
// - 다음 콜백 실행 전에 이전 클린업 함수 호출

function createEffect() {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 타이머 시뮬레이션 =====
// useEffect + setInterval 패턴을 시뮬레이션하세요.
// start(callback, interval): 타이머 시작 (이미 실행 중이면 재시작)
// stop(): 타이머 정지
// isRunning(): 실행 상태 반환
// getTickCount(): 콜백 호출 횟수 반환

function createTimer() {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 데이터 페처 시뮬레이션 =====
// useEffect에서의 데이터 가져오기 패턴을 시뮬레이션하세요.
// fetchFn: () => Promise 형태의 비동기 함수
// 반환 객체:
//   fetch(): 데이터를 가져옵니다 (Promise 반환)
//   getState(): { loading, data, error } 상태 반환
//
// 동작 규칙:
// - fetch() 호출 시 loading: true, error: null 로 설정
// - 성공 시 loading: false, data: 결과값, error: null
// - 실패 시 loading: false, data: null, error: 에러메시지
// - 이전 요청 중 새 요청 시작 시 이전 결과 무시 (경쟁 조건 방지)

function createDataFetcher(fetchFn) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 이펙트 시뮬레이션 테스트 ===");
const effect = createEffect();
let effectCount = 0;
let cleanupCount = 0;

// 첫 번째 실행: 항상 실행됨
effect.run(() => {
  effectCount++;
  return () => { cleanupCount++; };
}, [1, "hello"]);
console.assert(effectCount === 1, `첫 실행 실패: ${effectCount}`);
console.assert(cleanupCount === 0, "첫 실행에서 클린업이 호출되면 안 됩니다");

// 같은 의존성으로 실행: 실행되지 않음
effect.run(() => {
  effectCount++;
  return () => { cleanupCount++; };
}, [1, "hello"]);
console.assert(effectCount === 1, `같은 deps에서 실행되면 안 됩니다: ${effectCount}`);

// 의존성 변경: 실행됨 + 이전 클린업 호출
effect.run(() => {
  effectCount++;
  return () => { cleanupCount++; };
}, [2, "hello"]);
console.assert(effectCount === 2, `deps 변경 시 실행 실패: ${effectCount}`);
console.assert(cleanupCount === 1, `이전 클린업 호출 실패: ${cleanupCount}`);

// 수동 클린업
effect.cleanup();
console.assert(cleanupCount === 2, `수동 클린업 실패: ${cleanupCount}`);
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 타이머 시뮬레이션 테스트 ===");
const timer = createTimer();
console.assert(timer.isRunning() === false, "초기 상태는 정지");
console.assert(timer.getTickCount() === 0, "초기 틱 카운트는 0");

// 타이머 시작 (50ms 간격)
let timerValue = 0;
timer.start(() => { timerValue++; }, 50);
console.assert(timer.isRunning() === true, "시작 후 실행 상태");

// 150ms 후 확인 (약 2-3회 실행)
await new Promise((resolve) => setTimeout(resolve, 175));
console.assert(timer.getTickCount() >= 2, `틱 카운트 부족: ${timer.getTickCount()}`);
console.assert(timerValue >= 2, `timerValue 부족: ${timerValue}`);

// 타이머 정지
timer.stop();
console.assert(timer.isRunning() === false, "정지 후 상태");
const countAfterStop = timer.getTickCount();

// 정지 후 더 이상 증가하지 않음
await new Promise((resolve) => setTimeout(resolve, 100));
console.assert(timer.getTickCount() === countAfterStop, "정지 후 카운트 변화 없어야 합니다");

// 재시작 시 기존 타이머 정지 후 새로 시작
let newTimerValue = 0;
timer.start(() => { newTimerValue++; }, 50);
console.assert(timer.isRunning() === true, "재시작 후 실행 상태");
await new Promise((resolve) => setTimeout(resolve, 75));
timer.stop();
console.assert(newTimerValue >= 1, "재시작 후 콜백 실행 확인");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 데이터 페처 시뮬레이션 테스트 ===");

// 성공 케이스
const successFetcher = createDataFetcher(() =>
  new Promise((resolve) => setTimeout(() => resolve({ name: "김철수" }), 50))
);

// 초기 상태
let state = successFetcher.getState();
console.assert(state.loading === false, "초기 loading은 false");
console.assert(state.data === null, "초기 data는 null");
console.assert(state.error === null, "초기 error는 null");

// 데이터 가져오기 시작
const fetchPromise = successFetcher.fetch();
state = successFetcher.getState();
console.assert(state.loading === true, "fetch 중 loading은 true");

// 완료 대기
await fetchPromise;
state = successFetcher.getState();
console.assert(state.loading === false, "완료 후 loading은 false");
console.assert(state.data.name === "김철수", `데이터 확인 실패: ${JSON.stringify(state.data)}`);
console.assert(state.error === null, "성공 시 error는 null");

// 실패 케이스
const errorFetcher = createDataFetcher(() =>
  new Promise((_, reject) => setTimeout(() => reject(new Error("네트워크 오류")), 50))
);
await errorFetcher.fetch();
state = errorFetcher.getState();
console.assert(state.loading === false, "에러 후 loading은 false");
console.assert(state.data === null, "에러 시 data는 null");
console.assert(state.error === "네트워크 오류", `에러 메시지 확인 실패: ${state.error}`);

// 경쟁 조건 테스트: 느린 요청 후 빠른 요청
let callCount = 0;
const raceFetcher = createDataFetcher(() => {
  callCount++;
  const currentCall = callCount;
  const delay = currentCall === 1 ? 200 : 50; // 첫 번째는 느림, 두 번째는 빠름
  return new Promise((resolve) =>
    setTimeout(() => resolve({ call: currentCall }), delay)
  );
});

const slowPromise = raceFetcher.fetch(); // 느린 요청 (200ms)
const fastPromise = raceFetcher.fetch(); // 빠른 요청 (50ms) - 이것이 최종 결과여야 함

await Promise.all([slowPromise, fastPromise]);
state = raceFetcher.getState();
console.assert(state.data.call === 2, `경쟁 조건: 마지막 요청 결과여야 합니다. got: ${state.data.call}`);
console.log("문제 3: 모든 테스트 통과!");

console.log("\n모든 테스트를 통과했습니다!");
