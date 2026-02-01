/**
 * 챕터 05 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 *
 * 실행 방법:
 * 1. npx create-react-app ch05-solution (이미 생성했다면 생략)
 * 2. cd ch05-solution
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 *
 * 참고: 문제 1의 온라인/오프라인 테스트는 브라우저 개발자 도구 >
 *       Network 탭에서 "Offline" 체크박스로 가능합니다.
 */

import React, { useState, useEffect, useRef } from "react";

// ============================================================
// 문제 1: 온라인 상태 감지 Hook
// ============================================================

// --- 커스텀 Hook: useOnlineStatus ---
function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // 클린업: 이벤트 리스너 해제
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return isOnline;
}

// --- 사용 컴포넌트 1: 온라인 인디케이터 ---
function OnlineIndicator() {
  const isOnline = useOnlineStatus();

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "8px",
        padding: "8px 16px",
        borderRadius: "20px",
        backgroundColor: isOnline ? "#dcfce7" : "#fef2f2",
        color: isOnline ? "#166534" : "#991b1b",
        fontWeight: "600",
        fontSize: "0.9rem",
      }}
    >
      <div
        style={{
          width: "10px",
          height: "10px",
          borderRadius: "50%",
          backgroundColor: isOnline ? "#22c55e" : "#dc2626",
        }}
      />
      {isOnline ? "온라인" : "오프라인"}
    </div>
  );
}

// --- 사용 컴포넌트 2: 저장 버튼 ---
function SaveButton() {
  const isOnline = useOnlineStatus();

  return (
    <button
      disabled={!isOnline}
      onClick={() => alert("저장되었습니다!")}
      style={{
        padding: "10px 24px",
        border: "none",
        borderRadius: "8px",
        cursor: isOnline ? "pointer" : "not-allowed",
        fontSize: "1rem",
        fontWeight: "500",
        backgroundColor: isOnline ? "#2563eb" : "#9ca3af",
        color: "#fff",
        opacity: isOnline ? 1 : 0.7,
      }}
    >
      {isOnline ? "저장" : "연결 대기 중..."}
    </button>
  );
}

function OnlineStatusDemo() {
  return (
    <div
      style={{
        padding: "24px",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        margin: "16px 0",
        fontFamily: "sans-serif",
      }}
    >
      <h2>문제 1: useOnlineStatus</h2>
      <p style={{ color: "#6b7280" }}>
        브라우저 개발자 도구 &gt; Network 탭에서 "Offline" 체크박스로 테스트하세요.
      </p>
      <div style={{ display: "flex", gap: "16px", alignItems: "center", flexWrap: "wrap" }}>
        <OnlineIndicator />
        <SaveButton />
      </div>
    </div>
  );
}

// ============================================================
// 문제 2: 스톱워치 앱
// ============================================================

