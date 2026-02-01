/**
 * 챕터 10 - 연습 문제 모범 답안
 *
 * 이 파일은 exercise.md의 다섯 문제에 대한 핵심 모범 답안을 담고 있습니다.
 *
 * 실행 방법:
 *   1. 프로젝트 설정:
 *      npm create vite@latest admin-dashboard -- --template react-ts
 *      cd admin-dashboard
 *      npm install react-router-dom @tanstack/react-query zustand recharts date-fns
 *
 *   2. src/ 하위에 FSD 구조로 파일 배치
 *
 *   3. 개발 서버 실행:
 *      npm run dev
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  useRef,
  useMemo,
  type ReactNode,
} from 'react';

// ============================================================
// 문제 1 답안: JWT 인증 시스템 완성
// ============================================================

// --- 타입 정의 ---

type Role = 'super_admin' | 'admin' | 'editor' | 'viewer';
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

interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  department?: string;
}

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

// --- API 클라이언트 (토큰 자동 관리) ---

/**
 * 인증된 API 클라이언트
 *
 * - 모든 요청에 자동으로 Authorization 헤더 추가
 * - 401 응답 시 토큰 자동 갱신 후 요청 재시도
 * - 동시 요청 시 토큰 갱신 중복 방지
 */
class AuthenticatedApiClient {
  private accessToken: string | null = null;
  private refreshPromise: Promise<string> | null = null;
  private onRefreshFailed: (() => void) | null = null;

  setAccessToken(token: string | null) {
    this.accessToken = token;
  }

  setOnRefreshFailed(callback: () => void) {
    this.onRefreshFailed = callback;
  }

  /**
   * 토큰 갱신 (중복 방지)
   * 여러 요청이 동시에 401을 받아도 갱신은 한 번만 실행됩니다.
   */
  private async refreshToken(): Promise<string> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      try {
        const response = await fetch('/api/auth/refresh', {
          method: 'POST',
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error('토큰 갱신 실패');
        }

        const data: AuthTokens = await response.json();
        this.accessToken = data.accessToken;
        return data.accessToken;
      } catch (error) {
        this.accessToken = null;
        this.onRefreshFailed?.();
        throw error;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  /**
   * 인증된 HTTP 요청
   */
  async request<T>(url: string, options: RequestInit = {}): Promise<T> {
    const makeRequest = async (token: string | null): Promise<Response> => {
      return fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...options.headers,
        },
        credentials: 'include',
      });
    };

    // 첫 번째 요청
    let response = await makeRequest(this.accessToken);

    // 401 응답 → 토큰 갱신 후 재시도
    if (response.status === 401) {
      try {
        const newToken = await this.refreshToken();
        response = await makeRequest(newToken);
      } catch {
        throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'API 요청 실패' }));
      throw new Error(error.message);
    }

    return response.json();
  }

  async get<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'GET' });
  }

  async post<T>(url: string, data?: unknown): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(url: string, data: unknown): Promise<T> {
    return this.request<T>(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'DELETE' });
  }
}

export const apiClient = new AuthenticatedApiClient();

// --- 로그인 폼 ---

interface LoginFormProps {
  onLogin: (email: string, password: string, rememberMe: boolean) => Promise<void>;
}

