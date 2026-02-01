/**
 * 챕터 08 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 *
 * 실행 방법:
 *   npx create-react-app ch08-solutions
 *   cd ch08-solutions
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 */

import React, { createContext, useContext, useState, useReducer, useEffect } from 'react';

// ══════════════════════════════════════════════
// 문제 1 답안: 언어 설정 Context
// ══════════════════════════════════════════════

// 번역 데이터
const translations = {
  ko: {
    greeting: '안녕하세요',
    welcome: '환영합니다',
    settings: '설정',
    language: '언어',
    home: '홈',
    about: '소개',
    footer: '모든 권리 보유',
    description: '이 앱은 다국어를 지원합니다.',
    currentLang: '현재 언어: 한국어',
  },
  en: {
    greeting: 'Hello',
    welcome: 'Welcome',
    settings: 'Settings',
    language: 'Language',
    home: 'Home',
    about: 'About',
    footer: 'All rights reserved',
    description: 'This app supports multiple languages.',
    currentLang: 'Current language: English',
  },
};

const LanguageContext = createContext();

function LanguageProvider({ children }) {
  const [lang, setLang] = useState('ko');

  // 번역 함수: 키를 받아 현재 언어의 텍스트 반환
  const t = (key) => translations[lang][key] || key;

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage는 LanguageProvider 안에서만 사용할 수 있습니다');
  }
  return context;
}

