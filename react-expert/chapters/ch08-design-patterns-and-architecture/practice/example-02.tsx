/**
 * 챕터 08 - 예제 02: Headless Component + HOC + Render Props 패턴
 *
 * 이 예제는 다음을 다룹니다:
 *   1. Headless Component 패턴 (useSelect 훅)
 *   2. Higher-Order Component (withAuth, withAnalytics)
 *   3. Render Props 패턴 (DataFetcher)
 *
 * 실행 방법:
 *   1. example-01의 프로젝트에서 계속:
 *      cd patterns-demo
 *
 *   2. 이 파일을 src/components/AdvancedPatterns.tsx로 복사
 *
 *   3. App.tsx에서 import:
 *      import { AdvancedPatternsDemo } from './components/AdvancedPatterns';
 *
 *   4. 개발 서버 실행:
 *      npm run dev
 */

import React, {
  useState,
  useRef,
  useCallback,
  useEffect,
  useMemo,
  type ReactNode,
  type ComponentType,
  type KeyboardEvent,
} from 'react';

// ============================================================
// 1. Headless Component 패턴: useSelect
// ============================================================

/**
 * Headless Select 훅
 *
 * UI 없이 Select(드롭다운)의 모든 로직을 제공합니다:
 * - 열기/닫기 상태 관리
 * - 키보드 네비게이션 (위/아래 화살표, Enter, Escape)
 * - ARIA 속성 자동 생성
 * - 검색(필터링) 기능
 * - 단일/다중 선택 지원
 */

interface SelectOption<T = string> {
  value: T;
  label: string;
  disabled?: boolean;
}

interface UseSelectOptions<T> {
  options: SelectOption<T>[];
  defaultValue?: T;
  onSelect?: (value: T) => void;
  isMulti?: boolean;
}

interface UseSelectReturn<T> {
  // 상태
  isOpen: boolean;
  selectedOption: SelectOption<T> | null;
  selectedOptions: SelectOption<T>[];
  highlightedIndex: number;
  searchQuery: string;
  filteredOptions: SelectOption<T>[];

  // 액션
  open: () => void;
  close: () => void;
  toggle: () => void;
  select: (option: SelectOption<T>) => void;
  setSearchQuery: (query: string) => void;

  // Props 생성자 (Headless 패턴의 핵심)
  getTriggerProps: () => {
    role: string;
    'aria-haspopup': string;
    'aria-expanded': boolean;
    'aria-label': string;
    onClick: () => void;
    onKeyDown: (e: KeyboardEvent) => void;
    tabIndex: number;
  };
  getMenuProps: () => {
    role: string;
    'aria-label': string;
    tabIndex: number;
  };
  getOptionProps: (option: SelectOption<T>, index: number) => {
    role: string;
    'aria-selected': boolean;
    'aria-disabled': boolean;
    'data-highlighted': boolean;
    onClick: () => void;
    onMouseEnter: () => void;
  };
  getSearchProps: () => {
    type: string;
    role: string;
    'aria-label': string;
    'aria-autocomplete': string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onKeyDown: (e: KeyboardEvent) => void;
  };
}

