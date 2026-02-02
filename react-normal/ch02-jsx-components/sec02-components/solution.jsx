// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 블로그 컴포넌트 구조 설계 =====
function designBlogComponents() {
  return {
    name: "App",
    role: "블로그 애플리케이션의 루트 컴포넌트",
    children: [
      {
        name: "Header",
        role: "사이트 로고, 네비게이션을 표시",
        children: [],
      },
      {
        name: "ArticleList",
        role: "게시글 목록을 표시",
        children: [
          { name: "ArticleCard", role: "개별 게시글 카드", children: [] },
          { name: "ArticleCard", role: "개별 게시글 카드", children: [] },
          { name: "ArticleCard", role: "개별 게시글 카드", children: [] },
        ],
      },
      {
        name: "Sidebar",
        role: "검색, 태그 등 부가 기능",
        children: [
          { name: "SearchBox", role: "게시글 검색", children: [] },
          { name: "TagList", role: "태그 목록 표시", children: [] },
        ],
      },
      {
        name: "Footer",
        role: "저작권 정보, 링크 표시",
        children: [],
      },
    ],
  };
}

// ===== 문제 2: 컴포넌트 트리 시각화 =====
function renderComponentTree(component, depth = 0) {
  // 현재 컴포넌트의 들여쓰기된 이름
  const indent = "  ".repeat(depth);
  let result = `${indent}${component.name}`;

  // 재귀적으로 자식 컴포넌트 처리
  if (component.children && component.children.length > 0) {
    for (const child of component.children) {
      result += "\n" + renderComponentTree(child, depth + 1);
    }
  }

  return result;
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 블로그 구조 테스트 ===");
const blog = designBlogComponents();
console.assert(blog.name === "App", "루트는 App이어야 합니다");
console.assert(blog.children.length >= 4, "최소 4개의 자식이 필요합니다");
const articleList = blog.children.find(c => c.name === "ArticleList");
console.assert(articleList, "ArticleList가 필요합니다");
console.assert(articleList.children.length > 0, "ArticleList에 자식이 필요합니다");
const sidebar = blog.children.find(c => c.name === "Sidebar");
console.assert(sidebar, "Sidebar가 필요합니다");
console.assert(sidebar.children.length >= 2, "Sidebar에 최소 2개 자식 필요합니다");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 트리 시각화 테스트 ===");
const testTree = {
  name: "App",
  children: [
    { name: "Header", children: [] },
    {
      name: "Main",
      children: [
        { name: "Content", children: [] },
      ],
    },
  ],
};
const result = renderComponentTree(testTree);
console.assert(result.includes("App"), "App이 포함되어야 합니다");
console.assert(result.includes("  Header"), "Header가 들여쓰기되어야 합니다");
console.assert(result.includes("  Main"), "Main이 들여쓰기되어야 합니다");
console.assert(result.includes("    Content"), "Content가 이중 들여쓰기되어야 합니다");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
