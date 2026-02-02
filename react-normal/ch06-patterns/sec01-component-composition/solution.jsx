// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 컴포넌트 분리 판단 =====
function shouldSplitComponent(component) {
  const reasons = [];
  const suggestedComponents = [];

  // 역할이 2개 이상이면 분리 권장
  if (component.roles.length > 1) {
    reasons.push(`역할이 ${component.roles.length}개로 단일 책임 원칙 위반`);
    // 각 역할을 별도 컴포넌트로 제안
    component.roles.forEach((role) => {
      const name = role.replace(/\s/g, "").replace("표시", "").replace("처리", "");
      suggestedComponents.push(name);
    });
  }

  // 코드가 50줄 초과면 분리 권장
  if (component.linesOfCode > 50) {
    reasons.push(`코드가 ${component.linesOfCode}줄로 너무 김`);
  }

  const shouldSplit = reasons.length > 0;
  const reason = shouldSplit ? reasons.join(", ") : "분리 불필요";

  return { shouldSplit, reason, suggestedComponents };
}

// ===== 문제 2: 상태 끌어올리기 시뮬레이션 =====
function createSharedState(initialValue) {
  let value = initialValue;
  const subscribers = [];

  return {
    getValue() {
      return value;
    },
    setValue(newValue) {
      value = newValue;
      // 모든 구독자에게 새 값 알림 (React의 리렌더링과 유사)
      subscribers.forEach((callback) => callback(value));
    },
    subscribe(callback) {
      subscribers.push(callback);
    },
  };
}

// ===== 문제 3: 레이아웃 합성 패턴 =====
function createLayout(config) {
  return {
    render(sections) {
      // children 패턴: header와 footer는 고정, 중간 내용은 동적
      const lines = [];
      lines.push(`[Header: ${config.header}]`);
      sections.forEach((section) => lines.push(section));
      lines.push(`[Footer: ${config.footer}]`);
      return lines.join("\n");
    },
  };
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
