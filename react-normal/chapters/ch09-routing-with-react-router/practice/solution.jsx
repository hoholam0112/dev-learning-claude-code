/**
 * 챕터 09 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 * 모든 문제의 답안이 하나의 앱으로 통합되어 있습니다.
 *
 * 실행 방법:
 *   npx create-react-app ch09-solutions
 *   cd ch09-solutions
 *   npm install react-router-dom
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 */

import React, { createContext, useContext, useState } from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  NavLink,
  Navigate,
  Outlet,
  useParams,
  useNavigate,
  useSearchParams,
  useLocation,
} from 'react-router-dom';

// ══════════════════════════════════════════════
// 더미 상품 데이터 (문제 1, 2 공통)
// ══════════════════════════════════════════════

const PRODUCTS = [
  { id: 1, name: 'React 완벽 가이드', price: 35000, category: '도서', description: 'React의 모든 것을 다루는 종합 가이드북입니다.' },
  { id: 2, name: 'JavaScript 딥다이브', price: 42000, category: '도서', description: 'JavaScript 엔진의 동작 원리부터 최신 문법까지 깊이 있게 다룹니다.' },
  { id: 3, name: '무선 마우스', price: 25000, category: '전자기기', description: '인체공학 디자인의 저소음 무선 마우스입니다.' },
  { id: 4, name: '기계식 키보드', price: 89000, category: '전자기기', description: '체리 MX 적축 스위치를 사용한 프리미엄 기계식 키보드입니다.' },
  { id: 5, name: '노트북 스탠드', price: 45000, category: '액세서리', description: '알루미늄 소재의 접이식 노트북 스탠드입니다.' },
  { id: 6, name: 'USB-C 허브', price: 32000, category: '액세서리', description: '7-in-1 USB-C 멀티 허브입니다.' },
];

// ══════════════════════════════════════════════
// 문제 3: 인증 Context
// ══════════════════════════════════════════════

const AuthContext = createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = (username) => {
    setUser({ name: username, loggedInAt: new Date().toLocaleTimeString() });
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  return useContext(AuthContext);
}

// ══════════════════════════════════════════════
// 문제 3: 보호된 라우트 컴포넌트
// ══════════════════════════════════════════════

function ProtectedRoute() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    // 로그인 페이지로 리다이렉트하면서, 원래 가려던 경로를 state에 저장
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}

// ══════════════════════════════════════════════
// 공통 레이아웃
// ══════════════════════════════════════════════

function Layout() {
  const { user, logout } = useAuth();

  const navLinkStyle = ({ isActive }) => ({
    textDecoration: 'none',
    padding: '8px 0',
    color: isActive ? '#1976d2' : '#555',
    fontWeight: isActive ? 'bold' : 'normal',
    borderBottom: isActive ? '2px solid #1976d2' : '2px solid transparent',
    fontSize: '14px',
  });

  return (
    <div style={styles.layout}>
      <header style={styles.header}>
        <Link to="/" style={styles.logo}>ShopApp</Link>
        <nav style={styles.nav}>
          <NavLink to="/" end style={navLinkStyle}>홈</NavLink>
          <NavLink to="/products" style={navLinkStyle}>상품</NavLink>
          {user && <NavLink to="/dashboard" style={navLinkStyle}>대시보드</NavLink>}
          {user && <NavLink to="/profile" style={navLinkStyle}>프로필</NavLink>}
          {user && <NavLink to="/settings" style={navLinkStyle}>설정</NavLink>}
          <NavLink to="/about" style={navLinkStyle}>소개</NavLink>
        </nav>
        <div>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '13px', color: '#666' }}>{user.name}님</span>
              <button onClick={logout} style={styles.logoutButton}>로그아웃</button>
            </div>
          ) : (
            <Link to="/login" style={styles.loginLink}>로그인</Link>
          )}
        </div>
      </header>

      <main style={styles.main}>
        <Outlet />
      </main>

      <footer style={styles.footer}>
        &copy; 2024 ShopApp. 챕터 09 연습 문제 답안.
      </footer>
    </div>
  );
}

// ══════════════════════════════════════════════
// 페이지 컴포넌트들
// ══════════════════════════════════════════════

