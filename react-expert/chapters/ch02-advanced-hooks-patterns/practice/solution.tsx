/**
 * 챕터 02 - 연습 문제 모범 답안
 *
 * 실행 방법:
 *   npx tsx practice/solution.tsx
 *
 * 브라우저 환경이 필요한 Hook(문제 2, 3)은 React 프로젝트에서 테스트하세요.
 * 여기서는 핵심 로직의 구조와 타입을 보여줍니다.
 */

import React, {
  useReducer,
  useCallback,
  useRef,
  useEffect,
  useSyncExternalStore,
} from "react";

// ============================================================
// 문제 1: 상태 머신 기반 useReducer
// ============================================================

/**
 * 상태 머신 설정 타입
 */
interface StateMachineConfig<S extends string, E extends string> {
  initial: S;
  states: Record<
    S,
    {
      on: Partial<
        Record<
          E,
          {
            target: S;
            action?: (context: any) => any;
          }
        >
      >;
    }
  >;
}

interface StateMachineState<S extends string> {
  value: S;
  context: Record<string, any>;
}

/**
 * createStateMachine - 상태 머신 설정 객체를 생성합니다.
 * 런타임에서 사용할 설정을 반환합니다.
 */
function createStateMachine<S extends string, E extends string>(
  config: StateMachineConfig<S, E>
): StateMachineConfig<S, E> {
  return config;
}

/**
 * useStateMachine - 상태 머신을 React Hook으로 사용합니다.
 *
 * 핵심: useReducer의 reducer에서 현재 상태의 전이 테이블을 확인하여
 * 허용된 전이만 수행합니다.
 */
function useStateMachine<S extends string, E extends string>(
  machine: StateMachineConfig<S, E>
) {
  type State = StateMachineState<S>;
  type Action = { type: E; payload?: any };

  const reducer = useCallback(
    (state: State, action: Action): State => {
      const currentStateConfig = machine.states[state.value];
      const transition = currentStateConfig.on[action.type];

      // 현재 상태에서 허용되지 않는 이벤트 → 무시
      if (!transition) {
        console.warn(
          `[StateMachine] "${state.value}" 상태에서 "${action.type}" 이벤트는 허용되지 않습니다.`
        );
        return state;
      }

      // 전이 실행
      const nextContext = transition.action
        ? transition.action(state.context)
        : state.context;

      return {
        value: transition.target,
        context: nextContext,
      };
    },
    [machine]
  );

  const [state, dispatch] = useReducer(reducer, {
    value: machine.initial,
    context: {},
  });

  const send = useCallback(
    (event: E, payload?: any) => {
      dispatch({ type: event, payload });
    },
    [dispatch]
  );

  const can = useCallback(
    (event: E): boolean => {
      const currentStateConfig = machine.states[state.value];
      return event in currentStateConfig.on;
    },
    [machine, state.value]
  );

  return {
    state: state.value,
    context: state.context,
    send,
    can,
  };
}

// 테스트
console.log("╔══════════════════════════════════════════╗");
console.log("║ 문제 1: 상태 머신 기반 useReducer        ║");
console.log("╚══════════════════════════════════════════╝\n");

// 상태 머신을 직접 시뮬레이션 (useReducer 없이)
const fetchMachine = createStateMachine({
  initial: "idle" as const,
  states: {
    idle: {
      on: {
        FETCH: { target: "loading" as const },
      },
    },
    loading: {
      on: {
        SUCCESS: { target: "success" as const },
        ERROR: { target: "error" as const },
      },
    },
    success: {
      on: {
        RESET: { target: "idle" as const },
        FETCH: { target: "loading" as const },
      },
    },
    error: {
      on: {
        RETRY: { target: "loading" as const },
        RESET: { target: "idle" as const },
      },
    },
  },
});

// reducer 로직을 직접 테스트
type FetchState = "idle" | "loading" | "success" | "error";
type FetchEvent = "FETCH" | "SUCCESS" | "ERROR" | "RETRY" | "RESET";

function simulateTransition(
  machine: StateMachineConfig<FetchState, FetchEvent>,
  currentState: FetchState,
  event: FetchEvent
): FetchState {
  const stateConfig = machine.states[currentState];
  const transition = stateConfig.on[event];

  if (!transition) {
    console.log(`  ⛔ "${currentState}" 에서 "${event}" → 무시됨`);
    return currentState;
  }

  console.log(`  ✅ "${currentState}" + "${event}" → "${transition.target}"`);
  return transition.target;
}

let currentState: FetchState = fetchMachine.initial;
console.log(`초기 상태: ${currentState}\n`);

