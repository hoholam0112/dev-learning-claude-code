/**
 * 챕터 08 - 연습 문제 모범 답안
 *
 * 이 파일은 exercise.md의 세 문제에 대한 모범 답안을 담고 있습니다.
 *
 * 실행 방법:
 *   1. Vite 프로젝트에서 실행:
 *      cd patterns-demo
 *
 *   2. 이 파일을 src/components/Solutions.tsx로 복사
 *
 *   3. App.tsx에서 import:
 *      import { ModalDemo, TableDemo } from './components/Solutions';
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
  useRef,
  useId,
  useMemo,
  type ReactNode,
  type ReactElement,
} from 'react';
import { createPortal } from 'react-dom';

// ============================================================
// 문제 1 답안: Compound Components - Modal 시스템
// ============================================================

// --- 타입 정의 ---

interface ModalContextValue {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  titleId: string;
  descriptionId: string;
}

interface ModalProps {
  /** 제어 모드: 외부에서 열림 상태를 관리 */
  open?: boolean;
  /** 제어 모드: 상태 변경 콜백 */
  onOpenChange?: (open: boolean) => void;
  /** 기본 열림 상태 (비제어 모드) */
  defaultOpen?: boolean;
  children: ReactNode;
}

interface ModalContentProps {
  children: ReactNode;
  className?: string;
  /** 오버레이 클릭으로 닫기 허용 여부 */
  closeOnOverlayClick?: boolean;
  /** 최대 너비 */
  maxWidth?: string;
}

interface AsChildProps {
  /** true이면 자식 요소에 props를 병합 */
  asChild?: boolean;
  children: ReactNode;
  className?: string;
}

// --- Context ---

const ModalContext = createContext<ModalContextValue | null>(null);

function useModalContext(): ModalContextValue {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('Modal 하위 컴포넌트는 <Modal> 내부에서 사용해야 합니다.');
  }
  return context;
}

// --- 유틸리티: asChild 지원 ---

function Slot({
  children,
  ...props
}: {
  children: ReactNode;
  [key: string]: unknown;
}) {
  if (React.isValidElement(children)) {
    return React.cloneElement(children, {
      ...props,
      ...(children.props as Record<string, unknown>),
    } as React.HTMLAttributes<HTMLElement>);
  }
  return <>{children}</>;
}

// --- 유틸리티: 포커스 트래핑 ---

function useFocusTrap(isActive: boolean) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableSelector =
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

    // 열릴 때 첫 번째 요소에 포커스
    const firstFocusable = container.querySelector<HTMLElement>(focusableSelector);
    firstFocusable?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const focusableElements = container.querySelectorAll<HTMLElement>(focusableSelector);
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isActive]);

  return containerRef;
}

// --- 컴포넌트 ---

function ModalRoot({
  open: controlledOpen,
  onOpenChange,
  defaultOpen = false,
  children,
}: ModalProps) {
  const [internalOpen, setInternalOpen] = useState(defaultOpen);
  const isControlled = controlledOpen !== undefined;
  const isOpen = isControlled ? controlledOpen : internalOpen;
  const id = useId();

  const openModal = useCallback(() => {
    if (!isControlled) setInternalOpen(true);
    onOpenChange?.(true);
  }, [isControlled, onOpenChange]);

  const closeModal = useCallback(() => {
    if (!isControlled) setInternalOpen(false);
    onOpenChange?.(false);
  }, [isControlled, onOpenChange]);

  const contextValue = useMemo(
    () => ({
      isOpen,
      open: openModal,
      close: closeModal,
      titleId: `${id}-title`,
      descriptionId: `${id}-description`,
    }),
    [isOpen, openModal, closeModal, id]
  );

  return (
    <ModalContext.Provider value={contextValue}>
      {children}
    </ModalContext.Provider>
  );
}