// 홈 페이지 (문제 1)
function Home() {
  return (
    <div>
      <h1>추천 상품</h1>
      <div style={styles.grid}>
        {PRODUCTS.slice(0, 3).map((p) => (
          <Link key={p.id} to={`/products/${p.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={styles.card}>
              <span style={styles.badge}>{p.category}</span>
              <h3>{p.name}</h3>
              <p style={styles.price}>{p.price.toLocaleString()}원</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

// 상품 목록 (문제 1 + 문제 2: 쿼리 파라미터 필터링)
function ProductListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryFilter = searchParams.get('category') || '';
  const sortOption = searchParams.get('sort') || '';

  const categories = [...new Set(PRODUCTS.map((p) => p.category))];

  // 필터링
  let filtered = categoryFilter
    ? PRODUCTS.filter((p) => p.category === categoryFilter)
    : [...PRODUCTS];

  // 정렬
  if (sortOption === 'price_asc') {
    filtered.sort((a, b) => a.price - b.price);
  } else if (sortOption === 'price_desc') {
    filtered.sort((a, b) => b.price - a.price);
  } else if (sortOption === 'name') {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  }

  // 파라미터 변경 헬퍼 (기존 파라미터 유지하며 하나만 변경)
  const updateParam = (key, value) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  const clearFilters = () => setSearchParams({});

  return (
    <div>
      <h1>상품 목록</h1>

      {/* 카테고리 필터 */}
      <div style={styles.filterSection}>
        <span style={styles.filterLabel}>카테고리:</span>
        <button
          onClick={() => updateParam('category', '')}
          style={{ ...styles.filterBtn, backgroundColor: !categoryFilter ? '#1976d2' : '#f5f5f5', color: !categoryFilter ? '#fff' : '#333' }}
        >
          전체
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => updateParam('category', cat)}
            style={{ ...styles.filterBtn, backgroundColor: categoryFilter === cat ? '#1976d2' : '#f5f5f5', color: categoryFilter === cat ? '#fff' : '#333' }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* 정렬 */}
      <div style={styles.filterSection}>
        <span style={styles.filterLabel}>정렬:</span>
        <select
          value={sortOption}
          onChange={(e) => updateParam('sort', e.target.value)}
          style={styles.select}
        >
          <option value="">기본</option>
          <option value="price_asc">가격 낮은순</option>
          <option value="price_desc">가격 높은순</option>
          <option value="name">이름순</option>
        </select>
        {(categoryFilter || sortOption) && (
          <button onClick={clearFilters} style={styles.clearBtn}>필터 초기화</button>
        )}
      </div>

      <p style={{ color: '#888', fontSize: '13px' }}>{filtered.length}개의 상품</p>

      {/* 상품 목록 */}
      {filtered.map((p) => (
        <Link key={p.id} to={`/products/${p.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={styles.listItem}>
            <div>
              <span style={styles.badge}>{p.category}</span>
              <h3 style={{ margin: '6px 0 4px' }}>{p.name}</h3>
              <p style={{ margin: 0, color: '#666', fontSize: '13px' }}>{p.description}</p>
            </div>
            <span style={styles.price}>{p.price.toLocaleString()}원</span>
          </div>
        </Link>
      ))}
    </div>
  );
}

// 상품 상세 (문제 1)
function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const product = PRODUCTS.find((p) => p.id === Number(id));

  if (!product) {
    return (
      <div style={styles.centerBox}>
        <h2>상품을 찾을 수 없습니다</h2>
        <p>상품 #{id}이(가) 존재하지 않습니다.</p>
        <button onClick={() => navigate('/products')} style={styles.primaryBtn}>
          상품 목록으로 돌아가기
        </button>
      </div>
    );
  }

  return (
    <div>
      <button onClick={() => navigate(-1)} style={styles.backBtn}>← 뒤로 가기</button>
      <span style={styles.badge}>{product.category}</span>
      <h1>{product.name}</h1>
      <p style={{ ...styles.price, fontSize: '24px' }}>{product.price.toLocaleString()}원</p>
      <p style={{ lineHeight: '1.8', color: '#555' }}>{product.description}</p>
      <button onClick={() => navigate('/products')} style={styles.primaryBtn}>
        목록으로 돌아가기
      </button>
    </div>
  );
}

// 로그인 페이지 (문제 3)
function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');

  // 이미 로그인되어 있으면 리다이렉트
  const from = location.state?.from?.pathname || '/';
  if (user) {
    return <Navigate to={from} replace />;
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim()) {
      login(username.trim());
      // 원래 가려던 페이지로 이동
      navigate(from, { replace: true });
    }
  };

  return (
    <div style={styles.centerBox}>
      <h1>로그인</h1>
      {from !== '/' && (
        <p style={{ color: '#f44336', fontSize: '14px' }}>
          이 페이지에 접근하려면 로그인이 필요합니다.
        </p>
      )}
      <form onSubmit={handleSubmit} style={{ maxWidth: '300px', margin: '0 auto' }}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="사용자명 입력"
          style={styles.input}
        />
        <button type="submit" style={{ ...styles.primaryBtn, width: '100%' }}>
          로그인
        </button>
      </form>
    </div>
  );
}

// 대시보드 (보호됨 - 문제 3)
function Dashboard() {
  const { user } = useAuth();
  return (
    <div>
      <h1>대시보드</h1>
      <p>환영합니다, <strong>{user.name}</strong>님! (로그인 시간: {user.loggedInAt})</p>
      <div style={styles.grid}>
        {['주문 내역', '포인트', '쿠폰', '찜 목록'].map((item) => (
          <div key={item} style={{ ...styles.card, textAlign: 'center' }}>
            <h3>{item}</h3>
          </div>
        ))}
      </div>
    </div>
  );
}