export function LoginForm({ onLogin }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (): boolean => {
    if (!email) {
      setError('이메일을 입력해주세요.');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('올바른 이메일 형식이 아닙니다.');
      return false;
    }
    if (!password) {
      setError('비밀번호를 입력해주세요.');
      return false;
    }
    if (password.length < 6) {
      setError('비밀번호는 6자 이상이어야 합니다.');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await onLogin(email, password, rememberMe);
    } catch (err) {
      setError(err instanceof Error ? err.message : '로그인에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      minHeight: '100vh', background: '#f5f5f5',
    }}>
      <form
        onSubmit={handleSubmit}
        aria-label="로그인"
        style={{
          width: '400px', padding: '40px', background: 'white',
          borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
        }}
      >
        <h1 style={{ textAlign: 'center', marginBottom: '32px' }}>관리자 로그인</h1>

        {error && (
          <div role="alert" style={{
            padding: '12px', background: '#ffebee', color: '#c62828',
            borderRadius: '8px', marginBottom: '16px',
          }}>
            {error}
          </div>
        )}

        <div style={{ marginBottom: '16px' }}>
          <label htmlFor="login-email" style={{ display: 'block', marginBottom: '4px', fontWeight: 600 }}>
            이메일
          </label>
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@example.com"
            disabled={isSubmitting}
            autoComplete="email"
            aria-required="true"
            style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label htmlFor="login-password" style={{ display: 'block', marginBottom: '4px', fontWeight: 600 }}>
            비밀번호
          </label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="비밀번호를 입력하세요"
            disabled={isSubmitting}
            autoComplete="current-password"
            aria-required="true"
            style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd', boxSizing: 'border-box' }}
          />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            로그인 상태 유지
          </label>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            width: '100%', padding: '12px', borderRadius: '6px',
            border: 'none', background: '#1a1a2e', color: 'white',
            fontSize: '16px', fontWeight: 600, cursor: 'pointer',
            opacity: isSubmitting ? 0.7 : 1,
          }}
        >
          {isSubmitting ? '로그인 중...' : '로그인'}
        </button>
      </form>
    </div>
  );
}

// ============================================================
// 문제 2 답안: 역할 기반 접근 제어 (RBAC) 시스템
// ============================================================

// --- 역할-권한 매핑 ---

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  viewer: ['dashboard:read', 'content:read'],
  editor: ['dashboard:read', 'content:read', 'content:write', 'analytics:read'],
  admin: [
    'dashboard:read', 'users:read', 'users:write',
    'content:read', 'content:write', 'content:delete',
    'analytics:read', 'analytics:export',
  ],
  super_admin: [
    'dashboard:read', 'users:read', 'users:write', 'users:delete',
    'content:read', 'content:write', 'content:delete',
    'analytics:read', 'analytics:export', 'settings:manage',
  ],
};

function hasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

// --- 동적 권한 검사 ---

interface DynamicPermissionCheck<TResource = unknown> {
  /** 정적 권한 */
  permission: Permission;
  /** 리소스 소유권 검사 (선택) */
  ownerCheck?: (resource: TResource, user: User) => boolean;
  /** 부서 기반 검사 (선택) */
  departmentCheck?: (user: User) => boolean;
}

function checkDynamicPermission<TResource>(
  user: User,
  check: DynamicPermissionCheck<TResource>,
  resource?: TResource
): boolean {
  // 1. 정적 권한 검사
  if (!hasPermission(user.role, check.permission)) {
    return false;
  }

  // 2. 소유권 검사 (리소스가 있을 때만)
  if (check.ownerCheck && resource) {
    if (!check.ownerCheck(resource, user)) {
      return false;
    }
  }

  // 3. 부서 기반 검사
  if (check.departmentCheck) {
    if (!check.departmentCheck(user)) {
      return false;
    }
  }

  return true;
}

// --- usePermission 훅 ---

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function usePermission() {
  const authContext = useContext(AuthContext);
  const user = authContext?.user;

  return useMemo(
    () => ({
      can: (permission: Permission): boolean =>
        user ? hasPermission(user.role, permission) : false,

      canDynamic: <T>(check: DynamicPermissionCheck<T>, resource?: T): boolean =>
        user ? checkDynamicPermission(user, check, resource) : false,

      canAny: (permissions: Permission[]): boolean =>
        user ? permissions.some((p) => hasPermission(user.role, p)) : false,

      canAll: (permissions: Permission[]): boolean =>
        user ? permissions.every((p) => hasPermission(user.role, p)) : false,

      role: user?.role ?? null,
    }),
    [user]
  );
}

// --- Can 컴포넌트 (동적 권한 지원) ---

interface CanProps<TResource = unknown> {
  /** 정적 권한 */
  permission?: Permission;
  /** 동적 권한 검사 */
  check?: DynamicPermissionCheck<TResource>;
  /** 검사 대상 리소스 */
  resource?: TResource;
  children: ReactNode;
  fallback?: ReactNode;
}

