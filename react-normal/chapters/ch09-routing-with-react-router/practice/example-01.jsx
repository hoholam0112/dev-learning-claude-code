/**
 * 챕터 09 - 예제 01: 다중 페이지 블로그 레이아웃
 *
 * 핵심 개념:
 * - BrowserRouter, Routes, Route로 라우팅 설정
 * - Link와 NavLink로 페이지 이동
 * - useParams로 URL 파라미터 읽기
 * - useNavigate로 프로그래밍 방식 이동
 * - 중첩 라우팅과 Outlet으로 공통 레이아웃
 * - 404 페이지 처리
 *
 * 실행 방법:
 *   npx create-react-app blog-demo
 *   cd blog-demo
 *   npm install react-router-dom
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 */

import React, { useState } from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  NavLink,
  Outlet,
  useParams,
  useNavigate,
  useSearchParams,
} from 'react-router-dom';

// ══════════════════════════════════════════════
// 더미 블로그 데이터
// ══════════════════════════════════════════════

const BLOG_POSTS = [
  {
    id: 1,
    title: 'React 시작하기',
    category: '입문',
    date: '2024-01-15',
    summary: 'React의 기본 개념과 시작 방법을 알아봅니다.',
    content:
      'React는 사용자 인터페이스를 구축하기 위한 JavaScript 라이브러리입니다. 컴포넌트 기반 아키텍처를 사용하며, 가상 DOM을 통해 효율적인 렌더링을 제공합니다. JSX 문법을 사용하여 JavaScript 안에서 HTML과 유사한 코드를 작성할 수 있습니다.',
  },
  {
    id: 2,
    title: 'useState 완전 정복',
    category: '기초',
    date: '2024-02-10',
    summary: 'React의 가장 기본적인 훅인 useState를 깊이 있게 다룹니다.',
    content:
      'useState는 함수형 컴포넌트에서 상태를 관리할 수 있게 해주는 가장 기본적인 훅입니다. 초기값을 인자로 받고, [현재값, 설정함수] 배열을 반환합니다. 함수형 업데이트, 지연 초기화 등 고급 패턴도 함께 알아봅니다.',
  },
  {
    id: 3,
    title: 'useEffect 이해하기',
    category: '기초',
    date: '2024-03-05',
    summary: '사이드 이펙트와 생명주기를 useEffect로 관리하는 방법',
    content:
      'useEffect는 컴포넌트의 사이드 이펙트를 관리하는 훅입니다. API 호출, 타이머 설정, 이벤트 리스너 등록 등 다양한 사이드 이펙트를 처리할 수 있습니다. 의존성 배열과 클린업 함수를 올바르게 사용하는 것이 핵심입니다.',
  },
  {
    id: 4,
    title: 'Context API로 전역 상태 관리',
    category: '중급',
    date: '2024-04-20',
    summary: 'Props Drilling 문제를 해결하는 Context 패턴을 학습합니다.',
    content:
      'Context API는 컴포넌트 트리를 통해 데이터를 직접 전달할 수 있는 방법을 제공합니다. createContext로 Context를 생성하고, Provider로 값을 공급하며, useContext로 값을 소비합니다. useReducer와 결합하면 더 강력한 상태 관리가 가능합니다.',
  },
  {
    id: 5,
    title: 'React Router 완벽 가이드',
    category: '중급',
    date: '2024-05-12',
    summary: 'SPA에서 라우팅을 구현하는 방법을 상세히 알아봅니다.',
    content:
      'React Router는 React 애플리케이션에서 클라이언트 사이드 라우팅을 구현하는 라이브러리입니다. BrowserRouter, Routes, Route, Link 등의 컴포넌트를 제공하며, useParams, useNavigate, useSearchParams 등의 훅으로 프로그래밍 방식의 라우팅을 지원합니다.',
  },
];

// ══════════════════════════════════════════════
// 공통 레이아웃 컴포넌트
// ══════════════════════════════════════════════

