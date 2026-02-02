// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: Props 전달 시뮬레이션 =====
function renderUserCard({ name, age, role = "회원" }) {
  // 구조 분해 할당에서 바로 기본값 설정
  // React에서도 동일한 패턴으로 props를 받음
  return `[${role}] ${name} (${age}세)`;
}

// ===== 문제 2: children 시뮬레이션 =====
function renderCard({ title, children }) {
  // children이 없을 때 기본값 처리
  // React에서 <Card title="제목" /> 처럼 children 없이 사용하는 경우와 동일
  const content = children ?? "(내용 없음)";
  return `=== ${title} ===\n${content}\n===============`;
}

// ===== 문제 3: 컴포넌트 재사용 시뮬레이션 =====
function renderAlert({ type = "info", message }) {
  // 타입별 접두사 매핑
  // React에서 같은 Alert 컴포넌트에 다른 type prop을 전달하는 것과 동일
  const prefixes = {
    info: "정보",
    warning: "경고",
    error: "오류",
  };
  const prefix = prefixes[type] || "정보";
  return `[${prefix}] ${message}`;
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: UserCard 테스트 ===");
console.assert(
  renderUserCard({ name: "김철수", age: 28, role: "관리자" }) === "[관리자] 김철수 (28세)",
  "관리자 테스트 실패"
);
console.assert(
  renderUserCard({ name: "이영희", age: 25 }) === "[회원] 이영희 (25세)",
  "기본 역할 테스트 실패"
);
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: Card 테스트 ===");
console.assert(
  renderCard({ title: "공지", children: "서버 점검 예정" }) === "=== 공지 ===\n서버 점검 예정\n===============",
  "기본 카드 테스트 실패"
);
console.assert(
  renderCard({ title: "빈 카드" }) === "=== 빈 카드 ===\n(내용 없음)\n===============",
  "빈 카드 테스트 실패"
);
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: Alert 테스트 ===");
console.assert(renderAlert({ type: "info", message: "안내" }) === "[정보] 안내", "정보 테스트 실패");
console.assert(renderAlert({ type: "warning", message: "주의" }) === "[경고] 주의", "경고 테스트 실패");
console.assert(renderAlert({ type: "error", message: "오류" }) === "[오류] 오류", "오류 테스트 실패");
console.assert(renderAlert({ message: "기본" }) === "[정보] 기본", "기본 타입 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
