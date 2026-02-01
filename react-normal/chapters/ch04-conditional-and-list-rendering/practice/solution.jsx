/**
 * 챕터 04 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 *
 * 실행 방법:
 * 1. npx create-react-app ch04-solution (이미 생성했다면 생략)
 * 2. cd ch04-solution
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React, { useState } from "react";

// ============================================================
// 문제 1: 사용자 목록 대시보드
// ============================================================

function UserDashboard() {
  const users = [
    { id: 1, name: "김철수", role: "관리자", isActive: true, lastLogin: "2024-01-15" },
    { id: 2, name: "이영희", role: "편집자", isActive: true, lastLogin: "2024-01-14" },
    { id: 3, name: "박민수", role: "뷰어", isActive: false, lastLogin: "2023-12-20" },
    { id: 4, name: "최지은", role: "편집자", isActive: true, lastLogin: "2024-01-15" },
    { id: 5, name: "정하나", role: "관리자", isActive: false, lastLogin: "2023-11-30" },
    { id: 6, name: "강동원", role: "뷰어", isActive: true, lastLogin: "2024-01-13" },
  ];

  const [filter, setFilter] = useState("all");

  // 역할별 색상 매핑
  const roleColors = {
    "관리자": { bg: "#fef2f2", text: "#dc2626" },
    "편집자": { bg: "#eff6ff", text: "#2563eb" },
    "뷰어": { bg: "#f3f4f6", text: "#6b7280" },
  };

  // 필터링
  const filteredUsers = users.filter((user) => {
    if (filter === "all") return true;
    if (filter === "active") return user.isActive;
    if (filter === "inactive") return !user.isActive;
    return true;
  });

  const containerStyle = {
    padding: "24px",
    fontFamily: "sans-serif",
    maxWidth: "600px",
    margin: "0 auto",
  };

  const filterButtonStyle = (isActive) => ({
    padding: "8px 16px",
    margin: "4px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "500",
    backgroundColor: isActive ? "#1e293b" : "#e5e7eb",
    color: isActive ? "#fff" : "#4b5563",
  });

  const cardStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "14px 16px",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    margin: "8px 0",
    backgroundColor: "#fff",
  };

  return (
    <div style={containerStyle}>
      <h2>사용자 대시보드</h2>

      {/* 필터 버튼 */}
      <div style={{ marginBottom: "16px" }}>
        <button onClick={() => setFilter("all")} style={filterButtonStyle(filter === "all")}>
          전체 ({users.length})
        </button>
        <button onClick={() => setFilter("active")} style={filterButtonStyle(filter === "active")}>
          활성 ({users.filter((u) => u.isActive).length})
        </button>
        <button onClick={() => setFilter("inactive")} style={filterButtonStyle(filter === "inactive")}>
          비활성 ({users.filter((u) => !u.isActive).length})
        </button>
      </div>

      <p style={{ color: "#6b7280", fontSize: "0.9rem" }}>
        {filteredUsers.length}명의 사용자
      </p>

      {/* 사용자 목록 또는 빈 상태 */}
      {filteredUsers.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px", color: "#9ca3af" }}>
          <p>해당 조건의 사용자가 없습니다.</p>
        </div>
      ) : (
        filteredUsers.map((user) => (
          <div key={user.id} style={cardStyle}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                <strong>{user.name}</strong>
                {/* 역할 뱃지 */}
                <span
                  style={{
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "0.75rem",
                    fontWeight: "600",
                    backgroundColor: roleColors[user.role].bg,
                    color: roleColors[user.role].text,
                  }}
                >
                  {user.role}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: "0.85rem", color: "#6b7280" }}>
                마지막 접속: {user.lastLogin}
              </p>
            </div>

            {/* 활성 상태 뱃지 - 조건부 렌더링 */}
            <span
              style={{
                padding: "4px 10px",
                borderRadius: "12px",
                fontSize: "0.8rem",
                fontWeight: "500",
                backgroundColor: user.isActive ? "#dcfce7" : "#f3f4f6",
                color: user.isActive ? "#166534" : "#6b7280",
              }}
            >
              {user.isActive ? "활성" : "비활성"}
            </span>
          </div>
        ))
      )}
    </div>
  );
}