// 프로필 (보호됨 - 문제 3)
function ProfilePage() {
  const { user } = useAuth();
  return (
    <div>
      <h1>프로필</h1>
      <div style={styles.card}>
        <p><strong>이름:</strong> {user.name}</p>
        <p><strong>로그인 시간:</strong> {user.loggedInAt}</p>
      </div>
    </div>
  );
}

// 설정 (보호됨 - 문제 3)
function SettingsPage() {
  return (
    <div>
      <h1>설정</h1>
      <div style={styles.card}>
        <p>알림 설정, 개인정보 설정 등이 여기에 표시됩니다.</p>
        <p style={{ color: '#666', fontSize: '13px' }}>
          이 페이지는 로그인한 사용자만 볼 수 있습니다.
        </p>
      </div>
    </div>
  );
}

// 소개 페이지
function About() {
  return (
    <div>
      <h1>소개</h1>
      <p style={{ lineHeight: '1.8' }}>
        이 앱은 React Router의 다양한 기능을 실습하기 위한 예제입니다.
      </p>
      <h2>구현된 기능</h2>
      <ul style={{ lineHeight: '2' }}>
        <li>NavLink를 이용한 활성 네비게이션 표시</li>
        <li>useParams를 이용한 동적 라우팅 (상품 상세)</li>
        <li>useSearchParams를 이용한 필터/정렬 (쿼리 파라미터)</li>
        <li>보호된 라우트 (로그인 필요 페이지)</li>
        <li>로그인 후 원래 페이지로 리다이렉트</li>
        <li>404 페이지 처리</li>
      </ul>
    </div>
  );
}

// 404 페이지
function NotFound() {
  const navigate = useNavigate();
  return (
    <div style={styles.centerBox}>
      <h1 style={{ fontSize: '64px', color: '#ccc', margin: 0 }}>404</h1>
      <h2>페이지를 찾을 수 없습니다</h2>
      <button onClick={() => navigate('/')} style={styles.primaryBtn}>
        홈으로 돌아가기
      </button>
    </div>
  );
}

// ══════════════════════════════════════════════
// 메인 App: 라우팅 설정
// ══════════════════════════════════════════════

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            {/* 공개 페이지 */}
            <Route index element={<Home />} />
            <Route path="products" element={<ProductListPage />} />
            <Route path="products/:id" element={<ProductDetail />} />
            <Route path="about" element={<About />} />
            <Route path="login" element={<LoginPage />} />

            {/* 보호된 페이지 (문제 3) */}
            <Route element={<ProtectedRoute />}>
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  layout: { maxWidth: '800px', margin: '0 auto', fontFamily: 'Arial, sans-serif', minHeight: '100vh', display: 'flex', flexDirection: 'column' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 20px', borderBottom: '1px solid #e0e0e0', flexWrap: 'wrap', gap: '8px' },
  logo: { fontSize: '20px', fontWeight: 'bold', color: '#1976d2', textDecoration: 'none' },
  nav: { display: 'flex', gap: '16px', flexWrap: 'wrap' },
  main: { flex: 1, padding: '24px 20px' },
  footer: { padding: '16px 20px', borderTop: '1px solid #e0e0e0', textAlign: 'center', color: '#888', fontSize: '12px' },
  loginLink: { color: '#1976d2', textDecoration: 'none', fontWeight: 'bold', fontSize: '14px' },
  logoutButton: { padding: '6px 14px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' },
  card: { padding: '16px', border: '1px solid #e0e0e0', borderRadius: '10px', backgroundColor: '#fff' },
  badge: { display: 'inline-block', padding: '2px 10px', backgroundColor: '#e3f2fd', color: '#1976d2', borderRadius: '12px', fontSize: '11px', fontWeight: 'bold' },
  price: { color: '#1976d2', fontWeight: 'bold', fontSize: '16px' },
  filterSection: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' },
  filterLabel: { fontWeight: 'bold', fontSize: '13px', color: '#555' },
  filterBtn: { padding: '6px 14px', border: '1px solid #ddd', borderRadius: '16px', cursor: 'pointer', fontSize: '12px' },
  select: { padding: '6px 12px', border: '1px solid #ddd', borderRadius: '6px', fontSize: '13px' },
  clearBtn: { padding: '6px 14px', backgroundColor: '#ff9800', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' },
  listItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', border: '1px solid #e0e0e0', borderRadius: '8px', marginBottom: '10px' },
  centerBox: { textAlign: 'center', padding: '40px 20px' },
  backBtn: { background: 'none', border: 'none', color: '#1976d2', cursor: 'pointer', fontSize: '14px', padding: 0, marginBottom: '16px' },
  primaryBtn: { padding: '12px 24px', backgroundColor: '#1976d2', color: 'white', border: 'none', borderRadius: '8px', fontSize: '15px', cursor: 'pointer', marginTop: '12px' },
  input: { width: '100%', padding: '12px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '14px', marginBottom: '12px', boxSizing: 'border-box' },
};

export default App;