function ModalTrigger({ asChild, children, className }: AsChildProps) {
  const { open } = useModalContext();

  if (asChild) {
    return <Slot onClick={open}>{children}</Slot>;
  }

  return (
    <button type="button" className={className} onClick={open}>
      {children}
    </button>
  );
}

function ModalContent({
  children,
  className,
  closeOnOverlayClick = true,
  maxWidth = '500px',
}: ModalContentProps) {
  const { isOpen, close, titleId } = useModalContext();
  const focusTrapRef = useFocusTrap(isOpen);

  // Escape 키로 닫기
  useEffect(() => {
    if (!isOpen) return;
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, close]);

  // body 스크롤 잠금
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div
      className="modal-overlay"
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
      }}
      onClick={(e) => {
        if (closeOnOverlayClick && e.target === e.currentTarget) {
          close();
        }
      }}
    >
      <div
        ref={focusTrapRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={className}
        style={{
          background: 'white',
          borderRadius: '8px',
          maxWidth,
          width: '100%',
          maxHeight: '85vh',
          overflow: 'auto',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        }}
      >
        {children}
      </div>
    </div>,
    document.body
  );
}

function ModalHeader({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const { close, titleId } = useModalContext();

  return (
    <div
      className={className}
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 24px',
        borderBottom: '1px solid #eee',
      }}
    >
      <h2 id={titleId} style={{ margin: 0 }}>
        {children}
      </h2>
      <button
        type="button"
        onClick={close}
        aria-label="모달 닫기"
        style={{
          border: 'none',
          background: 'none',
          fontSize: '20px',
          cursor: 'pointer',
        }}
      >
        &times;
      </button>
    </div>
  );
}

function ModalBody({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={className} style={{ padding: '24px' }}>
      {children}
    </div>
  );
}

function ModalFooter({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={className}
      style={{
        display: 'flex',
        justifyContent: 'flex-end',
        gap: '8px',
        padding: '16px 24px',
        borderTop: '1px solid #eee',
      }}
    >
      {children}
    </div>
  );
}

function ModalClose({ asChild, children, className }: AsChildProps) {
  const { close } = useModalContext();

  if (asChild) {
    return <Slot onClick={close}>{children}</Slot>;
  }

  return (
    <button type="button" className={className} onClick={close}>
      {children}
    </button>
  );
}

// Compound Component 합성
export const Modal = Object.assign(ModalRoot, {
  Trigger: ModalTrigger,
  Content: ModalContent,
  Header: ModalHeader,
  Body: ModalBody,
  Footer: ModalFooter,
  Close: ModalClose,
});

// --- Modal 사용 예시 ---

export function ModalDemo() {
  return (
    <div>
      <h2>Modal Compound Component</h2>

      <Modal>
        <Modal.Trigger asChild>
          <button style={{ padding: '8px 16px' }}>모달 열기</button>
        </Modal.Trigger>
        <Modal.Content>
          <Modal.Header>설정</Modal.Header>
          <Modal.Body>
            <p>모달 내부 콘텐츠입니다.</p>
            <p>Escape 키 또는 배경 클릭으로 닫을 수 있습니다.</p>
            <input
              type="text"
              placeholder="포커스 트래핑 테스트"
              style={{ width: '100%', padding: '8px', marginTop: '8px' }}
            />
          </Modal.Body>
          <Modal.Footer>
            <Modal.Close asChild>
              <button style={{ padding: '8px 16px' }}>취소</button>
            </Modal.Close>
            <button
              style={{
                padding: '8px 16px',
                background: '#2196F3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
              }}
            >
              확인
            </button>
          </Modal.Footer>
        </Modal.Content>
      </Modal>
    </div>
  );
}

// ============================================================
// 문제 2 답안: Headless Component - useTable 훅
// ============================================================

// --- 타입 정의 ---

interface ColumnDef<T> {
  /** 컬럼 고유 ID */
  id: string;
  /** 헤더 표시 텍스트 */
  header: string;
  /** 데이터 객체의 키 */
  accessorKey: keyof T;
  /** 정렬 가능 여부 */
  sortable?: boolean;
  /** 커스텀 셀 렌더링 */
  cell?: (value: T[keyof T], row: T) => ReactNode;
}