export function Can<TResource>({
  permission,
  check,
  resource,
  children,
  fallback = null,
}: CanProps<TResource>) {
  const { can, canDynamic } = usePermission();

  let hasAccess = true;

  if (permission) {
    hasAccess = can(permission);
  }

  if (check) {
    hasAccess = canDynamic(check, resource);
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>;
}

// --- 사용 예시: 동적 권한 ---

interface Post {
  id: string;
  authorId: string;
  title: string;
}

/**
 * 게시글 편집 버튼
 * - editor 이상: 자신의 게시글만 편집 가능
 * - admin 이상: 모든 게시글 편집 가능
 */
function PostEditButton({ post }: { post: Post }) {
  const { user } = useContext(AuthContext) ?? {};

  return (
    <Can<Post>
      check={{
        permission: 'content:write',
        ownerCheck: (resource, currentUser) =>
          currentUser.role === 'admin' ||
          currentUser.role === 'super_admin' ||
          resource.authorId === currentUser.id,
      }}
      resource={post}
    >
      <button>편집</button>
    </Can>
  );
}

// ============================================================
// 문제 3 답안: 데이터 시각화 대시보드
// ============================================================

// --- 날짜 필터 ---

type DateRange = '7d' | '30d' | '90d' | '1y' | 'custom';

interface DateFilterProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
}

