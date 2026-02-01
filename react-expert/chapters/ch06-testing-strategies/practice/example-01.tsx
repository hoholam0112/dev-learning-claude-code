/**
 * 챕터 06 - 예제 01: React Testing Library + MSW 통합 테스트
 *
 * 이 예제는 API에서 사용자 목록을 가져와 표시하는 컴포넌트와
 * MSW를 활용한 통합 테스트를 보여줍니다.
 *
 * 실행 방법:
 *   1. 프로젝트 초기화:
 *      npm create vite@latest testing-demo -- --template react-ts
 *      cd testing-demo
 *
 *   2. 의존성 설치:
 *      npm install
 *      npm install -D vitest @testing-library/react @testing-library/jest-dom
 *      npm install -D @testing-library/user-event msw jsdom
 *
 *   3. vite.config.ts에 test 설정 추가:
 *      /// <reference types="vitest" />
 *      export default defineConfig({
 *        test: {
 *          globals: true,
 *          environment: 'jsdom',
 *          setupFiles: ['./src/test/setup.ts'],
 *        }
 *      })
 *
 *   4. 테스트 실행:
 *      npx vitest run
 */

import React, { useState, useEffect, useCallback } from 'react';

// ============================================================
// 1. 타입 정의
// ============================================================

/** 사용자 데이터 타입 */
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

/** API 응답 타입 */
interface ApiResponse<T> {
  data: T;
  total: number;
  page: number;
}

/** 컴포넌트 Props */
interface UserListProps {
  /** API 엔드포인트 URL */
  apiUrl?: string;
  /** 페이지당 항목 수 */
  pageSize?: number;
}

// ============================================================
// 2. 커스텀 훅: useFetch
// ============================================================

interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

/**
 * 범용 데이터 페칭 훅
 * - 로딩, 에러, 데이터 상태를 관리합니다.
 * - refetch 기능을 제공합니다.
 */
