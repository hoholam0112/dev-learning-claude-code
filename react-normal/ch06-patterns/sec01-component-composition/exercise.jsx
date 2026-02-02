// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 컴포넌트 분리 판단 =====
// 주어진 컴포넌트 설명을 분석하여 분리 여부와 분리 방안을 반환하세요.
// 분리 기준: 역할이 2개 이상이거나, 코드 줄 수가 50 초과이거나, 재사용 가능성이 있는 경우

function shouldSplitComponent(component) {
  // TODO: 여기에 코드를 작성하세요
  // component: { name, roles: [], linesOfCode, isReusable }
  // 반환: { shouldSplit: boolean, reason: string, suggestedComponents: string[] }
}

// ===== 문제 2: 상태 끌어올리기 시뮬레이션 =====
// 두 자식 컴포넌트가 공유하는 상태를 부모에서 관리하는 패턴을 구현하세요.
// createSharedState(initialValue) → { getValue, setValue, subscribe }
// subscribe로 등록한 콜백이 값 변경 시 호출됩니다.

function createSharedState(initialValue) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 레이아웃 합성 패턴 =====
// children 패턴을 활용하는 레이아웃 함수를 만드세요.
// createLayout(config) → { render(sections) }
// config: { header, footer }
// sections: 메인 컨텐츠 배열
// 결과: "[Header: {header}]\n{sections 각 줄}\n[Footer: {footer}]"

function createLayout(config) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 컴포넌트 분리 판단 테스트 ===");
const result1 = shouldSplitComponent({
  name: "UserDashboard",
  roles: ["사용자 정보 표시", "주문 목록 표시", "통계 차트"],
  linesOfCode: 120,
  isReusable: false,
});
console.assert(result1.shouldSplit === true, "분리 판단 실패");
console.assert(result1.suggestedComponents.length >= 2, "분리 제안 실패");

const result2 = shouldSplitComponent({
  name: "Button",
  roles: ["버튼 렌더링"],
  linesOfCode: 15,
  isReusable: true,
});
console.assert(result2.shouldSplit === false, "작은 컴포넌트는 분리 불필요");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 상태 끌어올리기 테스트 ===");
const shared = createSharedState(0);
const changes = [];
shared.subscribe((val) => changes.push(val));
console.assert(shared.getValue() === 0, "초기값 테스트 실패");
shared.setValue(5);
console.assert(shared.getValue() === 5, "값 변경 테스트 실패");
console.assert(changes[0] === 5, "구독 알림 테스트 실패");
shared.setValue(10);
console.assert(changes.length === 2, "구독 횟수 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 레이아웃 합성 테스트 ===");
const layout = createLayout({ header: "내 사이트", footer: "Copyright 2024" });
const rendered = layout.render(["섹션 1", "섹션 2", "섹션 3"]);
console.assert(rendered.includes("[Header: 내 사이트]"), "헤더 테스트 실패");
console.assert(rendered.includes("섹션 1"), "섹션1 테스트 실패");
console.assert(rendered.includes("섹션 2"), "섹션2 테스트 실패");
console.assert(rendered.includes("[Footer: Copyright 2024]"), "푸터 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
