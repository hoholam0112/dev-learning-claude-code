/**
 * 챕터 10 - 예제 01: 인증 시스템 + RBAC + 대시보드 레이아웃
 *
 * 이 예제는 엔터프라이즈 관리자 대시보드의 핵심 모듈을 구현합니다:
 *   1. JWT 기반 인증 (Access/Refresh Token)
 *   2. 역할 기반 접근 제어 (RBAC)
 *   3. 보호된 라우트와 대시보드 레이아웃
 *
 * 실행 방법:
 *   1. 프로젝트 생성:
 *      npm create vite@latest admin-dashboard -- --template react-ts
 *      cd admin-dashboard
 *
 *   2. 의존성 설치:
 *      npm install react-router-dom @tanstack/react-query zustand
 *
 *   3. 이 파일을 참고하여 각 모듈을 src/ 하위에 구현
 *
 *   4. 개발 서버 실행:
 *      npm run dev
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useMemo,
  type ReactNode,
} from 'react';

// ============================================================
// 1. 타입 정의
// ============================================================

/** 사용자 역할 */
type Role = 'super_admin' | 'admin' | 'editor' | 'viewer';

/** 권한 */
type Permission =
  | 'dashboard:read'
  | 'users:read'
  | 'users:write'
  | 'users:delete'
  | 'content:read'
  | 'content:write'
  | 'content:delete'
  | 'analytics:read'
  | 'analytics:export'
  | 'settings:manage';

/** 사용자 정보 */
interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  avatar?: string;
  lastLoginAt: string;
}

/** 인증 상태 */
interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

/** 인증 액션 */
interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
}

/** 로그인 응답 */
interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

// ============================================================
// 2. 역할-권한 매핑
// ============================================================

/**
 * 역할별 권한 매핑 테이블
 * 상위 역할은 하위 역할의 모든 권한을 포함합니다.
 */
const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  viewer: ['dashboard:read', 'content:read'],
  editor: [
    'dashboard:read',
    'content:read',
    'content:write',
    'analytics:read',
  ],
  admin: [
    'dashboard:read',
    'users:read',
    'users:write',
    'content:read',
    'content:write',
    'content:delete',
    'analytics:read',
    'analytics:export',
  ],
  super_admin: [
    'dashboard:read',
    'users:read',
    'users:write',
    'users:delete',
    'content:read',
    'content:write',
    'content:delete',
    'analytics:read',
    'analytics:export',
    'settings:manage',
  ],
};

/** 사용자의 권한 확인 */
function hasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

/** 여러 권한 중 하나라도 있는지 확인 */
function hasAnyPermission(role: Role, permissions: Permission[]): boolean {
  return permissions.some((perm) => hasPermission(role, perm));
}

/** 모든 권한이 있는지 확인 */
function hasAllPermissions(role: Role, permissions: Permission[]): boolean {
  return permissions.every((perm) => hasPermission(role, perm));
}

// ============================================================
// 3. 인증 Context & Provider
// ============================================================

type AuthContextValue = AuthState & AuthActions;

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * useAuth 훅
 * 인증 상태와 액션에 접근합니다.
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth는 <AuthProvider> 내부에서 사용해야 합니다.');
  }
  return context;
}

/**
 * usePermission 훅
 * 현재 사용자의 권한을 확인합니다.
 */
export function usePermission() {
  const { user } = useAuth();

  return useMemo(
    () => ({
      /** 특정 권한이 있는지 확인 */
      can: (permission: Permission): boolean =>
        user ? hasPermission(user.role, permission) : false,

      /** 여러 권한 중 하나라도 있는지 확인 */
      canAny: (permissions: Permission[]): boolean =>
        user ? hasAnyPermission(user.role, permissions) : false,

      /** 모든 권한이 있는지 확인 */
      canAll: (permissions: Permission[]): boolean =>
        user ? hasAllPermissions(user.role, permissions) : false,

      /** 현재 역할 */
      role: user?.role ?? null,
    }),
    [user]
  );
}

