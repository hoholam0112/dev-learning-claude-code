/**
 * 챕터 01 - 예제 1: 프로필 카드 컴포넌트
 *
 * 학습 포인트:
 * - JSX 문법의 기본 규칙
 * - 함수형 컴포넌트 정의 방법
 * - 중괄호를 사용한 JavaScript 표현식 삽입
 * - className, 인라인 스타일 사용법
 *
 * 실행 방법:
 * 1. npx create-react-app ch01-demo
 * 2. cd ch01-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React from "react";

// --- 1. 가장 기본적인 컴포넌트 ---
// 컴포넌트는 JSX를 반환하는 함수입니다.
// 컴포넌트 이름은 반드시 대문자로 시작합니다.
function Welcome() {
  return <h1>React 세계에 오신 것을 환영합니다!</h1>;
}

// --- 2. JavaScript 표현식을 사용하는 컴포넌트 ---
// 중괄호 {} 안에 JavaScript 표현식을 넣을 수 있습니다.
function UserGreeting() {
  const userName = "김리액트";
  const currentHour = new Date().getHours();

  // 삼항 연산자는 표현식이므로 JSX 안에서 사용 가능합니다.
  const greeting = currentHour < 12 ? "좋은 아침이에요" : "좋은 하루 보내세요";

  return (
    <div>
      <h2>
        {userName}님, {greeting}!
      </h2>
      <p>
        현재 시각: {currentHour}시
      </p>
    </div>
  );
}

// --- 3. 스타일이 적용된 프로필 카드 컴포넌트 ---
// 인라인 스타일은 객체로 전달합니다 (camelCase 사용).
function ProfileCard() {
  const name = "김리액트";
  const role = "프론트엔드 개발자";
  const skills = ["React", "TypeScript", "Next.js"];
  const experienceYears = 3;

  // 인라인 스타일 객체
  const cardStyle = {
    border: "1px solid #e0e0e0",
    borderRadius: "12px",
    padding: "24px",
    maxWidth: "350px",
    margin: "20px auto",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
    fontFamily: "sans-serif",
  };

  const avatarStyle = {
    width: "80px",
    height: "80px",
    borderRadius: "50%",
    objectFit: "cover",
    display: "block",
    margin: "0 auto 12px",
  };

  const nameStyle = {
    fontSize: "1.4rem",
    fontWeight: "bold",
    textAlign: "center",
    margin: "0 0 4px 0",
    color: "#333",
  };

  const roleStyle = {
    color: "#666",
    textAlign: "center",
    margin: "0 0 16px 0",
  };

  const skillBadgeStyle = {
    display: "inline-block",
    backgroundColor: "#e3f2fd",
    color: "#1976d2",
    padding: "4px 10px",
    borderRadius: "12px",
    fontSize: "0.85rem",
    marginRight: "6px",
    marginBottom: "6px",
  };

  return (
    <div style={cardStyle}>
      {/* alt 속성에 표현식 사용 */}
      <img
        src="https://via.placeholder.com/80"
        alt={`${name}의 프로필 사진`}
        style={avatarStyle}
      />
      <h2 style={nameStyle}>{name}</h2>
      <p style={roleStyle}>{role}</p>

      {/* 구분선 - self-closing 태그 */}
      <hr />

      <div>
        <p style={{ fontWeight: "bold", marginBottom: "8px" }}>기술 스택:</p>
        {/* 배열의 join 메서드 대신 각각 뱃지로 표현 */}
        <div>
          {skills.map((skill) => (
            <span key={skill} style={skillBadgeStyle}>
              {skill}
            </span>
          ))}
        </div>
      </div>

      <p style={{ marginTop: "12px", color: "#888", fontSize: "0.9rem" }}>
        경력: {experienceYears}년차
      </p>
    </div>
  );
}

// --- 4. App 컴포넌트 (루트 컴포넌트) ---
// 여러 컴포넌트를 조합하여 하나의 화면을 구성합니다.
function App() {
  return (
    <div style={{ padding: "20px" }}>
      {/* 컴포넌트를 태그처럼 사용합니다 */}
      <Welcome />
      <UserGreeting />
      <ProfileCard />
    </div>
  );
}

export default App;
