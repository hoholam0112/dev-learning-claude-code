/**
 * 챕터 01 - 예제 2: 컴포넌트 분리와 조합 (포트폴리오 페이지)
 *
 * 학습 포인트:
 * - 컴포넌트를 작은 단위로 분리하는 방법
 * - 컴포넌트 트리 구성
 * - Fragment(<>...</>) 활용
 * - 컴포넌트 재사용
 *
 * 실행 방법:
 * 1. npx create-react-app ch01-demo (이미 생성했다면 생략)
 * 2. cd ch01-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React from "react";

// --- 공통 스타일 ---
const colors = {
  primary: "#2563eb",
  text: "#333",
  lightText: "#666",
  background: "#f8fafc",
  white: "#fff",
  border: "#e2e8f0",
};

// --- 작은 단위의 컴포넌트들 ---

// 네비게이션 링크 하나를 표현하는 컴포넌트
function NavLink() {
  // 여기서는 아직 props를 배우지 않았으므로 하드코딩합니다.
  // 챕터 02에서 props를 통해 동적으로 만드는 방법을 배웁니다.
  const linkStyle = {
    textDecoration: "none",
    color: colors.primary,
    fontWeight: "500",
    padding: "8px 16px",
  };

  return <a href="#section" style={linkStyle}>링크</a>;
}

// 헤더 영역 컴포넌트
function Header() {
  const headerStyle = {
    backgroundColor: colors.white,
    padding: "16px 32px",
    borderBottom: `1px solid ${colors.border}`,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  };

  const logoStyle = {
    fontSize: "1.5rem",
    fontWeight: "bold",
    color: colors.primary,
    margin: 0,
  };

  return (
    <header style={headerStyle}>
      <h1 style={logoStyle}>나의 포트폴리오</h1>
      <nav>
        {/* 같은 컴포넌트를 여러 번 사용할 수 있습니다 */}
        <NavLink />
        <NavLink />
        <NavLink />
      </nav>
    </header>
  );
}

// 아바타 이미지 컴포넌트
function Avatar() {
  const avatarStyle = {
    width: "120px",
    height: "120px",
    borderRadius: "50%",
    border: `3px solid ${colors.primary}`,
    objectFit: "cover",
  };

  return (
    <img
      src="https://via.placeholder.com/120"
      alt="프로필 아바타"
      style={avatarStyle}
    />
  );
}

// 자기소개 텍스트 컴포넌트
function Bio() {
  const name = "김리액트";
  const description = "사용자 경험을 중요시하는 프론트엔드 개발자입니다.";

  return (
    <div style={{ textAlign: "center" }}>
      <h2 style={{ color: colors.text, marginBottom: "8px" }}>{name}</h2>
      <p style={{ color: colors.lightText }}>{description}</p>
    </div>
  );
}

// 소개 섹션 = Avatar + Bio 조합
function AboutSection() {
  const sectionStyle = {
    padding: "40px",
    textAlign: "center",
    backgroundColor: colors.white,
    margin: "20px",
    borderRadius: "12px",
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
  };

  return (
    <section style={sectionStyle}>
      <Avatar />
      <Bio />
    </section>
  );
}

// 프로젝트 카드 컴포넌트
function ProjectCard() {
  const title = "Todo 앱";
  const description = "React로 만든 할 일 관리 애플리케이션";
  const techStack = "React, CSS Modules";

  const cardStyle = {
    backgroundColor: colors.white,
    border: `1px solid ${colors.border}`,
    borderRadius: "8px",
    padding: "20px",
    margin: "10px",
    flex: "1",
    minWidth: "200px",
  };

  return (
    <div style={cardStyle}>
      <h3 style={{ color: colors.text, marginTop: 0 }}>{title}</h3>
      <p style={{ color: colors.lightText }}>{description}</p>
      <p style={{ fontSize: "0.85rem", color: colors.primary }}>
        {techStack}
      </p>
    </div>
  );
}

// 프로젝트 목록 섹션
function ProjectsSection() {
  const sectionStyle = {
    padding: "20px",
    margin: "20px",
  };

  const gridStyle = {
    display: "flex",
    flexWrap: "wrap",
    gap: "16px",
  };

  return (
    <section style={sectionStyle}>
      <h2 style={{ color: colors.text }}>프로젝트</h2>
      <div style={gridStyle}>
        {/* 같은 컴포넌트를 재사용합니다 */}
        {/* 아직 props를 배우지 않았으므로 동일한 내용이 반복됩니다 */}
        <ProjectCard />
        <ProjectCard />
        <ProjectCard />
      </div>
    </section>
  );
}

// 푸터 컴포넌트
function Footer() {
  const currentYear = new Date().getFullYear();

  const footerStyle = {
    textAlign: "center",
    padding: "20px",
    borderTop: `1px solid ${colors.border}`,
    color: colors.lightText,
    fontSize: "0.9rem",
  };

  return (
    <footer style={footerStyle}>
      {/* JavaScript 표현식으로 현재 연도를 동적으로 표시 */}
      <p>&copy; {currentYear} 나의 포트폴리오. All rights reserved.</p>
    </footer>
  );
}

// --- App 컴포넌트 ---
// Fragment(<>...</>)를 사용하여 불필요한 div 래퍼 없이 여러 요소를 반환합니다.
/**
 * 컴포넌트 트리 구조:
 *
 *   App
 *   ├── Header
 *   │   ├── h1 (로고)
 *   │   └── nav
 *   │       ├── NavLink
 *   │       ├── NavLink
 *   │       └── NavLink
 *   ├── main
 *   │   ├── AboutSection
 *   │   │   ├── Avatar
 *   │   │   └── Bio
 *   │   └── ProjectsSection
 *   │       ├── ProjectCard
 *   │       ├── ProjectCard
 *   │       └── ProjectCard
 *   └── Footer
 */
function App() {
  const appStyle = {
    fontFamily: "'Segoe UI', sans-serif",
    backgroundColor: colors.background,
    minHeight: "100vh",
  };

  return (
    <div style={appStyle}>
      <Header />
      <main>
        <AboutSection />
        <ProjectsSection />
      </main>
      <Footer />
    </div>
  );
}

export default App;
