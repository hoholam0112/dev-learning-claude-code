/**
 * 챕터 10 - 예제 01: 완성형 할 일 관리 앱
 *
 * 통합 개념:
 * - Context + useReducer: 전역 상태 관리 (할 일 CRUD)
 * - React Router: 페이지 라우팅 (홈, 추가, 수정, 통계)
 * - 제어 컴포넌트: 폼 입력 처리
 * - useEffect: 로컬 스토리지 동기화
 * - 컴포넌트 분리: 재사용 가능한 구조
 *
 * 실행 방법:
 *   npx create-react-app todo-app
 *   cd todo-app
 *   npm install react-router-dom
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useState,
  useEffect,
  useRef,
} from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  NavLink,
  Outlet,
  useParams,
  useNavigate,
} from 'react-router-dom';

// ══════════════════════════════════════════════
// 1. Todo Context + Reducer (전역 상태 관리)
// ══════════════════════════════════════════════

const TodoContext = createContext();

const CATEGORIES = ['학습', '업무', '생활', '기타'];
const PRIORITIES = [
  { value: 'high', label: '높음', color: '#f44336' },
  { value: 'medium', label: '보통', color: '#ff9800' },
  { value: 'low', label: '낮음', color: '#4caf50' },
];

function todoReducer(state, action) {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [
          ...state.todos,
          {
            id: Date.now(),
            text: action.payload.text,
            category: action.payload.category || '기타',
            priority: action.payload.priority || 'medium',
            completed: false,
            createdAt: new Date().toISOString(),
          },
        ],
      };

    case 'DELETE_TODO':
      return {
        ...state,
        todos: state.todos.filter((todo) => todo.id !== action.payload),
      };

    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };

    case 'EDIT_TODO':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.payload.id
            ? { ...todo, ...action.payload.updates }
            : todo
        ),
      };

    case 'SET_FILTER':
      return { ...state, filter: action.payload };

    case 'CLEAR_COMPLETED':
      return {
        ...state,
        todos: state.todos.filter((todo) => !todo.completed),
      };

    default:
      return state;
  }
}

function TodoProvider({ children }) {
  // 로컬 스토리지에서 초기값 복원
  const [state, dispatch] = useReducer(todoReducer, {
    todos: JSON.parse(localStorage.getItem('todos') || '[]'),
    filter: 'all',
  });

  // todos 변경 시 로컬 스토리지에 저장
  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(state.todos));
  }, [state.todos]);

  // 필터링된 할 일 목록
  const filteredTodos = state.todos.filter((todo) => {
    if (state.filter === 'active') return !todo.completed;
    if (state.filter === 'completed') return todo.completed;
    return true; // 'all'
  });

  // 통계 데이터
  const stats = {
    total: state.todos.length,
    completed: state.todos.filter((t) => t.completed).length,
    active: state.todos.filter((t) => !t.completed).length,
    byCategory: CATEGORIES.reduce((acc, cat) => {
      acc[cat] = state.todos.filter((t) => t.category === cat).length;
      return acc;
    }, {}),
    byPriority: PRIORITIES.reduce((acc, p) => {
      acc[p.value] = state.todos.filter((t) => t.priority === p.value).length;
      return acc;
    }, {}),
  };

  return (
    <TodoContext.Provider
      value={{ state, dispatch, filteredTodos, stats, CATEGORIES, PRIORITIES }}
    >
      {children}
    </TodoContext.Provider>
  );
}

function useTodo() {
  const context = useContext(TodoContext);
  if (!context) throw new Error('useTodo는 TodoProvider 안에서 사용하세요');
  return context;
}

// ══════════════════════════════════════════════
// 2. 레이아웃 컴포넌트
// ══════════════════════════════════════════════

function Layout() {
  const { stats } = useTodo();

  const navStyle = ({ isActive }) => ({
    textDecoration: 'none',
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: isActive ? 'bold' : 'normal',
    backgroundColor: isActive ? '#1976d2' : 'transparent',
    color: isActive ? 'white' : '#555',
    transition: 'all 0.2s',
  });

  return (
    <div style={styles.layout}>
      <header style={styles.header}>
        <Link to="/" style={styles.logo}>
          Todo App
        </Link>
        <nav style={styles.nav}>
          <NavLink to="/" end style={navStyle}>
            할 일 ({stats.active})
          </NavLink>
          <NavLink to="/add" style={navStyle}>
            추가
          </NavLink>
          <NavLink to="/stats" style={navStyle}>
            통계
          </NavLink>
        </nav>
      </header>
      <main style={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}

// ══════════════════════════════════════════════
// 3. 홈 페이지: 할 일 목록
// ══════════════════════════════════════════════

function HomePage() {
  const { state, dispatch, filteredTodos, stats } = useTodo();

  return (
    <div>
      <h1>할 일 목록</h1>

      {/* 필터 바 */}
      <FilterBar
        currentFilter={state.filter}
        onFilterChange={(filter) =>
          dispatch({ type: 'SET_FILTER', payload: filter })
        }
        stats={stats}
      />

      {/* 할 일 목록 */}
      {filteredTodos.length === 0 ? (
        <div style={styles.emptyState}>
          <p>
            {state.filter === 'all'
              ? '할 일이 없습니다. 새로운 할 일을 추가해보세요!'
              : `${state.filter === 'active' ? '진행 중인' : '완료된'} 할 일이 없습니다.`}
          </p>
          <Link to="/add" style={styles.addLink}>
            + 할 일 추가하기
          </Link>
        </div>
      ) : (
        <div style={styles.todoList}>
          {filteredTodos.map((todo) => (
            <TodoItem key={todo.id} todo={todo} />
          ))}
        </div>
      )}

      {/* 완료된 항목 일괄 삭제 */}
      {stats.completed > 0 && (
        <button
          onClick={() => dispatch({ type: 'CLEAR_COMPLETED' })}
          style={styles.clearButton}
        >
          완료된 항목 삭제 ({stats.completed}개)
        </button>
      )}
    </div>
  );
}

