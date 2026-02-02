// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 블로그 컴포넌트 구조 설계 =====
// 블로그 페이지의 컴포넌트 트리를 설계하세요.
// 구조: App > Header, ArticleList, Sidebar, Footer
// ArticleList > ArticleCard (여러 개)
// Sidebar > SearchBox, TagList
// 각 컴포넌트: { name: "이름", role: "역할", children: [...] }

function designBlogComponents() {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 컴포넌트 트리 시각화 =====
// 컴포넌트 트리를 문자열로 시각화하세요.
// 각 레벨마다 "  " (공백 2칸)으로 들여쓰기합니다.
// 예: { name: "App", children: [{ name: "Header", children: [] }] }
// → "App\n  Header"

function renderComponentTree(component, depth = 0) {
  // TODO: 여기에 코드를 작성하세요
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
