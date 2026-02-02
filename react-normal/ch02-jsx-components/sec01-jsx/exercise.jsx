// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과
// 참고: 이 연습은 JSX 개념을 JavaScript 객체로 시뮬레이션합니다.

// ===== 문제 1: HTML → JSX 변환 =====
// 다음 HTML 속성들을 JSX 속성으로 변환하세요.
// "class" → "className", "for" → "htmlFor", "tabindex" → "tabIndex" 등

function convertToJSXAttributes(htmlAttributes) {
  // TODO: HTML 속성 객체를 JSX 속성 객체로 변환하세요
  // 입력: { class: "container", for: "name", tabindex: "1", onclick: "handler" }
  // 출력: { className: "container", htmlFor: "name", tabIndex: "1", onClick: "handler" }
}

// ===== 문제 2: 조건부 렌더링 시뮬레이션 =====
// 사용자 상태에 따라 렌더링할 컴포넌트 이름들의 배열을 반환하세요.
// 항상: ["Header"]
// isLoggedIn이 true: ["UserProfile"] 추가
// isLoggedIn이 false: ["LoginForm"] 추가
// hasNotifications가 true이고 isLoggedIn이 true: ["NotificationBadge"] 추가
// 항상: ["Footer"]

function getRenderedComponents(state) {
  // TODO: 여기에 코드를 작성하세요
  // state: { isLoggedIn, hasNotifications }
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
