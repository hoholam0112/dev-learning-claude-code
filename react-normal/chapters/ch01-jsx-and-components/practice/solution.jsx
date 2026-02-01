/**
 * 챕터 01 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 *
 * 실행 방법:
 * 1. npx create-react-app ch01-solution (이미 생성했다면 생략)
 * 2. cd ch01-solution
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React from "react";

// ============================================================
// 문제 1: 자기소개 카드 만들기
// ============================================================

function IntroCard() {
  // 정보를 변수로 선언
  const name = "박개발";
  const age = 28;
  const hobbies = ["코딩", "독서", "등산", "요리"];
  const introduction = "더 나은 웹을 만들기 위해 매일 공부하는 개발자입니다.";

  const cardStyle = {
    border: "1px solid #ddd",
    borderRadius: "12px",
    padding: "24px",
    maxWidth: "400px",
    margin: "20px auto",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
    fontFamily: "sans-serif",
  };

  const avatarStyle = {
    width: "100px",
    height: "100px",
    borderRadius: "50%",
    display: "block",
    margin: "0 auto 16px",
    objectFit: "cover",
  };

  return (
    <div className="intro-card" style={cardStyle}>
      {/* 프로필 이미지 - self-closing 태그 */}
      <img
        src="https://via.placeholder.com/100"
        alt={`${name}의 프로필 사진`}
        className="intro-card-avatar"
        style={avatarStyle}
      />

      {/* 이름과 나이 - 표현식 사용 */}
      <h2 style={{ textAlign: "center", marginBottom: "4px" }}>{name}</h2>
      <p style={{ textAlign: "center", color: "#888" }}>{age}세</p>

      {/* 자기소개 */}
      <p style={{ lineHeight: 1.6 }}>{introduction}</p>

      {/* 취미 - 배열을 join으로 문자열 변환 */}
      <div>
        <strong>취미:</strong>
        <p>{hobbies.join(", ")}</p>
      </div>
    </div>
  );
}

// ============================================================
// 문제 2: 레스토랑 메뉴 페이지
// ============================================================

// 레스토랑 헤더
function RestaurantHeader() {
  const headerStyle = {
    textAlign: "center",
    padding: "30px 20px",
    backgroundColor: "#1a1a2e",
    color: "#eee",
  };

  return (
    <header style={headerStyle}>
      <h1 style={{ margin: "0 0 8px 0", fontSize: "2rem" }}>맛있는 식당</h1>
      <p style={{ margin: 0, color: "#aaa" }}>
        정성을 담은 한 끼, 행복을 전하는 한 그릇
      </p>
    </header>
  );
}

// 메뉴 아이템 (각각 다른 데이터를 하드코딩)
function MenuItemBibimbap() {
  const name = "비빔밥";
  const price = 9000;
  const description = "신선한 나물과 고추장이 어우러진 전통 비빔밥";

  const itemStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "16px 0",
    borderBottom: "1px solid #eee",
  };

  return (
    <div style={itemStyle}>
      <div>
        <h3 style={{ margin: "0 0 4px 0" }}>{name}</h3>
        <p style={{ margin: 0, color: "#666", fontSize: "0.9rem" }}>
          {description}
        </p>
      </div>
      <span style={{ fontWeight: "bold", color: "#e74c3c", whiteSpace: "nowrap" }}>
        {price.toLocaleString()}원
      </span>
    </div>
  );
}

function MenuItemBulgogi() {
  const name = "불고기 정식";
  const price = 12000;
  const description = "달콤한 양념에 재운 소불고기와 반찬 세트";

  const itemStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "16px 0",
    borderBottom: "1px solid #eee",
  };

  return (
    <div style={itemStyle}>
      <div>
        <h3 style={{ margin: "0 0 4px 0" }}>{name}</h3>
        <p style={{ margin: 0, color: "#666", fontSize: "0.9rem" }}>
          {description}
        </p>
      </div>
      <span style={{ fontWeight: "bold", color: "#e74c3c", whiteSpace: "nowrap" }}>
        {price.toLocaleString()}원
      </span>
    </div>
  );
}

function MenuItemKimchiJjigae() {
  const name = "김치찌개";
  const price = 8000;
  const description = "잘 익은 김치로 끓인 깊은 맛의 김치찌개";

  const itemStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "16px 0",
    borderBottom: "1px solid #eee",
  };

  return (
    <div style={itemStyle}>
      <div>
        <h3 style={{ margin: "0 0 4px 0" }}>{name}</h3>
        <p style={{ margin: 0, color: "#666", fontSize: "0.9rem" }}>
          {description}
        </p>
      </div>
      <span style={{ fontWeight: "bold", color: "#e74c3c", whiteSpace: "nowrap" }}>
        {price.toLocaleString()}원
      </span>
    </div>
  );
}

// 메뉴 섹션 - MenuItem들을 포함
function MenuSection() {
  return (
    <section style={{ padding: "20px 40px", maxWidth: "600px", margin: "0 auto" }}>
      <h2 style={{ borderBottom: "2px solid #333", paddingBottom: "8px" }}>
        메뉴
      </h2>
      <MenuItemBibimbap />
      <MenuItemBulgogi />
      <MenuItemKimchiJjigae />
    </section>
  );
}

