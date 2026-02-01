/**
 * 챕터 03 - 예제 1: 카운터 앱과 토글 UI
 *
 * 학습 포인트:
 * - useState Hook 사용법
 * - 이벤트 핸들러 연결
 * - 상태 변경과 리렌더링
 * - 함수형 업데이트 (prev => prev + 1)
 * - 불리언 상태를 활용한 토글
 *
 * 실행 방법:
 * 1. npx create-react-app ch03-demo
 * 2. cd ch03-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React, { useState } from "react";

// --- 1. 기본 카운터 ---
function Counter() {
  // useState로 상태 선언: [상태값, 상태변경함수] = useState(초기값)
  const [count, setCount] = useState(0);

  // 이벤트 핸들러 함수들
  const handleIncrement = () => {
    setCount(count + 1);
  };

  const handleDecrement = () => {
    // 0 미만으로 내려가지 않도록 보호
    setCount(count > 0 ? count - 1 : 0);
  };

  const handleReset = () => {
    setCount(0);
  };

  const counterStyle = {
    textAlign: "center",
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const buttonStyle = {
    padding: "8px 20px",
    margin: "4px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "500",
  };

  return (
    <div style={counterStyle}>
      <h2>기본 카운터</h2>
      <p style={{ fontSize: "3rem", fontWeight: "bold", margin: "16px 0" }}>
        {count}
      </p>
      <div>
        <button
          onClick={handleDecrement}
          style={{ ...buttonStyle, backgroundColor: "#ef4444", color: "#fff" }}
        >
          -1
        </button>
        <button
          onClick={handleReset}
          style={{ ...buttonStyle, backgroundColor: "#6b7280", color: "#fff" }}
        >
          초기화
        </button>
        <button
          onClick={handleIncrement}
          style={{ ...buttonStyle, backgroundColor: "#22c55e", color: "#fff" }}
        >
          +1
        </button>
      </div>
    </div>
  );
}

// --- 2. 단계 조절 카운터 (함수형 업데이트 활용) ---
function StepCounter() {
  const [count, setCount] = useState(0);
  const [step, setStep] = useState(1);

  // 함수형 업데이트: 이전 값을 기반으로 업데이트
  const handleAdd = () => {
    setCount((prev) => prev + step);
  };

  const handleSubtract = () => {
    setCount((prev) => prev - step);
  };

  const containerStyle = {
    textAlign: "center",
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const stepButtonStyle = {
    padding: "4px 12px",
    margin: "2px",
    border: "1px solid #d1d5db",
    borderRadius: "4px",
    cursor: "pointer",
    backgroundColor: "#fff",
  };

  const buttonStyle = {
    padding: "8px 24px",
    margin: "4px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "1rem",
    color: "#fff",
  };

  return (
    <div style={containerStyle}>
      <h2>단계 조절 카운터</h2>

      {/* 단계 선택 */}
      <div style={{ marginBottom: "16px" }}>
        <span>단계: </span>
        {[1, 5, 10, 100].map((s) => (
          <button
            key={s}
            onClick={() => setStep(s)}
            style={{
              ...stepButtonStyle,
              backgroundColor: step === s ? "#2563eb" : "#fff",
              color: step === s ? "#fff" : "#333",
            }}
          >
            {s}
          </button>
        ))}
      </div>

      <p style={{ fontSize: "3rem", fontWeight: "bold", margin: "16px 0" }}>
        {count}
      </p>

      <div>
        <button
          onClick={handleSubtract}
          style={{ ...buttonStyle, backgroundColor: "#ef4444" }}
        >
          -{step}
        </button>
        <button
          onClick={() => setCount(0)}
          style={{ ...buttonStyle, backgroundColor: "#6b7280" }}
        >
          초기화
        </button>
        <button
          onClick={handleAdd}
          style={{ ...buttonStyle, backgroundColor: "#22c55e" }}
        >
          +{step}
        </button>
      </div>
    </div>
  );
}

