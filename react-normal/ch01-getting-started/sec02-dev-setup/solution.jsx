// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 프로젝트 구조 이해 =====
function getProjectStructure() {
  return {
    "src/main.jsx": "앱의 시작점(엔트리 포인트). ReactDOM으로 루트 컴포넌트를 렌더링합니다.",
    "src/App.jsx": "메인 컴포넌트. 앱의 전체 레이아웃과 구조를 정의합니다.",
    "public/": "정적 파일 디렉토리. 이미지, 폰트 등 빌드 없이 제공되는 파일을 저장합니다.",
    "package.json": "프로젝트 설정 파일. 의존성, 스크립트, 메타데이터를 정의합니다.",
    "index.html": "HTML 진입점. React 앱이 마운트되는 root 요소를 포함합니다.",
  };
}

// ===== 문제 2: npm 스크립트 매핑 =====
function getNpmScripts() {
  return {
    dev: {
      command: "vite",
      description: "개발 서버를 실행합니다. HMR로 코드 변경이 즉시 반영됩니다.",
    },
    build: {
      command: "vite build",
      description: "프로덕션용으로 앱을 빌드합니다. 최적화된 정적 파일을 생성합니다.",
    },
    preview: {
      command: "vite preview",
      description: "빌드된 결과를 로컬에서 미리 봅니다. 배포 전 확인에 사용합니다.",
    },
  };
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