// 언어 전환 앱 컴포넌트들
function LangHeader() {
  const { t, lang, setLang } = useLanguage();
  return (
    <header style={{ padding: '16px', borderBottom: '2px solid #1976d2', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <h2>{t('greeting')}!</h2>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>{t('language')}:</span>
        <select value={lang} onChange={(e) => setLang(e.target.value)} style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #ddd' }}>
          <option value="ko">한국어</option>
          <option value="en">English</option>
        </select>
      </div>
    </header>
  );
}

function LangMain() {
  const { t } = useLanguage();
  return (
    <main style={{ padding: '24px' }}>
      <h1>{t('welcome')}</h1>
      <p>{t('description')}</p>
      <nav style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
        <a href="#home" style={{ color: '#1976d2' }}>{t('home')}</a>
        <a href="#about" style={{ color: '#1976d2' }}>{t('about')}</a>
        <a href="#settings" style={{ color: '#1976d2' }}>{t('settings')}</a>
      </nav>
      <p style={{ marginTop: '24px', color: '#666' }}>{t('currentLang')}</p>
    </main>
  );
}

function LangFooter() {
  const { t } = useLanguage();
  return (
    <footer style={{ padding: '16px', borderTop: '1px solid #eee', color: '#888', textAlign: 'center' }}>
      &copy; 2024 MyApp. {t('footer')}.
    </footer>
  );
}

function LanguageApp() {
  return (
    <LanguageProvider>
      <div style={sharedStyles.card}>
        <LangHeader />
        <LangMain />
        <LangFooter />
      </div>
    </LanguageProvider>
  );
}

// ══════════════════════════════════════════════
// 문제 2 답안: 알림(Notification) 시스템
// ══════════════════════════════════════════════

const NotificationContext = createContext();

function notificationReducer(state, action) {
  switch (action.type) {
    case 'ADD_NOTIFICATION':
      return {
        notifications: [
          ...state.notifications,
          {
            id: Date.now(),
            message: action.payload.message,
            type: action.payload.type || 'info',
          },
        ],
      };
    case 'REMOVE_NOTIFICATION':
      return {
        notifications: state.notifications.filter(
          (n) => n.id !== action.payload
        ),
      };
    default:
      return state;
  }
}

function NotificationProvider({ children }) {
  const [state, dispatch] = useReducer(notificationReducer, {
    notifications: [],
  });

  const addNotification = (message, type = 'info') => {
    dispatch({ type: 'ADD_NOTIFICATION', payload: { message, type } });
  };

  const removeNotification = (id) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications: state.notifications,
        addNotification,
        removeNotification,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

function useNotification() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification은 NotificationProvider 안에서만 사용할 수 있습니다');
  }
  return context;
}

// 개별 알림 컴포넌트 (자동 제거 포함)
function NotificationItem({ notification }) {
  const { removeNotification } = useNotification();

  // 3초 후 자동 제거
  useEffect(() => {
    const timer = setTimeout(() => {
      removeNotification(notification.id);
    }, 3000);
    return () => clearTimeout(timer);
  }, [notification.id]);

  const typeColors = {
    success: { bg: '#e8f5e9', border: '#4caf50', text: '#2e7d32' },
    error: { bg: '#ffebee', border: '#f44336', text: '#c62828' },
    info: { bg: '#e3f2fd', border: '#1976d2', text: '#1565c0' },
  };

  const colors = typeColors[notification.type] || typeColors.info;

  return (
    <div
      style={{
        padding: '12px 16px',
        backgroundColor: colors.bg,
        borderLeft: `4px solid ${colors.border}`,
        borderRadius: '4px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px',
        animation: 'slideIn 0.3s ease',
      }}
    >
      <span style={{ color: colors.text }}>{notification.message}</span>
      <button
        onClick={() => removeNotification(notification.id)}
        style={{
          background: 'none',
          border: 'none',
          color: colors.text,
          cursor: 'pointer',
          fontSize: '18px',
          padding: '0 4px',
        }}
      >
        X
      </button>
    </div>
  );
}

// 알림 표시 영역
function NotificationContainer() {
  const { notifications } = useNotification();

  if (notifications.length === 0) return null;

  return (
    <div style={{ position: 'fixed', top: '20px', right: '20px', width: '320px', zIndex: 1000 }}>
      {notifications.map((n) => (
        <NotificationItem key={n.id} notification={n} />
      ))}
    </div>
  );
}

function NotificationApp() {
  const { addNotification } = useNotification();

  return (
    <div style={sharedStyles.card}>
      <h2>알림 시스템</h2>
      <p style={{ color: '#666', marginBottom: '16px' }}>
        버튼을 클릭하여 알림을 생성하세요. 3초 후 자동으로 사라집니다.
      </p>
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          onClick={() => addNotification('작업이 성공적으로 완료되었습니다!', 'success')}
          style={{ ...sharedStyles.button, backgroundColor: '#4caf50' }}
        >
          성공 알림
        </button>
        <button
          onClick={() => addNotification('오류가 발생했습니다. 다시 시도해주세요.', 'error')}
          style={{ ...sharedStyles.button, backgroundColor: '#f44336' }}
        >
          에러 알림
        </button>
        <button
          onClick={() => addNotification('새로운 업데이트가 있습니다.', 'info')}
          style={{ ...sharedStyles.button, backgroundColor: '#1976d2' }}
        >
          정보 알림
        </button>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════
// 문제 3 답안: 미니 상태 관리 라이브러리
// ══════════════════════════════════════════════

/**
 * createStore: 범용 상태 관리 유틸리티
 * Context, Provider, 커스텀 훅을 한 번에 생성한다.
 */
function createStore(reducer, initialState) {
  const StoreContext = createContext();

  function Provider({ children }) {
    const [state, dispatch] = useReducer(reducer, initialState);
    return (
      <StoreContext.Provider value={{ state, dispatch }}>
        {children}
      </StoreContext.Provider>
    );
  }

  function useStore() {
    const context = useContext(StoreContext);
    if (!context) {
      throw new Error('useStore는 해당 Provider 안에서만 사용할 수 있습니다');
    }
    return context;
  }

  return { Provider, useStore };
}

// ── 카운터 스토어 ──
const CounterStore = createStore(
  (state, action) => {
    switch (action.type) {
      case 'INCREMENT': return { ...state, count: state.count + 1 };
      case 'DECREMENT': return { ...state, count: state.count - 1 };
      case 'RESET': return { ...state, count: 0 };
      default: return state;
    }
  },
  { count: 0 }
);

// ── 할 일 스토어 ──
const TodoStore = createStore(
  (state, action) => {
    switch (action.type) {
      case 'ADD_TODO':
        return {
          ...state,
          todos: [...state.todos, { id: Date.now(), text: action.payload, done: false }],
        };
      case 'TOGGLE_TODO':
        return {
          ...state,
          todos: state.todos.map((todo) =>
            todo.id === action.payload ? { ...todo, done: !todo.done } : todo
          ),
        };
      case 'DELETE_TODO':
        return {
          ...state,
          todos: state.todos.filter((todo) => todo.id !== action.payload),
        };
      default:
        return state;
    }
  },
  { todos: [] }
);

// 카운터 컴포넌트
function CounterWidget() {
  const { state, dispatch } = CounterStore.useStore();
  return (
    <div style={{ ...sharedStyles.miniCard, borderColor: '#1976d2' }}>
      <h3>카운터 (createStore)</h3>
      <p style={{ fontSize: '32px', fontWeight: 'bold', textAlign: 'center' }}>
        {state.count}
      </p>
      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
        <button onClick={() => dispatch({ type: 'DECREMENT' })} style={sharedStyles.smallButton}>-1</button>
        <button onClick={() => dispatch({ type: 'RESET' })} style={sharedStyles.smallButton}>0</button>
        <button onClick={() => dispatch({ type: 'INCREMENT' })} style={sharedStyles.smallButton}>+1</button>
      </div>
    </div>
  );
}

// 할 일 컴포넌트
function TodoWidget() {
  const { state, dispatch } = TodoStore.useStore();
  const [input, setInput] = useState('');

  const handleAdd = (e) => {
    e.preventDefault();
    if (input.trim()) {
      dispatch({ type: 'ADD_TODO', payload: input.trim() });
      setInput('');
    }
  };

  return (
    <div style={{ ...sharedStyles.miniCard, borderColor: '#4caf50' }}>
      <h3>할 일 목록 (createStore)</h3>
      <form onSubmit={handleAdd} style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="할 일 입력"
          style={{ flex: 1, padding: '8px', border: '1px solid #ddd', borderRadius: '6px' }}
        />
        <button type="submit" style={{ ...sharedStyles.smallButton, backgroundColor: '#4caf50' }}>추가</button>
      </form>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {state.todos.map((todo) => (
          <li
            key={todo.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 0',
              borderBottom: '1px solid #f0f0f0',
            }}
          >
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })}
            />
            <span style={{ flex: 1, textDecoration: todo.done ? 'line-through' : 'none', color: todo.done ? '#999' : '#333' }}>
              {todo.text}
            </span>
            <button
              onClick={() => dispatch({ type: 'DELETE_TODO', payload: todo.id })}
              style={{ background: 'none', border: 'none', color: '#f44336', cursor: 'pointer' }}
            >
              삭제
            </button>
          </li>
        ))}
      </ul>
      {state.todos.length === 0 && (
        <p style={{ textAlign: 'center', color: '#999', fontSize: '13px' }}>
          할 일이 없습니다
        </p>
      )}
    </div>
  );
}