export function DateFilter({ value, onChange }: DateFilterProps) {
  const options: { value: DateRange; label: string }[] = [
    { value: '7d', label: '7일' },
    { value: '30d', label: '30일' },
    { value: '90d', label: '90일' },
    { value: '1y', label: '1년' },
  ];

  return (
    <div role="group" aria-label="기간 선택">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          aria-pressed={value === option.value}
          style={{
            padding: '6px 16px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            background: value === option.value ? '#1a1a2e' : 'white',
            color: value === option.value ? 'white' : '#333',
            cursor: 'pointer',
            marginRight: '4px',
          }}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

// --- 대시보드 페이지 ---

interface DashboardMetrics {
  revenue: { value: number; trend: number };
  users: { value: number; trend: number };
  orders: { value: number; trend: number };
  conversion: { value: number; trend: number };
}

interface KPICardProps {
  title: string;
  value: string;
  trend: number;
  icon: string;
  isLoading?: boolean;
}

function KPICard({ title, value, trend, icon, isLoading }: KPICardProps) {
  if (isLoading) {
    return (
      <div role="status" aria-label={`${title} 로딩 중`} style={{
        padding: '20px', background: 'white', borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      }}>
        <div style={{ width: '60%', height: '14px', background: '#eee', borderRadius: '4px' }} />
        <div style={{ width: '40%', height: '28px', background: '#eee', borderRadius: '4px', marginTop: '12px' }} />
      </div>
    );
  }

  const trendColor = trend > 0 ? '#4CAF50' : trend < 0 ? '#f44336' : '#9E9E9E';
  const trendArrow = trend > 0 ? '↑' : trend < 0 ? '↓' : '→';

  return (
    <article
      aria-label={`${title}: ${value}`}
      style={{
        padding: '20px', background: 'white', borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>{title}</p>
        <span style={{ fontSize: '24px' }}>{icon}</span>
      </div>
      <p style={{ margin: '8px 0 0', fontSize: '28px', fontWeight: 'bold' }}>{value}</p>
      <p style={{ margin: '8px 0 0', fontSize: '13px', color: trendColor }}>
        {trendArrow} {Math.abs(trend).toFixed(1)}% <span style={{ color: '#999' }}>전 기간 대비</span>
      </p>
    </article>
  );
}

export function DashboardPage() {
  const [dateRange, setDateRange] = useState<DateRange>('30d');
  const [isLoading, setIsLoading] = useState(false);

  // 실제로는 React Query 사용:
  // const { data: metrics, isLoading } = useQuery({
  //   queryKey: ['dashboard', 'metrics', dateRange],
  //   queryFn: () => apiClient.get(`/api/dashboard/metrics?range=${dateRange}`),
  //   refetchInterval: 60000,
  // });

  const metrics: DashboardMetrics = {
    revenue: { value: 45200000, trend: 8.3 },
    users: { value: 12470, trend: 12.5 },
    orders: { value: 890, trend: -2.1 },
    conversion: { value: 3.2, trend: 0.5 },
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h2 style={{ margin: 0 }}>대시보드</h2>
        <DateFilter value={dateRange} onChange={setDateRange} />
      </div>

      {/* KPI 그리드 */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px', marginBottom: '24px',
      }}>
        <KPICard
          title="총 매출"
          value={`${(metrics.revenue.value / 10000).toLocaleString()}만원`}
          trend={metrics.revenue.trend}
          icon="💰"
          isLoading={isLoading}
        />
        <KPICard
          title="전체 사용자"
          value={`${metrics.users.value.toLocaleString()}명`}
          trend={metrics.users.trend}
          icon="👥"
          isLoading={isLoading}
        />
        <KPICard
          title="신규 주문"
          value={`${metrics.orders.value}건`}
          trend={metrics.orders.trend}
          icon="📦"
          isLoading={isLoading}
        />
        <KPICard
          title="전환율"
          value={`${metrics.conversion.value}%`}
          trend={metrics.conversion.trend}
          icon="📈"
          isLoading={isLoading}
        />
      </div>

      {/* 차트 영역 (Recharts 사용 시) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '16px',
      }}>
        <div style={{ padding: '20px', background: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
          <h3>매출 추이</h3>
          {/*
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(v) => `${(v / 10000).toLocaleString()}만원`} />
                <Line type="monotone" dataKey="value" stroke="#2196F3" />
              </LineChart>
            </ResponsiveContainer>
          */}
          <p style={{ color: '#999', textAlign: 'center', padding: '40px' }}>
            Recharts 라인 차트 영역
          </p>
        </div>

        <div style={{ padding: '20px', background: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
          <h3>카테고리별 판매</h3>
          <p style={{ color: '#999', textAlign: 'center', padding: '40px' }}>
            Recharts 바 차트 영역
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// 문제 4 답안: 실시간 알림 시스템
// ============================================================

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
}

// --- 알림 센터 컴포넌트 ---

interface NotificationCenterProps {
  notifications: Notification[];
  onMarkAsRead: (id: string) => void;
  onMarkAllAsRead: () => void;
}

export function NotificationCenter({
  notifications,
  onMarkAsRead,
  onMarkAllAsRead,
}: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const unreadCount = notifications.filter((n) => !n.read).length;

  const typeIcons: Record<Notification['type'], string> = {
    info: 'ℹ️',
    warning: '⚠️',
    error: '🔴',
    success: '✅',
  };

  const typeColors: Record<Notification['type'], string> = {
    info: '#2196F3',
    warning: '#FF9800',
    error: '#f44336',
    success: '#4CAF50',
  };

  return (
    <div style={{ position: 'relative' }}>
      {/* 알림 벨 버튼 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label={`알림 ${unreadCount}개 안 읽음`}
        aria-expanded={isOpen}
        aria-haspopup="true"
        style={{
          border: 'none', background: 'none', cursor: 'pointer',
          fontSize: '20px', position: 'relative', padding: '4px',
        }}
      >
        🔔
        {unreadCount > 0 && (
          <span
            aria-hidden="true"
            style={{
              position: 'absolute', top: '-4px', right: '-4px',
              width: '18px', height: '18px', borderRadius: '50%',
              background: '#f44336', color: 'white', fontSize: '11px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* 알림 드롭다운 */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="알림 목록"
          style={{
            position: 'absolute', top: '100%', right: 0,
            width: '360px', maxHeight: '400px',
            background: 'white', borderRadius: '12px',
            boxShadow: '0 8px 30px rgba(0,0,0,0.15)',
            overflow: 'hidden', zIndex: 1000,
          }}
        >
          {/* 헤더 */}
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '12px 16px', borderBottom: '1px solid #eee',
          }}>
            <strong>알림 ({unreadCount}개 안 읽음)</strong>
            {unreadCount > 0 && (
              <button
                onClick={onMarkAllAsRead}
                style={{
                  border: 'none', background: 'none',
                  color: '#2196F3', cursor: 'pointer', fontSize: '13px',
                }}
              >
                모두 읽음
              </button>
            )}
          </div>

          {/* 알림 목록 */}
          <ul
            role="list"
            style={{
              listStyle: 'none', margin: 0, padding: 0,
              maxHeight: '340px', overflowY: 'auto',
            }}
          >
            {notifications.length === 0 ? (
              <li style={{ padding: '24px', textAlign: 'center', color: '#999' }}>
                새 알림이 없습니다.
              </li>
            ) : (
              notifications.map((notification) => (
                <li
                  key={notification.id}
                  onClick={() => onMarkAsRead(notification.id)}
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid #f5f5f5',
                    cursor: 'pointer',
                    background: notification.read ? 'transparent' : '#f0f7ff',
                    transition: 'background 0.2s',
                  }}
                  role="button"
                  tabIndex={0}
                  aria-label={`${notification.read ? '' : '안 읽음: '}${notification.title}`}
                >
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <span style={{ fontSize: '18px' }}>
                      {typeIcons[notification.type]}
                    </span>
                    <div style={{ flex: 1 }}>
                      <p style={{
                        margin: '0 0 4px', fontWeight: notification.read ? 'normal' : 'bold',
                        fontSize: '14px',
                      }}>
                        {notification.title}
                      </p>
                      <p style={{ margin: 0, fontSize: '13px', color: '#666' }}>
                        {notification.message}
                      </p>
                      <time
                        dateTime={notification.createdAt}
                        style={{ fontSize: '12px', color: '#999' }}
                      >
                        {new Date(notification.createdAt).toLocaleString('ko-KR')}
                      </time>
                    </div>
                    {!notification.read && (
                      <span
                        style={{
                          width: '8px', height: '8px', borderRadius: '50%',
                          background: typeColors[notification.type],
                          flexShrink: 0, marginTop: '4px',
                        }}
                        aria-hidden="true"
                      />
                    )}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

// ============================================================
// 문제 5 답안: 통합 프로젝트 구조
// ============================================================

/**
 * Feature-Sliced Design 기반 프로젝트 구조:
 *
 * src/
 * ├── app/
 * │   ├── providers/
 * │   │   ├── AuthProvider.tsx        # 인증 Context (문제 1)
 * │   │   ├── QueryProvider.tsx       # React Query 설정
 * │   │   └── ThemeProvider.tsx       # 테마 관리
 * │   ├── router/
 * │   │   ├── AppRouter.tsx           # 라우트 설정
 * │   │   └── ProtectedRoute.tsx      # 보호된 라우트 (문제 2)
 * │   └── App.tsx
 * │
 * ├── pages/
 * │   ├── login/
 * │   │   └── ui/LoginPage.tsx        # 로그인 페이지 (문제 1)
 * │   ├── dashboard/
 * │   │   └── ui/DashboardPage.tsx    # 대시보드 (문제 3)
 * │   ├── users/
 * │   │   └── ui/UsersPage.tsx        # 사용자 관리
 * │   └── settings/
 * │       └── ui/SettingsPage.tsx      # 설정 페이지
 * │
 * ├── widgets/
 * │   ├── sidebar/
 * │   │   └── ui/Sidebar.tsx          # 사이드바 (RBAC 메뉴 필터링)
 * │   ├── header/
 * │   │   └── ui/Header.tsx           # 헤더 (알림 센터 포함)
 * │   ├── kpi-grid/
 * │   │   └── ui/KPIGrid.tsx          # KPI 카드 그리드
 * │   └── chart-panel/
 * │       └── ui/ChartPanel.tsx       # 차트 패널
 * │
 * ├── features/
 * │   ├── auth/
 * │   │   ├── ui/LoginForm.tsx        # 로그인 폼
 * │   │   ├── model/useAuth.ts        # 인증 훅
 * │   │   ├── api/authApi.ts          # 인증 API
 * │   │   └── index.ts
 * │   ├── realtime/
 * │   │   ├── model/useWebSocket.ts   # WebSocket 훅 (문제 4)
 * │   │   └── index.ts
 * │   ├── notification/
 * │   │   ├── ui/NotificationCenter.tsx
 * │   │   ├── model/useNotifications.ts
 * │   │   └── index.ts
 * │   └── date-filter/
 * │       ├── ui/DateFilter.tsx
 * │       ├── model/useDateRange.ts
 * │       └── index.ts
 * │
 * ├── entities/
 * │   ├── user/
 * │   │   ├── ui/UserCard.tsx
 * │   │   ├── model/types.ts
 * │   │   ├── api/userApi.ts
 * │   │   └── index.ts
 * │   ├── metric/
 * │   │   ├── model/types.ts
 * │   │   ├── api/metricApi.ts
 * │   │   └── index.ts
 * │   └── notification/
 * │       ├── model/types.ts
 * │       └── index.ts
 * │
 * └── shared/
 *     ├── ui/
 *     │   ├── Button.tsx
 *     │   ├── Input.tsx
 *     │   ├── Modal.tsx
 *     │   ├── Toast.tsx
 *     │   └── index.ts
 *     ├── api/
 *     │   ├── client.ts               # AuthenticatedApiClient
 *     │   └── index.ts
 *     ├── lib/
 *     │   ├── permissions.ts          # RBAC 유틸리티
 *     │   ├── formatters.ts           # 값 포맷팅
 *     │   └── index.ts
 *     ├── hooks/
 *     │   ├── useDebounce.ts
 *     │   ├── useLocalStorage.ts
 *     │   └── index.ts
 *     └── config/
 *         └── env.ts                  # 환경 변수
 *
 * 의존성 규칙:
 *   pages → widgets → features → entities → shared
 *   (상위만 하위를 참조, 같은 레이어 간 참조 금지)
 */

// --- 앱 진입점 (App.tsx) ---

/**
 * ```tsx
 * // src/app/App.tsx
 * import { AuthProvider } from '@/features/auth';
 * import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
 * import { BrowserRouter } from 'react-router-dom';
 * import { AppRouter } from './router/AppRouter';
 *
 * const queryClient = new QueryClient({
 *   defaultOptions: {
 *     queries: {
 *       staleTime: 30000,
 *       retry: 1,
 *     },
 *   },
 * });
 *
 * export function App() {
 *   return (
 *     <QueryClientProvider client={queryClient}>
 *       <BrowserRouter>
 *         <AuthProvider>
 *           <AppRouter />
 *         </AuthProvider>
 *       </BrowserRouter>
 *     </QueryClientProvider>
 *   );
 * }
 * ```
 */

/**
 * ```tsx
 * // src/app/router/AppRouter.tsx
 * import { Routes, Route, Navigate } from 'react-router-dom';
 * import { lazy, Suspense } from 'react';
 * import { ProtectedRoute } from './ProtectedRoute';
 * import { DashboardLayout } from '@/widgets/sidebar';
 * import { LoginPage } from '@/pages/login';
 *
 * const DashboardPage = lazy(() => import('@/pages/dashboard'));
 * const UsersPage = lazy(() => import('@/pages/users'));
 * const SettingsPage = lazy(() => import('@/pages/settings'));
 *
 * export function AppRouter() {
 *   return (
 *     <Routes>
 *       <Route path="/login" element={<LoginPage />} />
 *
 *       <Route element={
 *         <ProtectedRoute requiredPermission="dashboard:read">
 *           <DashboardLayout />
 *         </ProtectedRoute>
 *       }>
 *         <Route path="/dashboard" element={
 *           <Suspense fallback={<div>로딩 중...</div>}>
 *             <DashboardPage />
 *           </Suspense>
 *         } />
 *         <Route path="/users" element={
 *           <ProtectedRoute requiredPermission="users:read">
 *             <Suspense fallback={<div>로딩 중...</div>}>
 *               <UsersPage />
 *             </Suspense>
 *           </ProtectedRoute>
 *         } />
 *         <Route path="/settings" element={
 *           <ProtectedRoute requiredPermission="settings:manage">
 *             <Suspense fallback={<div>로딩 중...</div>}>
 *               <SettingsPage />
 *             </Suspense>
 *           </ProtectedRoute>
 *         } />
 *       </Route>
 *
 *       <Route path="*" element={<Navigate to="/dashboard" replace />} />
 *     </Routes>
 *   );
 * }
 * ```
 */

export default DashboardPage;
