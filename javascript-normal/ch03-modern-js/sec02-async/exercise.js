// 실행: node exercise.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: delay 함수 =====
// 지정된 밀리초 후에 value로 resolve되는 Promise를 반환하세요.

function delay(ms, value) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 순차 실행 =====
// 비동기 함수 배열을 순서대로 실행하고 결과를 배열로 반환하세요.
// 각 함수는 () => Promise 형태입니다.

async function runSequential(asyncFunctions) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 안전한 다중 요청 =====
// 비동기 함수 배열을 병렬로 실행하되, 실패한 것은 null로 처리하세요.
// 각 함수는 () => Promise 형태입니다.

async function fetchAllSafe(asyncFunctions) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
async function runTests() {
  console.log("=== 문제 1: delay 테스트 ===");
  const start1 = Date.now();
  const result1 = await delay(100, "완료");
  const elapsed1 = Date.now() - start1;
  console.assert(result1 === "완료", "값 테스트 실패");
  console.assert(elapsed1 >= 90, "시간 테스트 실패");
  console.log("문제 1: 모든 테스트 통과!");

  console.log("\n=== 문제 2: 순차 실행 테스트 ===");
  const order = [];
  const fns = [
    async () => { order.push(1); await delay(50); return "a"; },
    async () => { order.push(2); await delay(30); return "b"; },
    async () => { order.push(3); await delay(10); return "c"; },
  ];
  const results2 = await runSequential(fns);
  console.assert(JSON.stringify(results2) === '["a","b","c"]', "결과 테스트 실패");
  console.assert(JSON.stringify(order) === "[1,2,3]", "순서 테스트 실패");
  console.log("문제 2: 모든 테스트 통과!");

  console.log("\n=== 문제 3: 안전한 다중 요청 테스트 ===");
  const safeFns = [
    async () => "성공1",
    async () => { throw new Error("실패"); },
    async () => "성공3",
  ];
  const results3 = await fetchAllSafe(safeFns);
  console.assert(results3[0] === "성공1", "성공1 테스트 실패");
  console.assert(results3[1] === null, "실패 처리 테스트 실패");
  console.assert(results3[2] === "성공3", "성공3 테스트 실패");
  console.log("문제 3: 모든 테스트 통과!");

  console.log("\n🎉 모든 테스트를 통과했습니다!");
}

runTests();
