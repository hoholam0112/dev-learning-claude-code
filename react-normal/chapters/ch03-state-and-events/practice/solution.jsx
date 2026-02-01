/**
 * 챕터 03 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 4개 문제에 대한 모범 답안이 포함되어 있습니다.
 *
 * 실행 방법:
 * 1. npx create-react-app ch03-solution (이미 생성했다면 생략)
 * 2. cd ch03-solution
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React, { useState } from "react";

// ============================================================
// 문제 1: 좋아요 버튼
// ============================================================

function LikeButton() {
  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(42);

  const handleToggleLike = () => {
    if (isLiked) {
      // 좋아요 취소
      setIsLiked(false);
      setLikeCount((prev) => prev - 1);
    } else {
      // 좋아요 누르기
      setIsLiked(true);
      setLikeCount((prev) => prev + 1);
    }
  };

  const buttonStyle = {
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 16px",
    border: "none",
    borderRadius: "20px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "500",
    transition: "all 0.2s",
    backgroundColor: isLiked ? "#fef2f2" : "#f3f4f6",
    color: isLiked ? "#dc2626" : "#6b7280",
    border: isLiked ? "1px solid #fecaca" : "1px solid #e5e7eb",
  };

  return (
    <div style={{ padding: "20px" }}>
      <button onClick={handleToggleLike} style={buttonStyle}>
        <span style={{ fontSize: "1.2rem" }}>{isLiked ? "❤️" : "🤍"}</span>
        <span>좋아요 {likeCount}</span>
      </button>
    </div>
  );
}

// ============================================================
// 문제 2: 색상 선택기
// ============================================================

function ColorPicker() {
  const [selectedColor, setSelectedColor] = useState("#ffffff");
  const [recentColors, setRecentColors] = useState([]);

  // 색상 팔레트
  const palette = [
    "#ef4444", "#f97316", "#eab308", "#22c55e",
    "#3b82f6", "#8b5cf6", "#ec4899", "#6b7280",
    "#14b8a6", "#f43f5e", "#a855f7", "#0ea5e9",
  ];

  const handleSelectColor = (color) => {
    setSelectedColor(color);

    // 최근 색상 업데이트: 중복 제거 후 앞에 추가, 최대 5개 유지
    setRecentColors((prev) => {
      const filtered = prev.filter((c) => c !== color);
      return [color, ...filtered].slice(0, 5);
    });
  };

  const handleReset = () => {
    setSelectedColor("#ffffff");
  };

  const containerStyle = {
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const colorSwatchStyle = (color) => ({
    width: "40px",
    height: "40px",
    borderRadius: "8px",
    backgroundColor: color,
    border: selectedColor === color ? "3px solid #1f2937" : "2px solid #e5e7eb",
    cursor: "pointer",
    transition: "transform 0.15s",
  });

  return (
    <div style={containerStyle}>
      <h2>색상 선택기</h2>

      {/* 미리보기 */}
      <div
        style={{
          width: "100%",
          height: "100px",
          borderRadius: "8px",
          backgroundColor: selectedColor,
          border: "1px solid #e5e7eb",
          marginBottom: "16px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "1.2rem",
          color: selectedColor === "#ffffff" ? "#999" : "#fff",
          textShadow: "0 1px 2px rgba(0,0,0,0.3)",
        }}
      >
        {selectedColor}
      </div>

      {/* 색상 팔레트 */}
      <p style={{ fontWeight: "bold", marginBottom: "8px" }}>팔레트:</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "16px" }}>
        {palette.map((color) => (
          <div
            key={color}
            style={colorSwatchStyle(color)}
            onClick={() => handleSelectColor(color)}
            title={color}
          />
        ))}
      </div>

      {/* 최근 사용 색상 */}
      {recentColors.length > 0 && (
        <div style={{ marginBottom: "16px" }}>
          <p style={{ fontWeight: "bold", marginBottom: "8px" }}>최근 사용:</p>
          <div style={{ display: "flex", gap: "8px" }}>
            {recentColors.map((color) => (
              <div
                key={color}
                style={{
                  ...colorSwatchStyle(color),
                  width: "32px",
                  height: "32px",
                }}
                onClick={() => handleSelectColor(color)}
                title={color}
              />
            ))}
          </div>
        </div>
      )}

      {/* 초기화 버튼 */}
      <button
        onClick={handleReset}
        style={{
          padding: "8px 16px",
          backgroundColor: "#6b7280",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        초기화 (흰색)
      </button>
    </div>
  );
}

// ============================================================
// 문제 3: 텍스트 편집기
// ============================================================

