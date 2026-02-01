/**
 * 챕터 06 - 예제 02: 커스텀 훅 테스트 + 접근성(a11y) 테스트
 *
 * 이 예제는 다음을 다룹니다:
 *   1. renderHook을 활용한 커스텀 훅 단위 테스트
 *   2. vitest-axe를 활용한 접근성 자동 테스트
 *   3. userEvent를 활용한 폼 상호작용 테스트
 *
 * 실행 방법:
 *   1. 추가 의존성 설치:
 *      npm install -D vitest-axe axe-core
 *
 *   2. 테스트 실행:
 *      npx vitest run --reporter=verbose
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';

// ============================================================
// 1. 커스텀 훅: useDebounce
// ============================================================

/**
 * 디바운스 훅
 * - 주어진 값이 delay(ms) 동안 변경되지 않으면 디바운스된 값을 업데이트합니다.
 * - 검색 입력 등에서 API 호출 횟수를 줄이는 데 사용합니다.
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

// ============================================================
// 2. 커스텀 훅: useAsync
// ============================================================

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface UseAsyncReturn<T> extends AsyncState<T> {
  execute: (...args: unknown[]) => Promise<T | undefined>;
  reset: () => void;
}

/**
 * 비동기 작업 훅
 * - 비동기 함수의 실행 상태를 관리합니다.
 * - execute()로 수동 실행, reset()으로 상태 초기화가 가능합니다.
 */
export function useAsync<T>(
  asyncFunction: (...args: unknown[]) => Promise<T>,
  immediate = false
): UseAsyncReturn<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const mountedRef = useRef(true);

  const execute = useCallback(
    async (...args: unknown[]) => {
      setState({ data: null, loading: true, error: null });
      try {
        const result = await asyncFunction(...args);
        if (mountedRef.current) {
          setState({ data: result, loading: false, error: null });
        }
        return result;
      } catch (err) {
        if (mountedRef.current) {
          setState({
            data: null,
            loading: false,
            error: err instanceof Error ? err : new Error(String(err)),
          });
        }
        return undefined;
      }
    },
    [asyncFunction]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
    return () => {
      mountedRef.current = false;
    };
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  return { ...state, execute, reset };
}

// ============================================================
// 3. 커스텀 훅: useLocalStorage
// ============================================================

/**
 * 로컬 스토리지 동기화 훅
 * - useState와 동일한 API를 제공하면서 localStorage와 동기화합니다.
 * - SSR 안전성을 고려합니다.
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      setStoredValue((prev) => {
        const newValue = value instanceof Function ? value(prev) : value;
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(newValue));
        }
        return newValue;
      });
    },
    [key]
  );

  return [storedValue, setValue];
}

// ============================================================
// 4. 검색 폼 컴포넌트 (접근성 테스트 대상)
// ============================================================

interface SearchResult {
  id: number;
  title: string;
  description: string;
}

interface SearchFormProps {
  onSearch?: (query: string) => Promise<SearchResult[]>;
}

/**
 * 접근성을 고려한 검색 폼
 * - ARIA 속성을 올바르게 사용합니다.
 * - 키보드 탐색을 지원합니다.
 * - 스크린 리더를 위한 상태 안내를 제공합니다.
 */
export function SearchForm({ onSearch }: SearchFormProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (!debouncedQuery.trim() || !onSearch) {
      setResults([]);
      return;
    }

    const performSearch = async () => {
      setIsSearching(true);
      setErrorMessage('');
      try {
        const data = await onSearch(debouncedQuery);
        setResults(data);
      } catch {
        setErrorMessage('검색 중 오류가 발생했습니다.');
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    };

    performSearch();
  }, [debouncedQuery, onSearch]);

  return (
    <section aria-label="검색">
      <form role="search" onSubmit={(e) => e.preventDefault()}>
        <div>
          <label htmlFor="search-input">검색어</label>
          <input
            id="search-input"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="검색어를 입력하세요"
            aria-describedby="search-help"
            aria-invalid={!!errorMessage}
            aria-errormessage={errorMessage ? 'search-error' : undefined}
            autoComplete="off"
          />
          <span id="search-help" className="sr-only">
            입력하면 자동으로 검색됩니다
          </span>
        </div>

        {/* 검색 상태 안내 (스크린 리더용) */}
        <div aria-live="polite" aria-atomic="true" role="status">
          {isSearching && '검색 중...'}
          {!isSearching && results.length > 0 && (
            <span>{results.length}개의 결과를 찾았습니다</span>
          )}
          {!isSearching && debouncedQuery && results.length === 0 && !errorMessage && (
            <span>검색 결과가 없습니다</span>
          )}
        </div>

        {/* 에러 메시지 */}
        {errorMessage && (
          <div id="search-error" role="alert">
            {errorMessage}
          </div>
        )}

        {/* 검색 결과 */}
        {results.length > 0 && (
          <ul role="list" aria-label="검색 결과">
            {results.map((result) => (
              <li key={result.id}>
                <article>
                  <h3>{result.title}</h3>
                  <p>{result.description}</p>
                </article>
              </li>
            ))}
          </ul>
        )}
      </form>
    </section>
  );
}

// ============================================================
// 5. 테스트 코드 (의사 코드 - 실제 테스트 파일에 작성)
// ============================================================