/**
 * AuthProvider
 *
 * JWT 인증 로직을 관리합니다:
 * - Access Token: 메모리에 저장 (XSS 방지)
 * - Refresh Token: httpOnly 쿠키 (서버 설정 필요)
 * - 자동 토큰 갱신: Access Token 만료 전 자동 갱신
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    isAuthenticated: false,
    isLoading: true, // 초기 로딩 (토큰 검증)
  });

  // 토큰 갱신 타이머
  const refreshTimerRef = React.useRef<ReturnType<typeof setTimeout>>();

  /**
   * 로그인
   */
  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // 쿠키 포함
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || '로그인에 실패했습니다.');
      }

      const data: LoginResponse = await response.json();

      setState({
        user: data.user,
        accessToken: data.accessToken,
        isAuthenticated: true,
        isLoading: false,
      });

      // Access Token 만료 전 자동 갱신 스케줄링 (만료 1분 전)
      scheduleTokenRefresh(data.expiresIn);
    } catch (error) {
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  /**
   * 로그아웃
   */
  const logout = useCallback(async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch {
      // 로그아웃 API 실패해도 클라이언트 상태는 초기화
    }

    setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
    });

    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
  }, []);

  /**
   * 토큰 갱신
   */
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        // Refresh Token도 만료 → 로그아웃
        await logout();
        return false;
      }

      const data: LoginResponse = await response.json();

      setState({
        user: data.user,
        accessToken: data.accessToken,
        isAuthenticated: true,
        isLoading: false,
      });

      scheduleTokenRefresh(data.expiresIn);
      return true;
    } catch {
      await logout();
      return false;
    }
  }, [logout]);

  /**
   * 토큰 갱신 스케줄링
   */
  function scheduleTokenRefresh(expiresIn: number) {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }

    // 만료 1분 전에 갱신
    const refreshTime = (expiresIn - 60) * 1000;
    refreshTimerRef.current = setTimeout(() => {
      refreshToken();
    }, Math.max(refreshTime, 0));
  }

  // 초기 마운트 시 토큰 검증
  useEffect(() => {
    refreshToken().finally(() => {
      setState((prev) => ({ ...prev, isLoading: false }));
    });

    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const contextValue = useMemo(
    () => ({ ...state, login, logout, refreshToken }),
    [state, login, logout, refreshToken]
  );

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
}

// ============================================================
// 4. 보호된 라우트 컴포넌트
// ============================================================

interface ProtectedRouteProps {
  children: ReactNode;
  /** 필요한 권한 (하나라도 있으면 접근 허용) */
  requiredPermission?: Permission;
  /** 필요한 권한 목록 (모두 있어야 접근 허용) */
  requiredPermissions?: Permission[];
  /** 접근 거부 시 표시할 컴포넌트 */
  fallback?: ReactNode;
}

/**
 * ProtectedRoute
 *
 * 인증되지 않은 사용자 → 로그인 페이지로 리다이렉트
 * 권한 부족 → 접근 거부 페이지 표시
 */
export function ProtectedRoute({
  children,
  requiredPermission,
  requiredPermissions,
  fallback,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const { can, canAll } = usePermission();

  // 로딩 중
  if (isLoading) {
    return (
      <div role="status" style={{ padding: '40px', textAlign: 'center' }}>
        인증 정보를 확인하는 중...
      </div>
    );
  }

  // 미인증
  if (!isAuthenticated) {
    // 실제로는 react-router의 <Navigate to="/login" />를 사용
    return (
      <div role="alert" style={{ padding: '40px', textAlign: 'center' }}>
        <h2>로그인이 필요합니다</h2>
        <p>이 페이지에 접근하려면 로그인해주세요.</p>
        <button
          onClick={() => {
            // navigate('/login')
            console.log('로그인 페이지로 이동');
          }}
        >
          로그인
        </button>
      </div>
    );
  }

  // 권한 검사
  const hasRequiredPermission = requiredPermission
    ? can(requiredPermission)
    : true;
  const hasRequiredPermissions = requiredPermissions
    ? canAll(requiredPermissions)
    : true;

  if (!hasRequiredPermission || !hasRequiredPermissions) {
    if (fallback) return <>{fallback}</>;

    return (
      <div role="alert" style={{ padding: '40px', textAlign: 'center' }}>
        <h2>접근 권한이 없습니다</h2>
        <p>
          이 페이지에 접근하려면 추가 권한이 필요합니다.
          <br />
          현재 역할: <strong>{user?.role}</strong>
        </p>
        <button
          onClick={() => {
            // navigate('/dashboard')
            console.log('대시보드로 이동');
          }}
        >
          대시보드로 이동
        </button>
      </div>
    );
  }

  return <>{children}</>;
}

// ============================================================
// 5. 대시보드 레이아웃
// ============================================================

interface NavItem {
  label: string;
  path: string;
  icon: string;
  permission?: Permission;
}

const navItems: NavItem[] = [
  { label: '대시보드', path: '/dashboard', icon: '📊', permission: 'dashboard:read' },
  { label: '사용자 관리', path: '/users', icon: '👥', permission: 'users:read' },
  { label: '콘텐츠 관리', path: '/content', icon: '📝', permission: 'content:read' },
  { label: '분석', path: '/analytics', icon: '📈', permission: 'analytics:read' },
  { label: '설정', path: '/settings', icon: '⚙️', permission: 'settings:manage' },
];

/**
 * 대시보드 레이아웃
 *
 * 사이드바 + 헤더 + 메인 콘텐츠 구조
 * 권한에 따라 네비게이션 항목을 필터링합니다.
 */
export function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const { can } = usePermission();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // 권한에 따라 표시할 네비게이션 항목 필터링
  const visibleNavItems = navItems.filter(
    (item) => !item.permission || can(item.permission)
  );

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* 사이드바 */}
      <aside
        style={{
          width: sidebarOpen ? '250px' : '60px',
          background: '#1a1a2e',
          color: 'white',
          transition: 'width 0.3s',
          overflow: 'hidden',
        }}
        aria-label="메인 네비게이션"
      >
        <div style={{ padding: '20px' }}>
          <h1 style={{ fontSize: sidebarOpen ? '18px' : '14px', margin: 0 }}>
            {sidebarOpen ? '관리자 대시보드' : '📊'}
          </h1>
        </div>

        <nav>
          <ul role="list" style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {visibleNavItems.map((item) => (
              <li key={item.path}>
                <a
                  href={item.path}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 20px',
                    color: 'white',
                    textDecoration: 'none',
                    transition: 'background 0.2s',
                  }}
                  aria-label={item.label}
                >
                  <span>{item.icon}</span>
                  {sidebarOpen && <span>{item.label}</span>}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* 메인 영역 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* 헤더 */}
        <header
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 24px',
            borderBottom: '1px solid #e0e0e0',
            background: 'white',
          }}
        >
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label={sidebarOpen ? '사이드바 닫기' : '사이드바 열기'}
            style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: '20px' }}
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* 알림 */}
            <button aria-label="알림" style={{ border: 'none', background: 'none', cursor: 'pointer' }}>
              🔔
            </button>

            {/* 사용자 정보 */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>{user?.name}</span>
              <span
                style={{
                  fontSize: '12px',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  background: '#e3f2fd',
                }}
              >
                {user?.role}
              </span>
              <button onClick={logout} style={{ cursor: 'pointer' }}>
                로그아웃
              </button>
            </div>
          </div>
        </header>

        {/* 콘텐츠 */}
        <main style={{ flex: 1, padding: '24px', background: '#f5f5f5' }}>
          {children}
        </main>
      </div>
    </div>
  );
}