interface SortState {
  columnId: string;
  direction: 'asc' | 'desc';
}

interface UseTableOptions<T> {
  data: T[];
  columns: ColumnDef<T>[];
  pageSize?: number;
  initialSort?: SortState;
}

interface UseTableReturn<T> {
  // 상태
  rows: T[];
  totalRows: number;
  currentPage: number;
  totalPages: number;
  sortState: SortState | null;
  searchQuery: string;
  selectedRows: Set<number>;

  // 액션
  setCurrentPage: (page: number) => void;
  setSort: (columnId: string) => void;
  setSearchQuery: (query: string) => void;
  toggleRowSelection: (index: number) => void;
  toggleAllSelection: () => void;
  isAllSelected: boolean;

  // Props 생성자
  getTableProps: () => {
    role: string;
    'aria-label': string;
    'aria-rowcount': number;
  };
  getHeaderProps: (column: ColumnDef<T>) => {
    role: string;
    scope: string;
    'aria-sort': 'ascending' | 'descending' | 'none';
    onClick: (() => void) | undefined;
    style: { cursor: string };
  };
  getRowProps: (row: T, index: number) => {
    role: string;
    'aria-selected': boolean;
    'aria-rowindex': number;
  };
  getCellProps: (column: ColumnDef<T>, row: T) => {
    role: string;
    children: ReactNode;
  };
}

export function useTable<T extends Record<string, unknown>>({
  data,
  columns,
  pageSize = 10,
  initialSort,
}: UseTableOptions<T>): UseTableReturn<T> {
  const [sortState, setSortState] = useState<SortState | null>(
    initialSort ?? null
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set());

  // 1단계: 필터링
  const filteredData = useMemo(() => {
    if (!searchQuery.trim()) return data;

    const query = searchQuery.toLowerCase();
    return data.filter((row) =>
      columns.some((col) => {
        const value = row[col.accessorKey];
        return String(value).toLowerCase().includes(query);
      })
    );
  }, [data, searchQuery, columns]);

  // 2단계: 정렬
  const sortedData = useMemo(() => {
    if (!sortState) return filteredData;

    const column = columns.find((col) => col.id === sortState.columnId);
    if (!column) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aVal = a[column.accessorKey];
      const bVal = b[column.accessorKey];

      let comparison = 0;
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal, 'ko');
      } else if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal;
      } else {
        comparison = String(aVal).localeCompare(String(bVal));
      }

      return sortState.direction === 'asc' ? comparison : -comparison;
    });
  }, [filteredData, sortState, columns]);

  // 3단계: 페이지네이션
  const totalPages = Math.ceil(sortedData.length / pageSize);
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize]);

  // 검색/정렬 변경 시 첫 페이지로 이동
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, sortState]);

  // 정렬 토글
  const setSort = useCallback(
    (columnId: string) => {
      const column = columns.find((col) => col.id === columnId);
      if (!column?.sortable) return;

      setSortState((prev) => {
        if (prev?.columnId === columnId) {
          if (prev.direction === 'asc') {
            return { columnId, direction: 'desc' };
          }
          return null; // 정렬 해제
        }
        return { columnId, direction: 'asc' };
      });
    },
    [columns]
  );

  // 행 선택
  const toggleRowSelection = useCallback((index: number) => {
    setSelectedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  }, []);

  const isAllSelected =
    paginatedData.length > 0 &&
    paginatedData.every((_, index) =>
      selectedRows.has((currentPage - 1) * pageSize + index)
    );

  const toggleAllSelection = useCallback(() => {
    setSelectedRows((prev) => {
      const newSet = new Set(prev);
      const pageStart = (currentPage - 1) * pageSize;

      if (isAllSelected) {
        // 전체 해제
        paginatedData.forEach((_, index) => newSet.delete(pageStart + index));
      } else {
        // 전체 선택
        paginatedData.forEach((_, index) => newSet.add(pageStart + index));
      }
      return newSet;
    });
  }, [currentPage, pageSize, paginatedData, isAllSelected]);

  // Props 생성자
  const getTableProps = useCallback(
    () => ({
      role: 'table' as const,
      'aria-label': '데이터 테이블',
      'aria-rowcount': sortedData.length,
    }),
    [sortedData.length]
  );

  const getHeaderProps = useCallback(
    (column: ColumnDef<T>) => ({
      role: 'columnheader' as const,
      scope: 'col' as const,
      'aria-sort': (sortState?.columnId === column.id
        ? sortState.direction === 'asc'
          ? 'ascending'
          : 'descending'
        : 'none') as 'ascending' | 'descending' | 'none',
      onClick: column.sortable ? () => setSort(column.id) : undefined,
      style: { cursor: column.sortable ? 'pointer' : 'default' },
    }),
    [sortState, setSort]
  );

  const getRowProps = useCallback(
    (_row: T, index: number) => ({
      role: 'row' as const,
      'aria-selected': selectedRows.has(
        (currentPage - 1) * pageSize + index
      ),
      'aria-rowindex': (currentPage - 1) * pageSize + index + 1,
    }),
    [selectedRows, currentPage, pageSize]
  );

  const getCellProps = useCallback(
    (column: ColumnDef<T>, row: T) => ({
      role: 'cell' as const,
      children: column.cell
        ? column.cell(row[column.accessorKey], row)
        : String(row[column.accessorKey] ?? ''),
    }),
    []
  );

  return {
    rows: paginatedData,
    totalRows: sortedData.length,
    currentPage,
    totalPages,
    sortState,
    searchQuery,
    selectedRows,
    setCurrentPage,
    setSort,
    setSearchQuery,
    toggleRowSelection,
    toggleAllSelection,
    isAllSelected,
    getTableProps,
    getHeaderProps,
    getRowProps,
    getCellProps,
  };
}

