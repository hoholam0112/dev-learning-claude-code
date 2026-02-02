// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 프로젝트 구조 이해 =====
// React 프로젝트의 주요 파일/디렉토리 역할을 매핑하세요.
// 키: 파일/디렉토리명, 값: 역할 설명

function getProjectStructure() {
  // TODO: 여기에 코드를 작성하세요
  // 포함해야 할 항목: "src/main.jsx", "src/App.jsx", "public/", "package.json", "index.html"
}

// ===== 문제 2: npm 스크립트 매핑 =====
// Vite React 프로젝트의 npm 스크립트를 매핑하세요.
// 키: 명령어 (dev, build, preview), 값: { command: 실행 명령, description: 설명 }

function getNpmScripts() {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 프로젝트 구조 테스트 ===");
const structure = getProjectStructure();
console.assert(structure["src/main.jsx"], "main.jsx 정보가 필요합니다");
console.assert(structure["src/App.jsx"], "App.jsx 정보가 필요합니다");
console.assert(structure["public/"], "public/ 정보가 필요합니다");
console.assert(structure["package.json"], "package.json 정보가 필요합니다");
console.assert(structure["index.html"], "index.html 정보가 필요합니다");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: npm 스크립트 테스트 ===");
const scripts = getNpmScripts();
console.assert(scripts.dev && scripts.dev.command, "dev 스크립트 정보가 필요합니다");
console.assert(scripts.build && scripts.build.command, "build 스크립트 정보가 필요합니다");
console.assert(scripts.preview && scripts.preview.command, "preview 스크립트 정보가 필요합니다");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