/**
 * Layout: 모든 페이지에 공통으로 적용되는 레이아웃
 * Outlet 컴포넌트가 자식 라우트의 내용을 렌더링하는 자리 역할을 한다.
 */
function Layout() {
  return (
    <div style={styles.layout}>
      {/* 헤더 + 네비게이션 */}
      <header style={styles.header}>
        <Link to="/" style={styles.logo}>
          React 블로그
        </Link>
        <nav style={styles.nav}>
          {/* NavLink는 현재 URL과 일치하면 isActive가 true */}
          <NavLink
            to="/"
            end  // end: 정확히 "/"일 때만 활성화 (하위 경로 제외)
            style={({ isActive }) => ({
              ...styles.navLink,
              color: isActive ? '#1976d2' : '#555',
              borderBottom: isActive ? '2px solid #1976d2' : '2px solid transparent',
            })}
          >
            홈
          </NavLink>
          <NavLink
            to="/posts"
            style={({ isActive }) => ({
              ...styles.navLink,
              color: isActive ? '#1976d2' : '#555',
              borderBottom: isActive ? '2px solid #1976d2' : '2px solid transparent',
            })}
          >
            게시글
          </NavLink>
          <NavLink
            to="/about"
            style={({ isActive }) => ({
              ...styles.navLink,
              color: isActive ? '#1976d2' : '#555',
              borderBottom: isActive ? '2px solid #1976d2' : '2px solid transparent',
            })}
          >
            소개
          </NavLink>
        </nav>
      </header>

      {/* 메인 컨텐츠: 자식 라우트가 여기에 렌더링됨 */}
      <main style={styles.main}>
        <Outlet />
      </main>

      {/* 푸터 */}
      <footer style={styles.footer}>
        <p>&copy; 2024 React 블로그. React Router로 만들었습니다.</p>
      </footer>
    </div>
  );
}

// ══════════════════════════════════════════════
// 페이지 컴포넌트들
// ══════════════════════════════════════════════

// 홈 페이지
function Home() {
  return (
    <div>
      <h1>React 블로그에 오신 것을 환영합니다</h1>
      <p style={styles.subtitle}>
        React 학습에 도움이 되는 글을 모았습니다.
      </p>

      {/* 최신 게시글 3개 */}
      <h2>최신 글</h2>
      <div style={styles.cardGrid}>
        {BLOG_POSTS.slice(0, 3).map((post) => (
          <Link
            key={post.id}
            to={`/posts/${post.id}`}
            style={styles.cardLink}
          >
            <div style={styles.card}>
              <span style={styles.badge}>{post.category}</span>
              <h3>{post.title}</h3>
              <p style={styles.cardSummary}>{post.summary}</p>
              <span style={styles.date}>{post.date}</span>
            </div>
          </Link>
        ))}
      </div>

      <div style={{ textAlign: 'center', marginTop: '24px' }}>
        <Link to="/posts" style={styles.viewAllLink}>
          모든 게시글 보기 →
        </Link>
      </div>
    </div>
  );
}