function StopWatch() {
  const [time, setTime] = useState(0); // 밀리초 단위
  const [isRunning, setIsRunning] = useState(false);
  const [laps, setLaps] = useState([]); // 랩 시간 기록 (밀리초)
  const [lastLapTime, setLastLapTime] = useState(0); // 마지막 랩 시점

  const intervalRef = useRef(null); // setInterval ID 저장

  // 타이머 관리
  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        setTime((prev) => prev + 10);
      }, 10);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning]);

  // 시간 포맷팅 함수
  const formatTime = (ms) => {
    const mins = Math.floor(ms / 60000);
    const secs = Math.floor((ms % 60000) / 1000);
    const centisecs = Math.floor((ms % 1000) / 10);
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}.${centisecs.toString().padStart(2, "0")}`;
  };

  const handleStart = () => setIsRunning(true);

  const handleStop = () => setIsRunning(false);

  const handleReset = () => {
    setIsRunning(false);
    setTime(0);
    setLaps([]);
    setLastLapTime(0);
  };

  const handleLap = () => {
    const lapTime = time - lastLapTime;
    setLaps((prev) => [lapTime, ...prev]); // 최신순으로 추가
    setLastLapTime(time);
  };

  // 가장 빠른/느린 랩 찾기
  const fastestLap = laps.length > 1 ? Math.min(...laps) : null;
  const slowestLap = laps.length > 1 ? Math.max(...laps) : null;

  const getLapColor = (lapTime) => {
    if (laps.length <= 1) return "#1f2937";
    if (lapTime === fastestLap) return "#22c55e"; // 초록 (가장 빠름)
    if (lapTime === slowestLap) return "#dc2626"; // 빨강 (가장 느림)
    return "#1f2937";
  };

  const buttonStyle = {
    padding: "10px 24px",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "500",
    margin: "4px",
    color: "#fff",
  };

  return (
    <div
      style={{
        padding: "24px",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        margin: "16px 0",
        fontFamily: "sans-serif",
        textAlign: "center",
      }}
    >
      <h2>문제 2: 스톱워치</h2>

      {/* 시간 표시 */}
      <p
        style={{
          fontSize: "3.5rem",
          fontWeight: "bold",
          fontFamily: "monospace",
          margin: "20px 0",
          color: isRunning ? "#2563eb" : "#1f2937",
        }}
      >
        {formatTime(time)}
      </p>

      {/* 버튼 */}
      <div>
        {!isRunning ? (
          <>
            <button
              onClick={handleStart}
              style={{ ...buttonStyle, backgroundColor: "#22c55e" }}
            >
              {time === 0 ? "시작" : "재개"}
            </button>
            {time > 0 && (
              <button
                onClick={handleReset}
                style={{ ...buttonStyle, backgroundColor: "#6b7280" }}
              >
                초기화
              </button>
            )}
          </>
        ) : (
          <>
            <button
              onClick={handleStop}
              style={{ ...buttonStyle, backgroundColor: "#ef4444" }}
            >
              정지
            </button>
            <button
              onClick={handleLap}
              style={{ ...buttonStyle, backgroundColor: "#8b5cf6" }}
            >
              랩
            </button>
          </>
        )}
      </div>

      {/* 랩 기록 */}
      {laps.length > 0 && (
        <div style={{ marginTop: "20px", textAlign: "left" }}>
          <h3>랩 기록</h3>
          <div style={{ maxHeight: "200px", overflow: "auto" }}>
            {laps.map((lapTime, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "8px 12px",
                  borderBottom: "1px solid #f3f4f6",
                  color: getLapColor(lapTime),
                  fontWeight: getLapColor(lapTime) !== "#1f2937" ? "bold" : "normal",
                }}
              >
                <span>랩 {laps.length - index}</span>
                <span style={{ fontFamily: "monospace" }}>
                  {formatTime(lapTime)}
                  {lapTime === fastestLap && laps.length > 1 && " (최고)"}
                  {lapTime === slowestLap && laps.length > 1 && " (최저)"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// 문제 3: 데이터 페칭 Hook (useFetch)
// ============================================================

// --- 커스텀 Hook: useFetch ---
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trigger, setTrigger] = useState(0); // refetch 트리거

  useEffect(() => {
    // URL이 없으면 요청하지 않음
    if (!url) {
      setData(null);
      setLoading(false);
      return;
    }

    let isCancelled = false;

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`HTTP 오류: ${response.status}`);
        }

        const json = await response.json();

        if (!isCancelled) {
          setData(json);
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

    fetchData();

    // 클린업: 언마운트 또는 URL 변경 시 이전 요청 무시
    return () => {
      isCancelled = true;
    };
  }, [url, trigger]); // url 또는 trigger가 변경되면 재실행

  // refetch 함수
  const refetch = () => setTrigger((prev) => prev + 1);

  return { data, loading, error, refetch };
}

// --- 사용 컴포넌트: PostViewer ---
function PostViewer() {
  const [selectedPostId, setSelectedPostId] = useState(null);

  // 게시물 목록 페칭
  const {
    data: posts,
    loading: postsLoading,
    error: postsError,
    refetch: refetchPosts,
  } = useFetch("https://jsonplaceholder.typicode.com/posts");

  // 선택된 게시물 상세 페칭 (selectedPostId가 있을 때만)
  const {
    data: selectedPost,
    loading: postLoading,
    error: postError,
  } = useFetch(
    selectedPostId
      ? `https://jsonplaceholder.typicode.com/posts/${selectedPostId}`
      : null
  );

  const containerStyle = {
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  return (
    <div style={containerStyle}>
      <h2>문제 3: useFetch - 게시물 뷰어</h2>

      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
        {/* 좌측: 게시물 목록 */}
        <div style={{ flex: 1, minWidth: "250px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <h3 style={{ margin: 0 }}>게시물 목록</h3>
            <button
              onClick={refetchPosts}
              style={{
                padding: "4px 12px",
                backgroundColor: "#f3f4f6",
                border: "1px solid #d1d5db",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "0.85rem",
              }}
            >
              새로고침
            </button>
          </div>

          {/* 로딩 상태 */}
          {postsLoading && (
            <p style={{ textAlign: "center", color: "#6b7280", padding: "20px" }}>
              로딩 중...
            </p>
          )}

          {/* 에러 상태 */}
          {postsError && (
            <div
              style={{
                padding: "12px",
                backgroundColor: "#fef2f2",
                color: "#dc2626",
                borderRadius: "6px",
              }}
            >
              오류: {postsError}
            </div>
          )}

          {/* 데이터 상태 */}
          {posts && !postsLoading && (
            <ul style={{ listStyle: "none", padding: 0, maxHeight: "400px", overflow: "auto" }}>
              {posts.slice(0, 10).map((post) => (
                <li
                  key={post.id}
                  onClick={() => setSelectedPostId(post.id)}
                  style={{
                    padding: "10px 12px",
                    borderBottom: "1px solid #f3f4f6",
                    cursor: "pointer",
                    backgroundColor:
                      selectedPostId === post.id ? "#eff6ff" : "transparent",
                    borderLeft:
                      selectedPostId === post.id
                        ? "3px solid #2563eb"
                        : "3px solid transparent",
                    transition: "all 0.15s",
                  }}
                >
                  <span style={{ fontSize: "0.85rem", color: "#9ca3af" }}>
                    #{post.id}
                  </span>
                  <p
                    style={{
                      margin: "4px 0 0",
                      fontSize: "0.9rem",
                      fontWeight: selectedPostId === post.id ? "600" : "400",
                    }}
                  >
                    {post.title}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* 우측: 게시물 상세 */}
        <div
          style={{
            flex: 1,
            minWidth: "250px",
            backgroundColor: "#f8fafc",
            borderRadius: "8px",
            padding: "16px",
          }}
        >
          <h3 style={{ marginTop: 0 }}>상세 내용</h3>

          {/* 선택 안 됨 */}
          {!selectedPostId && (
            <p style={{ color: "#9ca3af", textAlign: "center", padding: "40px 0" }}>
              좌측에서 게시물을 선택하세요
            </p>
          )}

          {/* 로딩 */}
          {selectedPostId && postLoading && (
            <p style={{ color: "#6b7280", textAlign: "center" }}>로딩 중...</p>
          )}

          {/* 에러 */}
          {postError && (
            <p style={{ color: "#dc2626" }}>오류: {postError}</p>
          )}

          {/* 상세 데이터 */}
          {selectedPost && !postLoading && (
            <div>
              <span
                style={{
                  padding: "2px 8px",
                  backgroundColor: "#eff6ff",
                  color: "#2563eb",
                  borderRadius: "4px",
                  fontSize: "0.75rem",
                }}
              >
                #{selectedPost.id}
              </span>
              <h4 style={{ margin: "8px 0" }}>{selectedPost.title}</h4>
              <p style={{ lineHeight: 1.7, color: "#4b5563" }}>
                {selectedPost.body}
              </p>
            </div>
          )}
        </div>
      </div>
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
    <div
      style={{
        backgroundColor: "#f8fafc",
        minHeight: "100vh",
        padding: "20px",
        maxWidth: "800px",
        margin: "0 auto",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          fontFamily: "sans-serif",
          color: "#1e293b",
        }}
      >
        챕터 05 연습 문제 답안
      </h1>

      <div style={dividerStyle}>문제 1: 온라인 상태 감지 Hook</div>
      <OnlineStatusDemo />

      <div style={dividerStyle}>문제 2: 스톱워치 앱</div>
      <StopWatch />

      <div style={dividerStyle}>문제 3: 데이터 페칭 Hook (useFetch)</div>
      <PostViewer />
    </div>
  );
}

export default App;