// 필터 바 컴포넌트
function FilterBar({ currentFilter, onFilterChange, stats }) {
  const filters = [
    { value: 'all', label: `전체 (${stats.total})` },
    { value: 'active', label: `진행중 (${stats.active})` },
    { value: 'completed', label: `완료 (${stats.completed})` },
  ];

  return (
    <div style={styles.filterBar}>
      {filters.map((f) => (
        <button
          key={f.value}
          onClick={() => onFilterChange(f.value)}
          style={{
            ...styles.filterButton,
            backgroundColor: currentFilter === f.value ? '#1976d2' : '#f5f5f5',
            color: currentFilter === f.value ? 'white' : '#333',
          }}
        >
          {f.label}
        </button>
      ))}
    </div>
  );
}

// 개별 할 일 항목 컴포넌트
function TodoItem({ todo }) {
  const { dispatch, PRIORITIES } = useTodo();
  const navigate = useNavigate();
  const priorityInfo = PRIORITIES.find((p) => p.value === todo.priority);

  return (
    <div
      style={{
        ...styles.todoItem,
        opacity: todo.completed ? 0.6 : 1,
      }}
    >
      {/* 완료 체크박스 */}
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })}
        style={styles.checkbox}
      />

      {/* 할 일 정보 */}
      <div style={styles.todoInfo}>
        <p
          style={{
            ...styles.todoText,
            textDecoration: todo.completed ? 'line-through' : 'none',
          }}
        >
          {todo.text}
        </p>
        <div style={styles.todoMeta}>
          <span style={styles.categoryBadge}>{todo.category}</span>
          <span
            style={{
              ...styles.priorityDot,
              backgroundColor: priorityInfo?.color || '#999',
            }}
          />
          <span style={{ fontSize: '11px', color: '#999' }}>
            {priorityInfo?.label}
          </span>
        </div>
      </div>

      {/* 액션 버튼 */}
      <div style={styles.todoActions}>
        <button
          onClick={() => navigate(`/edit/${todo.id}`)}
          style={styles.editButton}
        >
          수정
        </button>
        <button
          onClick={() => {
            if (window.confirm('정말 삭제하시겠습니까?')) {
              dispatch({ type: 'DELETE_TODO', payload: todo.id });
            }
          }}
          style={styles.deleteButton}
        >
          삭제
        </button>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════