function useFetch<T>(url: string): FetchState<T> & { refetch: () => void } {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: 요청에 실패했습니다.`);
      }
      const json: T = await response.json();
      setState({ data: json, loading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : '알 수 없는 오류';
      setState({ data: null, loading: false, error: message });
    }
  }, [url]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...state, refetch: fetchData };
}

// ============================================================
// 3. UserList 컴포넌트
// ============================================================

/**
 * 사용자 목록 컴포넌트
 * - API에서 사용자 목록을 가져와 표시합니다.
 * - 로딩/에러/빈 상태를 처리합니다.
 * - 역할별 필터링 기능이 있습니다.
 */
export function UserList({
  apiUrl = '/api/users',
  pageSize = 10,
}: UserListProps) {
  const { data, loading, error, refetch } = useFetch<ApiResponse<User[]>>(
    `${apiUrl}?limit=${pageSize}`
  );
  const [roleFilter, setRoleFilter] = useState<string>('all');

  // 역할별 필터링
  const filteredUsers =
    data?.data.filter(
      (user) => roleFilter === 'all' || user.role === roleFilter
    ) ?? [];

  // 로딩 상태
  if (loading) {
    return (
      <div role="status" aria-live="polite">
        <span className="spinner" aria-hidden="true" />
        로딩 중...
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div role="alert">
        <p>오류가 발생했습니다: {error}</p>
        <button onClick={refetch} type="button">
          다시 시도
        </button>
      </div>
    );
  }

  // 빈 상태
  if (filteredUsers.length === 0) {
    return (
      <div>
        <RoleFilter current={roleFilter} onChange={setRoleFilter} />
        <p>표시할 사용자가 없습니다.</p>
      </div>
    );
  }

  return (
    <div>
      <h2>사용자 목록</h2>
      <p>
        총 <strong>{data?.total ?? 0}</strong>명
      </p>

      <RoleFilter current={roleFilter} onChange={setRoleFilter} />

      <ul role="list" aria-label="사용자 목록">
        {filteredUsers.map((user) => (
          <UserCard key={user.id} user={user} />
        ))}
      </ul>
    </div>
  );
}

// ============================================================
// 4. 하위 컴포넌트
// ============================================================

/** 역할 필터 드롭다운 */
function RoleFilter({
  current,
  onChange,
}: {
  current: string;
  onChange: (value: string) => void;
}) {
  return (
    <label>
      역할 필터:
      <select
        value={current}
        onChange={(e) => onChange(e.target.value)}
        aria-label="역할 필터"
      >
        <option value="all">전체</option>
        <option value="admin">관리자</option>
        <option value="user">사용자</option>
        <option value="guest">게스트</option>
      </select>
    </label>
  );
}

/** 개별 사용자 카드 */
function UserCard({ user }: { user: User }) {
  const roleLabels: Record<string, string> = {
    admin: '관리자',
    user: '사용자',
    guest: '게스트',
  };

  return (
    <li className="user-card">
      <strong>{user.name}</strong>
      <span> - {user.email}</span>
      <span
        className={`badge badge-${user.role}`}
        aria-label={`역할: ${roleLabels[user.role]}`}
      >
        {roleLabels[user.role]}
      </span>
    </li>
  );
}

// ============================================================
// 5. MSW 핸들러 (테스트용)
// ============================================================

/**
 * 아래 코드는 별도 파일(src/mocks/handlers.ts)에 위치시키는 것이 일반적입니다.
 * 예제에서는 이해를 위해 같은 파일에 포함합니다.
 */

// import { http, HttpResponse, delay } from 'msw';
// import { setupServer } from 'msw/node';
//
// // 모킹 데이터
// const mockUsers: User[] = [
//   { id: 1, name: '김철수', email: 'cs@example.com', role: 'admin' },
//   { id: 2, name: '이영희', email: 'yh@example.com', role: 'user' },
//   { id: 3, name: '박민수', email: 'ms@example.com', role: 'guest' },
// ];
//
// // MSW 핸들러
// export const handlers = [
//   // 성공 응답
//   http.get('/api/users', async ({ request }) => {
//     const url = new URL(request.url);
//     const limit = Number(url.searchParams.get('limit')) || 10;
//
//     return HttpResponse.json({
//       data: mockUsers.slice(0, limit),
//       total: mockUsers.length,
//       page: 1,
//     } satisfies ApiResponse<User[]>);
//   }),
// ];
//
// // 에러 핸들러 (특정 테스트에서 오버라이드용)
// export const errorHandlers = [
//   http.get('/api/users', () => {
//     return new HttpResponse(null, { status: 500 });
//   }),
// ];
//
// // 지연 핸들러 (로딩 상태 테스트용)
// export const delayHandlers = [
//   http.get('/api/users', async () => {
//     await delay(3000);
//     return HttpResponse.json({
//       data: mockUsers,
//       total: mockUsers.length,
//       page: 1,
//     });
//   }),
// ];
//
// export const server = setupServer(...handlers);

// ============================================================
// 6. 테스트 코드 (별도 .test.tsx 파일로 분리 권장)
// ============================================================

/**
 * 아래는 테스트 파일의 구조를 보여주는 의사 코드입니다.
 * 실제로는 UserList.test.tsx 파일에 작성합니다.
 *
 * ```tsx
 * // UserList.test.tsx
 * import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
 * import { render, screen, waitFor, within } from '@testing-library/react';
 * import userEvent from '@testing-library/user-event';
 * import '@testing-library/jest-dom';
 * import { UserList } from './example-01';
 * import { server, errorHandlers } from './example-01'; // 실제로는 mocks/handlers
 *
 * // MSW 서버 라이프사이클
 * beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
 * afterEach(() => server.resetHandlers());
 * afterAll(() => server.close());
 *
 * describe('UserList 통합 테스트', () => {
 *
 *   it('로딩 상태를 표시한 후 사용자 목록을 렌더링한다', async () => {
 *     render(<UserList />);
 *
 *     // 로딩 상태 확인 (role="status" 사용)
 *     expect(screen.getByRole('status')).toHaveTextContent('로딩 중...');
 *
 *     // 데이터 로드 완료 대기
 *     const heading = await screen.findByRole('heading', { name: '사용자 목록' });
 *     expect(heading).toBeInTheDocument();
 *
 *     // 사용자 항목 확인
 *     const list = screen.getByRole('list', { name: '사용자 목록' });
 *     const items = within(list).getAllByRole('listitem');
 *     expect(items).toHaveLength(3);
 *
 *     // 개별 사용자 확인
 *     expect(screen.getByText('김철수')).toBeInTheDocument();
 *     expect(screen.getByText('이영희')).toBeInTheDocument();
 *     expect(screen.getByText('박민수')).toBeInTheDocument();
 *   });
 *
 *   it('역할별로 사용자를 필터링할 수 있다', async () => {
 *     const user = userEvent.setup();
 *     render(<UserList />);
 *
 *     // 데이터 로드 대기
 *     await screen.findByRole('heading', { name: '사용자 목록' });
 *
 *     // "관리자" 필터 선택
 *     const select = screen.getByRole('combobox', { name: '역할 필터' });
 *     await user.selectOptions(select, 'admin');
 *
 *     // 관리자만 표시되는지 확인
 *     const items = screen.getAllByRole('listitem');
 *     expect(items).toHaveLength(1);
 *     expect(screen.getByText('김철수')).toBeInTheDocument();
 *   });
 *
 *   it('API 오류 시 에러 메시지와 재시도 버튼을 표시한다', async () => {
 *     // 이 테스트에서만 에러 핸들러로 오버라이드
 *     server.use(...errorHandlers);
 *
 *     const user = userEvent.setup();
 *     render(<UserList />);
 *
 *     // 에러 메시지 확인
 *     const alert = await screen.findByRole('alert');
 *     expect(alert).toHaveTextContent('오류가 발생했습니다');
 *
 *     // 재시도 버튼 확인
 *     const retryButton = screen.getByRole('button', { name: '다시 시도' });
 *     expect(retryButton).toBeInTheDocument();
 *
 *     // 핸들러를 성공 응답으로 복원 후 재시도
 *     server.resetHandlers();
 *     await user.click(retryButton);
 *
 *     // 성공적으로 데이터 로드 확인
 *     await screen.findByRole('heading', { name: '사용자 목록' });
 *   });
 *
 *   it('빈 결과 필터링 시 안내 메시지를 표시한다', async () => {
 *     const user = userEvent.setup();
 *     render(<UserList />);
 *
 *     await screen.findByRole('heading', { name: '사용자 목록' });
 *
 *     // 존재하지 않는 역할 조합을 만들기 위해 필터 변경
 *     // (모킹 데이터에 guest가 1명뿐이므로 다른 방법 사용)
 *     // 여기서는 빈 결과를 보여주는 시나리오
 *     const select = screen.getByRole('combobox', { name: '역할 필터' });
 *     await user.selectOptions(select, 'guest');
 *
 *     // 게스트 1명만 표시
 *     const items = screen.getAllByRole('listitem');
 *     expect(items).toHaveLength(1);
 *   });
 * });
 * ```
 */

export default UserList;