// 레스토랑 푸터
function RestaurantFooter() {
  const footerStyle = {
    textAlign: "center",
    padding: "20px",
    backgroundColor: "#f5f5f5",
    color: "#666",
    fontSize: "0.9rem",
  };

  return (
    <footer style={footerStyle}>
      <p>영업시간: 오전 11:00 ~ 오후 9:00 (매주 월요일 휴무)</p>
      <p>연락처: 02-1234-5678</p>
      <p>주소: 서울시 강남구 맛있는길 123</p>
    </footer>
  );
}

// 레스토랑 앱 - Fragment 사용
function RestaurantApp() {
  return (
    <>
      <RestaurantHeader />
      <MenuSection />
      <RestaurantFooter />
    </>
  );
}

// ============================================================
// 문제 3: 날씨 대시보드
// ============================================================

/**
 * 컴포넌트 트리:
 *
 *   WeatherDashboard
 *   ├── h2 (도시명)
 *   ├── WeatherIcon
 *   ├── TemperatureDisplay
 *   └── WeatherDetails
 */

// 날씨 아이콘 컴포넌트
function WeatherIcon() {
  const weatherStatus = "맑음"; // "맑음", "흐림", "비", "눈" 중 하나

  // 날씨 상태에 따른 이모지 매핑
  const icon =
    weatherStatus === "맑음"
      ? "☀️"
      : weatherStatus === "흐림"
      ? "☁️"
      : weatherStatus === "비"
      ? "🌧️"
      : weatherStatus === "눈"
      ? "❄️"
      : "🌤️";

  return (
    <div style={{ fontSize: "4rem", textAlign: "center" }}>
      <span role="img" aria-label={weatherStatus}>
        {icon}
      </span>
      <p style={{ fontSize: "1rem", color: "#666" }}>{weatherStatus}</p>
    </div>
  );
}

// 온도 표시 컴포넌트
function TemperatureDisplay() {
  const celsius = 24;

  // JSX 표현식 안에서 화씨 변환 계산
  const fahrenheit = ((celsius * 9) / 5 + 32).toFixed(1);

  // 온도에 따른 색상 결정
  const tempColor =
    celsius >= 30 ? "#e74c3c" : celsius >= 20 ? "#e67e22" : "#3498db";

  const tempStyle = {
    textAlign: "center",
    margin: "16px 0",
  };

  const numberStyle = {
    fontSize: "3rem",
    fontWeight: "bold",
    color: tempColor,
  };

  return (
    <div style={tempStyle}>
      <span style={numberStyle}>{celsius}°C</span>
      <p style={{ color: "#999", fontSize: "1.1rem" }}>
        {/* 화씨 변환값을 표현식으로 표시 */}
        화씨 {fahrenheit}°F
      </p>
    </div>
  );
}

// 상세 날씨 정보 컴포넌트
function WeatherDetails() {
  const humidity = 65;
  const windSpeed = 12;
  const rainProbability = 20;

  const detailsStyle = {
    display: "flex",
    justifyContent: "space-around",
    padding: "16px",
    backgroundColor: "#f8f9fa",
    borderRadius: "8px",
    margin: "16px 0",
  };

  const detailItemStyle = {
    textAlign: "center",
  };

  const labelStyle = {
    fontSize: "0.85rem",
    color: "#888",
    marginBottom: "4px",
  };

  const valueStyle = {
    fontSize: "1.2rem",
    fontWeight: "bold",
    color: "#333",
  };

  return (
    <div style={detailsStyle}>
      <div style={detailItemStyle}>
        <p style={labelStyle}>습도</p>
        <p style={valueStyle}>{humidity}%</p>
      </div>
      <div style={detailItemStyle}>
        <p style={labelStyle}>풍속</p>
        <p style={valueStyle}>{windSpeed}km/h</p>
      </div>
      <div style={detailItemStyle}>
        <p style={labelStyle}>강수확률</p>
        <p style={valueStyle}>{rainProbability}%</p>
      </div>
    </div>
  );
}

// 날씨 대시보드 - 모든 컴포넌트 조합
function WeatherDashboard() {
  const city = "서울";
  const today = new Date().toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });

  const dashboardStyle = {
    maxWidth: "400px",
    margin: "20px auto",
    padding: "24px",
    borderRadius: "16px",
    backgroundColor: "#fff",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    fontFamily: "sans-serif",
  };

  return (
    <div style={dashboardStyle}>
      <h2 style={{ textAlign: "center", marginBottom: "4px" }}>
        {city} 날씨
      </h2>
      <p style={{ textAlign: "center", color: "#999", marginTop: 0 }}>
        {today}
      </p>
      <WeatherIcon />
      <TemperatureDisplay />
      <WeatherDetails />
    </div>
  );
}

// ============================================================
// 통합 App 컴포넌트 - 모든 문제의 답안을 한 번에 확인
// ============================================================

function App() {
  const sectionTitleStyle = {
    textAlign: "center",
    padding: "16px",
    margin: "40px 0 0 0",
    backgroundColor: "#667eea",
    color: "white",
    fontSize: "1.2rem",
  };

  return (
    <div style={{ fontFamily: "sans-serif", backgroundColor: "#f0f2f5", minHeight: "100vh" }}>
      {/* 문제 1 */}
      <div style={sectionTitleStyle}>문제 1: 자기소개 카드</div>
      <IntroCard />

      {/* 문제 2 */}
      <div style={sectionTitleStyle}>문제 2: 레스토랑 메뉴 페이지</div>
      <RestaurantApp />

      {/* 문제 3 */}
      <div style={sectionTitleStyle}>문제 3: 날씨 대시보드</div>
      <WeatherDashboard />
    </div>
  );
}

export default App;