// 4. 추가/수정 페이지: TodoForm
// ══════════════════════════════════════════════

function AddPage() {
  return (
    <div>
      <h1>할 일 추가</h1>
      <TodoForm mode="add" />
    </div>
  );
}

function EditPage() {
  const { id } = useParams();
  const { state } = useTodo();
  const navigate = useNavigate();
  const todo = state.todos.find((t) => t.id === Number(id));

  if (!todo) {
    return (
      <div style={styles.emptyState}>
        <h2>할 일을 찾을 수 없습니다</h2>
        <button onClick={() => navigate('/')} style={styles.primaryButton}>
          목록으로 돌아가기
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1>할 일 수정</h1>
      <TodoForm mode="edit" todo={todo} />
    </div>
  );
}

function TodoForm({ mode, todo }) {
  const { dispatch, CATEGORIES, PRIORITIES } = useTodo();
  const navigate = useNavigate();
  const inputRef = useRef(null);

  const [formData, setFormData] = useState({
    text: todo?.text || '',
    category: todo?.category || '기타',
    priority: todo?.priority || 'medium',
  });

  const [error, setError] = useState('');

  // 폼 마운트 시 입력란에 포커스
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.text.trim()) {
      setError('할 일 내용을 입력해주세요');
      inputRef.current?.focus();
      return;
    }

    if (mode === 'add') {
      dispatch({ type: 'ADD_TODO', payload: formData });
    } else {
      dispatch({
        type: 'EDIT_TODO',
        payload: { id: todo.id, updates: formData },
      });
    }

    navigate('/');
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      {/* 할 일 내용 */}
      <div style={styles.formGroup}>
        <label style={styles.label}>할 일</label>
        <input
          ref={inputRef}
          type="text"
          name="text"
          value={formData.text}
          onChange={handleChange}
          placeholder="할 일을 입력하세요"
          style={{
            ...styles.input,
            borderColor: error ? '#f44336' : '#ddd',
          }}
        />
        {error && <span style={styles.errorText}>{error}</span>}
      </div>

      {/* 카테고리 */}
      <div style={styles.formGroup}>
        <label style={styles.label}>카테고리</label>
        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
          style={styles.select}
        >
          {CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* 우선순위 */}
      <div style={styles.formGroup}>
        <label style={styles.label}>우선순위</label>
        <div style={styles.radioGroup}>
          {PRIORITIES.map((p) => (
            <label key={p.value} style={styles.radioLabel}>
              <input
                type="radio"
                name="priority"
                value={p.value}
                checked={formData.priority === p.value}
                onChange={handleChange}
              />
              <span style={{ color: p.color, fontWeight: 'bold' }}>
                {p.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* 버튼 */}
      <div style={styles.formActions}>
        <button type="submit" style={styles.primaryButton}>
          {mode === 'add' ? '추가하기' : '수정하기'}
        </button>
        <button
          type="button"
          onClick={() => navigate(-1)}
          style={styles.cancelButton}
        >
          취소
        </button>
      </div>
    </form>
  );
}

// ══════════════════════════════════════════════
// 5. 통계 페이지
// ══════════════════════════════════════════════

function StatsPage() {
  const { stats, CATEGORIES, PRIORITIES } = useTodo();

  const completionRate =
    stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;

  return (
    <div>
      <h1>통계</h1>

      {stats.total === 0 ? (
        <div style={styles.emptyState}>
          <p>아직 할 일이 없습니다. 할 일을 추가하면 통계를 확인할 수 있습니다.</p>
          <Link to="/add" style={styles.addLink}>
            + 할 일 추가하기
          </Link>
        </div>
      ) : (
        <>
          {/* 전체 요약 */}
          <div style={styles.statsGrid}>
            <div style={{ ...styles.statCard, borderColor: '#1976d2' }}>
              <p style={styles.statNumber}>{stats.total}</p>
              <p style={styles.statLabel}>전체</p>
            </div>
            <div style={{ ...styles.statCard, borderColor: '#ff9800' }}>
              <p style={styles.statNumber}>{stats.active}</p>
              <p style={styles.statLabel}>진행중</p>
            </div>
            <div style={{ ...styles.statCard, borderColor: '#4caf50' }}>
              <p style={styles.statNumber}>{stats.completed}</p>
              <p style={styles.statLabel}>완료</p>
            </div>
            <div style={{ ...styles.statCard, borderColor: '#9c27b0' }}>
              <p style={styles.statNumber}>{completionRate}%</p>
              <p style={styles.statLabel}>완료율</p>
            </div>
          </div>

          {/* 완료율 프로그레스 바 */}
          <div style={styles.progressSection}>
            <h3>진행 상황</h3>
            <div style={styles.progressBar}>
              <div
                style={{
                  ...styles.progressFill,
                  width: `${completionRate}%`,
                  backgroundColor:
                    completionRate >= 80
                      ? '#4caf50'
                      : completionRate >= 50
                      ? '#ff9800'
                      : '#f44336',
                }}
              />
            </div>
            <p style={{ fontSize: '13px', color: '#666' }}>
              {stats.completed}/{stats.total} 완료
            </p>
          </div>

          {/* 카테고리별 */}
          <div style={styles.statSection}>
            <h3>카테고리별</h3>
            {CATEGORIES.map((cat) => (
              <div key={cat} style={styles.statRow}>
                <span>{cat}</span>
                <div style={styles.miniBar}>
                  <div
                    style={{
                      ...styles.miniBarFill,
                      width: `${stats.total > 0 ? (stats.byCategory[cat] / stats.total) * 100 : 0}%`,
                    }}
                  />
                </div>
                <span style={styles.statCount}>{stats.byCategory[cat]}개</span>
              </div>
            ))}
          </div>

          {/* 우선순위별 */}
          <div style={styles.statSection}>
            <h3>우선순위별</h3>
            {PRIORITIES.map((p) => (
              <div key={p.value} style={styles.statRow}>
                <span style={{ color: p.color, fontWeight: 'bold' }}>
                  {p.label}
                </span>
                <div style={styles.miniBar}>
                  <div
                    style={{
                      ...styles.miniBarFill,
                      width: `${stats.total > 0 ? (stats.byPriority[p.value] / stats.total) * 100 : 0}%`,
                      backgroundColor: p.color,
                    }}
                  />
                </div>
                <span style={styles.statCount}>
                  {stats.byPriority[p.value]}개
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// 6. App: 라우팅 설정
// ══════════════════════════════════════════════

function App() {
  return (
    <BrowserRouter>
      <TodoProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="add" element={<AddPage />} />
            <Route path="edit/:id" element={<EditPage />} />
            <Route path="stats" element={<StatsPage />} />
            <Route
              path="*"
              element={
                <div style={styles.emptyState}>
                  <h1>404</h1>
                  <p>페이지를 찾을 수 없습니다.</p>
                  <Link to="/" style={styles.addLink}>
                    홈으로 돌아가기
                  </Link>
                </div>
              }
            />
          </Route>
        </Routes>
      </TodoProvider>
    </BrowserRouter>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  layout: {
    maxWidth: '650px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif',
    minHeight: '100vh',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 20px',
    borderBottom: '1px solid #e0e0e0',
  },
  logo: {
    fontSize: '22px',
    fontWeight: 'bold',
    color: '#1976d2',
    textDecoration: 'none',
  },
  nav: { display: 'flex', gap: '8px' },
  main: { padding: '24px 20px' },
  filterBar: { display: 'flex', gap: '8px', marginBottom: '20px' },
  filterButton: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    borderRadius: '20px',
    cursor: 'pointer',
    fontSize: '13px',
    transition: 'all 0.2s',
  },
  todoList: { display: 'flex', flexDirection: 'column', gap: '8px' },
  todoItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '14px 16px',
    border: '1px solid #e0e0e0',
    borderRadius: '10px',
    backgroundColor: '#fff',
    transition: 'opacity 0.2s',
  },
  checkbox: { width: '20px', height: '20px', cursor: 'pointer' },
  todoInfo: { flex: 1 },
  todoText: { margin: '0 0 4px 0', fontSize: '15px' },
  todoMeta: { display: 'flex', alignItems: 'center', gap: '8px' },
  categoryBadge: {
    padding: '1px 8px',
    backgroundColor: '#e3f2fd',
    color: '#1976d2',
    borderRadius: '10px',
    fontSize: '11px',
  },
  priorityDot: { width: '8px', height: '8px', borderRadius: '50%' },
  todoActions: { display: 'flex', gap: '6px' },
  editButton: {
    padding: '6px 12px',
    backgroundColor: 'transparent',
    color: '#1976d2',
    border: '1px solid #1976d2',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  deleteButton: {
    padding: '6px 12px',
    backgroundColor: 'transparent',
    color: '#f44336',
    border: '1px solid #f44336',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  clearButton: {
    marginTop: '16px',
    padding: '10px 20px',
    backgroundColor: '#757575',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  emptyState: { textAlign: 'center', padding: '40px 20px', color: '#888' },
  addLink: {
    color: '#1976d2',
    textDecoration: 'none',
    fontWeight: 'bold',
    fontSize: '15px',
  },
  form: { display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '500px' },
  formGroup: { display: 'flex', flexDirection: 'column', gap: '6px' },
  label: { fontWeight: 'bold', fontSize: '14px' },
  input: {
    padding: '12px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '15px',
    outline: 'none',
  },
  select: {
    padding: '12px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '15px',
  },
  radioGroup: { display: 'flex', gap: '20px', marginTop: '4px' },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  errorText: { color: '#f44336', fontSize: '12px' },
  formActions: { display: 'flex', gap: '10px', marginTop: '8px' },
  primaryButton: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  cancelButton: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#757575',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '12px',
    marginBottom: '24px',
  },
  statCard: {
    padding: '16px',
    borderRadius: '10px',
    backgroundColor: '#fafafa',
    borderLeft: '4px solid',
    textAlign: 'center',
  },
  statNumber: { fontSize: '28px', fontWeight: 'bold', margin: '0 0 4px 0' },
  statLabel: { fontSize: '13px', color: '#888', margin: 0 },
  progressSection: { marginBottom: '24px' },
  progressBar: {
    height: '12px',
    backgroundColor: '#e0e0e0',
    borderRadius: '6px',
    overflow: 'hidden',
    marginBottom: '8px',
  },
  progressFill: {
    height: '100%',
    borderRadius: '6px',
    transition: 'width 0.5s ease',
  },
  statSection: {
    marginBottom: '24px',
    padding: '16px',
    backgroundColor: '#fafafa',
    borderRadius: '10px',
  },
  statRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '8px 0',
  },
  miniBar: {
    flex: 1,
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  miniBarFill: {
    height: '100%',
    backgroundColor: '#1976d2',
    borderRadius: '4px',
    transition: 'width 0.3s',
  },
  statCount: { minWidth: '30px', textAlign: 'right', fontSize: '13px', color: '#666' },
};

export default App;