// can() 시뮬레이션
const canFetch = "FETCH" in fetchMachine.states[currentState].on;
const canSuccess = "SUCCESS" in fetchMachine.states[currentState].on;
console.log(`can('FETCH'): ${canFetch}`);
console.log(`can('SUCCESS'): ${canSuccess}\n`);

// 전이 테스트
currentState = simulateTransition(fetchMachine, currentState, "FETCH");
currentState = simulateTransition(fetchMachine, currentState, "RESET"); // 무시됨
currentState = simulateTransition(fetchMachine, currentState, "SUCCESS");
currentState = simulateTransition(fetchMachine, currentState, "FETCH");
currentState = simulateTransition(fetchMachine, currentState, "ERROR");
currentState = simulateTransition(fetchMachine, currentState, "RETRY");
currentState = simulateTransition(fetchMachine, currentState, "SUCCESS");
currentState = simulateTransition(fetchMachine, currentState, "RESET");

console.log(`\n최종 상태: ${currentState}`);

// ============================================================
// 문제 2: useSyncExternalStore로 반응형 LocalStorage Hook
// ============================================================

console.log("\n\n╔══════════════════════════════════════════╗");
console.log("║ 문제 2: 반응형 LocalStorage Hook          ║");
console.log("╚══════════════════════════════════════════╝\n");

/**
 * 내부 구독 시스템
 * 같은 탭 내에서의 localStorage 변경을 감지하기 위한 이벤트 버스
 */
const localStorageListeners = new Map<string, Set<() => void>>();

function notifyLocalStorageChange(key: string): void {
  const listeners = localStorageListeners.get(key);
  if (listeners) {
    listeners.forEach((listener) => listener());
  }
}

/**
 * 스냅샷 캐시
 * useSyncExternalStore의 getSnapshot이 안정적인 참조를 반환하도록
 * 파싱된 값을 캐시합니다.
 */
const snapshotCache = new Map<string, { raw: string | null; parsed: any }>();

function getLocalStorageSnapshot<T>(key: string, initialValue: T): T {
  if (typeof window === "undefined") return initialValue;

  const raw = localStorage.getItem(key);
  const cached = snapshotCache.get(key);

  // 캐시된 raw 값과 동일하면 캐시된 parsed 값 반환 (참조 안정성)
  if (cached && cached.raw === raw) {
    return cached.parsed;
  }

  // 새로 파싱
  let parsed: T;
  try {
    parsed = raw !== null ? JSON.parse(raw) : initialValue;
  } catch {
    parsed = initialValue;
  }

  snapshotCache.set(key, { raw, parsed });
  return parsed;
}

/**
 * useSharedLocalStorage - 여러 탭에서 동기화되는 localStorage Hook
 *
 * useSyncExternalStore를 사용하여 구현합니다.
 */
function useSharedLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  // subscribe: localStorage 변경 이벤트 + 내부 이벤트 구독
  const subscribe = useCallback(
    (callback: () => void) => {
      // 같은 탭 내 변경 감지
      if (!localStorageListeners.has(key)) {
        localStorageListeners.set(key, new Set());
      }
      localStorageListeners.get(key)!.add(callback);

      // 다른 탭 변경 감지
      const storageHandler = (event: StorageEvent) => {
        if (event.key === key) {
          // 캐시 무효화
          snapshotCache.delete(key);
          callback();
        }
      };

      window.addEventListener("storage", storageHandler);

      return () => {
        localStorageListeners.get(key)?.delete(callback);
        window.removeEventListener("storage", storageHandler);
      };
    },
    [key]
  );

  // getSnapshot: 현재 localStorage 값 반환
  const getSnapshot = useCallback(
    () => getLocalStorageSnapshot<T>(key, initialValue),
    [key, initialValue]
  );

  // getServerSnapshot: SSR용
  const getServerSnapshot = useCallback(() => initialValue, [initialValue]);

  const value = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  // setValue: 값 설정 후 구독자에게 알림
  const setValue = useCallback(
    (newValue: T | ((prev: T) => T)) => {
      const current = getLocalStorageSnapshot<T>(key, initialValue);
      const resolved =
        typeof newValue === "function"
          ? (newValue as (prev: T) => T)(current)
          : newValue;

      localStorage.setItem(key, JSON.stringify(resolved));
      snapshotCache.delete(key); // 캐시 무효화
      notifyLocalStorageChange(key); // 같은 탭 구독자에게 알림
    },
    [key, initialValue]
  );

  // removeValue: 키 삭제
  const removeValue = useCallback(() => {
    localStorage.removeItem(key);
    snapshotCache.delete(key);
    notifyLocalStorageChange(key);
  }, [key]);

  return [value, setValue, removeValue];
}