function TextEditor() {
  const [text, setText] = useState("안녕하세요! React 텍스트 편집기입니다.");
  const [fontSize, setFontSize] = useState(16);
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const [textColor, setTextColor] = useState("#1f2937");

  const colorOptions = [
    { value: "#1f2937", label: "검정" },
    { value: "#dc2626", label: "빨강" },
    { value: "#2563eb", label: "파랑" },
    { value: "#16a34a", label: "초록" },
    { value: "#9333ea", label: "보라" },
  ];

  // 글자 수 계산
  const charCount = text.length;
  // 단어 수 계산 (공백 기준 분리, 빈 문자열 제외)
  const wordCount = text.trim() === "" ? 0 : text.trim().split(/\s+/).filter(Boolean).length;

  const containerStyle = {
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const toolbarStyle = {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
    alignItems: "center",
    padding: "12px",
    backgroundColor: "#f8fafc",
    borderRadius: "8px",
    marginBottom: "16px",
  };

  const toolButtonStyle = (isActive) => ({
    padding: "6px 12px",
    border: "1px solid #d1d5db",
    borderRadius: "4px",
    cursor: "pointer",
    backgroundColor: isActive ? "#2563eb" : "#fff",
    color: isActive ? "#fff" : "#333",
    fontWeight: "bold",
    fontSize: "0.9rem",
  });

  const previewStyle = {
    padding: "16px",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    minHeight: "100px",
    fontSize: `${fontSize}px`,
    fontWeight: isBold ? "bold" : "normal",
    fontStyle: isItalic ? "italic" : "normal",
    color: textColor,
    lineHeight: 1.6,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  };

  return (
    <div style={containerStyle}>
      <h2>텍스트 편집기</h2>

      {/* 도구 모음 */}
      <div style={toolbarStyle}>
        {/* 글자 크기 */}
        <button
          onClick={() => setFontSize((prev) => Math.max(12, prev - 2))}
          style={toolButtonStyle(false)}
          disabled={fontSize <= 12}
        >
          A-
        </button>
        <span style={{ fontSize: "0.85rem", minWidth: "40px", textAlign: "center" }}>
          {fontSize}px
        </span>
        <button
          onClick={() => setFontSize((prev) => Math.min(32, prev + 2))}
          style={toolButtonStyle(false)}
          disabled={fontSize >= 32}
        >
          A+
        </button>

        <span style={{ color: "#d1d5db" }}>|</span>

        {/* 굵게 */}
        <button
          onClick={() => setIsBold((prev) => !prev)}
          style={toolButtonStyle(isBold)}
        >
          B
        </button>

        {/* 기울임 */}
        <button
          onClick={() => setIsItalic((prev) => !prev)}
          style={{ ...toolButtonStyle(isItalic), fontStyle: "italic" }}
        >
          I
        </button>

        <span style={{ color: "#d1d5db" }}>|</span>

        {/* 색상 선택 */}
        {colorOptions.map((option) => (
          <div
            key={option.value}
            onClick={() => setTextColor(option.value)}
            style={{
              width: "24px",
              height: "24px",
              borderRadius: "50%",
              backgroundColor: option.value,
              cursor: "pointer",
              border: textColor === option.value ? "3px solid #1f2937" : "2px solid #e5e7eb",
            }}
            title={option.label}
          />
        ))}
      </div>

      {/* 텍스트 입력 */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{
          width: "100%",
          minHeight: "100px",
          padding: "12px",
          border: "1px solid #d1d5db",
          borderRadius: "8px",
          fontSize: "1rem",
          resize: "vertical",
          boxSizing: "border-box",
          marginBottom: "12px",
        }}
        placeholder="텍스트를 입력하세요..."
      />

      {/* 통계 */}
      <p style={{ fontSize: "0.85rem", color: "#6b7280", marginBottom: "12px" }}>
        글자 수: {charCount} | 단어 수: {wordCount}
      </p>

      {/* 미리보기 */}
      <p style={{ fontWeight: "bold", marginBottom: "4px" }}>미리보기:</p>
      <div style={previewStyle}>
        {text || "(텍스트를 입력하세요)"}
      </div>
    </div>
  );
}

// ============================================================
// 문제 4: 장바구니
// ============================================================

function ShoppingCart() {
  // 상품 데이터 (고정)
  const products = [
    { id: 1, name: "노트북", price: 1200000 },
    { id: 2, name: "마우스", price: 35000 },
    { id: 3, name: "키보드", price: 89000 },
    { id: 4, name: "모니터", price: 450000 },
  ];

  // 장바구니 상태
  const [cartItems, setCartItems] = useState([]);

  // 상품 추가
  const handleAddToCart = (product) => {
    setCartItems((prev) => {
      const existingItem = prev.find((item) => item.id === product.id);
      if (existingItem) {
        // 이미 있으면 수량 +1
        return prev.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      // 없으면 새로 추가
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  // 수량 증가
  const handleIncrease = (id) => {
    setCartItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, quantity: item.quantity + 1 } : item
      )
    );
  };

  // 수량 감소 (최소 1)
  const handleDecrease = (id) => {
    setCartItems((prev) =>
      prev.map((item) =>
        item.id === id
          ? { ...item, quantity: Math.max(1, item.quantity - 1) }
          : item
      )
    );
  };

  // 삭제
  const handleRemove = (id) => {
    setCartItems((prev) => prev.filter((item) => item.id !== id));
  };

  // 총 금액 계산
  const totalPrice = cartItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  // 총 수량 계산
  const totalQuantity = cartItems.reduce(
    (sum, item) => sum + item.quantity,
    0
  );

  const containerStyle = {
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const buttonStyle = {
    padding: "6px 14px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "0.9rem",
  };

  const quantityButtonStyle = {
    padding: "2px 10px",
    border: "1px solid #d1d5db",
    borderRadius: "4px",
    cursor: "pointer",
    backgroundColor: "#fff",
    fontSize: "1rem",
  };

  return (
    <div style={containerStyle}>
      <h2>장바구니</h2>

      {/* 상품 목록 */}
      <div style={{ marginBottom: "24px" }}>
        <h3>상품 목록</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
          {products.map((product) => {
            const inCart = cartItems.find((item) => item.id === product.id);
            return (
              <div
                key={product.id}
                style={{
                  padding: "12px",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <p style={{ margin: "0 0 4px 0", fontWeight: "bold" }}>
                    {product.name}
                  </p>
                  <p style={{ margin: 0, color: "#2563eb" }}>
                    {product.price.toLocaleString()}원
                  </p>
                </div>
                <button
                  onClick={() => handleAddToCart(product)}
                  style={{
                    ...buttonStyle,
                    backgroundColor: inCart ? "#22c55e" : "#2563eb",
                    color: "#fff",
                  }}
                >
                  {inCart ? `담김 (${inCart.quantity})` : "담기"}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* 장바구니 */}
      <div>
        <h3>
          내 장바구니{" "}
          {totalQuantity > 0 && (
            <span style={{ fontSize: "0.9rem", color: "#6b7280" }}>
              ({totalQuantity}개)
            </span>
          )}
        </h3>

        {cartItems.length === 0 ? (
          <p style={{ textAlign: "center", color: "#9ca3af", padding: "20px" }}>
            장바구니가 비어있습니다
          </p>
        ) : (
          <>
            {cartItems.map((item) => (
              <div
                key={item.id}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "12px 0",
                  borderBottom: "1px solid #f3f4f6",
                }}
              >
                <div>
                  <p style={{ margin: "0 0 4px 0", fontWeight: "500" }}>
                    {item.name}
                  </p>
                  <p style={{ margin: 0, fontSize: "0.9rem", color: "#6b7280" }}>
                    {item.price.toLocaleString()}원 x {item.quantity}
                  </p>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <button
                    onClick={() => handleDecrease(item.id)}
                    style={quantityButtonStyle}
                  >
                    -
                  </button>
                  <span style={{ minWidth: "24px", textAlign: "center" }}>
                    {item.quantity}
                  </span>
                  <button
                    onClick={() => handleIncrease(item.id)}
                    style={quantityButtonStyle}
                  >
                    +
                  </button>
                  <button
                    onClick={() => handleRemove(item.id)}
                    style={{
                      ...buttonStyle,
                      backgroundColor: "#fef2f2",
                      color: "#dc2626",
                      border: "1px solid #fecaca",
                      marginLeft: "8px",
                    }}
                  >
                    삭제
                  </button>
                </div>
              </div>
            ))}

            {/* 합계 */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "16px 0",
                fontWeight: "bold",
                fontSize: "1.1rem",
              }}
            >
              <span>총 금액:</span>
              <span style={{ color: "#2563eb" }}>
                {totalPrice.toLocaleString()}원
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ============================================================
// 통합 App 컴포넌트
// ============================================================

function App() {
  const sectionStyle = {
    textAlign: "center",
    padding: "12px",
    margin: "30px 0 0 0",
    backgroundColor: "#667eea",
    color: "white",
    borderRadius: "8px 8px 0 0",
    fontSize: "1rem",
    fontWeight: "bold",
  };

  return (
    <div
      style={{
        fontFamily: "sans-serif",
        backgroundColor: "#f8fafc",
        minHeight: "100vh",
        padding: "20px",
        maxWidth: "700px",
        margin: "0 auto",
      }}
    >
      <h1 style={{ textAlign: "center", color: "#1e293b" }}>
        챕터 03 연습 문제 답안
      </h1>

      <div style={sectionStyle}>문제 1: 좋아요 버튼</div>
      <LikeButton />

      <div style={sectionStyle}>문제 2: 색상 선택기</div>
      <ColorPicker />

      <div style={sectionStyle}>문제 3: 텍스트 편집기</div>
      <TextEditor />

      <div style={sectionStyle}>문제 4: 장바구니</div>
      <ShoppingCart />
    </div>
  );
}

export default App;
