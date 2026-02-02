// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과
// 참고: 이 연습은 React 개념을 JavaScript로 연습합니다.

// ===== 문제 1: React 핵심 개념 정리 =====
// React의 3가지 핵심 특징을 객체 배열로 정리하세요.
// 각 객체: { name: "특징 이름", description: "설명" }
// 특징: "선언적", "컴포넌트 기반", "범용성"

function getReactFeatures() {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 선언적 UI 사고방식 =====
// 상태에 따라 표시할 메시지를 반환하세요.
// isLoggedIn: true → "환영합니다, {username}님!"
// isLoggedIn: false → "로그인이 필요합니다."
// isLoading: true → "로딩 중..."

function getUIMessage(state) {
  // TODO: 여기에 코드를 작성하세요
  // state: { isLoggedIn, isLoading, username }
}

// ===== 문제 3: 컴포넌트 구조 설계 =====
// 쇼핑몰 페이지의 컴포넌트 트리를 객체로 표현하세요.
// 최소 구조: App > Header, ProductList, Footer
// ProductList > ProductCard (여러 개)

function designComponentTree() {
  // TODO: 여기에 코드를 작성하세요
  // 반환 형식: { name: "컴포넌트명", children: [...] }
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: React 핵심 개념 테스트 ===");
const features = getReactFeatures();
console.assert(features.length === 3, "3개의 특징이 있어야 합니다");
console.assert(features[0].name && features[0].description, "name과 description이 필요합니다");
console.assert(features.some(f => f.name === "선언적"), "선언적 특징이 포함되어야 합니다");
console.assert(features.some(f => f.name === "컴포넌트 기반"), "컴포넌트 기반 특징이 포함되어야 합니다");
console.assert(features.some(f => f.name === "범용성"), "범용성 특징이 포함되어야 합니다");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 선언적 UI 테스트 ===");
console.assert(
  getUIMessage({ isLoggedIn: false, isLoading: false, username: "" }) === "로그인이 필요합니다.",
  "비로그인 테스트 실패"
);
console.assert(
  getUIMessage({ isLoggedIn: true, isLoading: false, username: "김철수" }) === "환영합니다, 김철수님!",
  "로그인 테스트 실패"
);
console.assert(
  getUIMessage({ isLoggedIn: false, isLoading: true, username: "" }) === "로딩 중...",
  "로딩 테스트 실패"
);
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 컴포넌트 구조 테스트 ===");
const tree = designComponentTree();
console.assert(tree.name === "App", "루트는 App이어야 합니다");
console.assert(tree.children.length >= 3, "최소 3개의 자식 컴포넌트가 필요합니다");
const productList = tree.children.find(c => c.name === "ProductList");
console.assert(productList, "ProductList 컴포넌트가 필요합니다");
console.assert(productList.children && productList.children.length > 0, "ProductList에 자식이 필요합니다");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