export function useSelect<T = string>({
  options,
  defaultValue,
  onSelect,
  isMulti = false,
}: UseSelectOptions<T>): UseSelectReturn<T> {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValues, setSelectedValues] = useState<Set<T>>(
    defaultValue ? new Set([defaultValue]) : new Set()
  );
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [searchQuery, setSearchQuery] = useState('');

  // 검색 필터링
  const filteredOptions = useMemo(
    () =>
      options.filter((opt) =>
        opt.label.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    [options, searchQuery]
  );

  // 선택된 옵션들
  const selectedOptions = useMemo(
    () => options.filter((opt) => selectedValues.has(opt.value)),
    [options, selectedValues]
  );

  const selectedOption = selectedOptions[0] ?? null;

  // 열기/닫기
  const open = useCallback(() => {
    setIsOpen(true);
    setHighlightedIndex(0);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setHighlightedIndex(-1);
    setSearchQuery('');
  }, []);

  const toggle = useCallback(() => {
    if (isOpen) close();
    else open();
  }, [isOpen, open, close]);

  // 선택
  const select = useCallback(
    (option: SelectOption<T>) => {
      if (option.disabled) return;

      if (isMulti) {
        setSelectedValues((prev) => {
          const newSet = new Set(prev);
          if (newSet.has(option.value)) {
            newSet.delete(option.value);
          } else {
            newSet.add(option.value);
          }
          return newSet;
        });
      } else {
        setSelectedValues(new Set([option.value]));
        close();
      }

      onSelect?.(option.value);
    },
    [isMulti, close, onSelect]
  );

  // 키보드 네비게이션
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          if (!isOpen) {
            open();
          } else {
            setHighlightedIndex((prev) =>
              Math.min(prev + 1, filteredOptions.length - 1)
            );
          }
          break;
        case 'ArrowUp':
          e.preventDefault();
          setHighlightedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          e.preventDefault();
          if (isOpen && highlightedIndex >= 0) {
            select(filteredOptions[highlightedIndex]);
          } else {
            open();
          }
          break;
        case 'Escape':
          e.preventDefault();
          close();
          break;
        case 'Home':
          e.preventDefault();
          setHighlightedIndex(0);
          break;
        case 'End':
          e.preventDefault();
          setHighlightedIndex(filteredOptions.length - 1);
          break;
      }
    },
    [isOpen, highlightedIndex, filteredOptions, open, close, select]
  );

  // 외부 클릭 감지
  useEffect(() => {
    if (!isOpen) return;
    const handleClickOutside = () => close();
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isOpen, close]);

  // Props 생성자들 (Headless 패턴의 핵심)
  const getTriggerProps = useCallback(
    () => ({
      role: 'combobox' as const,
      'aria-haspopup': 'listbox' as const,
      'aria-expanded': isOpen,
      'aria-label': selectedOption ? selectedOption.label : '선택하세요',
      onClick: (e: React.MouseEvent) => {
        e.stopPropagation();
        toggle();
      },
      onKeyDown: handleKeyDown,
      tabIndex: 0,
    }),
    [isOpen, selectedOption, toggle, handleKeyDown]
  );

  const getMenuProps = useCallback(
    () => ({
      role: 'listbox' as const,
      'aria-label': '옵션 목록',
      tabIndex: -1,
    }),
    []
  );

  const getOptionProps = useCallback(
    (option: SelectOption<T>, index: number) => ({
      role: 'option' as const,
      'aria-selected': selectedValues.has(option.value),
      'aria-disabled': !!option.disabled,
      'data-highlighted': index === highlightedIndex,
      onClick: (e: React.MouseEvent) => {
        e.stopPropagation();
        select(option);
      },
      onMouseEnter: () => setHighlightedIndex(index),
    }),
    [selectedValues, highlightedIndex, select]
  );

  const getSearchProps = useCallback(
    () => ({
      type: 'text' as const,
      role: 'searchbox' as const,
      'aria-label': '옵션 검색',
      'aria-autocomplete': 'list' as const,
      value: searchQuery,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setSearchQuery(e.target.value),
      onKeyDown: handleKeyDown,
    }),
    [searchQuery, handleKeyDown]
  );

  return {
    isOpen,
    selectedOption,
    selectedOptions,
    highlightedIndex,
    searchQuery,
    filteredOptions,
    open,
    close,
    toggle,
    select,
    setSearchQuery,
    getTriggerProps: getTriggerProps as UseSelectReturn<T>['getTriggerProps'],
    getMenuProps,
    getOptionProps,
    getSearchProps,
  };
}

// --- Headless Select 사용 예시 (UI 구현) ---