// ============================================================
// 6. 조건부 권한 렌더링 컴포넌트
// ============================================================

/**
 * Can 컴포넌트
 *
 * 선언적으로 권한 기반 렌더링을 처리합니다.
 */
interface CanProps {
  permission: Permission;
  children: ReactNode;
  fallback?: ReactNode;
}

export function Can({ permission, children, fallback = null }: CanProps) {
  const { can } = usePermission();

  if (!can(permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

// --- 사용 예시 ---

export function DashboardPageExample() {
  return (
    <DashboardLayout>
      <h2>대시보드</h2>

      {/* 모든 사용자가 볼 수 있는 영역 */}
      <section aria-label="개요">
        <p>환영합니다!</p>
      </section>

      {/* 관리자만 볼 수 있는 영역 */}
      <Can permission="users:read">
        <section aria-label="사용자 통계">
          <h3>사용자 통계</h3>
          <p>전체 사용자: 1,234명</p>
        </section>
      </Can>

      {/* 슈퍼 관리자만 볼 수 있는 영역 */}
      <Can
        permission="settings:manage"
        fallback={<p>시스템 설정은 슈퍼 관리자만 접근할 수 있습니다.</p>}
      >
        <section aria-label="시스템 설정">
          <h3>시스템 설정</h3>
          <button>설정 변경</button>
        </section>
      </Can>
    </DashboardLayout>
  );
}

export default DashboardPageExample;
