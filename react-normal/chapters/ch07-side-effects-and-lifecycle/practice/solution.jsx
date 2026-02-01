/**
 * 챕터 07 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 *
 * 실행 방법:
 *   npx create-react-app ch07-solutions
 *   cd ch07-solutions
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 */

import React, { useState, useEffect, useRef } from 'react';

// ══════════════════════════════════════════════
// 문제 1 답안: 온라인 상태 감지기
// ══════════════════════════════════════════════

function OnlineStatusDetector() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setHistory((prev) => [
        { time: new Date().toLocaleTimeString(), status: '온라인' },
        ...prev,
      ].slice(0, 10)); // 최근 10개만 유지
    };

    const handleOffline = () => {
      setIsOnline(false);
      setHistory((prev) => [
        { time: new Date().toLocaleTimeString(), status: '오프라인' },
        ...prev,
      ].slice(0, 10));
    };

    // 이벤트 리스너 등록
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    console.log('온라인/오프라인 이벤트 리스너 등록됨');

    // 클린업: 이벤트 리스너 해제 (메모리 누수 방지)
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      console.log('온라인/오프라인 이벤트 리스너 해제됨');
    };
  }, []); // 마운트 시 1번만 실행

  return (
    <div style={styles.card}>
      <h2>온라인 상태 감지기</h2>

      <div style={styles.statusBadge}>
        <div
          style={{
            ...styles.statusDot,
            backgroundColor: isOnline ? '#4caf50' : '#f44336',
          }}
        />
        <span style={{ fontSize: '20px', fontWeight: 'bold' }}>
          {isOnline ? '온라인' : '오프라인'}
        </span>
      </div>

      <p style={styles.hint}>
        개발자 도구 &gt; Network 탭에서 "Offline"을 체크하여 테스트하세요.
      </p>

      {history.length > 0 && (
        <div style={styles.historyBox}>
          <h4>상태 변경 이력</h4>
          {history.map((entry, index) => (
            <div key={index} style={styles.historyItem}>
              <span>{entry.time}</span>
              <span
                style={{
                  color: entry.status === '온라인' ? '#4caf50' : '#f44336',
                  fontWeight: 'bold',
                }}
              >
                {entry.status}으로 전환
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// 문제 2 답안: 디바운스 검색 + API 호출
// ══════════════════════════════════════════════

function DebouncedSearch() {
  const [query, setQuery] = useState('');
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  // 디바운스된 검색 실행
  useEffect(() => {
    // 빈 검색어면 API 호출하지 않음
    if (!query.trim()) {
      setPosts([]);
      setHasSearched(false);
      return;
    }

    // 500ms 디바운스
    const timer = setTimeout(() => {
      fetchPosts(query.trim());
    }, 500);

    // 클린업: 이전 타이머 제거
    return () => clearTimeout(timer);
  }, [query]);

  const fetchPosts = async (searchQuery) => {
    let isCancelled = false;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        'https://jsonplaceholder.typicode.com/posts'
      );

      if (!response.ok) {
        throw new Error(`HTTP 에러: ${response.status}`);
      }

      const data = await response.json();

      if (!isCancelled) {
        // 클라이언트 측 필터링
        const filtered = data.filter(
          (post) =>
            post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            post.body.toLowerCase().includes(searchQuery.toLowerCase())
        );
        setPosts(filtered);
        setHasSearched(true);
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
  };

  return (
    <div style={styles.card}>
      <h2>포스트 검색</h2>

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="포스트 제목 또는 내용으로 검색..."
        style={styles.searchInput}
      />

      {/* 상태별 UI */}
      {loading && <p style={styles.loadingText}>검색 중...</p>}

      {error && (
        <div style={styles.errorBox}>
          <p>에러: {error}</p>
          <button
            onClick={() => fetchPosts(query.trim())}
            style={styles.retryButton}
          >
            재시도
          </button>
        </div>
      )}

      {!loading && !error && !query.trim() && (
        <p style={styles.placeholder}>검색어를 입력하세요</p>
      )}

      {!loading && !error && hasSearched && posts.length === 0 && (
        <p style={styles.placeholder}>
          "{query}"에 대한 검색 결과가 없습니다
        </p>
      )}

      {!loading && posts.length > 0 && (
        <>
          <p style={styles.resultCount}>{posts.length}개의 결과</p>
          <div style={styles.postGrid}>
            {posts.slice(0, 10).map((post) => (
              <div key={post.id} style={styles.postCard}>
                <h4 style={styles.postTitle}>{post.title}</h4>
                <p style={styles.postBody}>
                  {post.body.slice(0, 100)}...
                </p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// 문제 3 답안: 카운트다운 타이머
// ══════════════════════════════════════════════

function CountdownTimer() {
  const [inputMinutes, setInputMinutes] = useState(0);
  const [inputSeconds, setInputSeconds] = useState(30);
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isFinished, setIsFinished] = useState(false);

  // 이펙트 1: 카운트다운 타이머
  useEffect(() => {
    if (!isRunning || remainingSeconds <= 0) return;

    const intervalId = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          setIsRunning(false);
          setIsFinished(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    // 클린업: 타이머 해제
    return () => clearInterval(intervalId);
  }, [isRunning, remainingSeconds]);

  // 이펙트 2: document.title 업데이트
  useEffect(() => {
    if (isFinished) {
      document.title = '타이머 종료!';
    } else if (isRunning) {
      const mins = Math.floor(remainingSeconds / 60);
      const secs = remainingSeconds % 60;
      document.title = `남은 시간: ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    } else {
      document.title = 'React 카운트다운 타이머';
    }

    // 클린업: 원래 타이틀로 복원
    return () => {
      document.title = 'React App';
    };
  }, [remainingSeconds, isRunning, isFinished]);

  // 이펙트 3: 타이머 종료 시 알림
  useEffect(() => {
    if (isFinished) {
      alert('타이머 종료!');
    }
  }, [isFinished]);

  const handleStart = () => {
    if (!isRunning && remainingSeconds === 0) {
      // 새로 시작
      const totalSeconds = inputMinutes * 60 + inputSeconds;
      if (totalSeconds <= 0) return;
      setRemainingSeconds(totalSeconds);
      setIsFinished(false);
    }
    setIsRunning(true);
  };

  const handlePause = () => {
    setIsRunning(false);
  };

  const handleReset = () => {
    setIsRunning(false);
    setRemainingSeconds(0);
    setIsFinished(false);
  };

  // 시간 포맷팅
  const displayMinutes = Math.floor(remainingSeconds / 60);
  const displaySeconds = remainingSeconds % 60;
  const formattedTime = `${String(displayMinutes).padStart(2, '0')}:${String(displaySeconds).padStart(2, '0')}`;

  const isWarning = remainingSeconds > 0 && remainingSeconds <= 10;

  return (
    <div style={styles.card}>
      <h2>카운트다운 타이머</h2>

      {/* 시간 설정 (실행 중이 아닐 때만) */}
      {!isRunning && remainingSeconds === 0 && !isFinished && (
        <div style={styles.timeInputGroup}>
          <div style={styles.timeField}>
            <label>분</label>
            <input
              type="number"
              min="0"
              max="59"
              value={inputMinutes}
              onChange={(e) =>
                setInputMinutes(Math.max(0, Math.min(59, Number(e.target.value))))
              }
              style={styles.timeInput}
            />
          </div>
          <span style={styles.timeSeparator}>:</span>
          <div style={styles.timeField}>
            <label>초</label>
            <input
              type="number"
              min="0"
              max="59"
              value={inputSeconds}
              onChange={(e) =>
                setInputSeconds(Math.max(0, Math.min(59, Number(e.target.value))))
              }
              style={styles.timeInput}
            />
          </div>
        </div>
      )}

      {/* 타이머 디스플레이 */}
      <div
        style={{
          ...styles.timerDisplay,
          color: isFinished
            ? '#4caf50'
            : isWarning
            ? '#f44336'
            : '#333',
        }}
      >
        {isFinished ? '완료!' : formattedTime}
      </div>

      {/* 진행률 바 */}
      {(isRunning || remainingSeconds > 0) && !isFinished && (
        <div style={styles.progressBar}>
          <div
            style={{
              ...styles.progressFill,
              width: `${(remainingSeconds / (inputMinutes * 60 + inputSeconds)) * 100}%`,
              backgroundColor: isWarning ? '#f44336' : '#1976d2',
            }}
          />
        </div>
      )}

      {/* 버튼 그룹 */}
      <div style={styles.buttonGroup}>
        {!isRunning ? (
          <button
            onClick={handleStart}
            style={styles.startButton}
            disabled={
              remainingSeconds === 0 &&
              inputMinutes === 0 &&
              inputSeconds === 0
            }
          >
            {remainingSeconds > 0 ? '재개' : '시작'}
          </button>
        ) : (
          <button onClick={handlePause} style={styles.pauseButton}>
            일시정지
          </button>
        )}
        <button onClick={handleReset} style={styles.resetButton}>
          초기화
        </button>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════
// 메인 App: 탭으로 문제 전환
// ══════════════════════════════════════════════

function App() {
  const [activeTab, setActiveTab] = useState(1);

  const tabs = [
    { id: 1, label: '문제 1: 온라인 감지', component: <OnlineStatusDetector /> },
    { id: 2, label: '문제 2: 디바운스 검색', component: <DebouncedSearch /> },
    { id: 3, label: '문제 3: 카운트다운', component: <CountdownTimer /> },
  ];

  return (
    <div style={styles.container}>
      <h1>챕터 07 연습 문제 답안</h1>

      <div style={styles.tabBar}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...styles.tab,
              ...(activeTab === tab.id ? styles.activeTab : {}),
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {tabs.find((tab) => tab.id === activeTab)?.component}
    </div>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  container: {
    maxWidth: '600px',
    margin: '20px auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  card: {
    padding: '24px',
    border: '1px solid #e0e0e0',
    borderRadius: '12px',
    backgroundColor: '#fff',
  },
  tabBar: {
    display: 'flex',
    gap: '8px',
    marginBottom: '20px',
    flexWrap: 'wrap',
  },
  tab: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    borderRadius: '20px',
    backgroundColor: '#f5f5f5',
    cursor: 'pointer',
    fontSize: '13px',
  },
  activeTab: {
    backgroundColor: '#1976d2',
    color: 'white',
    borderColor: '#1976d2',
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    padding: '20px',
    margin: '16px 0',
  },
  statusDot: {
    width: '16px',
    height: '16px',
    borderRadius: '50%',
  },
  hint: {
    color: '#888',
    fontSize: '13px',
    textAlign: 'center',
    marginBottom: '16px',
  },
  historyBox: {
    marginTop: '16px',
    padding: '12px',
    backgroundColor: '#fafafa',
    borderRadius: '8px',
  },
  historyItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '6px 0',
    fontSize: '13px',
    borderBottom: '1px solid #eee',
  },
  searchInput: {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '15px',
    outline: 'none',
    boxSizing: 'border-box',
    marginBottom: '16px',
  },
  loadingText: {
    textAlign: 'center',
    color: '#1976d2',
    fontSize: '15px',
  },
  errorBox: {
    textAlign: 'center',
    padding: '20px',
    backgroundColor: '#ffebee',
    borderRadius: '8px',
  },
  retryButton: {
    padding: '8px 20px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    marginTop: '8px',
  },
  placeholder: {
    textAlign: 'center',
    color: '#999',
    fontSize: '15px',
    padding: '30px 0',
  },
  resultCount: {
    fontSize: '13px',
    color: '#666',
    marginBottom: '12px',
  },
  postGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    maxHeight: '400px',
    overflowY: 'auto',
  },
  postCard: {
    padding: '12px 16px',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
  },
  postTitle: {
    margin: '0 0 6px 0',
    fontSize: '14px',
    color: '#333',
  },
  postBody: {
    margin: 0,
    fontSize: '13px',
    color: '#888',
    lineHeight: '1.4',
  },
  timeInputGroup: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'center',
    gap: '8px',
    marginBottom: '20px',
  },
  timeField: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
  },
  timeInput: {
    width: '80px',
    padding: '10px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '20px',
    textAlign: 'center',
    outline: 'none',
  },
  timeSeparator: {
    fontSize: '32px',
    fontWeight: 'bold',
    paddingBottom: '8px',
  },
  timerDisplay: {
    fontSize: '64px',
    fontWeight: 'bold',
    fontFamily: 'monospace',
    textAlign: 'center',
    padding: '20px',
    transition: 'color 0.3s',
  },
  progressBar: {
    height: '6px',
    backgroundColor: '#e0e0e0',
    borderRadius: '3px',
    overflow: 'hidden',
    marginBottom: '20px',
  },
  progressFill: {
    height: '100%',
    borderRadius: '3px',
    transition: 'width 1s linear, background-color 0.3s',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    justifyContent: 'center',
  },
  startButton: {
    padding: '12px 32px',
    backgroundColor: '#4caf50',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  pauseButton: {
    padding: '12px 32px',
    backgroundColor: '#ff9800',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  resetButton: {
    padding: '12px 32px',
    backgroundColor: '#757575',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
};

export default App;