function CustomSelect() {
  const {
    isOpen,
    selectedOption,
    filteredOptions,
    getTriggerProps,
    getMenuProps,
    getOptionProps,
    getSearchProps,
  } = useSelect({
    options: [
      { value: 'react', label: 'React' },
      { value: 'vue', label: 'Vue' },
      { value: 'angular', label: 'Angular' },
      { value: 'svelte', label: 'Svelte' },
      { value: 'solid', label: 'SolidJS', disabled: true },
    ],
    onSelect: (value) => console.log('선택됨:', value),
  });

  return (
    <div style={{ position: 'relative', width: '250px' }}>
      <button
        {...getTriggerProps()}
        style={{
          width: '100%',
          padding: '8px 12px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          textAlign: 'left',
          cursor: 'pointer',
        }}
      >
        {selectedOption?.label ?? '프레임워크를 선택하세요'}
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            border: '1px solid #ccc',
            borderRadius: '4px',
            background: 'white',
            zIndex: 10,
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          }}
        >
          <input
            {...getSearchProps()}
            placeholder="검색..."
            style={{
              width: '100%',
              padding: '8px',
              border: 'none',
              borderBottom: '1px solid #eee',
              outline: 'none',
            }}
          />
          <ul {...getMenuProps()} style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {filteredOptions.map((option, index) => {
              const optionProps = getOptionProps(option, index);
              return (
                <li
                  key={String(option.value)}
                  {...optionProps}
                  style={{
                    padding: '8px 12px',
                    cursor: option.disabled ? 'not-allowed' : 'pointer',
                    background: optionProps['data-highlighted'] ? '#e3f2fd' : 'transparent',
                    opacity: option.disabled ? 0.5 : 1,
                    fontWeight: optionProps['aria-selected'] ? 'bold' : 'normal',
                  }}
                >
                  {option.label}
                  {optionProps['aria-selected'] && ' ✓'}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

// ============================================================
// 2. Higher-Order Component (HOC) 패턴
// ============================================================

// --- 인증 관련 타입 ---

interface User {
  id: string;
  name: string;
  role: 'admin' | 'editor' | 'viewer';
}

interface WithAuthProps {
  user: User;
}

// 시뮬레이션용 인증 상태
const mockUser: User | null = {
  id: '1',
  name: '김관리자',
  role: 'admin',
};

function useAuth() {
  return {
    user: mockUser,
    isAuthenticated: !!mockUser,
    isLoading: false,
  };
}

/**
 * withAuth HOC
 *
 * 인증이 필요한 컴포넌트를 래핑합니다.
 * - 인증되지 않은 사용자는 로그인 페이지로 리다이렉트
 * - 권한이 부족한 사용자에게 접근 거부 표시
 * - 인증된 사용자 정보를 props로 주입
 */
function withAuth<P extends WithAuthProps>(
  WrappedComponent: ComponentType<P>,
  options: { requiredRole?: User['role'] } = {}
) {
  // displayName 설정 (디버깅용)
  const displayName =
    WrappedComponent.displayName || WrappedComponent.name || 'Component';

  function WithAuthComponent(props: Omit<P, keyof WithAuthProps>) {
    const { user, isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
      return (
        <div role="status" aria-label="인증 확인 중">
          인증 정보를 확인하는 중...
        </div>
      );
    }

    if (!isAuthenticated || !user) {
      return (
        <div role="alert">
          <h2>로그인이 필요합니다</h2>
          <p>이 페이지에 접근하려면 로그인해주세요.</p>
          <button onClick={() => console.log('로그인 페이지로 이동')}>
            로그인
          </button>
        </div>
      );
    }

    // 역할 기반 접근 제어
    const roleHierarchy: Record<User['role'], number> = {
      viewer: 0,
      editor: 1,
      admin: 2,
    };

    if (
      options.requiredRole &&
      roleHierarchy[user.role] < roleHierarchy[options.requiredRole]
    ) {
      return (
        <div role="alert">
          <h2>접근 권한이 없습니다</h2>
          <p>
            이 페이지는 <strong>{options.requiredRole}</strong> 이상 권한이
            필요합니다. 현재 권한: <strong>{user.role}</strong>
          </p>
        </div>
      );
    }

    return <WrappedComponent {...(props as P)} user={user} />;
  }

  WithAuthComponent.displayName = `withAuth(${displayName})`;
  return WithAuthComponent;
}

// --- Analytics HOC ---

interface AnalyticsEvent {
  event: string;
  component: string;
  timestamp: number;
  props?: Record<string, unknown>;
}

/**
 * withAnalytics HOC
 *
 * 컴포넌트의 마운트/언마운트와 주요 이벤트를 추적합니다.
 */
function withAnalytics<P extends object>(
  WrappedComponent: ComponentType<P>,
  componentName: string
) {
  const displayName =
    WrappedComponent.displayName || WrappedComponent.name || 'Component';

  function WithAnalyticsComponent(props: P) {
    const mountTimeRef = useRef(Date.now());

    useEffect(() => {
      // 마운트 이벤트
      const event: AnalyticsEvent = {
        event: 'component_mount',
        component: componentName,
        timestamp: Date.now(),
      };
      console.log('[Analytics]', event);

      return () => {
        // 언마운트 이벤트 (체류 시간 포함)
        const duration = Date.now() - mountTimeRef.current;
        console.log('[Analytics]', {
          event: 'component_unmount',
          component: componentName,
          timestamp: Date.now(),
          duration: `${duration}ms`,
        });
      };
    }, []);

    return <WrappedComponent {...props} />;
  }

  WithAnalyticsComponent.displayName = `withAnalytics(${displayName})`;
  return WithAnalyticsComponent;
}

// --- HOC 사용 예시 ---

function AdminDashboard({ user }: WithAuthProps) {
  return (
    <div>
      <h2>관리자 대시보드</h2>
      <p>환영합니다, {user.name}님! (역할: {user.role})</p>
      <ul>
        <li>사용자 관리</li>
        <li>콘텐츠 관리</li>
        <li>시스템 설정</li>
      </ul>
    </div>
  );
}

// HOC 적용: 인증 + 관리자 권한 + 분석 추적
const ProtectedAdminDashboard = withAnalytics(
  withAuth(AdminDashboard, { requiredRole: 'admin' }),
  'AdminDashboard'
);

// ============================================================
// 3. Render Props 패턴
// ============================================================

/**
 * DataFetcher - Render Props 패턴
 *
 * 데이터 페칭 로직을 캡슐화하고 렌더링을 외부에 위임합니다.
 * 주로 라이브러리에서 유연한 API를 제공할 때 사용합니다.
 */

interface DataFetcherProps<T> {
  url: string;
  children: (state: {
    data: T | null;
    loading: boolean;
    error: string | null;
    refetch: () => void;
  }) => ReactNode;
}

function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const json: T = await response.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 렌더링을 children 함수에 위임
  return <>{children({ data, loading, error, refetch: fetchData })}</>;
}

/**
 * Toggle - Render Props 패턴
 *
 * 토글 상태 로직을 제공합니다.
 */
interface ToggleProps {
  initialOn?: boolean;
  children: (state: {
    on: boolean;
    toggle: () => void;
    setOn: () => void;
    setOff: () => void;
  }) => ReactNode;
}

function Toggle({ initialOn = false, children }: ToggleProps) {
  const [on, setOnState] = useState(initialOn);

  const toggle = useCallback(() => setOnState((prev) => !prev), []);
  const setOn = useCallback(() => setOnState(true), []);
  const setOff = useCallback(() => setOnState(false), []);

  return <>{children({ on, toggle, setOn, setOff })}</>;
}

// ============================================================
// 4. 종합 데모
// ============================================================

export function AdvancedPatternsDemo() {
  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '24px' }}>
      <h1>고급 설계 패턴 데모</h1>

      {/* Headless Select */}
      <section>
        <h2>1. Headless Component (useSelect)</h2>
        <p>로직은 훅이 제공하고, UI는 자유롭게 구현합니다.</p>
        <CustomSelect />
      </section>

      <hr style={{ margin: '32px 0' }} />

      {/* HOC */}
      <section>
        <h2>2. HOC (withAuth + withAnalytics)</h2>
        <p>인증 및 분석 추적이 자동으로 적용됩니다.</p>
        <ProtectedAdminDashboard />
      </section>

      <hr style={{ margin: '32px 0' }} />

      {/* Render Props - Toggle */}
      <section>
        <h2>3. Render Props (Toggle)</h2>
        <Toggle>
          {({ on, toggle }) => (
            <div>
              <p>상태: {on ? '켜짐' : '꺼짐'}</p>
              <button onClick={toggle}>
                {on ? '끄기' : '켜기'}
              </button>
            </div>
          )}
        </Toggle>
      </section>

      <hr style={{ margin: '32px 0' }} />

      {/* Render Props - DataFetcher */}
      <section>
        <h2>4. Render Props (DataFetcher)</h2>
        <DataFetcher<{ title: string }[]>
          url="https://jsonplaceholder.typicode.com/posts?_limit=3"
        >
          {({ data, loading, error, refetch }) => {
            if (loading) return <p>로딩 중...</p>;
            if (error) return (
              <div>
                <p>오류: {error}</p>
                <button onClick={refetch}>다시 시도</button>
              </div>
            );
            return (
              <ul>
                {data?.map((post, i) => (
                  <li key={i}>{post.title}</li>
                ))}
              </ul>
            );
          }}
        </DataFetcher>
      </section>
    </div>
  );
}

export default AdvancedPatternsDemo;
