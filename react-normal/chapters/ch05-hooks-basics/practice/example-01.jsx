/**
 * 챕터 05 - 예제 1: useEffect, useRef 활용 예제
 *
 * 학습 포인트:
 * - useEffect의 다양한 사용 패턴 (마운트, 의존성 변경, 클린업)
 * - useRef로 DOM 요소 접근하기
 * - useRef로 렌더링 무관 값 저장하기
 * - 데이터 페칭 (API 호출) 패턴
 * - 타이머와 클린업 함수
 *
 * 실행 방법:
 * 1. npx create-react-app ch05-demo
 * 2. cd ch05-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React, { useState, useEffect, useRef } from "react";

// --- 1. useEffect 기본: 문서 제목 변경 ---
function DocumentTitle() {
  const [count, setCount] = useState(0);

  // count가 변경될 때마다 문서 제목 업데이트
  useEffect(() => {
    document.title = `클릭 ${count}회 | React Hooks`;

    // 클린업: 컴포넌트 언마운트 시 원래 제목 복원
    return () => {
      document.title = "React App";
    };
  }, [count]); // count가 변경될 때 실행

  const containerStyle = {
    padding: "20px",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  return (
    <div style={containerStyle}>
      <h2>1. useEffect: 문서 제목 변경</h2>
      <p>브라우저 탭의 제목이 클릭 수에 따라 변합니다.</p>
      <p style={{ fontSize: "2rem", fontWeight: "bold" }}>{count}회 클릭</p>
      <button
        onClick={() => setCount((prev) => prev + 1)}
        style={{
          padding: "8px 20px",
          backgroundColor: "#2563eb",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "1rem",
        }}
      >
        클릭!
      </button>
    </div>
  );
}

// --- 2. useEffect: 데이터 페칭 (API 호출) ---
function UserFetcher() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 컴포넌트 언마운트 시 요청을 무시하기 위한 플래그
    let isCancelled = false;

    async function fetchUsers() {
      try {
        setLoading(true);
        // JSONPlaceholder: 무료 가짜 API
        const response = await fetch(
          "https://jsonplaceholder.typicode.com/users"
        );
        if (!response.ok) throw new Error("서버 오류");
        const data = await response.json();

        // 언마운트되었으면 상태 업데이트 하지 않음
        if (!isCancelled) {
          setUsers(data.slice(0, 5)); // 5명만 표시
        }
      } catch (err) {
        if (!isCancelled) {
          setError(err.message);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    fetchUsers();

    // 클린업: 컴포넌트 언마운트 시 요청 무시
    return () => {
      isCancelled = true;
    };
  }, []); // 빈 배열: 마운트 시 1번만 실행

  const containerStyle = {
    padding: "20px",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  // 조건부 렌더링: 로딩, 에러, 데이터
  if (loading) {
    return (
      <div style={containerStyle}>
        <h2>2. useEffect: 데이터 페칭</h2>
        <p style={{ textAlign: "center", color: "#6b7280" }}>로딩 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <h2>2. useEffect: 데이터 페칭</h2>
        <p style={{ color: "#dc2626" }}>오류: {error}</p>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <h2>2. useEffect: 데이터 페칭 (API 호출)</h2>
      <p style={{ color: "#6b7280", fontSize: "0.9rem" }}>
        JSONPlaceholder API에서 사용자 목록을 가져왔습니다.
      </p>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {users.map((user) => (
          <li
            key={user.id}
            style={{
              padding: "10px 14px",
              borderBottom: "1px solid #f3f4f6",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <strong>{user.name}</strong>
            <span style={{ color: "#6b7280" }}>{user.email}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// --- 3. useEffect: 타이머와 클린업 ---
function Timer() {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    // isRunning이 false이면 타이머를 시작하지 않음
    if (!isRunning) return;

    const intervalId = setInterval(() => {
      setSeconds((prev) => prev + 1);
    }, 1000);

    // 클린업: isRunning이 false로 변경되거나 컴포넌트 언마운트 시 타이머 해제
    return () => {
      clearInterval(intervalId);
    };
  }, [isRunning]); // isRunning 변경 시 이펙트 재실행

  const formatTime = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const containerStyle = {
    padding: "20px",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    margin: "16px 0",
    fontFamily: "sans-serif",
    textAlign: "center",
  };

  const buttonStyle = {
    padding: "8px 20px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "1rem",
    margin: "4px",
    color: "#fff",
  };

  return (
    <div style={containerStyle}>
      <h2>3. useEffect: 타이머와 클린업</h2>
      <p style={{ fontSize: "3rem", fontWeight: "bold", fontFamily: "monospace" }}>
        {formatTime(seconds)}
      </p>
      <div>
        <button
          onClick={() => setIsRunning(true)}
          disabled={isRunning}
          style={{
            ...buttonStyle,
            backgroundColor: isRunning ? "#9ca3af" : "#22c55e",
          }}
        >
          시작
        </button>
        <button
          onClick={() => setIsRunning(false)}
          disabled={!isRunning}
          style={{
            ...buttonStyle,
            backgroundColor: !isRunning ? "#9ca3af" : "#ef4444",
          }}
        >
          정지
        </button>
        <button
          onClick={() => {
            setIsRunning(false);
            setSeconds(0);
          }}
          style={{ ...buttonStyle, backgroundColor: "#6b7280" }}
        >
          초기화
        </button>
      </div>
    </div>
  );
}

// --- 4. useRef: DOM 접근 ---
function AutoFocusSearch() {
  const inputRef = useRef(null);

  // 마운트 시 자동 포커스
  useEffect(() => {
    inputRef.current.focus();
  }, []);

  const containerStyle = {
    padding: "20px",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  return (
    <div style={containerStyle}>
      <h2>4. useRef: DOM 접근 (자동 포커스)</h2>
      <p style={{ color: "#6b7280" }}>
        페이지 로드 시 검색창에 자동으로 포커스됩니다.
      </p>
      <div style={{ display: "flex", gap: "8px" }}>
        <input
          ref={inputRef}
          type="text"
          placeholder="검색어를 입력하세요 (자동 포커스)"
          style={{
            flex: 1,
            padding: "10px 14px",
            border: "1px solid #d1d5db",
            borderRadius: "8px",
            fontSize: "1rem",
          }}
        />
        <button
          onClick={() => inputRef.current.focus()}
          style={{
            padding: "10px 16px",
            backgroundColor: "#8b5cf6",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
          }}
        >
          포커스
        </button>
      </div>
    </div>
  );
}

// --- 5. useRef: 이전 값 기억하기 ---
function PreviousValue() {
  const [count, setCount] = useState(0);
  const prevCountRef = useRef(0);

  useEffect(() => {
    // 렌더링 후에 현재 값을 ref에 저장
    // 다음 렌더링에서 "이전 값"으로 사용 가능
    prevCountRef.current = count;
  }, [count]);

  const containerStyle = {
    padding: "20px",
    border: "1px solid #e5e7eb",
    borderRadius: "10px",
    margin: "16px 0",
    fontFamily: "sans-serif",
    textAlign: "center",
  };

  return (
    <div style={containerStyle}>
      <h2>5. useRef: 이전 값 기억하기</h2>
      <p>
        현재 값: <strong style={{ fontSize: "1.5rem" }}>{count}</strong>
      </p>
      <p style={{ color: "#6b7280" }}>
        이전 값: <strong>{prevCountRef.current}</strong>
      </p>
      <div>
        <button
          onClick={() => setCount((prev) => prev + 1)}
          style={{
            padding: "8px 20px",
            backgroundColor: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            margin: "4px",
          }}
        >
          +1
        </button>
        <button
          onClick={() => setCount((prev) => prev - 1)}
          style={{
            padding: "8px 20px",
            backgroundColor: "#ef4444",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            margin: "4px",
          }}
        >
          -1
        </button>
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
      <h1 style={{ textAlign: "center" }}>챕터 05: Hooks 기초 - useEffect & useRef</h1>

      <DocumentTitle />
      <UserFetcher />
      <Timer />
      <AutoFocusSearch />
      <PreviousValue />
    </div>
  );
}

export default App;
