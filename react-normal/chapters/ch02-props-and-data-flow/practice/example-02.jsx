/**
 * 챕터 02 - 예제 2: children을 활용한 레이아웃 컴포넌트
 *
 * 학습 포인트:
 * - children prop의 작동 방식
 * - 레이아웃(Layout) 패턴
 * - 합성(Composition)을 통한 유연한 UI 구성
 * - props와 children을 함께 사용하기
 *
 * 실행 방법:
 * 1. npx create-react-app ch02-demo (이미 생성했다면 생략)
 * 2. cd ch02-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React from "react";

// --- 1. 기본 children 사용 ---

// Panel 컴포넌트: children으로 내부 내용을 유연하게 받습니다.
function Panel({ title, children }) {
  const panelStyle = {
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    margin: "16px 0",
    overflow: "hidden",
    fontFamily: "sans-serif",
  };

  const headerStyle = {
    backgroundColor: "#f3f4f6",
    padding: "12px 16px",
    fontWeight: "bold",
    borderBottom: "1px solid #e5e7eb",
  };

  const bodyStyle = {
    padding: "16px",
  };

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>{title}</div>
      <div style={bodyStyle}>{children}</div>
    </div>
  );
}

// --- 2. 레이아웃 컴포넌트 ---

// PageLayout: 헤더, 메인, 푸터 구조의 레이아웃
function PageLayout({ children }) {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header
        style={{
          backgroundColor: "#1e293b",
          color: "#fff",
          padding: "16px 24px",
          fontSize: "1.2rem",
          fontWeight: "bold",
        }}
      >
        마이 앱
      </header>

      {/* children이 메인 콘텐츠 영역에 렌더링됩니다 */}
      <main style={{ flex: 1, padding: "24px", backgroundColor: "#f8fafc" }}>
        {children}
      </main>

      <footer
        style={{
          backgroundColor: "#1e293b",
          color: "#94a3b8",
          padding: "12px 24px",
          textAlign: "center",
          fontSize: "0.85rem",
        }}
      >
        &copy; 2024 마이 앱. All rights reserved.
      </footer>
    </div>
  );
}

// --- 3. Alert 컴포넌트 (타입별 스타일 + children) ---

function Alert({ type = "info", title, children }) {
  // 타입에 따른 스타일 매핑
  const typeConfig = {
    info: {
      backgroundColor: "#eff6ff",
      borderColor: "#bfdbfe",
      color: "#1e40af",
      icon: "ℹ️",
    },
    success: {
      backgroundColor: "#f0fdf4",
      borderColor: "#bbf7d0",
      color: "#166534",
      icon: "✅",
    },
    warning: {
      backgroundColor: "#fffbeb",
      borderColor: "#fde68a",
      color: "#92400e",
      icon: "⚠️",
    },
    error: {
      backgroundColor: "#fef2f2",
      borderColor: "#fecaca",
      color: "#991b1b",
      icon: "❌",
    },
  };

  const config = typeConfig[type];

  const alertStyle = {
    backgroundColor: config.backgroundColor,
    border: `1px solid ${config.borderColor}`,
    borderRadius: "8px",
    padding: "12px 16px",
    margin: "12px 0",
    color: config.color,
    fontFamily: "sans-serif",
  };

  return (
    <div style={alertStyle}>
      <div style={{ fontWeight: "bold", marginBottom: "4px" }}>
        {config.icon} {title}
      </div>
      {/* children으로 Alert 내용을 유연하게 전달 */}
      <div style={{ fontSize: "0.9rem" }}>{children}</div>
    </div>
  );
}

// --- 4. Modal 컴포넌트 (컨테이너 패턴) ---