// --- useTable 사용 예시 ---

interface Employee {
  id: number;
  name: string;
  department: string;
  salary: number;
  joinDate: string;
}

const sampleEmployees: Employee[] = [
  { id: 1, name: '김철수', department: '개발팀', salary: 5500, joinDate: '2020-03-15' },
  { id: 2, name: '이영희', department: '디자인팀', salary: 4800, joinDate: '2021-07-20' },
  { id: 3, name: '박민수', department: '개발팀', salary: 6200, joinDate: '2019-01-10' },
  { id: 4, name: '정수연', department: '마케팅팀', salary: 4500, joinDate: '2022-02-28' },
  { id: 5, name: '최준호', department: '개발팀', salary: 5800, joinDate: '2020-11-05' },
  { id: 6, name: '한소영', department: '디자인팀', salary: 5100, joinDate: '2021-04-12' },
  { id: 7, name: '윤재현', department: '마케팅팀', salary: 4700, joinDate: '2022-08-30' },
  { id: 8, name: '장미경', department: '인사팀', salary: 5000, joinDate: '2020-06-18' },
];

const employeeColumns: ColumnDef<Employee>[] = [
  { id: 'name', header: '이름', accessorKey: 'name', sortable: true },
  { id: 'department', header: '부서', accessorKey: 'department', sortable: true },
  {
    id: 'salary',
    header: '연봉 (만원)',
    accessorKey: 'salary',
    sortable: true,
    cell: (value) => `${(value as number).toLocaleString()}만원`,
  },
  { id: 'joinDate', header: '입사일', accessorKey: 'joinDate', sortable: true },
];