// 게시글 목록 페이지 (검색 기능 포함)
function PostList() {
  // useSearchParams로 URL 쿼리 파라미터 관리
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryFilter = searchParams.get('category') || '';

  // 카테고리 필터링
  const filteredPosts = categoryFilter
    ? BLOG_POSTS.filter((post) => post.category === categoryFilter)
    : BLOG_POSTS;

  const categories = [...new Set(BLOG_POSTS.map((p) => p.category))];

  return (
    <div>
      <h1>게시글 목록</h1>

      {/* 카테고리 필터 */}
      <div style={styles.filterBar}>
        <button
          onClick={() => setSearchParams({})}
          style={{
            ...styles.filterButton,
            backgroundColor: !categoryFilter ? '#1976d2' : '#f5f5f5',
            color: !categoryFilter ? 'white' : '#333',
          }}
        >
          전체
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSearchParams({ category: cat })}
            style={{
              ...styles.filterButton,
              backgroundColor: categoryFilter === cat ? '#1976d2' : '#f5f5f5',
              color: categoryFilter === cat ? 'white' : '#333',
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      <p style={styles.resultInfo}>{filteredPosts.length}개의 게시글</p>

      {/* 게시글 목록 */}
      {filteredPosts.map((post) => (
        <Link
          key={post.id}
          to={`/posts/${post.id}`}
          style={styles.postListLink}
        >
          <div style={styles.postListItem}>
            <div>
              <span style={styles.badge}>{post.category}</span>
              <h3 style={{ margin: '8px 0 4px 0' }}>{post.title}</h3>
              <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
                {post.summary}
              </p>
            </div>
            <span style={styles.date}>{post.date}</span>
          </div>
        </Link>
      ))}
    </div>
  );
}

// 게시글 상세 페이지
function PostDetail() {
  // useParams로 URL 파라미터 읽기
  const { id } = useParams();
  const navigate = useNavigate();

  // id는 문자열이므로 숫자로 변환하여 비교
  const post = BLOG_POSTS.find((p) => p.id === Number(id));

  // 게시글이 없는 경우
  if (!post) {
    return (
      <div style={styles.notFoundBox}>
        <h2>게시글을 찾을 수 없습니다</h2>
        <p>게시글 #{id}이(가) 존재하지 않습니다.</p>
        <button
          onClick={() => navigate('/posts')}
          style={styles.backButton}
        >
          게시글 목록으로 돌아가기
        </button>
      </div>
    );
  }

  // 이전/다음 게시글
  const currentIndex = BLOG_POSTS.findIndex((p) => p.id === post.id);
  const prevPost = BLOG_POSTS[currentIndex - 1];
  const nextPost = BLOG_POSTS[currentIndex + 1];

  return (
    <article>
      {/* 뒤로 가기 버튼 */}
      <button
        onClick={() => navigate(-1)}  // 히스토리 뒤로 가기
        style={styles.backLink}
      >
        ← 뒤로 가기
      </button>

      <span style={styles.badge}>{post.category}</span>
      <h1 style={{ marginTop: '8px' }}>{post.title}</h1>
      <p style={styles.date}>{post.date}</p>

      <div style={styles.articleContent}>
        <p>{post.content}</p>
      </div>

      {/* 이전/다음 네비게이션 */}
      <div style={styles.postNav}>
        {prevPost ? (
          <Link to={`/posts/${prevPost.id}`} style={styles.postNavLink}>
            ← {prevPost.title}
          </Link>
        ) : (
          <span />
        )}
        {nextPost ? (
          <Link to={`/posts/${nextPost.id}`} style={styles.postNavLink}>
            {nextPost.title} →
          </Link>
        ) : (
          <span />
        )}
      </div>
    </article>
  );
}

// 소개 페이지
function About() {
  return (
    <div>
      <h1>소개</h1>
      <p style={styles.aboutText}>
        이 블로그는 React 학습자를 위한 교육 자료입니다.
        <br />
        React Router를 사용하여 SPA(Single Page Application) 방식으로 구현되었습니다.
      </p>

      <h2>사용된 기술</h2>
      <ul style={styles.techList}>
        <li>React 18</li>
        <li>React Router v6</li>
        <li>useState, useEffect, useParams, useNavigate</li>
        <li>중첩 라우팅 (Nested Routes)</li>
        <li>쿼리 파라미터 (useSearchParams)</li>
      </ul>
    </div>
  );
}

// 404 페이지
function NotFound() {
  const navigate = useNavigate();

  return (
    <div style={styles.notFoundBox}>
      <h1 style={{ fontSize: '64px', margin: '0 0 16px 0', color: '#ccc' }}>
        404
      </h1>
      <h2>페이지를 찾을 수 없습니다</h2>
      <p style={{ color: '#666' }}>
        요청하신 페이지가 존재하지 않습니다.
      </p>
      <button
        onClick={() => navigate('/')}
        style={styles.backButton}
      >
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
      <Routes>
        {/* 공통 레이아웃으로 감싸기 */}
        <Route path="/" element={<Layout />}>
          {/* index: "/"에서 표시할 컴포넌트 */}
          <Route index element={<Home />} />

          {/* 게시글 관련 라우트 */}
          <Route path="posts" element={<PostList />} />
          <Route path="posts/:id" element={<PostDetail />} />

          {/* 소개 페이지 */}
          <Route path="about" element={<About />} />

          {/* 404: 위의 어떤 경로에도 매칭되지 않을 때 */}
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  layout: {
    maxWidth: '800px',
    margin: '0 auto',
    fontFamily: 'Arial, sans-serif',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 24px',
    borderBottom: '1px solid #e0e0e0',
  },
  logo: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1976d2',
    textDecoration: 'none',
  },
  nav: {
    display: 'flex',
    gap: '24px',
  },
  navLink: {
    textDecoration: 'none',
    padding: '8px 0',
    fontWeight: '500',
    fontSize: '15px',
    transition: 'all 0.2s',
  },
  main: {
    flex: 1,
    padding: '24px',
  },
  footer: {
    padding: '20px 24px',
    borderTop: '1px solid #e0e0e0',
    textAlign: 'center',
    color: '#888',
    fontSize: '13px',
  },
  subtitle: {
    color: '#666',
    fontSize: '16px',
    marginBottom: '32px',
  },
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
    gap: '16px',
  },
  cardLink: {
    textDecoration: 'none',
    color: 'inherit',
  },
  card: {
    padding: '20px',
    border: '1px solid #e0e0e0',
    borderRadius: '10px',
    transition: 'box-shadow 0.2s',
    height: '100%',
    boxSizing: 'border-box',
  },
  cardSummary: {
    color: '#666',
    fontSize: '14px',
    lineHeight: '1.5',
  },
  badge: {
    display: 'inline-block',
    padding: '2px 10px',
    backgroundColor: '#e3f2fd',
    color: '#1976d2',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 'bold',
  },
  date: {
    color: '#999',
    fontSize: '13px',
  },
  viewAllLink: {
    color: '#1976d2',
    textDecoration: 'none',
    fontWeight: 'bold',
  },
  filterBar: {
    display: 'flex',
    gap: '8px',
    marginBottom: '20px',
  },
  filterButton: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    borderRadius: '20px',
    cursor: 'pointer',
    fontSize: '13px',
    transition: 'all 0.2s',
  },
  resultInfo: {
    color: '#888',
    fontSize: '13px',
    marginBottom: '12px',
  },
  postListLink: {
    textDecoration: 'none',
    color: 'inherit',
  },
  postListItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: '16px',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    marginBottom: '12px',
    transition: 'background-color 0.2s',
  },
  backLink: {
    display: 'inline-block',
    background: 'none',
    border: 'none',
    color: '#1976d2',
    cursor: 'pointer',
    fontSize: '14px',
    padding: '0',
    marginBottom: '16px',
  },
  articleContent: {
    lineHeight: '1.8',
    fontSize: '16px',
    color: '#444',
    padding: '20px 0',
    borderTop: '1px solid #eee',
    borderBottom: '1px solid #eee',
    margin: '20px 0',
  },
  postNav: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '24px',
  },
  postNavLink: {
    color: '#1976d2',
    textDecoration: 'none',
    fontSize: '14px',
  },
  notFoundBox: {
    textAlign: 'center',
    padding: '60px 20px',
  },
  backButton: {
    padding: '12px 24px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '15px',
    cursor: 'pointer',
    marginTop: '16px',
  },
  aboutText: {
    lineHeight: '1.8',
    color: '#555',
    fontSize: '15px',
  },
  techList: {
    lineHeight: '2',
    color: '#555',
  },
};

export default App;
