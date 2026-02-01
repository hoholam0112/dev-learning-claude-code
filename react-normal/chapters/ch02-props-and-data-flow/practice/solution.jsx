/**
 * 챕터 02 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 *
 * 실행 방법:
 * 1. npx create-react-app ch02-solution (이미 생성했다면 생략)
 * 2. cd ch02-solution
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React from "react";

// ============================================================
// 문제 1: 재사용 가능한 Badge 컴포넌트
// ============================================================

function Badge({ text, color = "gray", size = "medium" }) {
  // 색상 매핑 객체
  const colorMap = {
    green: { backgroundColor: "#dcfce7", color: "#166534" },
    red: { backgroundColor: "#fef2f2", color: "#991b1b" },
    blue: { backgroundColor: "#eff6ff", color: "#1e40af" },
    gray: { backgroundColor: "#f3f4f6", color: "#374151" },
  };

  // 크기 매핑 객체
  const sizeMap = {
    small: { padding: "2px 6px", fontSize: "0.7rem" },
    medium: { padding: "4px 10px", fontSize: "0.85rem" },
    large: { padding: "6px 14px", fontSize: "1rem" },
  };

  const badgeStyle = {
    display: "inline-block",
    ...colorMap[color],
    ...sizeMap[size],
    borderRadius: "9999px",
    fontWeight: "600",
    margin: "4px",
    fontFamily: "sans-serif",
  };

  return <span style={badgeStyle}>{text}</span>;
}

function BadgeDemo() {
  return (
    <section style={{ marginBottom: "40px" }}>
      <h2>문제 1: Badge 컴포넌트</h2>

      <h3>색상 변형</h3>
      <div>
        <Badge text="성공" color="green" />
        <Badge text="오류" color="red" />
        <Badge text="정보" color="blue" />
        <Badge text="기본" color="gray" />
        <Badge text="기본값" /> {/* 기본값: color="gray", size="medium" */}
      </div>

      <h3>크기 변형</h3>
      <div>
        <Badge text="Small" color="blue" size="small" />
        <Badge text="Medium" color="blue" size="medium" />
        <Badge text="Large" color="blue" size="large" />
      </div>

      <h3>실제 사용 예시</h3>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span style={{ fontWeight: "bold" }}>React</span>
        <Badge text="v18.2" color="blue" size="small" />
        <Badge text="안정" color="green" size="small" />
      </div>
    </section>
  );
}

// ============================================================
// 문제 2: 상품 카드 시스템
// ============================================================