export function TableDemo() {
  const {
    rows,
    totalRows,
    currentPage,
    totalPages,
    sortState,
    searchQuery,
    selectedRows,
    setCurrentPage,
    setSearchQuery,
    toggleRowSelection,
    toggleAllSelection,
    isAllSelected,
    getTableProps,
    getHeaderProps,
    getRowProps,
    getCellProps,
  } = useTable({
    data: sampleEmployees,
    columns: employeeColumns,
    pageSize: 5,
  });

  const getSortIndicator = (columnId: string) => {
    if (sortState?.columnId !== columnId) return ' ↕';
    return sortState.direction === 'asc' ? ' ↑' : ' ↓';
  };

  return (
    <div>
      <h2>Headless Table (useTable)</h2>

      {/* 검색 */}
      <div style={{ marginBottom: '16px' }}>
        <label htmlFor="table-search">검색: </label>
        <input
          id="table-search"
          type="search"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="이름, 부서 등으로 검색"
          style={{ padding: '6px 12px', width: '250px' }}
        />
        <span style={{ marginLeft: '16px' }}>
          총 {totalRows}건 | 선택: {selectedRows.size}건
        </span>
      </div>

      {/* 테이블 */}
      <table
        {...getTableProps()}
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          border: '1px solid #ddd',
        }}
      >
        <thead>
          <tr>
            <th style={{ padding: '8px', borderBottom: '2px solid #ddd' }}>
              <input
                type="checkbox"
                checked={isAllSelected}
                onChange={toggleAllSelection}
                aria-label="전체 선택"
              />
            </th>
            {employeeColumns.map((column) => {
              const headerProps = getHeaderProps(column);
              return (
                <th
                  key={column.id}
                  {...headerProps}
                  style={{
                    ...headerProps.style,
                    padding: '8px',
                    borderBottom: '2px solid #ddd',
                    textAlign: 'left',
                    userSelect: 'none',
                  }}
                >
                  {column.header}
                  {column.sortable && getSortIndicator(column.id)}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => {
            const rowProps = getRowProps(row, index);
            const globalIndex = (currentPage - 1) * 5 + index;
            return (
              <tr
                key={row.id}
                {...rowProps}
                style={{
                  background: rowProps['aria-selected'] ? '#e3f2fd' : 'transparent',
                }}
              >
                <td style={{ padding: '8px', borderBottom: '1px solid #eee' }}>
                  <input
                    type="checkbox"
                    checked={selectedRows.has(globalIndex)}
                    onChange={() => toggleRowSelection(globalIndex)}
                    aria-label={`${row.name} 선택`}
                  />
                </td>
                {employeeColumns.map((column) => {
                  const cellProps = getCellProps(column, row);
                  return (
                    <td
                      key={column.id}
                      {...cellProps}
                      style={{ padding: '8px', borderBottom: '1px solid #eee' }}
                    >
                      {cellProps.children}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* 페이지네이션 */}
      <div style={{ marginTop: '16px', display: 'flex', gap: '8px', alignItems: 'center' }}>
        <button
          onClick={() => setCurrentPage(currentPage - 1)}
          disabled={currentPage <= 1}
        >
          이전
        </button>
        <span>
          {currentPage} / {totalPages} 페이지
        </span>
        <button
          onClick={() => setCurrentPage(currentPage + 1)}
          disabled={currentPage >= totalPages}
        >
          다음
        </button>
      </div>
    </div>
  );
}

// ============================================================
// 문제 3 답안: Feature-Sliced Design 프로젝트 구조
// ============================================================

/**
 * FSD 프로젝트 구조 설계 및 핵심 코드
 *
 * 디렉토리 구조:
 *
 * src/
 * ├── app/                          # 레이어 1: 앱
 * │   ├── providers/
 * │   │   ├── AuthProvider.tsx
 * │   │   ├── ThemeProvider.tsx
 * │   │   └── index.ts
 * │   ├── router/
 * │   │   └── AppRouter.tsx
 * │   ├── App.tsx
 * │   └── index.ts
 * │
 * ├── pages/                        # 레이어 2: 페이지
 * │   ├── home/
 * │   │   ├── ui/
 * │   │   │   └── HomePage.tsx
 * │   │   └── index.ts              # 공개 API
 * │   ├── profile/
 * │   │   ├── ui/
 * │   │   │   └── ProfilePage.tsx
 * │   │   └── index.ts
 * │   └── settings/
 * │       ├── ui/
 * │       │   └── SettingsPage.tsx
 * │       └── index.ts
 * │
 * ├── widgets/                      # 레이어 3: 위젯
 * │   ├── header/
 * │   │   ├── ui/
 * │   │   │   ├── Header.tsx
 * │   │   │   └── NavigationMenu.tsx
 * │   │   └── index.ts
 * │   └── post-feed/
 * │       ├── ui/
 * │       │   ├── PostFeed.tsx
 * │       │   └── PostFeedSkeleton.tsx
 * │       ├── model/
 * │       │   └── useFeedFilters.ts
 * │       └── index.ts
 * │
 * ├── features/                     # 레이어 4: 기능
 * │   ├── auth/
 * │   │   ├── ui/
 * │   │   │   ├── LoginForm.tsx
 * │   │   │   └── SignupForm.tsx
 * │   │   ├── model/
 * │   │   │   ├── useAuth.ts
 * │   │   │   └── types.ts
 * │   │   ├── api/
 * │   │   │   └── authApi.ts
 * │   │   └── index.ts
 * │   ├── create-post/
 * │   │   ├── ui/
 * │   │   │   └── CreatePostForm.tsx
 * │   │   ├── model/
 * │   │   │   └── useCreatePost.ts
 * │   │   ├── api/
 * │   │   │   └── postApi.ts
 * │   │   └── index.ts
 * │   ├── like-post/
 * │   │   ├── ui/
 * │   │   │   └── LikeButton.tsx
 * │   │   ├── model/
 * │   │   │   └── useLike.ts
 * │   │   └── index.ts
 * │   └── search/
 * │       ├── ui/
 * │       │   ├── SearchBar.tsx
 * │       │   └── SearchResults.tsx
 * │       ├── model/
 * │       │   └── useSearch.ts
 * │       └── index.ts
 * │
 * ├── entities/                     # 레이어 5: 엔티티
 * │   ├── user/
 * │   │   ├── ui/
 * │   │   │   ├── UserAvatar.tsx
 * │   │   │   └── UserCard.tsx
 * │   │   ├── model/
 * │   │   │   ├── types.ts
 * │   │   │   └── useUser.ts
 * │   │   ├── api/
 * │   │   │   └── userApi.ts
 * │   │   └── index.ts              # 공개 API
 * │   ├── post/
 * │   │   ├── ui/
 * │   │   │   ├── PostCard.tsx
 * │   │   │   └── PostContent.tsx
 * │   │   ├── model/
 * │   │   │   └── types.ts
 * │   │   └── index.ts
 * │   └── notification/
 * │       ├── ui/
 * │       │   └── NotificationItem.tsx
 * │       ├── model/
 * │       │   └── types.ts
 * │       └── index.ts
 * │
 * └── shared/                       # 레이어 6: 공유
 *     ├── ui/
 *     │   ├── Button.tsx
 *     │   ├── Input.tsx
 *     │   ├── Modal.tsx
 *     │   └── index.ts
 *     ├── api/
 *     │   ├── client.ts             # API 클라이언트 (axios/fetch)
 *     │   └── index.ts
 *     ├── lib/
 *     │   ├── formatDate.ts
 *     │   ├── debounce.ts
 *     │   └── index.ts
 *     ├── config/
 *     │   └── env.ts
 *     └── types/
 *         └── common.ts
 */

// --- entities/user/model/types.ts ---

export interface UserEntity {
  id: string;
  username: string;
  displayName: string;
  avatar: string;
  bio: string;
  followersCount: number;
  followingCount: number;
}

// --- entities/user/index.ts (공개 API) ---
// export { UserAvatar } from './ui/UserAvatar';
// export { UserCard } from './ui/UserCard';
// export { useUser } from './model/useUser';
// export type { UserEntity } from './model/types';

// --- entities/post/model/types.ts ---

export interface PostEntity {
  id: string;
  author: UserEntity;
  content: string;
  images: string[];
  likesCount: number;
  commentsCount: number;
  isLiked: boolean;
  createdAt: string;
}

// --- features/auth/model/useAuth.ts ---

interface AuthState {
  user: UserEntity | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  signup: (data: { email: string; password: string; username: string }) => Promise<void>;
}

// 실제 구현에서는 zustand 또는 context를 사용
// export function useAuth(): AuthState { ... }

// --- features/create-post/index.ts (공개 API) ---
// export { CreatePostForm } from './ui/CreatePostForm';
// export { useCreatePost } from './model/useCreatePost';

// --- widgets/post-feed/ui/PostFeed.tsx ---

/**
 * PostFeed 위젯
 *
 * features/와 entities/를 조합하여 하나의 독립적인 UI 블록을 만듭니다.
 * - entities/post - PostCard 사용
 * - features/like-post - LikeButton 사용
 * - features/create-post - CreatePostForm 사용
 */
interface PostFeedProps {
  posts: PostEntity[];
  isLoading: boolean;
}

export function PostFeed({ posts, isLoading }: PostFeedProps) {
  if (isLoading) {
    return <PostFeedSkeleton />;
  }

  return (
    <section aria-label="게시글 피드">
      {posts.map((post) => (
        <article key={post.id}>
          {/* entities/user - UserAvatar */}
          <div>
            <img src={post.author.avatar} alt={post.author.displayName} />
            <strong>{post.author.displayName}</strong>
          </div>

          {/* entities/post - PostContent */}
          <p>{post.content}</p>

          {/* features/like-post - LikeButton */}
          <button aria-pressed={post.isLiked}>
            {post.isLiked ? '❤️' : '🤍'} {post.likesCount}
          </button>
        </article>
      ))}
    </section>
  );
}

function PostFeedSkeleton() {
  return (
    <div role="status" aria-label="게시글 로딩 중">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="skeleton-post" />
      ))}
    </div>
  );
}

// --- pages/home/ui/HomePage.tsx ---

/**
 * HomePage
 *
 * widgets/와 features/를 조합하여 페이지를 구성합니다.
 * - widgets/header
 * - widgets/post-feed
 * - features/create-post
 * - features/search
 */
export function HomePage() {
  // 실제 구현에서는 데이터 페칭 훅 사용
  const posts: PostEntity[] = [];
  const isLoading = false;

  return (
    <main>
      {/* widgets/header */}
      <header>
        <h1>홈</h1>
        {/* features/search - SearchBar */}
        <input type="search" placeholder="검색..." />
      </header>

      {/* features/create-post - CreatePostForm */}
      <section aria-label="새 게시글 작성">
        <textarea placeholder="무슨 생각을 하고 계신가요?" />
        <button>게시</button>
      </section>

      {/* widgets/post-feed */}
      <PostFeed posts={posts} isLoading={isLoading} />
    </main>
  );
}

/**
 * FSD 핵심 규칙 정리:
 *
 * 1. 단방향 의존성:
 *    pages → widgets → features → entities → shared
 *    (상위만 하위를 참조)
 *
 * 2. 슬라이스 격리:
 *    - features/auth/ → entities/user/ (O) 하위 레이어 참조 가능
 *    - features/auth/ → features/search/ (X) 같은 레이어 참조 불가
 *    - entities/user/ → features/auth/ (X) 상위 레이어 참조 불가
 *
 * 3. 공개 API (index.ts):
 *    - 각 슬라이스는 index.ts를 통해서만 외부에 노출
 *    - 내부 구현(model/, api/ 등)은 직접 import 불가
 *    - import { UserCard } from '@/entities/user';      (O)
 *    - import { UserCard } from '@/entities/user/ui/...; (X)
 */

export default { ModalDemo, TableDemo, HomePage };
