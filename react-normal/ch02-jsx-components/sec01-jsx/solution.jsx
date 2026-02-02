// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: HTML → JSX 변환 =====
function convertToJSXAttributes(htmlAttributes) {
  // HTML → JSX 속성 매핑 테이블
  const attributeMap = {
    class: "className",
    for: "htmlFor",
    tabindex: "tabIndex",
    onclick: "onClick",
    onchange: "onChange",
    onsubmit: "onSubmit",
    readonly: "readOnly",
    maxlength: "maxLength",
    colspan: "colSpan",
    rowspan: "rowSpan",
  };

  const result = {};
  for (const [key, value] of Object.entries(htmlAttributes)) {
    // 매핑 테이블에 있으면 변환된 이름 사용, 없으면 원래 이름 유지
    const jsxKey = attributeMap[key] || key;
    result[jsxKey] = value;
  }
  return result;
}

// ===== 문제 2: 조건부 렌더링 시뮬레이션 =====
function getRenderedComponents(state) {
  const components = [];

  // 항상 렌더링
  components.push("Header");

  // 로그인 상태에 따라 조건부 렌더링 (삼항 연산자 패턴)
  if (state.isLoggedIn) {
    components.push("UserProfile");
  } else {
    components.push("LoginForm");
  }

  // && 패턴: 두 조건 모두 만족할 때만 렌더링
  if (state.isLoggedIn && state.hasNotifications) {
    components.push("NotificationBadge");
  }

  // 항상 렌더링
  components.push("Footer");

  return components;
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: JSX 속성 변환 테스트 ===");
const jsxAttrs = convertToJSXAttributes({
  class: "container",
  for: "name",
  tabindex: "1",
  onclick: "handler",
});
console.assert(jsxAttrs.className === "container", "className 변환 실패");
console.assert(jsxAttrs.htmlFor === "name", "htmlFor 변환 실패");
console.assert(jsxAttrs.tabIndex === "1", "tabIndex 변환 실패");
console.assert(jsxAttrs.onClick === "handler", "onClick 변환 실패");
console.assert(!jsxAttrs.class, "class가 남아있으면 안 됩니다");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 조건부 렌더링 테스트 ===");
const loggedIn = getRenderedComponents({ isLoggedIn: true, hasNotifications: true });
console.assert(loggedIn[0] === "Header", "Header 테스트 실패");
console.assert(loggedIn.includes("UserProfile"), "UserProfile 테스트 실패");
console.assert(loggedIn.includes("NotificationBadge"), "NotificationBadge 테스트 실패");
console.assert(loggedIn[loggedIn.length - 1] === "Footer", "Footer 테스트 실패");

const loggedOut = getRenderedComponents({ isLoggedIn: false, hasNotifications: false });
console.assert(loggedOut.includes("LoginForm"), "LoginForm 테스트 실패");
console.assert(!loggedOut.includes("UserProfile"), "로그아웃 시 UserProfile 없어야 합니다");
console.assert(!loggedOut.includes("NotificationBadge"), "로그아웃 시 NotificationBadge 없어야 합니다");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