function ProductCard({
  name,
  price,
  discount = 0,
  imageUrl,
  tags = [],
  inStock = true,
}) {
  // 할인가 계산
  const discountedPrice = Math.round(price * (1 - discount / 100));

  const cardStyle = {
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    overflow: "hidden",
    width: "260px",
    margin: "8px",
    fontFamily: "sans-serif",
    opacity: inStock ? 1 : 0.5,
    position: "relative",
    transition: "opacity 0.3s",
  };

  const imageStyle = {
    width: "100%",
    height: "200px",
    objectFit: "cover",
    display: "block",
  };

  const bodyStyle = {
    padding: "14px",
  };

  const tagStyle = {
    display: "inline-block",
    backgroundColor: "#f3f4f6",
    color: "#4b5563",
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "0.75rem",
    marginRight: "4px",
    marginBottom: "4px",
  };

  const discountBadgeStyle = {
    position: "absolute",
    top: "10px",
    right: "10px",
    backgroundColor: "#dc2626",
    color: "#fff",
    padding: "4px 8px",
    borderRadius: "4px",
    fontSize: "0.85rem",
    fontWeight: "bold",
  };

  const soldOutStyle = {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    color: "#fff",
    padding: "8px 24px",
    borderRadius: "8px",
    fontSize: "1.2rem",
    fontWeight: "bold",
  };

  return (
    <div style={cardStyle}>
      <img src={imageUrl} alt={name} style={imageStyle} />

      {/* 할인율 뱃지 */}
      {discount > 0 && <div style={discountBadgeStyle}>{discount}% OFF</div>}

      {/* 품절 표시 */}
      {!inStock && <div style={soldOutStyle}>품절</div>}

      <div style={bodyStyle}>
        <h3 style={{ margin: "0 0 8px 0", fontSize: "1rem" }}>{name}</h3>

        {/* 가격 표시 */}
        <div style={{ marginBottom: "8px" }}>
          {discount > 0 ? (
            <>
              {/* 원래 가격 (취소선) */}
              <span
                style={{
                  textDecoration: "line-through",
                  color: "#9ca3af",
                  marginRight: "8px",
                  fontSize: "0.9rem",
                }}
              >
                {price.toLocaleString()}원
              </span>
              {/* 할인가 (강조) */}
              <span
                style={{
                  color: "#dc2626",
                  fontWeight: "bold",
                  fontSize: "1.1rem",
                }}
              >
                {discountedPrice.toLocaleString()}원
              </span>
            </>
          ) : (
            <span style={{ fontWeight: "bold", fontSize: "1.1rem" }}>
              {price.toLocaleString()}원
            </span>
          )}
        </div>

        {/* 태그 */}
        {tags.length > 0 && (
          <div>
            {tags.map((tag) => (
              <span key={tag} style={tagStyle}>
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ProductCardDemo() {
  return (
    <section style={{ marginBottom: "40px" }}>
      <h2>문제 2: 상품 카드 시스템</h2>
      <div style={{ display: "flex", flexWrap: "wrap" }}>
        <ProductCard
          name="무선 블루투스 이어폰"
          price={89000}
          discount={20}
          imageUrl="https://via.placeholder.com/260x200/4F46E5/fff?text=Earbuds"
          tags={["베스트", "무료배송"]}
          inStock={true}
        />
        <ProductCard
          name="노트북 거치대"
          price={35000}
          imageUrl="https://via.placeholder.com/260x200/059669/fff?text=Stand"
          tags={["인기"]}
          inStock={true}
        />
        <ProductCard
          name="기계식 키보드"
          price={120000}
          discount={15}
          imageUrl="https://via.placeholder.com/260x200/DC2626/fff?text=Keyboard"
          tags={["한정판", "청축"]}
          inStock={false}
        />
        <ProductCard
          name="USB-C 허브"
          price={45000}
          imageUrl="https://via.placeholder.com/260x200/D97706/fff?text=USB+Hub"
          tags={["필수템"]}
        />
      </div>
    </section>
  );
}

// ============================================================
// 문제 3: children을 활용한 탭 UI
// ============================================================

// 탭 패널 컴포넌트
function TabPanel({ title, children }) {
  const panelStyle = {
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    margin: "12px 0",
    overflow: "hidden",
    fontFamily: "sans-serif",
  };

  const titleStyle = {
    backgroundColor: "#1e293b",
    color: "#fff",
    padding: "12px 16px",
    fontWeight: "bold",
    fontSize: "1rem",
  };

  const contentStyle = {
    padding: "16px",
    backgroundColor: "#fff",
  };

  return (
    <div style={panelStyle}>
      <div style={titleStyle}>{title}</div>
      <div style={contentStyle}>{children}</div>
    </div>
  );
}

// 정보 박스 컴포넌트
function InfoBox({ variant = "note", children }) {
  const variantConfig = {
    tip: {
      backgroundColor: "#f0fdf4",
      borderLeft: "4px solid #22c55e",
      icon: "💡",
      label: "팁",
    },
    note: {
      backgroundColor: "#eff6ff",
      borderLeft: "4px solid #3b82f6",
      icon: "📝",
      label: "노트",
    },
    warning: {
      backgroundColor: "#fffbeb",
      borderLeft: "4px solid #f59e0b",
      icon: "⚠️",
      label: "주의",
    },
  };

  const config = variantConfig[variant];

  const boxStyle = {
    backgroundColor: config.backgroundColor,
    borderLeft: config.borderLeft,
    padding: "12px 16px",
    margin: "8px 0",
    borderRadius: "0 4px 4px 0",
    fontFamily: "sans-serif",
  };

  const labelStyle = {
    fontWeight: "bold",
    marginBottom: "4px",
    fontSize: "0.9rem",
  };

  return (
    <div style={boxStyle}>
      <div style={labelStyle}>
        {config.icon} {config.label}
      </div>
      <div style={{ fontSize: "0.9rem", lineHeight: 1.6 }}>{children}</div>
    </div>
  );
}

// 탭 컨테이너 컴포넌트
function TabContainer({ children }) {
  const containerStyle = {
    maxWidth: "700px",
    margin: "0 auto",
    padding: "16px",
  };

  return <div style={containerStyle}>{children}</div>;
}

function TabUIDemo() {
  return (
    <section style={{ marginBottom: "40px" }}>
      <h2>문제 3: 탭 UI</h2>
      <TabContainer>
        <TabPanel title="React 소개">
          <p>React는 Facebook에서 만든 UI 라이브러리입니다.</p>
          <InfoBox variant="tip">
            React는 컴포넌트 기반으로 UI를 구성합니다.
            작은 컴포넌트를 조합하여 복잡한 UI를 만들 수 있습니다.
          </InfoBox>
          <InfoBox variant="note">
            React 18부터 Concurrent Features가 도입되었습니다.
          </InfoBox>
        </TabPanel>

        <TabPanel title="Props 활용법">
          <p>Props는 컴포넌트 간 데이터 전달의 핵심입니다.</p>
          <ul>
            <li>부모에서 자식으로 데이터 전달</li>
            <li>구조 분해 할당으로 깔끔하게 받기</li>
            <li>기본값으로 안전하게 처리</li>
          </ul>
          <InfoBox variant="warning">
            Props는 읽기 전용입니다. 자식 컴포넌트에서 절대 수정하면 안 됩니다!
          </InfoBox>
        </TabPanel>

        <TabPanel title="자주 묻는 질문">
          <h3 style={{ marginTop: 0 }}>Q: props와 state의 차이는?</h3>
          <p>
            props는 외부에서 전달받는 값이고,
            state는 컴포넌트 내부에서 관리하는 값입니다.
          </p>
          <InfoBox variant="tip">
            state에 대해서는 챕터 03에서 자세히 배웁니다!
          </InfoBox>
        </TabPanel>
      </TabContainer>
    </section>
  );
}

// ============================================================
// 통합 App 컴포넌트
// ============================================================

function App() {
  return (
    <div
      style={{
        fontFamily: "sans-serif",
        backgroundColor: "#f8fafc",
        minHeight: "100vh",
        padding: "20px",
        maxWidth: "900px",
        margin: "0 auto",
      }}
    >
      <h1 style={{ textAlign: "center", color: "#1e293b" }}>
        챕터 02 연습 문제 답안
      </h1>

      <BadgeDemo />
      <ProductCardDemo />
      <TabUIDemo />
    </div>
  );
}

export default App;
