// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 데이터 페칭 상태 관리 =====
// 클로저를 사용하여 내부 상태를 캡슐화합니다.
// React의 useState와 비슷한 패턴으로, 상태를 직접 수정하지 않고
// 전용 메서드를 통해서만 변경할 수 있도록 합니다.

function createFetchState() {
  // 내부 상태 - 외부에서 직접 접근 불가
  let state = {
    status: "idle",   // 현재 상태: "idle" | "loading" | "success" | "error"
    data: null,       // 성공 시 받은 데이터
    error: null,      // 에러 시 에러 메시지
  };

  return {
    // 현재 상태를 반환
    getState() {
      return state;
    },

    // 로딩 시작: 이전 데이터와 에러를 초기화
    // React에서: setState({ status: "loading", data: null, error: null })
    startLoading() {
      state = { status: "loading", data: null, error: null };
    },

    // 데이터 수신 성공: 데이터를 저장하고 에러를 초기화
    // React에서: setState({ status: "success", data, error: null })
    setData(data) {
      state = { status: "success", data, error: null };
    },

    // 에러 발생: 에러 메시지를 저장하고 데이터를 초기화
    // React에서: setState({ status: "error", data: null, error })
    setError(error) {
      state = { status: "error", data: null, error };
    },
  };
}

// ===== 문제 2: 비동기 데이터 페칭 =====
// try/catch로 비동기 함수의 성공/실패를 처리합니다.
// React의 useEffect 안에서 데이터를 가져오는 패턴과 동일한 로직입니다.

async function executeFetch(fetchFn) {
  try {
    // fetchFn을 실행하고 결과를 기다림
    const data = await fetchFn();

    // 성공: 데이터를 포함한 상태 객체 반환
    return { status: "success", data, error: null };
  } catch (err) {
    // 실패: 에러 메시지를 포함한 상태 객체 반환
    // err.message로 Error 객체에서 메시지만 추출
    return { status: "error", data: null, error: err.message };
  }
}

// ===== 문제 3: 데이터 표시 로직 =====
// 상태에 따라 사용자에게 보여줄 메시지를 결정합니다.
// React에서 조건부 렌더링 시 사용하는 패턴과 동일합니다.

function renderFetchResult(state) {
  switch (state.status) {
    case "idle":
      // 아직 요청 전
      return "대기 중";

    case "loading":
      // 데이터를 가져오는 중
      return "로딩 중...";

    case "error":
      // 에러 발생 - 에러 메시지를 함께 표시
      return `오류: ${state.error}`;

    case "success":
      // 성공했지만 데이터가 빈 배열인 경우와 데이터가 있는 경우를 구분
      if (Array.isArray(state.data) && state.data.length === 0) {
        return "데이터가 없습니다";
      }
      return `총 ${state.data.length}건의 데이터`;

    default:
      // 예상치 못한 상태
      return "알 수 없는 상태";
  }
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
