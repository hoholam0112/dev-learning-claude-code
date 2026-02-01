/**
 * 챕터 05 - 예제 2: 커스텀 Hook 모음
 *
 * 학습 포인트:
 * - 커스텀 Hook의 설계와 구현
 * - useState + useEffect 조합
 * - 실용적인 커스텀 Hook 패턴
 * - 여러 컴포넌트에서 커스텀 Hook 재사용
 *
 * 실행 방법:
 * 1. npx create-react-app ch05-demo (이미 생성했다면 생략)
 * 2. cd ch05-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React, { useState, useEffect, useRef } from "react";

// ============================================================
// 커스텀 Hook 1: useWindowSize (윈도우 크기 감지)
// ============================================================
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    // 이벤트 리스너 등록
    window.addEventListener("resize", handleResize);

    // 클린업: 이벤트 리스너 해제
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []); // 마운트 시 1번만 등록

  return size;
}

// --- 사용 컴포넌트 ---
function WindowSizeDisplay() {
  const { width, height } = useWindowSize();

  // 화면 크기에 따른 디바이스 타입 결정
  const deviceType =
    width < 768 ? "모바일" : width < 1024 ? "태블릿" : "데스크탑";

  const deviceColor =
    width < 768 ? "#dc2626" : width < 1024 ? "#f59e0b" : "#22c55e";

  return (
    <div
      style={{
        padding: "20px",
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        margin: "16px 0",
        fontFamily: "sans-serif",
      }}
    >
      <h2>useWindowSize</h2>
      <p>브라우저 창 크기를 조절해보세요!</p>
      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
        <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px", flex: 1 }}>
          <p style={{ margin: 0, color: "#6b7280", fontSize: "0.85rem" }}>너비</p>
          <p style={{ margin: 0, fontWeight: "bold", fontSize: "1.5rem" }}>{width}px</p>
        </div>
        <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px", flex: 1 }}>
          <p style={{ margin: 0, color: "#6b7280", fontSize: "0.85rem" }}>높이</p>
          <p style={{ margin: 0, fontWeight: "bold", fontSize: "1.5rem" }}>{height}px</p>
        </div>
        <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px", flex: 1 }}>
          <p style={{ margin: 0, color: "#6b7280", fontSize: "0.85rem" }}>디바이스</p>
          <p style={{ margin: 0, fontWeight: "bold", fontSize: "1.5rem", color: deviceColor }}>
            {deviceType}
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// 커스텀 Hook 2: useLocalStorage (로컬 스토리지 동기화)
// ============================================================
function useLocalStorage(key, initialValue) {
  // 초기값: 로컬 스토리지에 저장된 값이 있으면 사용, 없으면 initialValue
  const [value, setValue] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  // value가 변경되면 로컬 스토리지에 저장
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error("로컬 스토리지 저장 실패:", error);
    }
  }, [key, value]);

  return [value, setValue];
}

// --- 사용 컴포넌트 ---
function ThemeSettings() {
  // 브라우저를 새로고침해도 값이 유지됩니다!
  const [theme, setTheme] = useLocalStorage("app-theme", "light");
  const [fontSize, setFontSize] = useLocalStorage("app-fontSize", 16);
  const [username, setUsername] = useLocalStorage("app-username", "");

  const isDark = theme === "dark";

  return (
    <div
      style={{
        padding: "20px",
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        margin: "16px 0",
        fontFamily: "sans-serif",
        backgroundColor: isDark ? "#1e293b" : "#fff",
        color: isDark ? "#e2e8f0" : "#1e293b",
        transition: "all 0.3s",
      }}
    >
      <h2>useLocalStorage</h2>
      <p style={{ color: isDark ? "#94a3b8" : "#6b7280" }}>
        설정을 변경하고 페이지를 새로고침해보세요. 값이 유지됩니다!
      </p>

      {/* 테마 토글 */}
      <div style={{ marginBottom: "12px" }}>
        <label style={{ fontWeight: "bold" }}>테마: </label>
        <button
          onClick={() => setTheme(isDark ? "light" : "dark")}
          style={{
            padding: "6px 14px",
            borderRadius: "6px",
            border: "none",
            cursor: "pointer",
            backgroundColor: isDark ? "#f8fafc" : "#1e293b",
            color: isDark ? "#1e293b" : "#f8fafc",
          }}
        >
          {isDark ? "라이트 모드로" : "다크 모드로"}
        </button>
      </div>

      {/* 글자 크기 */}
      <div style={{ marginBottom: "12px" }}>
        <label style={{ fontWeight: "bold" }}>
          글자 크기: {fontSize}px
        </label>
        <input
          type="range"
          min="12"
          max="24"
          value={fontSize}
          onChange={(e) => setFontSize(Number(e.target.value))}
          style={{ display: "block", width: "100%", marginTop: "4px" }}
        />
      </div>

      {/* 이름 입력 */}
      <div style={{ marginBottom: "12px" }}>
        <label style={{ fontWeight: "bold" }}>이름: </label>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="이름을 입력하세요"
          style={{
            padding: "6px 12px",
            border: `1px solid ${isDark ? "#475569" : "#d1d5db"}`,
            borderRadius: "6px",
            backgroundColor: isDark ? "#334155" : "#fff",
            color: isDark ? "#e2e8f0" : "#1e293b",
          }}
        />
      </div>

      {/* 미리보기 */}
      <div
        style={{
          padding: "12px",
          backgroundColor: isDark ? "#334155" : "#f8fafc",
          borderRadius: "8px",
          fontSize: `${fontSize}px`,
        }}
      >
        미리보기: {username ? `안녕하세요, ${username}님!` : "이름을 입력하세요"}
      </div>
    </div>
  );
}

