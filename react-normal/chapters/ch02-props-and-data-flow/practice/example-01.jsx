/**
 * 챕터 02 - 예제 1: 재사용 가능한 Button과 Card 컴포넌트
 *
 * 학습 포인트:
 * - props로 컴포넌트에 데이터 전달하기
 * - 구조 분해 할당으로 props 받기
 * - 기본값 설정하기
 * - 다양한 타입의 props (문자열, 숫자, 불리언, 배열, 함수)
 *
 * 실행 방법:
 * 1. npx create-react-app ch02-demo
 * 2. cd ch02-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React from "react";

// --- 1. 재사용 가능한 Button 컴포넌트 ---
// 구조 분해 할당과 기본값을 사용합니다.
function Button({ text = "클릭", variant = "primary", size = "medium", onClick }) {
  // variant에 따른 스타일 매핑
  const variantStyles = {
    primary: { backgroundColor: "#2563eb", color: "#fff" },
    secondary: { backgroundColor: "#6b7280", color: "#fff" },
    danger: { backgroundColor: "#dc2626", color: "#fff" },
    outline: {
      backgroundColor: "transparent",
      color: "#2563eb",
      border: "2px solid #2563eb",
    },
  };

  // size에 따른 패딩 매핑
  const sizeStyles = {
    small: { padding: "4px 12px", fontSize: "0.85rem" },
    medium: { padding: "8px 20px", fontSize: "1rem" },
    large: { padding: "12px 28px", fontSize: "1.15rem" },
  };

  const buttonStyle = {
    ...variantStyles[variant],
    ...sizeStyles[size],
    border: variantStyles[variant].border || "none",
    borderRadius: "6px",
    cursor: "pointer",
    margin: "4px",
    fontWeight: "500",
    transition: "opacity 0.2s",
  };

  return (
    <button style={buttonStyle} onClick={onClick}>
      {text}
    </button>
  );
}

// --- 2. 재사용 가능한 Card 컴포넌트 ---
function Card({ title, subtitle, imageUrl, tags = [], footer }) {
  const cardStyle = {
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    overflow: "hidden",
    maxWidth: "320px",
    margin: "12px",
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
    fontFamily: "sans-serif",
  };

  const imageStyle = {
    width: "100%",
    height: "180px",
    objectFit: "cover",
  };

  const bodyStyle = {
    padding: "16px",
  };

  const tagStyle = {
    display: "inline-block",
    backgroundColor: "#eff6ff",
    color: "#2563eb",
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "0.8rem",
    marginRight: "4px",
    marginBottom: "4px",
  };

  const footerStyle = {
    padding: "12px 16px",
    borderTop: "1px solid #e5e7eb",
    backgroundColor: "#f9fafb",
    fontSize: "0.9rem",
    color: "#6b7280",
  };

  return (
    <div style={cardStyle}>
      {/* imageUrl이 있을 때만 이미지 표시 */}
      {imageUrl && <img src={imageUrl} alt={title} style={imageStyle} />}

      <div style={bodyStyle}>
        <h3 style={{ margin: "0 0 4px 0", color: "#111" }}>{title}</h3>
        {subtitle && (
          <p style={{ margin: "0 0 12px 0", color: "#6b7280" }}>{subtitle}</p>
        )}

        {/* 태그 배열이 있으면 표시 */}
        {tags.length > 0 && (
          <div>
            {tags.map((tag) => (
              <span key={tag} style={tagStyle}>
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* footer가 있을 때만 푸터 표시 */}
      {footer && <div style={footerStyle}>{footer}</div>}
    </div>
  );
}

// --- 3. UserProfile 컴포넌트 ---
// 여러 타입의 props를 받는 예제
function UserProfile({ name, age, role, isOnline = false, skills = [] }) {
  const profileStyle = {
    display: "flex",
    alignItems: "center",
    padding: "16px",
    margin: "8px 0",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    fontFamily: "sans-serif",
  };

  const statusDotStyle = {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    backgroundColor: isOnline ? "#22c55e" : "#9ca3af",
    marginRight: "12px",
  };

  return (
    <div style={profileStyle}>
      <div style={statusDotStyle} />
      <div>
        <h3 style={{ margin: "0 0 2px 0" }}>
          {name} <span style={{ color: "#999", fontWeight: "normal" }}>({age}세)</span>
        </h3>
        <p style={{ margin: "0 0 4px 0", color: "#666" }}>{role}</p>
        <p style={{ margin: 0, fontSize: "0.85rem", color: "#2563eb" }}>
          {skills.join(" · ")}
        </p>
      </div>
    </div>
  );
}

// --- App 컴포넌트 ---
function App() {
  // 이벤트 핸들러 함수를 props로 전달
  const handleClick = (action) => {
    alert(`${action} 버튼이 클릭되었습니다!`);
  };

  return (
    <div style={{ padding: "24px", fontFamily: "sans-serif", maxWidth: "800px", margin: "0 auto" }}>
      <h1>챕터 02: Props와 데이터 흐름</h1>

      {/* --- Button 컴포넌트 재사용 --- */}
      <section style={{ marginBottom: "40px" }}>
        <h2>1. Button 컴포넌트</h2>
        <p style={{ color: "#666" }}>같은 Button 컴포넌트를 다른 props로 재사용합니다.</p>

        <h3>variant (스타일 변형)</h3>
        <div>
          <Button text="Primary" variant="primary" onClick={() => handleClick("Primary")} />
          <Button text="Secondary" variant="secondary" onClick={() => handleClick("Secondary")} />
          <Button text="Danger" variant="danger" onClick={() => handleClick("Danger")} />
          <Button text="Outline" variant="outline" onClick={() => handleClick("Outline")} />
        </div>

        <h3>size (크기)</h3>
        <div>
          <Button text="Small" size="small" />
          <Button text="Medium" size="medium" />
          <Button text="Large" size="large" />
        </div>

        <h3>기본값 사용</h3>
        <div>
          {/* props를 전달하지 않으면 기본값이 적용됩니다 */}
          <Button />
          <p style={{ fontSize: "0.85rem", color: "#999" }}>
            아무 props도 전달하지 않으면 text="클릭", variant="primary", size="medium"
          </p>
        </div>
      </section>

      {/* --- Card 컴포넌트 재사용 --- */}
      <section style={{ marginBottom: "40px" }}>
        <h2>2. Card 컴포넌트</h2>
        <div style={{ display: "flex", flexWrap: "wrap" }}>
          <Card
            title="React 입문"
            subtitle="컴포넌트 기반 UI 라이브러리"
            imageUrl="https://via.placeholder.com/320x180/2563eb/fff?text=React"
            tags={["React", "JavaScript", "Frontend"]}
            footer="2024년 1월 게시"
          />
          <Card
            title="TypeScript 기초"
            subtitle="타입 안전한 JavaScript"
            imageUrl="https://via.placeholder.com/320x180/3178c6/fff?text=TypeScript"
            tags={["TypeScript", "정적타입"]}
            footer="2024년 2월 게시"
          />
          <Card
            title="간단한 카드"
            subtitle="이미지와 태그가 없는 카드"
            /* imageUrl, tags, footer 를 전달하지 않음 - 기본값/조건부 렌더링 */
          />
        </div>
      </section>

      {/* --- UserProfile 컴포넌트 --- */}
      <section>
        <h2>3. UserProfile 컴포넌트</h2>
        <UserProfile
          name="김리액트"
          age={25}
          role="프론트엔드 개발자"
          isOnline={true}
          skills={["React", "TypeScript", "Next.js"]}
        />
        <UserProfile
          name="이백엔드"
          age={30}
          role="백엔드 개발자"
          isOnline={false}
          skills={["Node.js", "PostgreSQL", "Docker"]}
        />
        <UserProfile
          name="박신입"
          age={22}
          role="인턴"
          /* isOnline과 skills를 전달하지 않으면 기본값 사용 */
        />
      </section>
    </div>
  );
}

export default App;
