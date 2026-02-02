// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: delay 함수 =====
function delay(ms, value) {
  // Promise를 생성하고, setTimeout으로 지정된 시간 후 resolve
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), ms);
  });
}

// ===== 문제 2: 순차 실행 =====
async function runSequential(asyncFunctions) {
  const results = [];
  // for...of로 순회하며 하나씩 await
  // 이전 함수가 완료되어야 다음 함수가 실행됨
  for (const fn of asyncFunctions) {
    const result = await fn();
    results.push(result);
  }
  return results;
}

// ===== 문제 3: 안전한 다중 요청 =====
async function fetchAllSafe(asyncFunctions) {
  // 각 함수를 try/catch로 감싸서 실패 시 null 반환
  const safePromises = asyncFunctions.map(async (fn) => {
    try {
      return await fn();
    } catch {
      return null;
    }
  });
  // Promise.all로 병렬 실행
  return Promise.all(safePromises);
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