// ============================================================
// 커스텀 Hook 3: useDebounce (디바운스)
// ============================================================
function useDebounce(value, delay = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // delay ms 후에 값을 업데이트
    const timerId = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 클린업: value가 변경되면 이전 타이머 취소
    return () => {
      clearTimeout(timerId);
    };
  }, [value, delay]);

  return debouncedValue;
}

// --- 사용 컴포넌트 ---
function SearchWithDebounce() {
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearch = useDebounce(searchTerm, 500);
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  // 디바운스된 값이 변경될 때만 API 호출 (시뮬레이션)
  useEffect(() => {
    if (debouncedSearch.trim() === "") {
      setResults([]);
      return;
    }

    setSearching(true);

    // 실제 API 호출 대신 시뮬레이션
    const timer = setTimeout(() => {
      const mockResults = [
        "React 기초 강좌",
        "React Hooks 완벽 가이드",
        "React와 TypeScript",
        "React Native 입문",
        "React 테스팅 전략",
      ].filter((item) =>
        item.toLowerCase().includes(debouncedSearch.toLowerCase())
      );
      setResults(mockResults);
      setSearching(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [debouncedSearch]);

  return (
    <div
      style={{
        padding: "20px",
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        margin: "16px 0",
        fontFamily: "sans-serif",
      }}
    >
      <h2>useDebounce</h2>
      <p style={{ color: "#6b7280" }}>
        빠르게 입력해도 500ms 후에 한 번만 검색합니다.
      </p>

      <input
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="검색어 입력 (예: React)"
        style={{
          width: "100%",
          padding: "10px 14px",
          border: "1px solid #d1d5db",
          borderRadius: "8px",
          fontSize: "1rem",
          boxSizing: "border-box",
          marginBottom: "8px",
        }}
      />

      <p style={{ fontSize: "0.85rem", color: "#9ca3af" }}>
        입력값: "{searchTerm}" | 디바운스 값: "{debouncedSearch}"
      </p>

      {searching && <p style={{ color: "#2563eb" }}>검색 중...</p>}

      {results.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {results.map((result, index) => (
            <li
              key={index}
              style={{
                padding: "8px 12px",
                borderBottom: "1px solid #f3f4f6",
                fontSize: "0.9rem",
              }}
            >
              {result}
            </li>
          ))}
        </ul>
      )}

      {debouncedSearch && !searching && results.length === 0 && (
        <p style={{ color: "#9ca3af" }}>검색 결과가 없습니다.</p>
      )}
    </div>
  );
}

// ============================================================
// 커스텀 Hook 4: useCounter (카운터 로직)
// ============================================================
function useCounter(initialValue = 0, { min = -Infinity, max = Infinity, step = 1 } = {}) {
  const [count, setCount] = useState(initialValue);

  const increment = () => setCount((prev) => Math.min(max, prev + step));
  const decrement = () => setCount((prev) => Math.max(min, prev - step));
  const reset = () => setCount(initialValue);
  const set = (value) => setCount(Math.min(max, Math.max(min, value)));

  return { count, increment, decrement, reset, set };
}

// --- 사용 컴포넌트 ---
function CounterDemo() {
  // 같은 커스텀 Hook을 다른 설정으로 여러 번 사용
  const counter1 = useCounter(0, { min: 0, max: 10 });
  const counter2 = useCounter(50, { min: 0, max: 100, step: 5 });

  const buttonStyle = {
    padding: "6px 16px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    margin: "4px",
    color: "#fff",
    fontSize: "0.9rem",
  };

  return (
    <div
      style={{
        padding: "20px",
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        margin: "16px 0",
        fontFamily: "sans-serif",
      }}
    >
      <h2>useCounter (커스텀 Hook 재사용)</h2>

      {/* 카운터 1: 0~10, step 1 */}
      <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px", marginBottom: "12px" }}>
        <h3 style={{ margin: "0 0 8px 0" }}>카운터 1 (범위: 0~10, 단계: 1)</h3>
        <span style={{ fontSize: "2rem", fontWeight: "bold" }}>{counter1.count}</span>
        <div>
          <button onClick={counter1.decrement} style={{ ...buttonStyle, backgroundColor: "#ef4444" }}>
            -1
          </button>
          <button onClick={counter1.reset} style={{ ...buttonStyle, backgroundColor: "#6b7280" }}>
            초기화
          </button>
          <button onClick={counter1.increment} style={{ ...buttonStyle, backgroundColor: "#22c55e" }}>
            +1
          </button>
        </div>
      </div>

      {/* 카운터 2: 0~100, step 5 */}
      <div style={{ padding: "12px", backgroundColor: "#f8fafc", borderRadius: "8px" }}>
        <h3 style={{ margin: "0 0 8px 0" }}>카운터 2 (범위: 0~100, 단계: 5)</h3>
        <span style={{ fontSize: "2rem", fontWeight: "bold" }}>{counter2.count}</span>
        <div>
          <button onClick={counter2.decrement} style={{ ...buttonStyle, backgroundColor: "#ef4444" }}>
            -5
          </button>
          <button onClick={counter2.reset} style={{ ...buttonStyle, backgroundColor: "#6b7280" }}>
            초기화
          </button>
          <button onClick={counter2.increment} style={{ ...buttonStyle, backgroundColor: "#22c55e" }}>
            +5
          </button>
        </div>
        {/* 슬라이더로도 조작 */}
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={counter2.count}
          onChange={(e) => counter2.set(Number(e.target.value))}
          style={{ width: "100%", marginTop: "8px" }}
        />
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
        maxWidth: "700px",
        margin: "0 auto",
        fontFamily: "sans-serif",
      }}
    >
      <h1 style={{ textAlign: "center" }}>챕터 05: 커스텀 Hook 모음</h1>

      <WindowSizeDisplay />
      <ThemeSettings />
      <SearchWithDebounce />
      <CounterDemo />
    </div>
  );
}

export default App;
