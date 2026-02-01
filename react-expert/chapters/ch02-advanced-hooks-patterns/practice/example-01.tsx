/**
 * 챕터 02 - 예제 1: 고급 커스텀 Hook 라이브러리
 *
 * 여러 기본 Hook을 합성하여 실용적인 커스텀 Hook을 구현합니다.
 * 각 Hook은 단일 책임 원칙을 따르며, 상위 Hook에서 조합하여 사용합니다.
 *
 * 실행 방법:
 *   npx tsx practice/example-01.tsx
 *   (Node.js 환경에서는 React 시뮬레이션으로 로직만 검증합니다)
 *
 * 브라우저 환경에서 사용하려면:
 *   - React 프로젝트에 아래 Hook들을 복사하여 사용하세요.
 */

import {
  useState,
  useEffect,
  useCallback,
  useRef,
  useReducer,
  useMemo,
} from "react";

// ============================================================
// 1단계: 유틸리티 Hooks
// ============================================================

/**
 * useDebounce - 값의 변경을 지연시킵니다.
 *
 * 검색 입력 등에서 사용자가 타이핑을 멈출 때까지 기다린 후
 * API 호출을 수행하는 데 유용합니다.
 *
 * @param value - 디바운스할 값
 * @param delay - 지연 시간 (밀리초)
 * @returns 디바운스된 값
 */
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // 값이 변경되면 이전 타이머를 취소
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * usePrevious - 이전 렌더링의 값을 기억합니다.
 *
 * 현재 값과 이전 값을 비교해야 할 때 유용합니다.
 * ref를 사용하므로 리렌더링을 유발하지 않습니다.
 *
 * @param value - 추적할 값
 * @returns 이전 렌더링에서의 값 (첫 렌더링에서는 undefined)
 */
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T | undefined>(undefined);

  useEffect(() => {
    ref.current = value;
  });

  return ref.current;
}

/**
 * useLocalStorage - localStorage와 동기화되는 상태를 관리합니다.
 *
 * useState처럼 사용하되, 값이 localStorage에 자동으로 저장되고
 * 페이지 새로고침 후에도 값이 유지됩니다.
 *
 * @param key - localStorage 키
 * @param initialValue - 초기값 (localStorage에 값이 없을 때)
 * @returns [value, setValue] 튜플
 */
function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // 초기값은 lazy initialization으로 한 번만 계산
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  // 값이 변경될 때 localStorage에 저장
  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      setStoredValue((prev) => {
        const nextValue =
          typeof value === "function" ? (value as (prev: T) => T)(prev) : value;
        if (typeof window !== "undefined") {
          window.localStorage.setItem(key, JSON.stringify(nextValue));
        }
        return nextValue;
      });
    },
    [key]
  );

  return [storedValue, setValue];
}

/**
 * useAsync - 비동기 함수의 상태를 관리합니다.
 *
 * loading, data, error 상태를 자동으로 추적하며,
 * 의존성 변경 시 자동으로 재실행합니다.
 *
 * @param asyncFn - 실행할 비동기 함수
 * @param deps - 의존성 배열
 * @returns { data, loading, error, retry }
 */
interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

type AsyncAction<T> =
  | { type: "LOADING" }
  | { type: "SUCCESS"; data: T }
  | { type: "ERROR"; error: Error };

function asyncReducer<T>(
  state: AsyncState<T>,
  action: AsyncAction<T>
): AsyncState<T> {
  switch (action.type) {
    case "LOADING":
      return { ...state, loading: true, error: null };
    case "SUCCESS":
      return { data: action.data, loading: false, error: null };
    case "ERROR":
      return { ...state, loading: false, error: action.error };
  }
}

function useAsync<T>(
  asyncFn: () => Promise<T>,
  deps: readonly any[] = []
): AsyncState<T> & { retry: () => void } {
  const [state, dispatch] = useReducer(asyncReducer<T>, {
    data: null,
    loading: true,
    error: null,
  });

  const execute = useCallback(() => {
    dispatch({ type: "LOADING" });
    asyncFn()
      .then((data) => dispatch({ type: "SUCCESS", data }))
      .catch((error) =>
        dispatch({ type: "ERROR", error: error instanceof Error ? error : new Error(String(error)) })
      );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    execute();
  }, [execute]);

  return { ...(state as AsyncState<T>), retry: execute };
}