// ============================================================
// 문제 2: 영화 리뷰 게시판
// ============================================================

function MovieReviewBoard() {
  const [reviews, setReviews] = useState([
    {
      id: 1,
      title: "인터스텔라",
      rating: 5,
      content: "우주와 시간에 대한 놀라운 영화입니다. 눈물 없이 볼 수 없었어요.",
      author: "영화팬",
      date: "2024-01-15",
    },
    {
      id: 2,
      title: "기생충",
      rating: 5,
      content: "한국 영화의 새로운 역사를 쓴 작품. 모든 장면이 완벽합니다.",
      author: "시네마홀릭",
      date: "2024-01-10",
    },
    {
      id: 3,
      title: "어바웃 타임",
      rating: 3,
      content: "따뜻한 로맨스 영화. 가볍게 보기 좋습니다.",
      author: "일반관객",
      date: "2024-01-08",
    },
  ]);

  const [newReview, setNewReview] = useState({
    title: "",
    rating: 5,
    content: "",
    author: "",
  });

  const [sortBy, setSortBy] = useState("recent");

  // 새 리뷰 추가
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!newReview.title.trim() || !newReview.content.trim() || !newReview.author.trim()) {
      alert("모든 필드를 입력해주세요.");
      return;
    }

    const review = {
      ...newReview,
      id: Date.now(),
      date: new Date().toISOString().split("T")[0],
    };

    setReviews((prev) => [review, ...prev]);
    setNewReview({ title: "", rating: 5, content: "", author: "" });
  };

  // 삭제
  const handleDelete = (id) => {
    setReviews((prev) => prev.filter((r) => r.id !== id));
  };

  // 정렬
  const sortedReviews = [...reviews].sort((a, b) => {
    if (sortBy === "recent") return b.id - a.id;
    if (sortBy === "rating") return b.rating - a.rating;
    return 0;
  });

  // 별 표시 함수
  const renderStars = (rating) => "★".repeat(rating) + "☆".repeat(5 - rating);

  const containerStyle = {
    padding: "24px",
    fontFamily: "sans-serif",
    maxWidth: "600px",
    margin: "0 auto",
  };

  const inputStyle = {
    padding: "8px 12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "1rem",
    width: "100%",
    boxSizing: "border-box",
    marginBottom: "8px",
  };

  return (
    <div style={containerStyle}>
      <h2>영화 리뷰 게시판</h2>

      {/* 리뷰 작성 폼 */}
      <form
        onSubmit={handleSubmit}
        style={{
          padding: "16px",
          backgroundColor: "#f8fafc",
          borderRadius: "10px",
          marginBottom: "24px",
        }}
      >
        <h3 style={{ marginTop: 0 }}>리뷰 작성</h3>
        <input
          style={inputStyle}
          placeholder="영화 제목"
          value={newReview.title}
          onChange={(e) => setNewReview((prev) => ({ ...prev, title: e.target.value }))}
        />
        <div style={{ marginBottom: "8px" }}>
          <span>평점: </span>
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              onClick={() => setNewReview((prev) => ({ ...prev, rating: star }))}
              style={{
                cursor: "pointer",
                fontSize: "1.5rem",
                color: star <= newReview.rating ? "#f59e0b" : "#d1d5db",
              }}
            >
              ★
            </span>
          ))}
        </div>
        <textarea
          style={{ ...inputStyle, minHeight: "60px", resize: "vertical" }}
          placeholder="리뷰 내용"
          value={newReview.content}
          onChange={(e) => setNewReview((prev) => ({ ...prev, content: e.target.value }))}
        />
        <input
          style={inputStyle}
          placeholder="작성자"
          value={newReview.author}
          onChange={(e) => setNewReview((prev) => ({ ...prev, author: e.target.value }))}
        />
        <button
          type="submit"
          style={{
            padding: "10px 20px",
            backgroundColor: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            width: "100%",
            fontSize: "1rem",
          }}
        >
          등록
        </button>
      </form>

      {/* 정렬 */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
        <span style={{ color: "#6b7280" }}>총 {reviews.length}개의 리뷰</span>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{ padding: "6px 10px", border: "1px solid #d1d5db", borderRadius: "6px" }}
        >
          <option value="recent">최신순</option>
          <option value="rating">평점순</option>
        </select>
      </div>

      {/* 리뷰 목록 */}
      {sortedReviews.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px", color: "#9ca3af" }}>
          <p>리뷰가 없습니다. 첫 리뷰를 작성해보세요!</p>
        </div>
      ) : (
        sortedReviews.map((review) => (
          <div
            key={review.id}
            style={{
              padding: "16px",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              margin: "8px 0",
              backgroundColor: "#fff",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h3 style={{ margin: "0 0 4px 0", display: "flex", alignItems: "center", gap: "8px" }}>
                  {review.title}
                  {/* 평점 4 이상이면 추천 뱃지 표시 - 조건부 렌더링 */}
                  {review.rating >= 4 && (
                    <span
                      style={{
                        padding: "2px 8px",
                        borderRadius: "4px",
                        fontSize: "0.7rem",
                        backgroundColor: "#dcfce7",
                        color: "#166534",
                        fontWeight: "bold",
                      }}
                    >
                      추천
                    </span>
                  )}
                </h3>
                <p style={{ margin: "0 0 8px 0", color: "#f59e0b" }}>
                  {renderStars(review.rating)}
                </p>
              </div>
              <button
                onClick={() => handleDelete(review.id)}
                style={{
                  padding: "4px 8px",
                  backgroundColor: "#fef2f2",
                  color: "#dc2626",
                  border: "1px solid #fecaca",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "0.8rem",
                }}
              >
                삭제
              </button>
            </div>
            <p style={{ margin: "0 0 8px 0", lineHeight: 1.5 }}>{review.content}</p>
            <p style={{ margin: 0, fontSize: "0.8rem", color: "#9ca3af" }}>
              {review.author} | {review.date}
            </p>
          </div>
        ))
      )}
    </div>
  );
}

