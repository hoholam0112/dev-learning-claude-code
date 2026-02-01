/**
 * 챕터 08 - 예제 01: 테마 전환 + 인증 상태 관리
 *
 * 핵심 개념:
 * - createContext / useContext로 전역 상태 관리
 * - Provider 패턴으로 컴포넌트 트리 전체에 데이터 공급
 * - 커스텀 훅으로 Context 사용 편의성 향상
 * - 다중 Context 결합
 *
 * 실행 방법:
 *   npx create-react-app context-demo
 *   cd context-demo
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 */

import React, { createContext, useContext, useState } from 'react';

// ══════════════════════════════════════════════
// 1. Theme Context: 테마(다크/라이트) 전역 관리
// ══════════════════════════════════════════════

// Context 생성
const ThemeContext = createContext();

// Theme Provider 컴포넌트
function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => setIsDark((prev) => !prev);

  // theme 객체를 value로 전달
  const theme = {
    isDark,
    toggleTheme,
    colors: isDark
      ? { bg: '#1a1a2e', text: '#eee', card: '#16213e', accent: '#e94560' }
      : { bg: '#f5f5f5', text: '#333', card: '#ffffff', accent: '#1976d2' },
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
}

// 커스텀 훅: useTheme
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme은 ThemeProvider 안에서만 사용할 수 있습니다');
  }
  return context;
}

// ══════════════════════════════════════════════
// 2. Auth Context: 인증 상태 전역 관리
// ══════════════════════════════════════════════

const AuthContext = createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = (username) => {
    // 실제로는 API 호출 후 토큰 저장 등을 수행
    setUser({ name: username, loggedInAt: new Date().toLocaleTimeString() });
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// 커스텀 훅: useAuth
function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth는 AuthProvider 안에서만 사용할 수 있습니다');
  }
  return context;
}

// ══════════════════════════════════════════════
// 3. UI 컴포넌트들 (Context를 소비)
// ══════════════════════════════════════════════

// 헤더: 테마 토글 + 사용자 정보 표시
function Header() {
  const { isDark, toggleTheme, colors } = useTheme();
  const { user, logout } = useAuth();

  return (
    <header
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 24px',
        backgroundColor: colors.card,
        borderBottom: `2px solid ${colors.accent}`,
      }}
    >
      <h2 style={{ margin: 0, color: colors.text }}>My App</h2>

      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        {/* 테마 전환 버튼 */}
        <button
          onClick={toggleTheme}
          style={{
            padding: '8px 16px',
            backgroundColor: colors.accent,
            color: 'white',
            border: 'none',
            borderRadius: '20px',
            cursor: 'pointer',
            fontSize: '13px',
          }}
        >
          {isDark ? '라이트 모드' : '다크 모드'}
        </button>

        {/* 로그인 상태 표시 */}
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: colors.text, fontSize: '14px' }}>
              {user.name}님
            </span>
            <button
              onClick={logout}
              style={{
                padding: '8px 16px',
                backgroundColor: 'transparent',
                color: colors.accent,
                border: `1px solid ${colors.accent}`,
                borderRadius: '20px',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              로그아웃
            </button>
          </div>
        ) : (
          <span style={{ color: colors.text, fontSize: '14px' }}>
            로그인이 필요합니다
          </span>
        )}
      </div>
    </header>
  );
}

// 로그인 폼
function LoginForm() {
  const { login } = useAuth();
  const { colors } = useTheme();
  const [username, setUsername] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim()) {
      login(username.trim());
      setUsername('');
    }
  };

  return (
    <div
      style={{
        padding: '32px',
        backgroundColor: colors.card,
        borderRadius: '12px',
        maxWidth: '400px',
        margin: '40px auto',
      }}
    >
      <h3 style={{ color: colors.text, marginTop: 0 }}>로그인</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="사용자명을 입력하세요"
          style={{
            width: '100%',
            padding: '12px',
            border: `2px solid ${colors.accent}`,
            borderRadius: '8px',
            fontSize: '14px',
            boxSizing: 'border-box',
            marginBottom: '12px',
            backgroundColor: colors.bg,
            color: colors.text,
          }}
        />
        <button
          type="submit"
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: colors.accent,
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer',
          }}
        >
          로그인
        </button>
      </form>
    </div>
  );
}

// 대시보드: 로그인 후 표시
function Dashboard() {
  const { user } = useAuth();
  const { colors } = useTheme();

  return (
    <div
      style={{
        padding: '32px',
        backgroundColor: colors.card,
        borderRadius: '12px',
        maxWidth: '600px',
        margin: '40px auto',
      }}
    >
      <h3 style={{ color: colors.text, marginTop: 0 }}>대시보드</h3>
      <p style={{ color: colors.text }}>
        환영합니다, <strong>{user.name}</strong>님!
      </p>
      <p style={{ color: colors.text, opacity: 0.7, fontSize: '13px' }}>
        로그인 시간: {user.loggedInAt}
      </p>

      {/* 카드 그리드 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '20px' }}>
        {['프로젝트', '알림', '설정', '도움말'].map((item) => (
          <div
            key={item}
            style={{
              padding: '20px',
              backgroundColor: colors.bg,
              borderRadius: '8px',
              textAlign: 'center',
              color: colors.text,
              border: `1px solid ${colors.accent}30`,
            }}
          >
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

// 메인 콘텐츠: 로그인 여부에 따라 다른 화면 표시
function MainContent() {
  const { user } = useAuth();

  return user ? <Dashboard /> : <LoginForm />;
}

// ══════════════════════════════════════════════
// 4. 최상위 App 컴포넌트
// ══════════════════════════════════════════════

function AppContent() {
  const { colors } = useTheme();

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: colors.bg,
        transition: 'background-color 0.3s, color 0.3s',
      }}
    >
      <Header />
      <MainContent />
    </div>
  );
}

/**
 * App 컴포넌트: Provider들을 중첩하여 전체 앱에 Context 제공
 *
 * Provider 중첩 순서:
 * ThemeProvider (바깥) -> AuthProvider (안쪽) -> 실제 컴포넌트
 *
 * 이렇게 하면 AuthProvider 내부에서도 ThemeContext에 접근할 수 있습니다.
 */
function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
