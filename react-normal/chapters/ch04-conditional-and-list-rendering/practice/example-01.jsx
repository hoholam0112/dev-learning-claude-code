/**
 * 챕터 04 - 예제 1: 상품 목록과 필터링 UI
 *
 * 학습 포인트:
 * - 조건부 렌더링 (삼항 연산자, && 연산자, if 조기 반환)
 * - 리스트 렌더링 (map)
 * - key 속성의 올바른 사용
 * - filter와 map을 조합한 동적 리스트
 * - 검색 + 카테고리 필터 조합
 *
 * 실행 방법:
 * 1. npx create-react-app ch04-demo
 * 2. cd ch04-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React, { useState } from "react";

// --- 상품 데이터 ---
const PRODUCTS = [
  { id: 1, name: "맥북 프로 14인치", price: 2390000, category: "노트북", inStock: true, rating: 4.8 },
  { id: 2, name: "아이패드 에어", price: 929000, category: "태블릿", inStock: true, rating: 4.6 },
  { id: 3, name: "에어팟 프로", price: 359000, category: "이어폰", inStock: false, rating: 4.7 },
  { id: 4, name: "갤럭시 S24", price: 1155000, category: "스마트폰", inStock: true, rating: 4.5 },
  { id: 5, name: "갤럭시 탭 S9", price: 1099000, category: "태블릿", inStock: true, rating: 4.4 },
  { id: 6, name: "LG 그램 17인치", price: 1890000, category: "노트북", inStock: true, rating: 4.3 },
  { id: 7, name: "소니 WF-1000XM5", price: 359000, category: "이어폰", inStock: true, rating: 4.8 },
  { id: 8, name: "아이폰 15 프로", price: 1550000, category: "스마트폰", inStock: false, rating: 4.9 },
  { id: 9, name: "맥북 에어 15인치", price: 1890000, category: "노트북", inStock: true, rating: 4.7 },
  { id: 10, name: "갤럭시 버즈3 프로", price: 289000, category: "이어폰", inStock: true, rating: 4.2 },
];

// 카테고리 목록 추출
const CATEGORIES = ["전체", ...new Set(PRODUCTS.map((p) => p.category))];

// --- 개별 상품 카드 컴포넌트 ---
function ProductCard({ name, price, category, inStock, rating }) {
  const cardStyle = {
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    padding: "16px",
    margin: "8px",
    flex: "1 1 calc(50% - 16px)",
    minWidth: "250px",
    fontFamily: "sans-serif",
    opacity: inStock ? 1 : 0.6,
    position: "relative",
    backgroundColor: "#fff",
  };

  const categoryBadgeStyle = {
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "0.75rem",
    fontWeight: "600",
    backgroundColor: "#eff6ff",
    color: "#2563eb",
  };

  // 별점을 별 문자로 변환
  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.5;
    let stars = "★".repeat(fullStars);
    if (hasHalf) stars += "½";
    return stars;
  };

  return (
    <div style={cardStyle}>
      {/* 품절 표시: 조건부 렌더링 (&&) */}
      {!inStock && (
        <div
          style={{
            position: "absolute",
            top: "8px",
            right: "8px",
            backgroundColor: "#dc2626",
            color: "#fff",
            padding: "2px 8px",
            borderRadius: "4px",
            fontSize: "0.75rem",
            fontWeight: "bold",
          }}
        >
          품절
        </div>
      )}

      <span style={categoryBadgeStyle}>{category}</span>
      <h3 style={{ margin: "8px 0 4px 0", fontSize: "1rem" }}>{name}</h3>
      <p style={{ margin: "0 0 4px 0", fontWeight: "bold", color: "#2563eb" }}>
        {price.toLocaleString()}원
      </p>
      <p style={{ margin: 0, fontSize: "0.85rem", color: "#f59e0b" }}>
        {renderStars(rating)} ({rating})
      </p>
    </div>
  );
}