// ============================================================
// 문제 3: 다단계 카테고리 네비게이션
// ============================================================

function CategoryNavigation() {
  const categories = [
    {
      id: "food",
      name: "음식",
      items: [
        { id: 1, name: "비빔밥", description: "한국 전통 음식", popular: true },
        { id: 2, name: "파스타", description: "이탈리아 면 요리", popular: false },
        { id: 3, name: "초밥", description: "일본 전통 음식", popular: true },
        { id: 4, name: "타코", description: "멕시코 전통 음식", popular: false },
      ],
    },
    {
      id: "drink",
      name: "음료",
      items: [
        { id: 5, name: "아메리카노", description: "에스프레소 + 물", popular: true },
        { id: 6, name: "녹차라떼", description: "녹차 + 우유", popular: true },
        { id: 7, name: "스무디", description: "과일 혼합 음료", popular: false },
      ],
    },
    {
      id: "dessert",
      name: "디저트",
      items: [
        { id: 8, name: "티라미수", description: "이탈리아 디저트", popular: true },
        { id: 9, name: "마카롱", description: "프랑스 디저트", popular: false },
      ],
    },
  ];

  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [showOnlyPopular, setShowOnlyPopular] = useState(false);

  // 선택된 카테고리 찾기
  const selectedCategory = categories.find((c) => c.id === selectedCategoryId);

  // 선택된 카테고리의 아이템 필터링
  const filteredItems = selectedCategory
    ? selectedCategory.items.filter((item) => (showOnlyPopular ? item.popular : true))
    : [];

  const containerStyle = {
    padding: "24px",
    fontFamily: "sans-serif",
    maxWidth: "600px",
    margin: "0 auto",
  };

  const tabStyle = (isActive) => ({
    padding: "12px 24px",
    border: "none",
    borderBottom: isActive ? "3px solid #2563eb" : "3px solid transparent",
    backgroundColor: isActive ? "#eff6ff" : "transparent",
    color: isActive ? "#2563eb" : "#6b7280",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: isActive ? "600" : "400",
    transition: "all 0.2s",
  });

  const itemCardStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "14px 16px",
    border: "1px solid #e5e7eb",
    borderRadius: "8px",
    margin: "8px 0",
    backgroundColor: "#fff",
  };

  return (
    <div style={containerStyle}>
      <h2>카테고리 네비게이션</h2>

      {/* 카테고리 탭 - map으로 렌더링 */}
      <div style={{ borderBottom: "1px solid #e5e7eb", marginBottom: "16px" }}>
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => setSelectedCategoryId(category.id)}
            style={tabStyle(selectedCategoryId === category.id)}
          >
            {category.name} ({category.items.length})
          </button>
        ))}
      </div>

      {/* 컨텐츠 영역 - 3단계 조건부 렌더링 */}
      {selectedCategory === undefined ? (
        // 1단계: 카테고리 선택 안 됨
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#9ca3af" }}>
          <p style={{ fontSize: "2rem" }}>👆</p>
          <p>위에서 카테고리를 선택하세요</p>
        </div>
      ) : (
        // 카테고리가 선택된 경우
        <div>
          {/* 인기 필터 토글 */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <h3 style={{ margin: 0 }}>{selectedCategory.name}</h3>
            <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.9rem" }}>
              <input
                type="checkbox"
                checked={showOnlyPopular}
                onChange={(e) => setShowOnlyPopular(e.target.checked)}
              />
              인기 항목만
            </label>
          </div>

          {filteredItems.length === 0 ? (
            // 2단계: 필터링 결과 없음
            <div style={{ textAlign: "center", padding: "40px", color: "#9ca3af" }}>
              <p>조건에 맞는 항목이 없습니다.</p>
            </div>
          ) : (
            // 3단계: 항목 리스트 표시
            <>
              <p style={{ color: "#6b7280", fontSize: "0.85rem" }}>
                {filteredItems.length}개의 항목
              </p>
              {filteredItems.map((item) => (
                <div key={item.id} style={itemCardStyle}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <strong>{item.name}</strong>
                      {/* 인기 뱃지 - 조건부 렌더링 */}
                      {item.popular && (
                        <span
                          style={{
                            padding: "2px 8px",
                            borderRadius: "12px",
                            fontSize: "0.7rem",
                            backgroundColor: "#fef3c7",
                            color: "#92400e",
                            fontWeight: "bold",
                          }}
                        >
                          인기
                        </span>
                      )}
                    </div>
                    <p style={{ margin: "4px 0 0 0", color: "#6b7280", fontSize: "0.9rem" }}>
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================
// 통합 App 컴포넌트
// ============================================================

function App() {
  const dividerStyle = {
    textAlign: "center",
    padding: "12px",
    margin: "30px 0 0 0",
    backgroundColor: "#667eea",
    color: "white",
    borderRadius: "8px 8px 0 0",
    fontSize: "1rem",
    fontWeight: "bold",
    fontFamily: "sans-serif",
  };

  return (
    <div style={{ backgroundColor: "#f8fafc", minHeight: "100vh", paddingBottom: "40px" }}>
      <h1 style={{ textAlign: "center", padding: "24px 0 0", fontFamily: "sans-serif", color: "#1e293b" }}>
        챕터 04 연습 문제 답안
      </h1>

      <div style={dividerStyle}>문제 1: 사용자 목록 대시보드</div>
      <UserDashboard />

      <div style={dividerStyle}>문제 2: 영화 리뷰 게시판</div>
      <MovieReviewBoard />

      <div style={dividerStyle}>문제 3: 다단계 카테고리 네비게이션</div>
      <CategoryNavigation />
    </div>
  );
}

export default App;
