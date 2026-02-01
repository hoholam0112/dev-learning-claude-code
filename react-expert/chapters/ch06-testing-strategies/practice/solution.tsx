/**
 * 챕터 06 - 연습 문제 모범 답안
 *
 * 이 파일은 exercise.md의 세 문제에 대한 모범 답안을 담고 있습니다.
 *
 * 실행 방법:
 *   1. 의존성 설치:
 *      npm install -D vitest @testing-library/react @testing-library/jest-dom
 *      npm install -D @testing-library/user-event msw jsdom vitest-axe
 *
 *   2. 테스트 실행:
 *      npx vitest run
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';

// ============================================================
// 문제 1 답안: 장바구니 컴포넌트 + 통합 테스트
// ============================================================

// --- 타입 정의 ---

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  imageUrl: string;
}

// --- 장바구니 컴포넌트 ---

export function ShoppingCart() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 장바구니 조회
  const fetchCart = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/cart');
      if (!response.ok) throw new Error('장바구니를 불러오지 못했습니다.');
      const data: CartItem[] = await response.json();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    } finally {
      setLoading(false);
    }
  }, []);

  // 수량 변경
  const updateQuantity = async (id: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      const response = await fetch(`/api/cart/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQuantity }),
      });
      if (!response.ok) throw new Error('수량 변경에 실패했습니다.');
      setItems((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, quantity: newQuantity } : item
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : '수량 변경 실패');
    }
  };

  // 항목 삭제
  const removeItem = async (id: number) => {
    try {
      const response = await fetch(`/api/cart/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('삭제에 실패했습니다.');
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : '삭제 실패');
    }
  };

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  // 총 금액 계산
  const totalPrice = items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  if (loading) {
    return (
      <div role="status" aria-live="polite">
        장바구니를 불러오는 중...
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert">
        <p>{error}</p>
        <button onClick={fetchCart} type="button">
          다시 시도
        </button>
      </div>
    );
  }

  if (items.length === 0) {
    return <p>장바구니가 비어있습니다.</p>;
  }

  return (
    <section aria-label="장바구니">
      <h2>장바구니</h2>
      <ul role="list" aria-label="장바구니 항목">
        {items.map((item) => (
          <li key={item.id} aria-label={item.name}>
            <div>
              <img src={item.imageUrl} alt={item.name} />
              <strong>{item.name}</strong>
              <span>{item.price.toLocaleString()}원</span>
            </div>
            <div>
              <button
                onClick={() => updateQuantity(item.id, item.quantity - 1)}
                aria-label={`${item.name} 수량 감소`}
                disabled={item.quantity <= 1}
              >
                -
              </button>
              <span aria-label={`${item.name} 수량`}>{item.quantity}</span>
              <button
                onClick={() => updateQuantity(item.id, item.quantity + 1)}
                aria-label={`${item.name} 수량 증가`}
              >
                +
              </button>
            </div>
            <span aria-label={`${item.name} 소계`}>
              {(item.price * item.quantity).toLocaleString()}원
            </span>
            <button
              onClick={() => removeItem(item.id)}
              aria-label={`${item.name} 삭제`}
            >
              삭제
            </button>
          </li>
        ))}
      </ul>
      <div aria-label="총 금액">
        <strong>총 금액: {totalPrice.toLocaleString()}원</strong>
      </div>
    </section>
  );
}

/**
 * 문제 1 테스트 코드:
 *
 * ```tsx
 * // ShoppingCart.test.tsx
 * import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
 * import { render, screen, within, waitFor } from '@testing-library/react';
 * import userEvent from '@testing-library/user-event';
 * import '@testing-library/jest-dom';
 * import { http, HttpResponse } from 'msw';
 * import { setupServer } from 'msw/node';
 * import { ShoppingCart } from './solution';
 *
 * const mockCartItems: CartItem[] = [
 *   { id: 1, name: 'React 입문서', price: 25000, quantity: 1, imageUrl: '/book1.jpg' },
 *   { id: 2, name: 'TypeScript 핸드북', price: 32000, quantity: 2, imageUrl: '/book2.jpg' },
 * ];
 *
 * const handlers = [
 *   http.get('/api/cart', () => {
 *     return HttpResponse.json(mockCartItems);
 *   }),
 *   http.patch('/api/cart/:id', async ({ params, request }) => {
 *     const { quantity } = await request.json() as { quantity: number };
 *     const item = mockCartItems.find(i => i.id === Number(params.id));
 *     if (!item) return new HttpResponse(null, { status: 404 });
 *     return HttpResponse.json({ ...item, quantity });
 *   }),
 *   http.delete('/api/cart/:id', ({ params }) => {
 *     const index = mockCartItems.findIndex(i => i.id === Number(params.id));
 *     if (index === -1) return new HttpResponse(null, { status: 404 });
 *     return HttpResponse.json({ success: true });
 *   }),
 * ];
 *
 * const server = setupServer(...handlers);
 *
 * beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
 * afterEach(() => server.resetHandlers());
 * afterAll(() => server.close());
 *
 * describe('ShoppingCart 통합 테스트', () => {
 *
 *   it('장바구니 항목을 올바르게 표시한다', async () => {
 *     render(<ShoppingCart />);
 *
 *     // 로딩 상태 확인
 *     expect(screen.getByRole('status')).toHaveTextContent('장바구니를 불러오는 중...');
 *
 *     // 데이터 로드 대기
 *     const list = await screen.findByRole('list', { name: '장바구니 항목' });
 *     const items = within(list).getAllByRole('listitem');
 *     expect(items).toHaveLength(2);
 *
 *     expect(screen.getByText('React 입문서')).toBeInTheDocument();
 *     expect(screen.getByText('TypeScript 핸드북')).toBeInTheDocument();
 *   });
 *
 *   it('수량 증가 시 총 금액이 업데이트된다', async () => {
 *     const user = userEvent.setup();
 *     render(<ShoppingCart />);
 *
 *     await screen.findByRole('list', { name: '장바구니 항목' });
 *
 *     // React 입문서 수량 증가
 *     const increaseButton = screen.getByRole('button', { name: 'React 입문서 수량 증가' });
 *     await user.click(increaseButton);
 *
 *     // 총 금액 확인: 25000*2 + 32000*2 = 114000
 *     await waitFor(() => {
 *       expect(screen.getByLabelText('총 금액')).toHaveTextContent('114,000원');
 *     });
 *   });
 *
 *   it('항목 삭제 후 목록에서 제거된다', async () => {
 *     const user = userEvent.setup();
 *     render(<ShoppingCart />);
 *
 *     await screen.findByRole('list', { name: '장바구니 항목' });
 *
 *     const deleteButton = screen.getByRole('button', { name: 'React 입문서 삭제' });
 *     await user.click(deleteButton);
 *
 *     await waitFor(() => {
 *       expect(screen.queryByText('React 입문서')).not.toBeInTheDocument();
 *     });
 *
 *     const items = screen.getAllByRole('listitem');
 *     expect(items).toHaveLength(1);
 *   });
 *
 *   it('API 오류 시 에러 메시지와 재시도 버튼을 표시한다', async () => {
 *     server.use(
 *       http.get('/api/cart', () => {
 *         return new HttpResponse(null, { status: 500 });
 *       })
 *     );
 *
 *     render(<ShoppingCart />);
 *
 *     const alert = await screen.findByRole('alert');
 *     expect(alert).toHaveTextContent('장바구니를 불러오지 못했습니다');
 *
 *     expect(screen.getByRole('button', { name: '다시 시도' })).toBeInTheDocument();
 *   });
 * });
 * ```
 */