// --- 빈 상태 컴포넌트 ---
function EmptyState({ message }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: "40px",
        color: "#9ca3af",
        fontFamily: "sans-serif",
      }}
    >
      <p style={{ fontSize: "2rem" }}>🔍</p>
      <p>{message}</p>
    </div>
  );
}

// --- 메인 상품 목록 컴포넌트 ---
function ProductList() {
  const [selectedCategory, setSelectedCategory] = useState("전체");
  const [searchTerm, setSearchTerm] = useState("");
  const [showOnlyInStock, setShowOnlyInStock] = useState(false);
  const [sortBy, setSortBy] = useState("name"); // "name", "price-asc", "price-desc"

  // 필터링 체인: 카테고리 -> 검색어 -> 재고 여부
  let filteredProducts = PRODUCTS
    .filter((p) =>
      selectedCategory === "전체" ? true : p.category === selectedCategory
    )
    .filter((p) =>
      p.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter((p) =>
      showOnlyInStock ? p.inStock : true
    );

  // 정렬
  filteredProducts = [...filteredProducts].sort((a, b) => {
    if (sortBy === "name") return a.name.localeCompare(b.name);
    if (sortBy === "price-asc") return a.price - b.price;
    if (sortBy === "price-desc") return b.price - a.price;
    if (sortBy === "rating") return b.rating - a.rating;
    return 0;
  });

  const containerStyle = {
    maxWidth: "800px",
    margin: "0 auto",
    padding: "24px",
    fontFamily: "sans-serif",
  };

  const filterBarStyle = {
    backgroundColor: "#f8fafc",
    padding: "16px",
    borderRadius: "10px",
    marginBottom: "20px",
  };

  const categoryButtonStyle = (isActive) => ({
    padding: "6px 14px",
    border: "none",
    borderRadius: "20px",
    margin: "4px",
    cursor: "pointer",
    fontSize: "0.85rem",
    fontWeight: "500",
    backgroundColor: isActive ? "#2563eb" : "#e5e7eb",
    color: isActive ? "#fff" : "#4b5563",
    transition: "all 0.2s",
  });

  return (
    <div style={containerStyle}>
      <h1>상품 목록</h1>

      {/* 필터 바 */}
      <div style={filterBarStyle}>
        {/* 검색 */}
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="상품명 검색..."
          style={{
            width: "100%",
            padding: "10px 14px",
            border: "1px solid #d1d5db",
            borderRadius: "8px",
            fontSize: "1rem",
            boxSizing: "border-box",
            marginBottom: "12px",
          }}
        />

        {/* 카테고리 필터 */}
        <div style={{ marginBottom: "12px" }}>
          {CATEGORIES.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              style={categoryButtonStyle(selectedCategory === category)}
            >
              {category}
            </button>
          ))}
        </div>

        {/* 추가 옵션 */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.9rem" }}>
            <input
              type="checkbox"
              checked={showOnlyInStock}
              onChange={(e) => setShowOnlyInStock(e.target.checked)}
            />
            재고 있는 상품만
          </label>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              padding: "6px 10px",
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              fontSize: "0.9rem",
            }}
          >
            <option value="name">이름순</option>
            <option value="price-asc">가격 낮은순</option>
            <option value="price-desc">가격 높은순</option>
            <option value="rating">평점순</option>
          </select>
        </div>
      </div>

      {/* 결과 수 표시 */}
      <p style={{ color: "#6b7280", fontSize: "0.9rem" }}>
        {filteredProducts.length}개의 상품
        {searchTerm && ` (검색어: "${searchTerm}")`}
      </p>

      {/* 상품 리스트 또는 빈 상태 - 조건부 렌더링 */}
      {filteredProducts.length === 0 ? (
        <EmptyState message="조건에 맞는 상품이 없습니다." />
      ) : (
        <div style={{ display: "flex", flexWrap: "wrap" }}>
          {/* map()으로 리스트 렌더링, key는 고유 id 사용 */}
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              name={product.name}
              price={product.price}
              category={product.category}
              inStock={product.inStock}
              rating={product.rating}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// --- App 컴포넌트 ---
function App() {
  return <ProductList />;
}

export default App;