function Modal({ title, isOpen = true, children, onClose }) {
  // isOpen이 false이면 아무것도 렌더링하지 않음
  if (!isOpen) return null;

  const overlayStyle = {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  };

  const modalStyle = {
    backgroundColor: "#fff",
    borderRadius: "12px",
    padding: "0",
    width: "90%",
    maxWidth: "500px",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
    fontFamily: "sans-serif",
  };

  const headerStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 20px",
    borderBottom: "1px solid #e5e7eb",
  };

  const closeButtonStyle = {
    background: "none",
    border: "none",
    fontSize: "1.5rem",
    cursor: "pointer",
    color: "#6b7280",
  };

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <div style={headerStyle}>
          <h3 style={{ margin: 0 }}>{title}</h3>
          <button style={closeButtonStyle} onClick={onClose}>
            &times;
          </button>
        </div>
        {/* children으로 모달 내용을 자유롭게 구성 */}
        <div style={{ padding: "20px" }}>{children}</div>
      </div>
    </div>
  );
}

// --- 5. Sidebar Layout (여러 영역에 children 사용) ---
// 이 컴포넌트는 children 대신 명시적 props로 영역을 나눕니다.
function SidebarLayout({ sidebar, children }) {
  const containerStyle = {
    display: "flex",
    gap: "16px",
    margin: "16px 0",
  };

  const sidebarStyle = {
    width: "250px",
    flexShrink: 0,
    backgroundColor: "#f1f5f9",
    borderRadius: "8px",
    padding: "16px",
  };

  const mainStyle = {
    flex: 1,
    backgroundColor: "#fff",
    borderRadius: "8px",
    padding: "16px",
    border: "1px solid #e5e7eb",
  };

  return (
    <div style={containerStyle}>
      <aside style={sidebarStyle}>{sidebar}</aside>
      <div style={mainStyle}>{children}</div>
    </div>
  );
}

// --- App 컴포넌트 ---
function App() {
  return (
    <PageLayout>
      <h1 style={{ fontFamily: "sans-serif" }}>children Prop 활용 예제</h1>

      {/* Panel: 같은 컴포넌트에 다른 내용을 넣기 */}
      <Panel title="공지사항">
        <p>이번 주 목요일에 코드 리뷰가 있습니다.</p>
        <p>참여를 원하시는 분은 슬랙 채널에 남겨주세요.</p>
      </Panel>

      <Panel title="오늘의 할 일">
        <ul>
          <li>React 공부하기</li>
          <li>알고리즘 1문제 풀기</li>
          <li>블로그 글 작성하기</li>
        </ul>
      </Panel>

      {/* Alert: 타입별로 다른 스타일 + 다른 내용 */}
      <h2 style={{ fontFamily: "sans-serif" }}>Alert 컴포넌트</h2>
      <Alert type="info" title="안내">
        <p>React 18 버전부터 자동 배칭(Automatic Batching)이 지원됩니다.</p>
      </Alert>
      <Alert type="success" title="성공">
        <p>프로필이 성공적으로 업데이트되었습니다.</p>
      </Alert>
      <Alert type="warning" title="경고">
        <p>비밀번호가 30일 이상 변경되지 않았습니다.</p>
      </Alert>
      <Alert type="error" title="오류">
        <p>서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.</p>
      </Alert>

      {/* SidebarLayout: sidebar prop과 children을 함께 사용 */}
      <h2 style={{ fontFamily: "sans-serif" }}>Sidebar 레이아웃</h2>
      <SidebarLayout
        sidebar={
          <nav>
            <h3>메뉴</h3>
            <ul style={{ listStyle: "none", padding: 0 }}>
              <li style={{ padding: "8px 0" }}>대시보드</li>
              <li style={{ padding: "8px 0" }}>프로필</li>
              <li style={{ padding: "8px 0" }}>설정</li>
            </ul>
          </nav>
        }
      >
        <h3>메인 콘텐츠</h3>
        <p>
          sidebar prop에는 사이드바 영역의 JSX를,
          children에는 메인 콘텐츠 영역의 JSX를 전달합니다.
        </p>
        <p>
          이렇게 하면 하나의 레이아웃 컴포넌트를 다양한 페이지에서
          재사용할 수 있습니다.
        </p>
      </SidebarLayout>
    </PageLayout>
  );
}

export default App;
