// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 데이터 페칭 상태 관리 =====
// API 호출의 상태(로딩, 성공, 에러)를 관리하는 함수를 만드세요.
// createFetchState() → { getState, startLoading, setData, setError }
// 상태: { status: "idle"|"loading"|"success"|"error", data: null, error: null }

function createFetchState() {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 비동기 데이터 페칭 =====
// fetchFn을 호출하고 상태를 관리하는 함수를 만드세요.
// executeFetch(fetchFn) → Promise<{ status, data, error }>

async function executeFetch(fetchFn) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 데이터 표시 로직 =====
// 상태에 따라 표시할 내용을 결정하는 함수를 만드세요.
// renderFetchResult(state) → string
// idle → "대기 중"
// loading → "로딩 중..."
// error → "오류: {error 메시지}"
// success, data가 빈 배열 → "데이터가 없습니다"
// success, data가 있음 → "총 {N}건의 데이터"

function renderFetchResult(state) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
async function runTests() {
  console.log("=== 문제 1: 페칭 상태 관리 테스트 ===");
  const fetchState = createFetchState();
  console.assert(fetchState.getState().status === "idle", "초기 상태 테스트 실패");
  fetchState.startLoading();
  console.assert(fetchState.getState().status === "loading", "로딩 상태 테스트 실패");
  fetchState.setData([1, 2, 3]);
  console.assert(fetchState.getState().status === "success", "성공 상태 테스트 실패");
  console.assert(fetchState.getState().data.length === 3, "데이터 테스트 실패");
  fetchState.setError("네트워크 오류");
  console.assert(fetchState.getState().status === "error", "에러 상태 테스트 실패");
  console.assert(fetchState.getState().error === "네트워크 오류", "에러 메시지 테스트 실패");
  console.log("문제 1: 모든 테스트 통과!");

  console.log("\n=== 문제 2: 비동기 페칭 테스트 ===");
  const successResult = await executeFetch(async () => ({ users: ["김철수", "이영희"] }));
  console.assert(successResult.status === "success", "성공 상태 테스트 실패");
  console.assert(successResult.data.users.length === 2, "성공 데이터 테스트 실패");

  const errorResult = await executeFetch(async () => { throw new Error("서버 오류"); });
  console.assert(errorResult.status === "error", "에러 상태 테스트 실패");
  console.assert(errorResult.error === "서버 오류", "에러 메시지 테스트 실패");
  console.log("문제 2: 모든 테스트 통과!");

  console.log("\n=== 문제 3: 데이터 표시 테스트 ===");
  console.assert(renderFetchResult({ status: "idle" }) === "대기 중", "idle 테스트 실패");
  console.assert(renderFetchResult({ status: "loading" }) === "로딩 중...", "loading 테스트 실패");
  console.assert(renderFetchResult({ status: "error", error: "404" }) === "오류: 404", "error 테스트 실패");
  console.assert(renderFetchResult({ status: "success", data: [] }) === "데이터가 없습니다", "빈 데이터 테스트 실패");
  console.assert(renderFetchResult({ status: "success", data: [1, 2, 3] }) === "총 3건의 데이터", "데이터 표시 테스트 실패");
  console.log("문제 3: 모든 테스트 통과!");

  console.log("\n🎉 모든 테스트를 통과했습니다!");
}

runTests();