// --- 3. 다크모드 토글 ---
function DarkModeToggle() {
  // 불리언 상태로 다크모드 on/off 관리
  const [isDarkMode, setIsDarkMode] = useState(false);

  // 토글: 현재 상태의 반대로 변경
  const handleToggle = () => {
    setIsDarkMode((prev) => !prev);
  };

  const containerStyle = {
    padding: "24px",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
    backgroundColor: isDarkMode ? "#1e293b" : "#ffffff",
    color: isDarkMode ? "#e2e8f0" : "#1e293b",
    border: `1px solid ${isDarkMode ? "#334155" : "#e5e7eb"}`,
    transition: "all 0.3s ease",
  };

  const toggleTrackStyle = {
    width: "60px",
    height: "30px",
    borderRadius: "15px",
    backgroundColor: isDarkMode ? "#2563eb" : "#d1d5db",
    position: "relative",
    cursor: "pointer",
    transition: "background-color 0.3s",
    display: "inline-block",
  };

  const toggleThumbStyle = {
    width: "26px",
    height: "26px",
    borderRadius: "50%",
    backgroundColor: "#fff",
    position: "absolute",
    top: "2px",
    left: isDarkMode ? "32px" : "2px",
    transition: "left 0.3s",
    boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
  };

  return (
    <div style={containerStyle}>
      <h2>다크모드 토글</h2>
      <p>현재 모드: {isDarkMode ? "다크 🌙" : "라이트 ☀️"}</p>

      <div style={toggleTrackStyle} onClick={handleToggle}>
        <div style={toggleThumbStyle} />
      </div>

      <p style={{ marginTop: "16px" }}>
        이 영역은 {isDarkMode ? "어두운" : "밝은"} 테마가 적용되어 있습니다.
        토글을 클릭하여 테마를 전환하세요.
      </p>
    </div>
  );
}

// --- 4. 아코디언 (열고 닫기) ---
function Accordion() {
  // 현재 열린 패널의 인덱스 (-1이면 모두 닫힘)
  const [openIndex, setOpenIndex] = useState(-1);

  const items = [
    {
      title: "React란 무엇인가요?",
      content:
        "React는 Facebook에서 개발한 UI 라이브러리입니다. 컴포넌트 기반으로 사용자 인터페이스를 구축할 수 있습니다.",
    },
    {
      title: "State가 왜 필요한가요?",
      content:
        "State는 컴포넌트의 동적인 데이터를 관리합니다. State가 변경되면 React가 자동으로 화면을 업데이트합니다.",
    },
    {
      title: "Props와 State의 차이는?",
      content:
        "Props는 부모로부터 전달받는 읽기 전용 데이터이고, State는 컴포넌트 내부에서 관리하는 변경 가능한 데이터입니다.",
    },
  ];

  const containerStyle = {
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    overflow: "hidden",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  return (
    <div>
      <h2>아코디언 (FAQ)</h2>
      <div style={containerStyle}>
        {items.map((item, index) => (
          <div key={index}>
            <button
              onClick={() =>
                // 이미 열린 패널을 클릭하면 닫고, 다른 패널을 클릭하면 열기
                setOpenIndex(openIndex === index ? -1 : index)
              }
              style={{
                width: "100%",
                padding: "16px",
                border: "none",
                borderBottom: "1px solid #e5e7eb",
                backgroundColor: openIndex === index ? "#eff6ff" : "#fff",
                cursor: "pointer",
                textAlign: "left",
                fontSize: "1rem",
                fontWeight: "600",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              {item.title}
              <span>{openIndex === index ? "▲" : "▼"}</span>
            </button>
            {/* 열린 패널의 내용만 표시 */}
            {openIndex === index && (
              <div
                style={{
                  padding: "16px",
                  backgroundColor: "#f9fafb",
                  borderBottom: "1px solid #e5e7eb",
                  lineHeight: 1.6,
                }}
              >
                {item.content}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// --- App 컴포넌트 ---
function App() {
  return (
    <div
      style={{
        padding: "24px",
        maxWidth: "600px",
        margin: "0 auto",
        fontFamily: "sans-serif",
      }}
    >
      <h1 style={{ textAlign: "center" }}>챕터 03: State와 이벤트</h1>

      <Counter />
      <StepCounter />
      <DarkModeToggle />
      <Accordion />
    </div>
  );
}

export default App;