function MiniStoreApp() {
  return (
    <CounterStore.Provider>
      <TodoStore.Provider>
        <div style={sharedStyles.card}>
          <h2>미니 상태 관리 라이브러리</h2>
          <p style={{ color: '#666', marginBottom: '16px' }}>
            createStore()로 생성된 독립적인 두 스토어가 동작합니다.
          </p>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '250px' }}>
              <CounterWidget />
            </div>
            <div style={{ flex: 1, minWidth: '250px' }}>
              <TodoWidget />
            </div>
          </div>
        </div>
      </TodoStore.Provider>
    </CounterStore.Provider>
  );
}

// ══════════════════════════════════════════════
// 메인 App: 탭으로 문제 전환
// ══════════════════════════════════════════════

function App() {
  const [activeTab, setActiveTab] = useState(1);

  return (
    <NotificationProvider>
      <div style={sharedStyles.container}>
        <h1>챕터 08 연습 문제 답안</h1>

        <div style={sharedStyles.tabBar}>
          {[
            { id: 1, label: '문제 1: 다국어' },
            { id: 2, label: '문제 2: 알림' },
            { id: 3, label: '문제 3: 미니 스토어' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                ...sharedStyles.tab,
                ...(activeTab === tab.id ? sharedStyles.activeTab : {}),
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 1 && <LanguageApp />}
        {activeTab === 2 && <NotificationApp />}
        {activeTab === 3 && <MiniStoreApp />}

        {/* 알림 컨테이너는 항상 렌더링 */}
        <NotificationContainer />
      </div>
    </NotificationProvider>
  );
}

// ──────────────────────────────────────────────
// 공유 스타일
// ──────────────────────────────────────────────

const sharedStyles = {
  container: {
    maxWidth: '700px',
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
  miniCard: {
    padding: '16px',
    border: '2px solid #e0e0e0',
    borderRadius: '10px',
    backgroundColor: '#fafafa',
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
  button: {
    padding: '10px 20px',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  smallButton: {
    padding: '8px 16px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
};

export default App;