/**
 * useMediaQuery - CSS 미디어 쿼리 상태를 반응형으로 추적합니다.
 *
 * @param query - CSS 미디어 쿼리 문자열
 * @returns 미디어 쿼리 매칭 여부
 */
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    if (typeof window === "undefined") return;

    const mediaQuery = window.matchMedia(query);
    const handler = (event: MediaQueryListEvent) => setMatches(event.matches);

    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

// ============================================================
// 2단계: 도메인 Hooks (1단계를 합성)
// ============================================================

/**
 * useFormField - 폼 필드 하나의 상태를 관리합니다.
 *
 * 값, 유효성 검사, 터치 상태, 에러 메시지를 종합적으로 관리합니다.
 * useReducer를 사용하여 복잡한 상태 전이를 처리합니다.
 */
interface FormFieldState<T> {
  value: T;
  error: string | null;
  touched: boolean;
  dirty: boolean;
}

type FormFieldAction<T> =
  | { type: "CHANGE"; value: T }
  | { type: "BLUR" }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "RESET"; initialValue: T };

function formFieldReducer<T>(
  state: FormFieldState<T>,
  action: FormFieldAction<T>
): FormFieldState<T> {
  switch (action.type) {
    case "CHANGE":
      return { ...state, value: action.value, dirty: true };
    case "BLUR":
      return { ...state, touched: true };
    case "SET_ERROR":
      return { ...state, error: action.error };
    case "RESET":
      return {
        value: action.initialValue,
        error: null,
        touched: false,
        dirty: false,
      };
  }
}

interface UseFormFieldOptions<T> {
  initialValue: T;
  validate?: (value: T) => string | null;
}

function useFormField<T>({ initialValue, validate }: UseFormFieldOptions<T>) {
  const [state, dispatch] = useReducer(formFieldReducer<T>, {
    value: initialValue,
    error: null,
    touched: false,
    dirty: false,
  });

  // 이전 값 추적 (변경 감지용)
  const prevValue = usePrevious(state.value);

  // 값 변경 시 유효성 검사
  useEffect(() => {
    if (prevValue !== undefined && prevValue !== state.value && validate) {
      const error = validate(state.value);
      dispatch({ type: "SET_ERROR", error });
    }
  }, [state.value, prevValue, validate]);

  const handlers = useMemo(
    () => ({
      onChange: (value: T) => dispatch({ type: "CHANGE", value }),
      onBlur: () => {
        dispatch({ type: "BLUR" });
        if (validate) {
          const error = validate(state.value);
          dispatch({ type: "SET_ERROR", error });
        }
      },
      reset: () => dispatch({ type: "RESET", initialValue }),
    }),
    [initialValue, validate, state.value]
  );

  return {
    ...state,
    ...handlers,
    isValid: state.error === null,
    showError: state.touched && state.error !== null,
  };
}

// ============================================================
// 3단계: 기능 Hooks (2단계를 합성)
// ============================================================

/**
 * useSearchForm - 검색 폼의 전체 로직을 관리합니다.
 *
 * 디바운스, 비동기 검색, 검색 이력, 폼 필드 상태를 합성합니다.
 * 이것이 Hook 합성의 최종 형태입니다.
 */
interface SearchResult<T> {
  query: string;
  results: T[];
  loading: boolean;
  error: Error | null;
  history: string[];
  handleSearch: (query: string) => void;
  clearHistory: () => void;
}