// 구조 설명 출력
console.log("useSharedLocalStorage 구조:");
console.log("  subscribe:");
console.log("    ├── window.addEventListener('storage', ...)  // 다른 탭 변경");
console.log("    └── localStorageListeners.add(...)           // 같은 탭 변경");
console.log("  getSnapshot:");
console.log("    └── getLocalStorageSnapshot(key, initial)    // 캐시된 값 반환");
console.log("  setValue:");
console.log("    ├── localStorage.setItem(key, JSON.stringify(value))");
console.log("    ├── snapshotCache.delete(key)                // 캐시 무효화");
console.log("    └── notifyLocalStorageChange(key)            // 구독자 알림");

// ============================================================
// 문제 3: Hook 합성 — useInfiniteScroll
// ============================================================

console.log("\n\n╔══════════════════════════════════════════╗");
console.log("║ 문제 3: useInfiniteScroll                 ║");
console.log("╚══════════════════════════════════════════╝\n");

/**
 * 무한 스크롤 상태 타입
 */
interface InfiniteScrollState<T> {
  items: T[];
  page: number;
  loading: boolean;
  error: Error | null;
  hasMore: boolean;
}

type InfiniteScrollAction<T> =
  | { type: "FETCH_START" }
  | { type: "FETCH_SUCCESS"; data: T[]; hasMore: boolean; nextPage: number }
  | { type: "FETCH_ERROR"; error: Error }
  | { type: "RESET"; initialPage: number };

function infiniteScrollReducer<T>(
  state: InfiniteScrollState<T>,
  action: InfiniteScrollAction<T>
): InfiniteScrollState<T> {
  switch (action.type) {
    case "FETCH_START":
      return { ...state, loading: true, error: null };

    case "FETCH_SUCCESS":
      return {
        ...state,
        items: [...state.items, ...action.data],
        page: action.nextPage,
        loading: false,
        hasMore: action.hasMore,
      };

    case "FETCH_ERROR":
      return { ...state, loading: false, error: action.error };

    case "RESET":
      return {
        items: [],
        page: action.initialPage,
        loading: false,
        error: null,
        hasMore: true,
      };
  }
}

interface UseInfiniteScrollOptions {
  threshold?: number;
  initialPage?: number;
  enabled?: boolean;
}

interface PageResult<T> {
  data: T[];
  hasMore: boolean;
  nextPage: number;
}

interface UseInfiniteScrollResult<T> {
  items: T[];
  loading: boolean;
  error: Error | null;
  hasMore: boolean;
  sentinelRef: React.RefObject<HTMLElement>;
  retry: () => void;
  reset: () => void;
}

/**
 * useInfiniteScroll - 무한 스크롤 Hook
 *
 * 합성 구조:
 * - useReducer: 페이지네이션 상태 (items, page, loading, error, hasMore)
 * - useRef: sentinel 요소 참조 + 중복 요청 방지 lock
 * - useCallback: loadPage 메모이제이션
 * - useEffect + IntersectionObserver: 뷰포트 감지
 * - AbortController: 요청 취소
 */