/**
 * ```tsx
 * // hooks.test.tsx - 커스텀 훅 테스트
 * import { describe, it, expect, vi } from 'vitest';
 * import { renderHook, act, waitFor } from '@testing-library/react';
 * import { useDebounce, useAsync, useLocalStorage } from './example-02';
 *
 * describe('useDebounce', () => {
 *   beforeEach(() => {
 *     vi.useFakeTimers();
 *   });
 *
 *   afterEach(() => {
 *     vi.useRealTimers();
 *   });
 *
 *   it('지정된 지연 시간 후에 값을 업데이트한다', () => {
 *     const { result, rerender } = renderHook(
 *       ({ value, delay }) => useDebounce(value, delay),
 *       { initialProps: { value: '초기값', delay: 300 } }
 *     );
 *
 *     // 초기 값 확인
 *     expect(result.current).toBe('초기값');
 *
 *     // 값 변경
 *     rerender({ value: '변경된 값', delay: 300 });
 *
 *     // 지연 시간 전에는 변경되지 않음
 *     expect(result.current).toBe('초기값');
 *
 *     // 지연 시간 후에 업데이트
 *     act(() => {
 *       vi.advanceTimersByTime(300);
 *     });
 *     expect(result.current).toBe('변경된 값');
 *   });
 *
 *   it('지연 시간 내 연속 변경 시 마지막 값만 반영한다', () => {
 *     const { result, rerender } = renderHook(
 *       ({ value, delay }) => useDebounce(value, delay),
 *       { initialProps: { value: 'a', delay: 500 } }
 *     );
 *
 *     // 빠르게 연속 변경
 *     rerender({ value: 'ab', delay: 500 });
 *     act(() => vi.advanceTimersByTime(200));
 *
 *     rerender({ value: 'abc', delay: 500 });
 *     act(() => vi.advanceTimersByTime(200));
 *
 *     rerender({ value: 'abcd', delay: 500 });
 *
 *     // 아직 초기값
 *     expect(result.current).toBe('a');
 *
 *     // 마지막 변경으로부터 500ms 후
 *     act(() => vi.advanceTimersByTime(500));
 *     expect(result.current).toBe('abcd');
 *   });
 * });
 *
 * describe('useAsync', () => {
 *   it('비동기 함수를 실행하고 상태를 관리한다', async () => {
 *     const mockFn = vi.fn().mockResolvedValue({ id: 1, name: '테스트' });
 *
 *     const { result } = renderHook(() => useAsync(mockFn));
 *
 *     // 초기 상태
 *     expect(result.current.loading).toBe(false);
 *     expect(result.current.data).toBeNull();
 *     expect(result.current.error).toBeNull();
 *
 *     // 실행
 *     await act(async () => {
 *       await result.current.execute();
 *     });
 *
 *     // 성공 상태
 *     expect(result.current.loading).toBe(false);
 *     expect(result.current.data).toEqual({ id: 1, name: '테스트' });
 *     expect(result.current.error).toBeNull();
 *   });
 *
 *   it('에러 발생 시 error 상태를 설정한다', async () => {
 *     const mockFn = vi.fn().mockRejectedValue(new Error('실패'));
 *
 *     const { result } = renderHook(() => useAsync(mockFn));
 *
 *     await act(async () => {
 *       await result.current.execute();
 *     });
 *
 *     expect(result.current.loading).toBe(false);
 *     expect(result.current.data).toBeNull();
 *     expect(result.current.error?.message).toBe('실패');
 *   });
 *
 *   it('reset()으로 상태를 초기화할 수 있다', async () => {
 *     const mockFn = vi.fn().mockResolvedValue('데이터');
 *     const { result } = renderHook(() => useAsync(mockFn));
 *
 *     await act(async () => {
 *       await result.current.execute();
 *     });
 *     expect(result.current.data).toBe('데이터');
 *
 *     act(() => {
 *       result.current.reset();
 *     });
 *     expect(result.current.data).toBeNull();
 *     expect(result.current.loading).toBe(false);
 *   });
 * });
 *
 * // SearchForm.test.tsx - 접근성 테스트
 * import { render, screen } from '@testing-library/react';
 * import userEvent from '@testing-library/user-event';
 * import { axe, toHaveNoViolations } from 'vitest-axe';
 * import { SearchForm } from './example-02';
 *
 * expect.extend(toHaveNoViolations);
 *
 * describe('SearchForm 접근성 테스트', () => {
 *
 *   it('초기 렌더링 시 접근성 위반이 없다', async () => {
 *     const { container } = render(<SearchForm />);
 *     const results = await axe(container);
 *     expect(results).toHaveNoViolations();
 *   });
 *
 *   it('검색 결과가 있을 때 접근성 위반이 없다', async () => {
 *     const mockSearch = vi.fn().mockResolvedValue([
 *       { id: 1, title: 'React 테스팅', description: '테스트 가이드' },
 *     ]);
 *
 *     const user = userEvent.setup();
 *     const { container } = render(<SearchForm onSearch={mockSearch} />);
 *
 *     await user.type(screen.getByLabelText('검색어'), 'React');
 *     await screen.findByText('1개의 결과를 찾았습니다');
 *
 *     const results = await axe(container);
 *     expect(results).toHaveNoViolations();
 *   });
 *
 *   it('에러 상태에서 접근성 위반이 없다', async () => {
 *     const mockSearch = vi.fn().mockRejectedValue(new Error('에러'));
 *
 *     const user = userEvent.setup();
 *     const { container } = render(<SearchForm onSearch={mockSearch} />);
 *
 *     await user.type(screen.getByLabelText('검색어'), 'test');
 *     await screen.findByRole('alert');
 *
 *     const results = await axe(container);
 *     expect(results).toHaveNoViolations();
 *   });
 *
 *   it('검색 입력 필드에 올바른 ARIA 속성이 있다', () => {
 *     render(<SearchForm />);
 *
 *     const input = screen.getByLabelText('검색어');
 *     expect(input).toHaveAttribute('type', 'search');
 *     expect(input).toHaveAttribute('aria-describedby', 'search-help');
 *
 *     // search role이 있는 form 확인
 *     expect(screen.getByRole('search')).toBeInTheDocument();
 *   });
 * });
 * ```
 */

export default SearchForm;
