// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: React 핵심 개념 정리 =====
function getReactFeatures() {
  return [
    {
      name: "선언적",
      description: "어떻게 만들지가 아니라 무엇을 보여줄지 기술하는 방식으로, 코드가 읽기 쉽고 예측 가능합니다.",
    },
    {
      name: "컴포넌트 기반",
      description: "UI를 독립적이고 재사용 가능한 조각으로 나누어 관리하며, 각 컴포넌트가 자체 로직을 가집니다.",
    },
    {
      name: "범용성",
      description: "웹(React), 모바일(React Native), 데스크톱 등 다양한 플랫폼에서 사용할 수 있습니다.",
    },
  ];
}

// ===== 문제 2: 선언적 UI 사고방식 =====
function getUIMessage(state) {
  // 선언적 사고: 현재 상태에 따라 보여줄 내용을 결정
  // 로딩 상태를 먼저 확인 (가장 우선순위가 높음)
  if (state.isLoading) return "로딩 중...";
  // 로그인 상태에 따라 메시지 결정
  if (state.isLoggedIn) return `환영합니다, ${state.username}님!`;
  return "로그인이 필요합니다.";
}

// ===== 문제 3: 컴포넌트 구조 설계 =====
function designComponentTree() {
  // 컴포넌트 트리를 객체 구조로 표현
  // 실제 React에서는 각 컴포넌트가 별도의 함수/파일이 됨
  return {
    name: "App",
    children: [
      {
        name: "Header",
        children: [
          { name: "Logo", children: [] },
          { name: "Navigation", children: [] },
          { name: "CartIcon", children: [] },
        ],
      },
      {
        name: "ProductList",
        children: [
          { name: "ProductCard", children: [] },
          { name: "ProductCard", children: [] },
          { name: "ProductCard", children: [] },
        ],
      },
      {
        name: "Footer",
        children: [],
      },
    ],
  };
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
