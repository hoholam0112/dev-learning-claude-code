/**
 * 챕터 07 - 예제 02: 타이머, 윈도우 이벤트, 로컬 스토리지
 *
 * 핵심 개념:
 * - setInterval과 클린업 (clearInterval)
 * - 윈도우 이벤트 리스너와 클린업 (removeEventListener)
 * - 로컬 스토리지와 useEffect 동기화
 * - 다양한 종류의 사이드 이펙트 실습
 *
 * 실행 방법:
 *   npx create-react-app effect-demo
 *   cd effect-demo
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 */

import React, { useState, useEffect, useRef } from 'react';

// ──────────────────────────────────────────────
// 예시 A: 스톱워치 (setInterval + 클린업)
// ──────────────────────────────────────────────

function Stopwatch() {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  /**
   * isRunning이 true일 때만 타이머를 설정한다.
   * 클린업에서 clearInterval을 호출하여 메모리 누수를 방지한다.
   *
   * 의존성 배열에 [isRunning]을 넣었으므로:
   * - isRunning이 true가 되면: 타이머 설정
   * - isRunning이 false가 되면: 이전 클린업 실행 -> 타이머 해제
   */
  useEffect(() => {
    let intervalId = null;

    if (isRunning) {
      intervalId = setInterval(() => {
        setSeconds((prev) => prev + 1); // 함수형 업데이트 사용
      }, 1000);
      console.log('타이머 시작됨');
    }

    // 클린업: 컴포넌트 언마운트 또는 isRunning 변경 시 실행
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
        console.log('타이머 정리됨');
      }
    };
  }, [isRunning]); // isRunning이 변경될 때만 재실행

  // 시:분:초 형식으로 변환
  const formatTime = (totalSeconds) => {
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const handleReset = () => {
    setIsRunning(false);
    setSeconds(0);
  };

  return (
    <div style={styles.card}>
      <h2>스톱워치</h2>
      <p style={styles.hint}>
        setInterval + clearInterval (클린업) 패턴
      </p>

      <div style={styles.timerDisplay}>{formatTime(seconds)}</div>

      <div style={styles.buttonGroup}>
        <button
          onClick={() => setIsRunning(!isRunning)}
          style={isRunning ? styles.stopButton : styles.startButton}
        >
          {isRunning ? '정지' : '시작'}
        </button>
        <button onClick={handleReset} style={styles.resetButton}>
          초기화
        </button>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────
// 예시 B: 윈도우 크기 추적기 (이벤트 리스너 + 클린업)
// ──────────────────────────────────────────────

function WindowSizeTracker() {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  // 크기 변경 이력
  const [history, setHistory] = useState([]);

  /**
   * 마운트 시 resize 이벤트 리스너를 등록하고,
   * 언마운트 시 제거한다.
   *
   * 빈 배열 []이므로 마운트 시 1번만 등록된다.
   * 클린업에서 removeEventListener로 메모리 누수를 방지한다.
   */
  useEffect(() => {
    const handleResize = () => {
      const newSize = {
        width: window.innerWidth,
        height: window.innerHeight,
      };
      setWindowSize(newSize);
    };

    // 이벤트 리스너 등록
    window.addEventListener('resize', handleResize);
    console.log('resize 이벤트 리스너 등록됨');

    // 클린업: 이벤트 리스너 해제
    return () => {
      window.removeEventListener('resize', handleResize);
      console.log('resize 이벤트 리스너 해제됨');
    };
  }, []); // 마운트 시 1번만 실행

  /**
   * windowSize가 변경될 때마다 이력에 추가한다.
   * 최근 5개까지만 유지한다.
   */
  useEffect(() => {
    setHistory((prev) => {
      const newEntry = {
        ...windowSize,
        time: new Date().toLocaleTimeString(),
      };
      return [newEntry, ...prev].slice(0, 5);
    });
  }, [windowSize.width, windowSize.height]);

  return (
    <div style={styles.card}>
      <h2>윈도우 크기 추적기</h2>
      <p style={styles.hint}>
        addEventListener + removeEventListener (클린업) 패턴
        <br />
        브라우저 크기를 변경해보세요!
      </p>

      <div style={styles.sizeDisplay}>
        <span style={styles.sizeValue}>{windowSize.width}</span>
        <span style={styles.sizeLabel}> x </span>
        <span style={styles.sizeValue}>{windowSize.height}</span>
        <span style={styles.sizeLabel}> px</span>
      </div>

      {history.length > 0 && (
        <div style={styles.historyBox}>
          <h4>변경 이력 (최근 5개)</h4>
          {history.map((entry, index) => (
            <div key={index} style={styles.historyItem}>
              <span>{entry.time}</span>
              <span>{entry.width} x {entry.height}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// 예시 C: 로컬 스토리지 메모장 (로컬 스토리지 동기화)
// ──────────────────────────────────────────────

function PersistentNotepad() {
  // 초기값을 로컬 스토리지에서 가져오기 (지연 초기화)
  const [note, setNote] = useState(() => {
    const saved = localStorage.getItem('notepad-content');
    return saved || '';
  });

  const [lastSaved, setLastSaved] = useState(null);
  const [charCount, setCharCount] = useState(note.length);

  /**
   * note가 변경될 때마다 로컬 스토리지에 저장한다.
   * 디바운스를 적용하여 타이핑 중에는 저장하지 않고,
   * 타이핑이 멈춘 후 500ms 뒤에 저장한다.
   */
  useEffect(() => {
    setCharCount(note.length);

    const timer = setTimeout(() => {
      localStorage.setItem('notepad-content', note);
      setLastSaved(new Date().toLocaleTimeString());
      console.log('로컬 스토리지에 저장됨');
    }, 500); // 500ms 디바운스

    // 클린업: 이전 타이머 제거
    return () => clearTimeout(timer);
  }, [note]);

  /**
   * 문서 타이틀을 메모 내용에 맞게 변경한다.
   * 이것도 사이드 이펙트의 하나이다.
   */
  useEffect(() => {
    const preview = note.slice(0, 20) || '빈 메모';
    document.title = `메모: ${preview}...`;

    // 클린업: 원래 타이틀로 복원
    return () => {
      document.title = 'React App';
    };
  }, [note]);

  const handleClear = () => {
    setNote('');
    localStorage.removeItem('notepad-content');
  };

  return (
    <div style={styles.card}>
      <h2>로컬 스토리지 메모장</h2>
      <p style={styles.hint}>
        localStorage + 디바운스 저장 패턴
        <br />
        페이지를 새로고침해도 메모가 유지됩니다!
      </p>

      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="메모를 작성하세요..."
        rows={6}
        style={styles.textarea}
      />

      <div style={styles.statusBar}>
        <span>{charCount}자</span>
        {lastSaved && <span>마지막 저장: {lastSaved}</span>}
      </div>

      <button onClick={handleClear} style={styles.resetButton}>
        메모 지우기
      </button>
    </div>
  );
}

// ──────────────────────────────────────────────
// 메인 App
// ──────────────────────────────────────────────

function App() {
  // 각 예시의 표시 여부 (언마운트 시 클린업 확인용)
  const [showStopwatch, setShowStopwatch] = useState(true);
  const [showWindowTracker, setShowWindowTracker] = useState(true);
  const [showNotepad, setShowNotepad] = useState(true);

  return (
    <div style={styles.container}>
      <h1>useEffect 다양한 활용</h1>
      <p style={styles.description}>
        각 컴포넌트를 표시/숨김하면 콘솔에서 클린업 함수의 실행을 확인할 수 있습니다.
      </p>

      {/* 토글 버튼들 */}
      <div style={styles.toggleBar}>
        <label style={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={showStopwatch}
            onChange={(e) => setShowStopwatch(e.target.checked)}
          />
          스톱워치
        </label>
        <label style={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={showWindowTracker}
            onChange={(e) => setShowWindowTracker(e.target.checked)}
          />
          윈도우 크기
        </label>
        <label style={styles.toggleLabel}>
          <input
            type="checkbox"
            checked={showNotepad}
            onChange={(e) => setShowNotepad(e.target.checked)}
          />
          메모장
        </label>
      </div>

      {/* 조건부 렌더링: 체크 해제 시 언마운트 -> 클린업 실행 */}
      {showStopwatch && <Stopwatch />}
      {showWindowTracker && <WindowSizeTracker />}
      {showNotepad && <PersistentNotepad />}
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
  description: {
    color: '#666',
    fontSize: '14px',
    lineHeight: '1.6',
    marginBottom: '20px',
  },
  toggleBar: {
    display: 'flex',
    gap: '16px',
    marginBottom: '20px',
    padding: '12px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
  },
  toggleLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  card: {
    padding: '24px',
    border: '1px solid #e0e0e0',
    borderRadius: '12px',
    marginBottom: '20px',
    backgroundColor: 'white',
  },
  hint: {
    color: '#888',
    fontSize: '13px',
    lineHeight: '1.5',
    marginBottom: '16px',
  },
  timerDisplay: {
    fontSize: '48px',
    fontWeight: 'bold',
    fontFamily: 'monospace',
    textAlign: 'center',
    padding: '20px',
    color: '#333',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    justifyContent: 'center',
  },
  startButton: {
    padding: '10px 32px',
    backgroundColor: '#4caf50',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  stopButton: {
    padding: '10px 32px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  resetButton: {
    padding: '10px 32px',
    backgroundColor: '#757575',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  sizeDisplay: {
    textAlign: 'center',
    padding: '20px',
    margin: '16px 0',
    backgroundColor: '#e3f2fd',
    borderRadius: '8px',
  },
  sizeValue: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1976d2',
  },
  sizeLabel: {
    fontSize: '18px',
    color: '#666',
  },
  historyBox: {
    marginTop: '16px',
    padding: '12px',
    backgroundColor: '#fafafa',
    borderRadius: '8px',
    border: '1px solid #eee',
  },
  historyItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '4px 0',
    fontSize: '13px',
    color: '#666',
    borderBottom: '1px solid #eee',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
    outline: 'none',
    boxSizing: 'border-box',
  },
  statusBar: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 0',
    fontSize: '12px',
    color: '#888',
  },
};

export default App;
