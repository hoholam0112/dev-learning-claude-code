/**
 * 챕터 07 - 예제 01: API 데이터 페칭과 실시간 검색
 *
 * 핵심 개념:
 * - useEffect로 API 데이터 가져오기
 * - 로딩/에러/데이터 상태 관리
 * - 디바운스(debounce)를 적용한 실시간 검색
 * - 클린업 함수로 불필요한 요청 방지
 *
 * 실행 방법:
 *   npx create-react-app effect-demo
 *   cd effect-demo
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 *
 * 사용 API: JSONPlaceholder (https://jsonplaceholder.typicode.com)
 *   - 무료 공개 테스트용 REST API입니다.
 */

import React, { useState, useEffect } from 'react';

// ──────────────────────────────────────────────
// UserList: 사용자 목록 페칭 + 실시간 검색
// ──────────────────────────────────────────────

function UserList() {
  // 세 가지 핵심 상태: 데이터, 로딩, 에러
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 검색 관련 상태
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);

  /**
   * 이펙트 1: 컴포넌트 마운트 시 사용자 목록을 가져온다.
   * 의존성 배열이 []이므로 딱 1번만 실행된다.
   */
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        setError(null);

        // JSONPlaceholder API에서 사용자 목록 가져오기
        const response = await fetch(
          'https://jsonplaceholder.typicode.com/users'
        );

        // HTTP 에러 처리
        if (!response.ok) {
          throw new Error(`HTTP 에러: ${response.status}`);
        }

        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false); // 성공이든 실패든 로딩 종료
      }
    };

    fetchUsers();
  }, []); // 빈 배열: 마운트 시 1번만 실행

  /**
   * 이펙트 2: 검색어 변경 시 디바운스 적용
   * 사용자가 타이핑을 멈춘 후 300ms 뒤에 검색을 수행한다.
   * 클린업으로 이전 타이머를 제거하여 불필요한 실행을 방지한다.
   */
  useEffect(() => {
    // 검색어가 변경될 때마다 콘솔에 로그 (디버깅용)
    if (searchQuery) {
      console.log(`검색어 변경: "${searchQuery}" (300ms 후 필터링 적용)`);
    }

    // 클린업: 이전 타이머가 있으면 제거
    // 이렇게 하면 빠르게 타이핑할 때 마지막 입력만 처리됨
    const timer = setTimeout(() => {
      if (searchQuery) {
        console.log(`필터링 적용: "${searchQuery}"`);
      }
    }, 300);

    return () => {
      clearTimeout(timer); // 클린업: 타이머 해제
    };
  }, [searchQuery]); // searchQuery가 변경될 때마다 실행

  // 검색어로 사용자 필터링 (이름 또는 이메일)
  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // ── 로딩 화면 ──
  if (loading) {
    return (
      <div style={styles.centerBox}>
        <div style={styles.spinner} />
        <p>사용자 목록을 불러오는 중...</p>
      </div>
    );
  }

  // ── 에러 화면 ──
  if (error) {
    return (
      <div style={styles.errorBox}>
        <h3>오류 발생</h3>
        <p>{error}</p>
        <button
          onClick={() => window.location.reload()}
          style={styles.retryButton}
        >
          다시 시도
        </button>
      </div>
    );
  }

  // ── 메인 화면 ──
  return (
    <div>
      <h2>사용자 목록</h2>

      {/* 검색 입력 */}
      <div style={styles.searchContainer}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="이름 또는 이메일로 검색..."
          style={styles.searchInput}
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery('')}
            style={styles.clearButton}
          >
            지우기
          </button>
        )}
      </div>

      <p style={styles.resultInfo}>
        총 {users.length}명 중 {filteredUsers.length}명 표시
      </p>

      {/* 사용자 목록 */}
      {filteredUsers.length === 0 ? (
        <p style={styles.noResult}>
          "{searchQuery}"에 대한 검색 결과가 없습니다
        </p>
      ) : (
        <div style={styles.userGrid}>
          {filteredUsers.map((user) => (
            <div
              key={user.id}
              style={{
                ...styles.userCard,
                ...(selectedUser?.id === user.id
                  ? styles.selectedCard
                  : {}),
              }}
              onClick={() => setSelectedUser(user)}
            >
              <h3 style={styles.userName}>{user.name}</h3>
              <p style={styles.userEmail}>{user.email}</p>
              <p style={styles.userCompany}>{user.company.name}</p>
            </div>
          ))}
        </div>
      )}

      {/* 선택된 사용자 상세 정보 */}
      {selectedUser && (
        <UserDetail
          userId={selectedUser.id}
          onClose={() => setSelectedUser(null)}
        />
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// UserDetail: 선택된 사용자의 게시글을 가져와 표시
// ──────────────────────────────────────────────

function UserDetail({ userId, onClose }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  /**
   * userId가 변경될 때마다 해당 사용자의 게시글을 가져온다.
   * 의존성 배열에 [userId]를 지정하여 userId 변경 시에만 재실행한다.
   */
  useEffect(() => {
    let isCancelled = false; // 컴포넌트 언마운트 후 state 업데이트 방지

    const fetchPosts = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `https://jsonplaceholder.typicode.com/posts?userId=${userId}`
        );
        const data = await response.json();

        // 컴포넌트가 아직 마운트되어 있을 때만 state 업데이트
        if (!isCancelled) {
          setPosts(data.slice(0, 3)); // 처음 3개만 표시
          setLoading(false);
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('게시글 로딩 실패:', err);
          setLoading(false);
        }
      }
    };

    fetchPosts();

    // 클린업: 이전 요청의 결과를 무시하도록 플래그 설정
    return () => {
      isCancelled = true;
    };
  }, [userId]); // userId가 변경될 때마다 실행

  return (
    <div style={styles.detailPanel}>
      <div style={styles.detailHeader}>
        <h3>최근 게시글</h3>
        <button onClick={onClose} style={styles.closeButton}>
          닫기
        </button>
      </div>

      {loading ? (
        <p>게시글을 불러오는 중...</p>
      ) : (
        <ul style={styles.postList}>
          {posts.map((post) => (
            <li key={post.id} style={styles.postItem}>
              <strong>{post.title}</strong>
              <p style={styles.postBody}>{post.body}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// 메인 App
// ──────────────────────────────────────────────

function App() {
  return (
    <div style={styles.container}>
      <h1>API 데이터 페칭 예제</h1>
      <p style={styles.description}>
        JSONPlaceholder API에서 사용자 목록을 가져옵니다.
        <br />
        검색어를 입력하면 실시간으로 필터링되며, 사용자를 클릭하면 게시글을 볼 수 있습니다.
      </p>
      <UserList />
    </div>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  container: {
    maxWidth: '700px',
    margin: '20px auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  description: {
    color: '#666',
    fontSize: '14px',
    lineHeight: '1.6',
    marginBottom: '20px',
  },
  centerBox: {
    textAlign: 'center',
    padding: '40px',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid #e0e0e0',
    borderTop: '4px solid #1976d2',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 16px',
  },
  errorBox: {
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#ffebee',
    borderRadius: '12px',
  },
  retryButton: {
    padding: '10px 24px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  searchContainer: {
    display: 'flex',
    gap: '8px',
    marginBottom: '12px',
  },
  searchInput: {
    flex: 1,
    padding: '12px 16px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '15px',
    outline: 'none',
  },
  clearButton: {
    padding: '12px 20px',
    backgroundColor: '#757575',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
  },
  resultInfo: {
    color: '#888',
    fontSize: '13px',
    marginBottom: '16px',
  },
  noResult: {
    textAlign: 'center',
    color: '#999',
    padding: '30px',
    fontSize: '15px',
  },
  userGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  userCard: {
    padding: '16px',
    border: '2px solid #e0e0e0',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'border-color 0.2s, background-color 0.2s',
  },
  selectedCard: {
    borderColor: '#1976d2',
    backgroundColor: '#e3f2fd',
  },
  userName: {
    margin: '0 0 4px 0',
    fontSize: '16px',
  },
  userEmail: {
    margin: '0',
    color: '#1976d2',
    fontSize: '14px',
  },
  userCompany: {
    margin: '4px 0 0 0',
    color: '#888',
    fontSize: '13px',
  },
  detailPanel: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#f5f5f5',
    borderRadius: '12px',
    border: '1px solid #ddd',
  },
  detailHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
  },
  closeButton: {
    padding: '6px 16px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  postList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  postItem: {
    padding: '12px',
    marginBottom: '8px',
    backgroundColor: 'white',
    borderRadius: '8px',
    border: '1px solid #e0e0e0',
  },
  postBody: {
    margin: '8px 0 0 0',
    color: '#666',
    fontSize: '13px',
    lineHeight: '1.5',
  },
};

export default App;