function useInfiniteScroll<T>(
  fetchPage: (page: number) => Promise<PageResult<T>>,
  options: UseInfiniteScrollOptions = {}
): UseInfiniteScrollResult<T> {
  const { threshold = 200, initialPage = 1, enabled = true } = options;

  // 상태 관리
  const [state, dispatch] = useReducer(infiniteScrollReducer<T>, {
    items: [],
    page: initialPage,
    loading: false,
    error: null,
    hasMore: true,
  });

  // Refs
  const sentinelRef = useRef<HTMLElement>(null);
  const isLoadingRef = useRef(false);       // 중복 요청 방지 lock
  const abortControllerRef = useRef<AbortController | null>(null);

  // 페이지 로딩 함수
  const loadPage = useCallback(
    async (page: number) => {
      // 중복 요청 방지
      if (isLoadingRef.current) return;
      isLoadingRef.current = true;

      // 이전 요청 취소
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      dispatch({ type: "FETCH_START" });

      try {
        const result = await fetchPage(page);

        // 언마운트 후 상태 업데이트 방지
        if (!abortControllerRef.current?.signal.aborted) {
          dispatch({
            type: "FETCH_SUCCESS",
            data: result.data,
            hasMore: result.hasMore,
            nextPage: result.nextPage,
          });
        }
      } catch (err) {
        if (!abortControllerRef.current?.signal.aborted) {
          dispatch({
            type: "FETCH_ERROR",
            error: err instanceof Error ? err : new Error(String(err)),
          });
        }
      } finally {
        isLoadingRef.current = false;
      }
    },
    [fetchPage]
  );

  // IntersectionObserver 설정
  useEffect(() => {
    if (!enabled || !state.hasMore || state.loading) return;

    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting && !isLoadingRef.current) {
          loadPage(state.page);
        }
      },
      {
        rootMargin: `0px 0px ${threshold}px 0px`,
      }
    );

    observer.observe(sentinel);

    return () => {
      observer.disconnect();
    };
  }, [enabled, state.hasMore, state.loading, state.page, loadPage, threshold]);

  // 언마운트 시 정리
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  // retry: 현재 페이지 재시도
  const retry = useCallback(() => {
    isLoadingRef.current = false; // lock 해제
    loadPage(state.page);
  }, [loadPage, state.page]);

  // reset: 초기 상태로 돌아가기
  const reset = useCallback(() => {
    abortControllerRef.current?.abort();
    isLoadingRef.current = false;
    dispatch({ type: "RESET", initialPage });
  }, [initialPage]);

  return {
    items: state.items as T[],
    loading: state.loading,
    error: state.error,
    hasMore: state.hasMore,
    sentinelRef: sentinelRef as React.RefObject<HTMLElement>,
    retry,
    reset,
  };
}

// 구조 설명 출력
console.log("useInfiniteScroll 합성 구조:");
console.log("  useInfiniteScroll");
console.log("  ├── useReducer (상태: items, page, loading, error, hasMore)");
console.log("  │     └── Actions: FETCH_START, FETCH_SUCCESS, FETCH_ERROR, RESET");
console.log("  ├── useRef x3");
console.log("  │     ├── sentinelRef (감시 대상 DOM 요소)");
console.log("  │     ├── isLoadingRef (중복 요청 방지 lock)");
console.log("  │     └── abortControllerRef (요청 취소용)");
console.log("  ├── useCallback: loadPage (페이지 로딩 함수)");
console.log("  │     ├── 중복 요청 방지 (isLoadingRef 확인)");
console.log("  │     ├── 이전 요청 취소 (AbortController)");
console.log("  │     └── dispatch로 상태 업데이트");
console.log("  └── useEffect x2");
console.log("        ├── IntersectionObserver 설정/해제");
console.log("        └── 언마운트 시 AbortController 정리");

console.log("\n\nReducer 상태 전이 시뮬레이션:");
console.log("─".repeat(50));

let scrollState: InfiniteScrollState<string> = {
  items: [],
  page: 1,
  loading: false,
  error: null,
  hasMore: true,
};

const scrollActions: InfiniteScrollAction<string>[] = [
  { type: "FETCH_START" },
  {
    type: "FETCH_SUCCESS",
    data: ["상품 1", "상품 2", "상품 3"],
    hasMore: true,
    nextPage: 2,
  },
  { type: "FETCH_START" },
  {
    type: "FETCH_SUCCESS",
    data: ["상품 4", "상품 5"],
    hasMore: true,
    nextPage: 3,
  },
  { type: "FETCH_START" },
  { type: "FETCH_ERROR", error: new Error("네트워크 오류") },
  // retry
  { type: "FETCH_START" },
  {
    type: "FETCH_SUCCESS",
    data: ["상품 6"],
    hasMore: false,
    nextPage: 4,
  },
];

scrollActions.forEach((action) => {
  scrollState = infiniteScrollReducer(scrollState, action);
  const itemCount = (scrollState.items as string[]).length;
  console.log(`dispatch(${action.type})`);
  console.log(
    `  → items: ${itemCount}개, page: ${scrollState.page}, loading: ${scrollState.loading}, hasMore: ${scrollState.hasMore}, error: ${scrollState.error?.message ?? "null"}`
  );
});

// reset
scrollState = infiniteScrollReducer(scrollState, {
  type: "RESET",
  initialPage: 1,
});
console.log(`dispatch(RESET)`);
console.log(
  `  → items: ${(scrollState.items as string[]).length}개, page: ${scrollState.page}, loading: ${scrollState.loading}, hasMore: ${scrollState.hasMore}`
);

console.log("\n✅ 모든 문제 풀이 완료!");

export {
  createStateMachine,
  useStateMachine,
  useSharedLocalStorage,
  useInfiniteScroll,
  StateMachineConfig,
  UseInfiniteScrollOptions,
  UseInfiniteScrollResult,
};
