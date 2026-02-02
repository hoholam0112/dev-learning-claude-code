// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 이펙트 시뮬레이션 =====
// React useEffect의 핵심 동작을 시뮬레이션합니다.
// useEffect는 의존성 배열의 값이 변경되었을 때만 콜백을 실행하고,
// 다음 실행 전에 이전 클린업 함수를 호출합니다.
function createEffect() {
  // 이전 의존성 배열을 저장 (React 내부에서도 이렇게 이전 deps를 기억합니다)
  let prevDeps = null;
  // 현재 클린업 함수 저장
  let cleanupFn = null;
  // 첫 번째 실행 여부 추적
  let isFirstRun = true;

  return {
    // useEffect(callback, deps)와 동일한 역할
    run(callback, deps) {
      // 의존성 변경 여부 확인
      let shouldRun = false;

      if (isFirstRun) {
        // 첫 실행은 항상 수행 (React도 마운트 시 항상 실행)
        shouldRun = true;
        isFirstRun = false;
      } else if (deps) {
        // 이전 deps와 현재 deps를 하나씩 비교 (얕은 비교)
        // React도 Object.is()를 사용하여 각 의존성을 비교합니다
        shouldRun = deps.some((dep, i) => dep !== prevDeps[i]);
      }

      if (shouldRun) {
        // 이전 클린업 함수 실행 (React의 cleanup 동작)
        // 새 이펙트를 실행하기 전에 이전 이펙트를 정리합니다
        if (cleanupFn) {
          cleanupFn();
          cleanupFn = null;
        }

        // 콜백 실행 후 반환값이 함수면 클린업으로 저장
        const result = callback();
        if (typeof result === "function") {
          cleanupFn = result;
        }
      }

      // 현재 deps를 저장 (다음 비교를 위해)
      prevDeps = deps ? [...deps] : null;
    },

    // 수동 클린업 (컴포넌트 언마운트 시뮬레이션)
    cleanup() {
      if (cleanupFn) {
        cleanupFn();
        cleanupFn = null;
      }
    },
  };
}

// ===== 문제 2: 타이머 시뮬레이션 =====
// useEffect에서 setInterval을 사용하고 클린업으로 clearInterval하는 패턴입니다.
// 실제 React에서의 사용 예:
//   useEffect(() => {
//     const id = setInterval(() => setCount(c => c + 1), 1000);
//     return () => clearInterval(id);  // 클린업
//   }, []);
function createTimer() {
  let timerId = null;     // setInterval의 반환 ID
  let tickCount = 0;      // 콜백 호출 횟수
  let running = false;    // 실행 상태

  return {
    // 타이머 시작 (이미 실행 중이면 재시작)
    // React에서 deps 변경 시 이전 타이머를 클린업하고 새로 시작하는 것과 동일
    start(callback, interval) {
      // 이미 실행 중이면 기존 타이머 정지 (클린업 역할)
      if (timerId !== null) {
        clearInterval(timerId);
      }

      running = true;
      timerId = setInterval(() => {
        tickCount++;
        callback();
      }, interval);
    },

    // 타이머 정지 (클린업 함수 역할)
    // clearInterval을 호출하지 않으면 메모리 누수가 발생합니다
    stop() {
      if (timerId !== null) {
        clearInterval(timerId);
        timerId = null;
      }
      running = false;
    },

    // 실행 상태 확인
    isRunning() {
      return running;
    },

    // 콜백 호출 횟수 반환
    getTickCount() {
      return tickCount;
    },
  };
}

// ===== 문제 3: 데이터 페처 시뮬레이션 =====
// useEffect에서 비동기 데이터를 가져올 때의 패턴입니다.
// loading/data/error 세 가지 상태를 관리하고,
// 경쟁 조건(race condition)을 cancelled 플래그로 방지합니다.
//
// 실제 React에서의 패턴:
//   useEffect(() => {
//     let cancelled = false;
//     fetch(url).then(data => {
//       if (!cancelled) setData(data);
//     });
//     return () => { cancelled = true; };
//   }, [url]);
function createDataFetcher(fetchFn) {
  // 상태 관리 (React의 useState에 해당)
  let state = {
    loading: false,
    data: null,
    error: null,
  };

  // 현재 활성 요청의 ID (경쟁 조건 방지용)
  // useEffect 클린업에서 cancelled = true 하는 것과 동일한 역할
  let currentRequestId = 0;

  return {
    // 데이터 가져오기 실행
    async fetch() {
      // 새 요청 ID 발급 (이전 요청 무효화)
      currentRequestId++;
      const thisRequestId = currentRequestId;

      // 로딩 시작
      state = { loading: true, data: state.data, error: null };

      try {
        const result = await fetchFn();

        // 경쟁 조건 확인: 이 요청이 여전히 최신인지 확인
        // 새로운 fetch()가 호출되었다면 이 결과는 무시
        if (thisRequestId === currentRequestId) {
          state = { loading: false, data: result, error: null };
        }
      } catch (err) {
        // 에러 발생 시에도 경쟁 조건 확인
        if (thisRequestId === currentRequestId) {
          state = { loading: false, data: null, error: err.message };
        }
      }
    },

    // 현재 상태 반환
    getState() {
      return { ...state };
    },
  };
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