// ============================================================
// 문제 2 답안: useInfiniteScroll 커스텀 훅
// ============================================================

interface InfiniteScrollOptions {
  /** API 엔드포인트 */
  url: string;
  /** 페이지당 항목 수 */
  pageSize: number;
}

interface InfiniteScrollState<T> {
  items: T[];
  loading: boolean;
  error: Error | null;
  hasMore: boolean;
  loadMore: () => void;
  /** Intersection Observer에 연결할 ref */
  sentinelRef: React.RefObject<HTMLDivElement | null>;
}

export function useInfiniteScroll<T>({
  url,
  pageSize,
}: InfiniteScrollOptions): InfiniteScrollState<T> {
  const [items, setItems] = useState<T[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  const loadingRef = useRef(false);

  const fetchPage = useCallback(
    async (pageNum: number) => {
      // 중복 요청 방지
      if (loadingRef.current) return;
      loadingRef.current = true;
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${url}?page=${pageNum}&limit=${pageSize}`
        );
        if (!response.ok) throw new Error('데이터를 불러오지 못했습니다.');
        const data = await response.json();
        const newItems: T[] = data.items;

        setItems((prev) => [...prev, ...newItems]);
        setHasMore(newItems.length === pageSize);
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setLoading(false);
        loadingRef.current = false;
      }
    },
    [url, pageSize]
  );

  // 초기 로딩
  useEffect(() => {
    fetchPage(1);
  }, [fetchPage]);

  // Intersection Observer 설정
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loadingRef.current) {
          setPage((prev) => {
            const nextPage = prev + 1;
            fetchPage(nextPage);
            return nextPage;
          });
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(sentinel);
    return () => observer.unobserve(sentinel);
  }, [hasMore, fetchPage]);

  const loadMore = useCallback(() => {
    if (hasMore && !loadingRef.current) {
      setPage((prev) => {
        const nextPage = prev + 1;
        fetchPage(nextPage);
        return nextPage;
      });
    }
  }, [hasMore, fetchPage]);

  return { items, loading, error, hasMore, loadMore, sentinelRef };
}

/**
 * 문제 2 테스트 코드:
 *
 * ```tsx
 * // useInfiniteScroll.test.tsx
 * import { describe, it, expect, vi, beforeAll, afterAll, afterEach } from 'vitest';
 * import { renderHook, act, waitFor } from '@testing-library/react';
 * import { http, HttpResponse } from 'msw';
 * import { setupServer } from 'msw/node';
 * import { useInfiniteScroll } from './solution';
 *
 * // IntersectionObserver 모킹
 * let observerCallback: IntersectionObserverCallback;
 * const mockObserve = vi.fn();
 * const mockUnobserve = vi.fn();
 * const mockDisconnect = vi.fn();
 *
 * beforeEach(() => {
 *   global.IntersectionObserver = vi.fn((callback) => {
 *     observerCallback = callback;
 *     return {
 *       observe: mockObserve,
 *       unobserve: mockUnobserve,
 *       disconnect: mockDisconnect,
 *     };
 *   }) as any;
 * });
 *
 * // 페이지네이션 데이터 생성
 * function generateItems(page: number, limit: number) {
 *   const start = (page - 1) * limit;
 *   const totalItems = 25; // 총 25개 항목
 *   const remaining = Math.max(0, totalItems - start);
 *   const count = Math.min(limit, remaining);
 *
 *   return {
 *     items: Array.from({ length: count }, (_, i) => ({
 *       id: start + i + 1,
 *       title: `항목 ${start + i + 1}`,
 *     })),
 *   };
 * }
 *
 * const server = setupServer(
 *   http.get('/api/items', ({ request }) => {
 *     const url = new URL(request.url);
 *     const page = Number(url.searchParams.get('page')) || 1;
 *     const limit = Number(url.searchParams.get('limit')) || 10;
 *     return HttpResponse.json(generateItems(page, limit));
 *   })
 * );
 *
 * beforeAll(() => server.listen());
 * afterEach(() => server.resetHandlers());
 * afterAll(() => server.close());
 *
 * describe('useInfiniteScroll', () => {
 *
 *   it('초기 데이터를 성공적으로 로드한다', async () => {
 *     const { result } = renderHook(() =>
 *       useInfiniteScroll({ url: '/api/items', pageSize: 10 })
 *     );
 *
 *     await waitFor(() => {
 *       expect(result.current.loading).toBe(false);
 *     });
 *
 *     expect(result.current.items).toHaveLength(10);
 *     expect(result.current.hasMore).toBe(true);
 *     expect(result.current.error).toBeNull();
 *   });
 *
 *   it('스크롤 시 다음 페이지를 자동으로 로드한다', async () => {
 *     const { result } = renderHook(() =>
 *       useInfiniteScroll({ url: '/api/items', pageSize: 10 })
 *     );
 *
 *     await waitFor(() => expect(result.current.items).toHaveLength(10));
 *
 *     // Intersection Observer 트리거
 *     act(() => {
 *       observerCallback(
 *         [{ isIntersecting: true }] as IntersectionObserverEntry[],
 *         {} as IntersectionObserver
 *       );
 *     });
 *
 *     await waitFor(() => {
 *       expect(result.current.items).toHaveLength(20);
 *     });
 *   });
 *
 *   it('마지막 페이지에 도달하면 hasMore가 false가 된다', async () => {
 *     const { result } = renderHook(() =>
 *       useInfiniteScroll({ url: '/api/items', pageSize: 10 })
 *     );
 *
 *     // 페이지 1 (10개) + 페이지 2 (10개) + 페이지 3 (5개)
 *     await waitFor(() => expect(result.current.items).toHaveLength(10));
 *
 *     act(() => {
 *       observerCallback([{ isIntersecting: true }] as any, {} as any);
 *     });
 *     await waitFor(() => expect(result.current.items).toHaveLength(20));
 *
 *     act(() => {
 *       observerCallback([{ isIntersecting: true }] as any, {} as any);
 *     });
 *     await waitFor(() => {
 *       expect(result.current.items).toHaveLength(25);
 *       expect(result.current.hasMore).toBe(false);
 *     });
 *   });
 *
 *   it('에러 발생 시 error 상태를 설정한다', async () => {
 *     server.use(
 *       http.get('/api/items', () => new HttpResponse(null, { status: 500 }))
 *     );
 *
 *     const { result } = renderHook(() =>
 *       useInfiniteScroll({ url: '/api/items', pageSize: 10 })
 *     );
 *
 *     await waitFor(() => {
 *       expect(result.current.error).not.toBeNull();
 *       expect(result.current.error?.message).toBe('데이터를 불러오지 못했습니다.');
 *     });
 *   });
 * });
 * ```
 */

// ============================================================
// 문제 3 답안: 접근성 준수 회원가입 폼
// ============================================================

interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

interface ValidationErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
}

/** 비밀번호 강도 계산 (0~4) */
function calculatePasswordStrength(password: string): number {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;
  return strength;
}

function getStrengthLabel(strength: number): string {
  const labels = ['매우 약함', '약함', '보통', '강함', '매우 강함'];
  return labels[strength];
}

/** 유효성 검사 */
function validate(data: SignupFormData): ValidationErrors {
  const errors: ValidationErrors = {};

  if (!data.email) {
    errors.email = '이메일을 입력해주세요.';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.email = '올바른 이메일 형식이 아닙니다.';
  }

  if (!data.password) {
    errors.password = '비밀번호를 입력해주세요.';
  } else if (data.password.length < 8) {
    errors.password = '비밀번호는 8자 이상이어야 합니다.';
  }

  if (data.password !== data.confirmPassword) {
    errors.confirmPassword = '비밀번호가 일치하지 않습니다.';
  }

  return errors;
}

export function SignupForm({
  onSubmit,
}: {
  onSubmit?: (data: SignupFormData) => Promise<void>;
}) {
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [toast, setToast] = useState<{
    message: string;
    type: 'success' | 'error';
  } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const passwordStrength = calculatePasswordStrength(formData.password);

  // 필드 변경 핸들러
  const handleChange = (field: keyof SignupFormData, value: string) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);

    // 터치된 필드만 실시간 검증
    if (touched[field]) {
      const newErrors = validate(newData);
      setErrors((prev) => ({
        ...prev,
        [field]: newErrors[field],
      }));
    }
  };

  // 필드 블러 핸들러
  const handleBlur = (field: keyof SignupFormData) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const newErrors = validate(formData);
    setErrors((prev) => ({
      ...prev,
      [field]: newErrors[field],
    }));
  };

  // 폼 제출 핸들러
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 모든 필드 터치 처리
    setTouched({ email: true, password: true, confirmPassword: true });

    const validationErrors = validate(formData);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) return;

    setSubmitting(true);
    try {
      await onSubmit?.(formData);
      setToast({ message: '회원가입이 완료되었습니다!', type: 'success' });
      setFormData({ email: '', password: '', confirmPassword: '' });
      setTouched({});
    } catch {
      setToast({ message: '회원가입에 실패했습니다.', type: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  // 토스트 닫기 (Escape 키 지원)
  const handleToastClose = () => setToast(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && toast) {
        handleToastClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toast]);

  return (
    <div>
      {/* 토스트 알림 */}
      {toast && (
        <div
          role="alert"
          aria-live="assertive"
          className={`toast toast-${toast.type}`}
        >
          <span>{toast.message}</span>
          <button
            onClick={handleToastClose}
            aria-label="알림 닫기"
            type="button"
          >
            닫기
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate aria-label="회원가입">
        <h2>회원가입</h2>

        {/* 이메일 필드 */}
        <div>
          <label htmlFor="signup-email">이메일</label>
          <input
            id="signup-email"
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            onBlur={() => handleBlur('email')}
            aria-invalid={touched.email && !!errors.email}
            aria-errormessage={errors.email ? 'email-error' : undefined}
            aria-required="true"
            autoComplete="email"
          />
          {touched.email && errors.email && (
            <div id="email-error" role="alert" aria-live="polite">
              {errors.email}
            </div>
          )}
        </div>

        {/* 비밀번호 필드 */}
        <div>
          <label htmlFor="signup-password">비밀번호</label>
          <input
            id="signup-password"
            type="password"
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            onBlur={() => handleBlur('password')}
            aria-invalid={touched.password && !!errors.password}
            aria-errormessage={errors.password ? 'password-error' : undefined}
            aria-required="true"
            autoComplete="new-password"
          />
          {touched.password && errors.password && (
            <div id="password-error" role="alert" aria-live="polite">
              {errors.password}
            </div>
          )}

          {/* 비밀번호 강도 표시기 */}
          {formData.password && (
            <div
              role="meter"
              aria-label="비밀번호 강도"
              aria-valuenow={passwordStrength}
              aria-valuemin={0}
              aria-valuemax={4}
              aria-valuetext={getStrengthLabel(passwordStrength)}
            >
              <div
                className="strength-bar"
                style={{ width: `${(passwordStrength / 4) * 100}%` }}
              />
              <span>{getStrengthLabel(passwordStrength)}</span>
            </div>
          )}
        </div>

        {/* 비밀번호 확인 필드 */}
        <div>
          <label htmlFor="signup-confirm-password">비밀번호 확인</label>
          <input
            id="signup-confirm-password"
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            onBlur={() => handleBlur('confirmPassword')}
            aria-invalid={
              touched.confirmPassword && !!errors.confirmPassword
            }
            aria-errormessage={
              errors.confirmPassword ? 'confirm-password-error' : undefined
            }
            aria-required="true"
            autoComplete="new-password"
          />
          {touched.confirmPassword && errors.confirmPassword && (
            <div id="confirm-password-error" role="alert" aria-live="polite">
              {errors.confirmPassword}
            </div>
          )}
        </div>

        {/* 제출 버튼 */}
        <button type="submit" disabled={submitting}>
          {submitting ? '처리 중...' : '가입하기'}
        </button>
      </form>
    </div>
  );
}

/**
 * 문제 3 테스트 코드:
 *
 * ```tsx
 * // SignupForm.test.tsx
 * import { describe, it, expect, vi } from 'vitest';
 * import { render, screen, waitFor } from '@testing-library/react';
 * import userEvent from '@testing-library/user-event';
 * import '@testing-library/jest-dom';
 * import { axe, toHaveNoViolations } from 'vitest-axe';
 * import { SignupForm } from './solution';
 *
 * expect.extend(toHaveNoViolations);
 *
 * describe('SignupForm 접근성 테스트', () => {
 *
 *   // === 접근성 자동 검사 ===
 *
 *   it('초기 렌더링 시 접근성 위반이 없다', async () => {
 *     const { container } = render(<SignupForm />);
 *     const results = await axe(container);
 *     expect(results).toHaveNoViolations();
 *   });
 *
 *   it('유효성 검사 에러 상태에서 접근성 위반이 없다', async () => {
 *     const user = userEvent.setup();
 *     const { container } = render(<SignupForm />);
 *
 *     // 빈 상태로 제출 시도
 *     await user.click(screen.getByRole('button', { name: '가입하기' }));
 *
 *     const results = await axe(container);
 *     expect(results).toHaveNoViolations();
 *   });
 *
 *   it('성공적인 제출 후 접근성 위반이 없다', async () => {
 *     const mockSubmit = vi.fn().mockResolvedValue(undefined);
 *     const user = userEvent.setup();
 *     const { container } = render(<SignupForm onSubmit={mockSubmit} />);
 *
 *     await user.type(screen.getByLabelText('이메일'), 'test@example.com');
 *     await user.type(screen.getByLabelText('비밀번호'), 'StrongPass1!');
 *     await user.type(screen.getByLabelText('비밀번호 확인'), 'StrongPass1!');
 *     await user.click(screen.getByRole('button', { name: '가입하기' }));
 *
 *     await screen.findByRole('alert');
 *     const results = await axe(container);
 *     expect(results).toHaveNoViolations();
 *   });
 *
 *   // === 키보드 네비게이션 ===
 *
 *   it('Tab으로 모든 폼 필드를 탐색할 수 있다', async () => {
 *     const user = userEvent.setup();
 *     render(<SignupForm />);
 *
 *     // 이메일 -> 비밀번호 -> 비밀번호 확인 -> 버튼 순서
 *     await user.tab();
 *     expect(screen.getByLabelText('이메일')).toHaveFocus();
 *
 *     await user.tab();
 *     expect(screen.getByLabelText('비밀번호')).toHaveFocus();
 *
 *     await user.tab();
 *     expect(screen.getByLabelText('비밀번호 확인')).toHaveFocus();
 *
 *     await user.tab();
 *     expect(screen.getByRole('button', { name: '가입하기' })).toHaveFocus();
 *   });
 *
 *   it('Enter로 폼을 제출할 수 있다', async () => {
 *     const mockSubmit = vi.fn().mockResolvedValue(undefined);
 *     const user = userEvent.setup();
 *     render(<SignupForm onSubmit={mockSubmit} />);
 *
 *     await user.type(screen.getByLabelText('이메일'), 'test@example.com');
 *     await user.type(screen.getByLabelText('비밀번호'), 'StrongPass1!');
 *     await user.type(screen.getByLabelText('비밀번호 확인'), 'StrongPass1!');
 *     await user.keyboard('{Enter}');
 *
 *     await waitFor(() => {
 *       expect(mockSubmit).toHaveBeenCalledWith({
 *         email: 'test@example.com',
 *         password: 'StrongPass1!',
 *         confirmPassword: 'StrongPass1!',
 *       });
 *     });
 *   });
 *
 *   it('Escape로 토스트 알림을 닫을 수 있다', async () => {
 *     const mockSubmit = vi.fn().mockResolvedValue(undefined);
 *     const user = userEvent.setup();
 *     render(<SignupForm onSubmit={mockSubmit} />);
 *
 *     await user.type(screen.getByLabelText('이메일'), 'test@example.com');
 *     await user.type(screen.getByLabelText('비밀번호'), 'StrongPass1!');
 *     await user.type(screen.getByLabelText('비밀번호 확인'), 'StrongPass1!');
 *     await user.click(screen.getByRole('button', { name: '가입하기' }));
 *
 *     // 토스트 표시 확인
 *     const toast = await screen.findByRole('alert');
 *     expect(toast).toHaveTextContent('회원가입이 완료되었습니다!');
 *
 *     // Escape로 닫기
 *     await user.keyboard('{Escape}');
 *     expect(screen.queryByRole('alert')).not.toBeInTheDocument();
 *   });
 *
 *   // === ARIA 속성 검증 ===
 *
 *   it('에러 시 aria-invalid와 aria-errormessage가 올바르게 설정된다', async () => {
 *     const user = userEvent.setup();
 *     render(<SignupForm />);
 *
 *     const emailInput = screen.getByLabelText('이메일');
 *
 *     // 잘못된 이메일 입력 후 블러
 *     await user.type(emailInput, 'invalid');
 *     await user.tab();
 *
 *     // aria-invalid 확인
 *     expect(emailInput).toHaveAttribute('aria-invalid', 'true');
 *     expect(emailInput).toHaveAttribute('aria-errormessage', 'email-error');
 *
 *     // 에러 메시지 확인
 *     const errorMessage = screen.getByText('올바른 이메일 형식이 아닙니다.');
 *     expect(errorMessage).toHaveAttribute('role', 'alert');
 *   });
 *
 *   it('비밀번호 강도 표시기에 올바른 ARIA 속성이 있다', async () => {
 *     const user = userEvent.setup();
 *     render(<SignupForm />);
 *
 *     await user.type(screen.getByLabelText('비밀번호'), 'StrongPass1!');
 *
 *     const meter = screen.getByRole('meter', { name: '비밀번호 강도' });
 *     expect(meter).toHaveAttribute('aria-valuenow', '4');
 *     expect(meter).toHaveAttribute('aria-valuemin', '0');
 *     expect(meter).toHaveAttribute('aria-valuemax', '4');
 *     expect(meter).toHaveAttribute('aria-valuetext', '매우 강함');
 *   });
 * });
 * ```
 */

export default SignupForm;