function useSearchForm<T>(
  searchFn: (query: string) => Promise<T[]>,
  options: { debounceMs?: number; maxHistory?: number } = {}
): SearchResult<T> {
  const { debounceMs = 300, maxHistory = 10 } = options;

  // 1단계 Hook: 검색어 입력 필드
  const queryField = useFormField({
    initialValue: "",
    validate: (v: string) => (v.length > 100 ? "검색어가 너무 깁니다" : null),
  });

  // 1단계 Hook: 디바운스
  const debouncedQuery = useDebounce(queryField.value, debounceMs);

  // 1단계 Hook: 검색 이력 (localStorage)
  const [history, setHistory] = useLocalStorage<string[]>("search-history", []);

  // 1단계 Hook: 비동기 검색 실행
  const { data, loading, error } = useAsync(
    () => (debouncedQuery ? searchFn(debouncedQuery) : Promise.resolve([])),
    [debouncedQuery]
  );

  // 검색 실행 시 이력에 추가
  useEffect(() => {
    if (debouncedQuery && !loading && data) {
      setHistory((prev) => {
        const updated = [
          debouncedQuery,
          ...prev.filter((q) => q !== debouncedQuery),
        ];
        return updated.slice(0, maxHistory);
      });
    }
  }, [debouncedQuery, loading, data, setHistory, maxHistory]);

  return {
    query: queryField.value,
    results: (data as T[]) ?? [],
    loading,
    error,
    history,
    handleSearch: queryField.onChange,
    clearHistory: () => setHistory([]),
  };
}

// ============================================================
// Node.js 환경에서의 데모 (로직 검증용)
// ============================================================

console.log("╔══════════════════════════════════════════╗");
console.log("║ 고급 커스텀 Hook 라이브러리 구조         ║");
console.log("╚══════════════════════════════════════════╝\n");

console.log("=== Hook 합성 계층 ===\n");
console.log("3단계: useSearchForm (기능 Hook)");
console.log("  ├── useFormField (도메인 Hook)");
console.log("  │     ├── useReducer (기본)");
console.log("  │     ├── usePrevious (유틸리티)");
console.log("  │     │     └── useRef + useEffect (기본)");
console.log("  │     └── useMemo (기본)");
console.log("  ├── useDebounce (유틸리티)");
console.log("  │     └── useState + useEffect (기본)");
console.log("  ├── useLocalStorage (유틸리티)");
console.log("  │     └── useState + useCallback (기본)");
console.log("  └── useAsync (유틸리티)");
console.log("        └── useReducer + useCallback + useEffect (기본)");

console.log("\n=== useReducer 상태 전이 시뮬레이션 ===\n");

// useReducer의 상태 전이를 직접 시뮬레이션
type DemoAction =
  | { type: "CHANGE"; value: string }
  | { type: "BLUR" }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "RESET"; initialValue: string };

const demoReducer = formFieldReducer<string>;

let state: FormFieldState<string> = {
  value: "",
  error: null,
  touched: false,
  dirty: false,
};

console.log("초기 상태:", JSON.stringify(state));

const actions: DemoAction[] = [
  { type: "CHANGE", value: "he" },
  { type: "CHANGE", value: "hello" },
  { type: "BLUR" },
  { type: "SET_ERROR", error: null },
  { type: "CHANGE", value: "" },
  { type: "SET_ERROR", error: "필수 입력 항목입니다" },
  { type: "RESET", initialValue: "" },
];

actions.forEach((action) => {
  state = demoReducer(state, action);
  console.log(`dispatch(${JSON.stringify(action)})`);
  console.log(`  → 상태: value="${state.value}", error=${state.error}, touched=${state.touched}, dirty=${state.dirty}`);
});

console.log("\n=== useAsync 상태 전이 시뮬레이션 ===\n");

let asyncState: AsyncState<string[]> = {
  data: null,
  loading: false,
  error: null,
};

const asyncActions: AsyncAction<string[]>[] = [
  { type: "LOADING" },
  { type: "SUCCESS", data: ["결과1", "결과2", "결과3"] },
  { type: "LOADING" },
  { type: "ERROR", error: new Error("네트워크 오류") },
];

asyncActions.forEach((action) => {
  asyncState = asyncReducer(asyncState, action);
  console.log(`dispatch({ type: "${action.type}" })`);
  console.log(`  → loading=${asyncState.loading}, data=${JSON.stringify(asyncState.data)}, error=${asyncState.error?.message ?? "null"}`);
});

console.log("\n✅ Hook 라이브러리 구조 확인 완료!");

export {
  useDebounce,
  usePrevious,
  useLocalStorage,
  useAsync,
  useMediaQuery,
  useFormField,
  useSearchForm,
};
