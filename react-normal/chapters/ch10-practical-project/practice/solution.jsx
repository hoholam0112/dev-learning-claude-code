/**
 * 챕터 10 - 연습 문제 모범 답안 (문제 1~5 통합)
 *
 * 이 파일은 example-01.jsx를 확장하여 5개 문제의 답안을 모두 포함합니다:
 * - 문제 1: 텍스트 검색 기능
 * - 문제 2: 정렬 기능
 * - 문제 3: 마감일(Due Date) 기능
 * - 문제 4: 다크 모드
 * - 문제 5: 서브태스크와 진행률
 *
 * 실행 방법:
 *   npx create-react-app ch10-solutions
 *   cd ch10-solutions
 *   npm install react-router-dom
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
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
// 문제 4: Theme Context (다크 모드)
// ══════════════════════════════════════════════

const ThemeContext = createContext();

function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches || false;
  });

  useEffect(() => {
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = () => setIsDark((prev) => !prev);

  const colors = isDark
    ? { bg: '#121212', surface: '#1e1e1e', text: '#e0e0e0', textSecondary: '#aaa', border: '#333', accent: '#64b5f6', danger: '#ef5350', success: '#66bb6a', warning: '#ffa726' }
    : { bg: '#f5f5f5', surface: '#ffffff', text: '#333333', textSecondary: '#666', border: '#e0e0e0', accent: '#1976d2', danger: '#f44336', success: '#4caf50', warning: '#ff9800' };

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme은 ThemeProvider 안에서 사용하세요');
  return ctx;
}

// ══════════════════════════════════════════════
// Todo Context + Reducer (문제 3, 5 확장 포함)
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
        todos: [...state.todos, {
          id: Date.now(),
          text: action.payload.text,
          category: action.payload.category || '기타',
          priority: action.payload.priority || 'medium',
          dueDate: action.payload.dueDate || null,
          completed: false,
          subtasks: [],
          createdAt: new Date().toISOString(),
        }],
      };
    case 'DELETE_TODO':
      return { ...state, todos: state.todos.filter((t) => t.id !== action.payload) };
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map((t) =>
          t.id === action.payload ? { ...t, completed: !t.completed } : t
        ),
      };
    case 'EDIT_TODO':
      return {
        ...state,
        todos: state.todos.map((t) =>
          t.id === action.payload.id ? { ...t, ...action.payload.updates } : t
        ),
      };
    case 'SET_FILTER':
      return { ...state, filter: action.payload };
    case 'CLEAR_COMPLETED':
      return { ...state, todos: state.todos.filter((t) => !t.completed) };

    // 문제 5: 서브태스크 액션
    case 'ADD_SUBTASK':
      return {
        ...state,
        todos: state.todos.map((t) =>
          t.id === action.payload.todoId
            ? { ...t, subtasks: [...(t.subtasks || []), { id: Date.now(), text: action.payload.text, completed: false }] }
            : t
        ),
      };
    case 'DELETE_SUBTASK':
      return {
        ...state,
        todos: state.todos.map((t) =>
          t.id === action.payload.todoId
            ? { ...t, subtasks: (t.subtasks || []).filter((s) => s.id !== action.payload.subtaskId) }
            : t
        ),
      };
    case 'TOGGLE_SUBTASK':
      return {
        ...state,
        todos: state.todos.map((t) =>
          t.id === action.payload.todoId
            ? {
                ...t,
                subtasks: (t.subtasks || []).map((s) =>
                  s.id === action.payload.subtaskId ? { ...s, completed: !s.completed } : s
                ),
              }
            : t
        ),
      };
    default:
      return state;
  }
}

function TodoProvider({ children }) {
  const [state, dispatch] = useReducer(todoReducer, {
    todos: JSON.parse(localStorage.getItem('todos-v2') || '[]'),
    filter: 'all',
  });

  useEffect(() => {
    localStorage.setItem('todos-v2', JSON.stringify(state.todos));
  }, [state.todos]);

  const filteredTodos = state.todos.filter((todo) => {
    if (state.filter === 'active') return !todo.completed;
    if (state.filter === 'completed') return todo.completed;
    return true;
  });

  // 문제 3: 기한 관련 통계
  const today = new Date().setHours(0, 0, 0, 0);
  const overdueTodos = state.todos.filter(
    (t) => t.dueDate && !t.completed && new Date(t.dueDate).setHours(0, 0, 0, 0) < today
  );

  // 전체 서브태스크 통계
  const allSubtasks = state.todos.flatMap((t) => t.subtasks || []);
  const completedSubtasks = allSubtasks.filter((s) => s.completed);

  const stats = {
    total: state.todos.length,
    completed: state.todos.filter((t) => t.completed).length,
    active: state.todos.filter((t) => !t.completed).length,
    overdue: overdueTodos.length,
    totalSubtasks: allSubtasks.length,
    completedSubtasks: completedSubtasks.length,
    byCategory: CATEGORIES.reduce((acc, c) => { acc[c] = state.todos.filter((t) => t.category === c).length; return acc; }, {}),
    byPriority: PRIORITIES.reduce((acc, p) => { acc[p.value] = state.todos.filter((t) => t.priority === p.value).length; return acc; }, {}),
  };

  return (
    <TodoContext.Provider value={{ state, dispatch, filteredTodos, stats, CATEGORIES, PRIORITIES }}>
      {children}
    </TodoContext.Provider>
  );
}

function useTodo() {
  const ctx = useContext(TodoContext);
  if (!ctx) throw new Error('useTodo는 TodoProvider 안에서 사용하세요');
  return ctx;
}

// ══════════════════════════════════════════════
// D-Day 유틸리티 (문제 3)
// ══════════════════════════════════════════════

function getDDay(dueDateStr) {
  if (!dueDateStr) return null;
  const today = new Date().setHours(0, 0, 0, 0);
  const due = new Date(dueDateStr).setHours(0, 0, 0, 0);
  const diff = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
  if (diff > 0) return { text: `D-${diff}`, status: 'future' };
  if (diff === 0) return { text: 'D-Day', status: 'today' };
  return { text: `D+${Math.abs(diff)}`, status: 'overdue' };
}

// ══════════════════════════════════════════════
// Layout
// ══════════════════════════════════════════════

function Layout() {
  const { stats } = useTodo();
  const { isDark, toggleTheme, colors } = useTheme();

  const navStyle = ({ isActive }) => ({
    textDecoration: 'none',
    padding: '6px 14px',
    borderRadius: '16px',
    fontSize: '13px',
    fontWeight: isActive ? 'bold' : 'normal',
    backgroundColor: isActive ? colors.accent : 'transparent',
    color: isActive ? '#fff' : colors.textSecondary,
  });

  return (
    <div style={{ maxWidth: '650px', margin: '0 auto', fontFamily: 'Arial, sans-serif', minHeight: '100vh', backgroundColor: colors.bg, color: colors.text, transition: 'all 0.3s' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 20px', borderBottom: `1px solid ${colors.border}` }}>
        <Link to="/" style={{ fontSize: '20px', fontWeight: 'bold', color: colors.accent, textDecoration: 'none' }}>
          Todo App
        </Link>
        <nav style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          <NavLink to="/" end style={navStyle}>할 일 ({stats.active})</NavLink>
          <NavLink to="/add" style={navStyle}>추가</NavLink>
          <NavLink to="/stats" style={navStyle}>통계</NavLink>
          <button onClick={toggleTheme} style={{ padding: '6px 12px', borderRadius: '16px', border: `1px solid ${colors.border}`, backgroundColor: colors.surface, color: colors.text, cursor: 'pointer', fontSize: '12px', marginLeft: '4px' }}>
            {isDark ? '라이트' : '다크'}
          </button>
        </nav>
      </header>
      <main style={{ padding: '20px' }}><Outlet /></main>
    </div>
  );
}

// ══════════════════════════════════════════════
// HomePage (문제 1: 검색, 문제 2: 정렬)
// ══════════════════════════════════════════════

function HomePage() {
  const { state, dispatch, filteredTodos, stats } = useTodo();
  const { colors } = useTheme();

  // 문제 1: 검색
  const [searchQuery, setSearchQuery] = useState('');
  // 문제 2: 정렬
  const [sortBy, setSortBy] = useState('newest');

  // 검색 적용
  let displayTodos = searchQuery
    ? filteredTodos.filter((t) => t.text.toLowerCase().includes(searchQuery.toLowerCase()))
    : filteredTodos;

  // 정렬 적용
  const priorityOrder = { high: 3, medium: 2, low: 1 };
  displayTodos = [...displayTodos].sort((a, b) => {
    switch (sortBy) {
      case 'newest': return new Date(b.createdAt) - new Date(a.createdAt);
      case 'oldest': return new Date(a.createdAt) - new Date(b.createdAt);
      case 'priority_high': return priorityOrder[b.priority] - priorityOrder[a.priority];
      case 'priority_low': return priorityOrder[a.priority] - priorityOrder[b.priority];
      case 'category': return a.category.localeCompare(b.category);
      case 'due_date': {
        if (!a.dueDate && !b.dueDate) return 0;
        if (!a.dueDate) return 1;
        if (!b.dueDate) return -1;
        return new Date(a.dueDate) - new Date(b.dueDate);
      }
      default: return 0;
    }
  });

  return (
    <div>
      <h1 style={{ margin: '0 0 16px' }}>할 일 목록</h1>

      {/* 문제 1: 검색 바 */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="할 일 검색..."
            style={{ width: '100%', padding: '10px 36px 10px 12px', border: `1px solid ${colors.border}`, borderRadius: '8px', fontSize: '14px', backgroundColor: colors.surface, color: colors.text, boxSizing: 'border-box' }}
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: colors.textSecondary, cursor: 'pointer', fontSize: '16px' }}>
              X
            </button>
          )}
        </div>
        {/* 문제 2: 정렬 */}
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} style={{ padding: '10px', border: `1px solid ${colors.border}`, borderRadius: '8px', fontSize: '13px', backgroundColor: colors.surface, color: colors.text }}>
          <option value="newest">최신순</option>
          <option value="oldest">오래된 순</option>
          <option value="priority_high">우선순위 높은순</option>
          <option value="priority_low">우선순위 낮은순</option>
          <option value="category">카테고리순</option>
          <option value="due_date">기한 임박순</option>
        </select>
      </div>

      {/* 필터 바 */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
        {[
          { value: 'all', label: `전체 (${stats.total})` },
          { value: 'active', label: `진행중 (${stats.active})` },
          { value: 'completed', label: `완료 (${stats.completed})` },
        ].map((f) => (
          <button
            key={f.value}
            onClick={() => dispatch({ type: 'SET_FILTER', payload: f.value })}
            style={{ padding: '6px 14px', border: `1px solid ${colors.border}`, borderRadius: '16px', cursor: 'pointer', fontSize: '12px', backgroundColor: state.filter === f.value ? colors.accent : colors.surface, color: state.filter === f.value ? '#fff' : colors.text }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {searchQuery && (
        <p style={{ fontSize: '13px', color: colors.textSecondary, marginBottom: '8px' }}>
          "{searchQuery}" 검색 결과: {displayTodos.length}개
        </p>
      )}

      {/* 할 일 목록 */}
      {displayTodos.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: colors.textSecondary }}>
          <p>{searchQuery ? `"${searchQuery}"에 대한 검색 결과가 없습니다` : '할 일이 없습니다'}</p>
          <Link to="/add" style={{ color: colors.accent, textDecoration: 'none', fontWeight: 'bold' }}>+ 할 일 추가하기</Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {displayTodos.map((todo) => (
            <TodoItem key={todo.id} todo={todo} searchQuery={searchQuery} />
          ))}
        </div>
      )}

      {stats.completed > 0 && (
        <button onClick={() => dispatch({ type: 'CLEAR_COMPLETED' })} style={{ marginTop: '16px', padding: '8px 16px', backgroundColor: colors.surface, color: colors.textSecondary, border: `1px solid ${colors.border}`, borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>
          완료된 항목 삭제 ({stats.completed}개)
        </button>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// TodoItem (문제 1: 하이라이트, 문제 3: D-Day, 문제 5: 서브태스크)
// ══════════════════════════════════════════════

function TodoItem({ todo, searchQuery = '' }) {
  const { dispatch, PRIORITIES } = useTodo();
  const { colors } = useTheme();
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(false);
  const [subtaskInput, setSubtaskInput] = useState('');

  const priorityInfo = PRIORITIES.find((p) => p.value === todo.priority);
  const dday = getDDay(todo.dueDate);
  const subtasks = todo.subtasks || [];
  const subtasksDone = subtasks.filter((s) => s.completed).length;
  const subtaskProgress = subtasks.length > 0 ? Math.round((subtasksDone / subtasks.length) * 100) : null;

  // 문제 3: 마감일에 따른 스타일
  let borderColor = colors.border;
  if (dday && !todo.completed) {
    if (dday.status === 'overdue') borderColor = colors.danger;
    else if (dday.status === 'today') borderColor = colors.warning;
  }

  // 문제 1: 검색어 하이라이트
  const highlightText = (text, query) => {
    if (!query) return text;
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase()
        ? <mark key={i} style={{ backgroundColor: '#fff3e0', padding: '0 2px', borderRadius: '2px' }}>{part}</mark>
        : part
    );
  };

  const handleAddSubtask = (e) => {
    e.preventDefault();
    if (subtaskInput.trim()) {
      dispatch({ type: 'ADD_SUBTASK', payload: { todoId: todo.id, text: subtaskInput.trim() } });
      setSubtaskInput('');
    }
  };

  return (
    <div style={{ border: `1px solid ${borderColor}`, borderRadius: '10px', backgroundColor: colors.surface, opacity: todo.completed ? 0.6 : 1, transition: 'all 0.2s' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 14px' }}>
        <input type="checkbox" checked={todo.completed} onChange={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })} style={{ width: '18px', height: '18px', cursor: 'pointer' }} />

        <div style={{ flex: 1, cursor: 'pointer' }} onClick={() => setIsExpanded(!isExpanded)}>
          <p style={{ margin: '0 0 4px', fontSize: '14px', textDecoration: todo.completed ? 'line-through' : 'none', color: colors.text }}>
            {highlightText(todo.text, searchQuery)}
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
            <span style={{ padding: '1px 8px', backgroundColor: `${colors.accent}20`, color: colors.accent, borderRadius: '10px', fontSize: '10px' }}>{todo.category}</span>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: priorityInfo?.color }} />
            <span style={{ fontSize: '10px', color: colors.textSecondary }}>{priorityInfo?.label}</span>
            {dday && (
              <span style={{ fontSize: '10px', fontWeight: 'bold', color: dday.status === 'overdue' ? colors.danger : dday.status === 'today' ? colors.warning : colors.textSecondary }}>
                {dday.text}
              </span>
            )}
            {subtaskProgress !== null && (
              <span style={{ fontSize: '10px', color: colors.textSecondary }}>
                [{subtasksDone}/{subtasks.length}]
              </span>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '4px' }}>
          <button onClick={() => navigate(`/edit/${todo.id}`)} style={{ padding: '4px 10px', backgroundColor: 'transparent', color: colors.accent, border: `1px solid ${colors.accent}`, borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}>수정</button>
          <button onClick={() => { if (window.confirm('삭제하시겠습니까?')) dispatch({ type: 'DELETE_TODO', payload: todo.id }); }} style={{ padding: '4px 10px', backgroundColor: 'transparent', color: colors.danger, border: `1px solid ${colors.danger}`, borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}>삭제</button>
        </div>
      </div>

      {/* 문제 5: 서브태스크 확장 영역 */}
      {isExpanded && (
        <div style={{ padding: '0 14px 12px 44px', borderTop: `1px solid ${colors.border}` }}>
          <form onSubmit={handleAddSubtask} style={{ display: 'flex', gap: '6px', marginTop: '10px', marginBottom: '8px' }}>
            <input value={subtaskInput} onChange={(e) => setSubtaskInput(e.target.value)} placeholder="서브태스크 추가" style={{ flex: 1, padding: '6px 10px', border: `1px solid ${colors.border}`, borderRadius: '6px', fontSize: '12px', backgroundColor: colors.bg, color: colors.text }} />
            <button type="submit" style={{ padding: '6px 12px', backgroundColor: colors.accent, color: '#fff', border: 'none', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}>추가</button>
          </form>

          {subtasks.length === 0 ? (
            <p style={{ fontSize: '12px', color: colors.textSecondary }}>서브태스크가 없습니다</p>
          ) : (
            <>
              {subtaskProgress !== null && (
                <div style={{ height: '4px', backgroundColor: colors.border, borderRadius: '2px', marginBottom: '8px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${subtaskProgress}%`, backgroundColor: colors.success, borderRadius: '2px', transition: 'width 0.3s' }} />
                </div>
              )}
              {subtasks.map((st) => (
                <div key={st.id} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '4px 0' }}>
                  <input type="checkbox" checked={st.completed} onChange={() => dispatch({ type: 'TOGGLE_SUBTASK', payload: { todoId: todo.id, subtaskId: st.id } })} style={{ width: '14px', height: '14px' }} />
                  <span style={{ flex: 1, fontSize: '12px', textDecoration: st.completed ? 'line-through' : 'none', color: st.completed ? colors.textSecondary : colors.text }}>{st.text}</span>
                  <button onClick={() => dispatch({ type: 'DELETE_SUBTASK', payload: { todoId: todo.id, subtaskId: st.id } })} style={{ background: 'none', border: 'none', color: colors.danger, cursor: 'pointer', fontSize: '11px' }}>삭제</button>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// AddPage / EditPage / TodoForm (문제 3: 마감일 추가)
// ══════════════════════════════════════════════

function AddPage() {
  return <div><h1>할 일 추가</h1><TodoForm mode="add" /></div>;
}

function EditPage() {
  const { id } = useParams();
  const { state } = useTodo();
  const navigate = useNavigate();
  const { colors } = useTheme();
  const todo = state.todos.find((t) => t.id === Number(id));

  if (!todo) return (
    <div style={{ textAlign: 'center', padding: '40px' }}>
      <h2>할 일을 찾을 수 없습니다</h2>
      <button onClick={() => navigate('/')} style={{ padding: '10px 20px', backgroundColor: colors.accent, color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>돌아가기</button>
    </div>
  );

  return <div><h1>할 일 수정</h1><TodoForm mode="edit" todo={todo} /></div>;
}

function TodoForm({ mode, todo }) {
  const { dispatch, CATEGORIES, PRIORITIES } = useTodo();
  const { colors } = useTheme();
  const navigate = useNavigate();
  const inputRef = useRef(null);

  const [formData, setFormData] = useState({
    text: todo?.text || '',
    category: todo?.category || '기타',
    priority: todo?.priority || 'medium',
    dueDate: todo?.dueDate || '',
  });
  const [error, setError] = useState('');

  useEffect(() => { inputRef.current?.focus(); }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.text.trim()) { setError('할 일 내용을 입력해주세요'); return; }

    if (mode === 'add') {
      dispatch({ type: 'ADD_TODO', payload: formData });
    } else {
      dispatch({ type: 'EDIT_TODO', payload: { id: todo.id, updates: formData } });
    }
    navigate('/');
  };

  const inputStyle = { padding: '10px', border: `1px solid ${colors.border}`, borderRadius: '8px', fontSize: '14px', backgroundColor: colors.surface, color: colors.text };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '450px' }}>
      <div>
        <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '4px' }}>할 일 *</label>
        <input ref={inputRef} type="text" name="text" value={formData.text} onChange={handleChange} placeholder="할 일을 입력하세요" style={{ ...inputStyle, width: '100%', boxSizing: 'border-box', borderColor: error ? colors.danger : colors.border }} />
        {error && <span style={{ color: colors.danger, fontSize: '12px' }}>{error}</span>}
      </div>
      <div>
        <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '4px' }}>카테고리</label>
        <select name="category" value={formData.category} onChange={handleChange} style={{ ...inputStyle, width: '100%', boxSizing: 'border-box' }}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      <div>
        <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '4px' }}>우선순위</label>
        <div style={{ display: 'flex', gap: '16px' }}>
          {PRIORITIES.map((p) => (
            <label key={p.value} style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', fontSize: '13px' }}>
              <input type="radio" name="priority" value={p.value} checked={formData.priority === p.value} onChange={handleChange} />
              <span style={{ color: p.color, fontWeight: 'bold' }}>{p.label}</span>
            </label>
          ))}
        </div>
      </div>
      {/* 문제 3: 마감일 */}
      <div>
        <label style={{ fontWeight: 'bold', fontSize: '13px', display: 'block', marginBottom: '4px' }}>마감일 (선택사항)</label>
        <input type="date" name="dueDate" value={formData.dueDate} onChange={handleChange} style={{ ...inputStyle, width: '100%', boxSizing: 'border-box' }} />
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button type="submit" style={{ flex: 1, padding: '12px', backgroundColor: colors.accent, color: '#fff', border: 'none', borderRadius: '8px', fontSize: '15px', cursor: 'pointer' }}>
          {mode === 'add' ? '추가하기' : '수정하기'}
        </button>
        <button type="button" onClick={() => navigate(-1)} style={{ flex: 1, padding: '12px', backgroundColor: colors.surface, color: colors.text, border: `1px solid ${colors.border}`, borderRadius: '8px', fontSize: '15px', cursor: 'pointer' }}>
          취소
        </button>
      </div>
    </form>
  );
}

// ══════════════════════════════════════════════
// StatsPage (문제 3, 5 통계 추가)
// ══════════════════════════════════════════════

function StatsPage() {
  const { stats, CATEGORIES, PRIORITIES } = useTodo();
  const { colors } = useTheme();
  const completionRate = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
  const subtaskRate = stats.totalSubtasks > 0 ? Math.round((stats.completedSubtasks / stats.totalSubtasks) * 100) : 0;

  if (stats.total === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: colors.textSecondary }}>
        <h1>통계</h1>
        <p>할 일이 없습니다.</p>
        <Link to="/add" style={{ color: colors.accent, textDecoration: 'none', fontWeight: 'bold' }}>+ 할 일 추가하기</Link>
      </div>
    );
  }

  const StatCard = ({ label, value, color }) => (
    <div style={{ padding: '14px', borderRadius: '10px', backgroundColor: colors.surface, borderLeft: `4px solid ${color}`, textAlign: 'center' }}>
      <p style={{ fontSize: '28px', fontWeight: 'bold', margin: '0 0 2px', color: colors.text }}>{value}</p>
      <p style={{ fontSize: '12px', color: colors.textSecondary, margin: 0 }}>{label}</p>
    </div>
  );

  return (
    <div>
      <h1>통계</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '20px' }}>
        <StatCard label="전체" value={stats.total} color={colors.accent} />
        <StatCard label="진행중" value={stats.active} color={colors.warning} />
        <StatCard label="완료" value={stats.completed} color={colors.success} />
        <StatCard label="기한 초과" value={stats.overdue} color={colors.danger} />
      </div>

      {/* 진행률 바 */}
      <div style={{ marginBottom: '20px' }}>
        <h3>할 일 완료율: {completionRate}%</h3>
        <div style={{ height: '10px', backgroundColor: colors.border, borderRadius: '5px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${completionRate}%`, backgroundColor: completionRate >= 80 ? colors.success : completionRate >= 50 ? colors.warning : colors.danger, borderRadius: '5px', transition: 'width 0.5s' }} />
        </div>
      </div>

      {/* 문제 5: 서브태스크 통계 */}
      {stats.totalSubtasks > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h3>서브태스크 완료율: {subtaskRate}% ({stats.completedSubtasks}/{stats.totalSubtasks})</h3>
          <div style={{ height: '10px', backgroundColor: colors.border, borderRadius: '5px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${subtaskRate}%`, backgroundColor: colors.accent, borderRadius: '5px', transition: 'width 0.5s' }} />
          </div>
        </div>
      )}

      {/* 카테고리별 */}
      <div style={{ padding: '16px', backgroundColor: colors.surface, borderRadius: '10px', marginBottom: '16px' }}>
        <h3 style={{ marginTop: 0 }}>카테고리별</h3>
        {CATEGORIES.map((cat) => (
          <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '6px 0' }}>
            <span style={{ minWidth: '40px', fontSize: '13px' }}>{cat}</span>
            <div style={{ flex: 1, height: '8px', backgroundColor: colors.border, borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${stats.total > 0 ? (stats.byCategory[cat] / stats.total) * 100 : 0}%`, backgroundColor: colors.accent, borderRadius: '4px' }} />
            </div>
            <span style={{ fontSize: '12px', color: colors.textSecondary, minWidth: '24px', textAlign: 'right' }}>{stats.byCategory[cat]}</span>
          </div>
        ))}
      </div>

      {/* 우선순위별 */}
      <div style={{ padding: '16px', backgroundColor: colors.surface, borderRadius: '10px' }}>
        <h3 style={{ marginTop: 0 }}>우선순위별</h3>
        {PRIORITIES.map((p) => (
          <div key={p.value} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '6px 0' }}>
            <span style={{ minWidth: '40px', fontSize: '13px', color: p.color, fontWeight: 'bold' }}>{p.label}</span>
            <div style={{ flex: 1, height: '8px', backgroundColor: colors.border, borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${stats.total > 0 ? (stats.byPriority[p.value] / stats.total) * 100 : 0}%`, backgroundColor: p.color, borderRadius: '4px' }} />
            </div>
            <span style={{ fontSize: '12px', color: colors.textSecondary, minWidth: '24px', textAlign: 'right' }}>{stats.byPriority[p.value]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════
// App
// ══════════════════════════════════════════════

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <TodoProvider>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="add" element={<AddPage />} />
              <Route path="edit/:id" element={<EditPage />} />
              <Route path="stats" element={<StatsPage />} />
              <Route path="*" element={
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <h1 style={{ fontSize: '48px', color: '#ccc' }}>404</h1>
                  <p>페이지를 찾을 수 없습니다</p>
                  <Link to="/" style={{ color: '#1976d2' }}>홈으로</Link>
                </div>
              } />
            </Route>
          </Routes>
        </TodoProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
