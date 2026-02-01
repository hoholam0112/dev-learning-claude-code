/**
 * 챕터 02 - 예제 2: useSyncExternalStore로 외부 저장소 연동
 *
 * useSyncExternalStore를 활용하여 외부 상태 저장소를 구현하고
 * React와 안전하게 연동하는 방법을 보여줍니다.
 *
 * 이 예제에서 구현하는 것:
 * 1. 타입 안전한 외부 저장소 (Store)
 * 2. 선택적 구독 (selector 패턴)
 * 3. 브라우저 API 연동 (온라인 상태, 화면 크기)
 * 4. Undo/Redo를 지원하는 히스토리 저장소
 *
 * 실행 방법:
 *   npx tsx practice/example-02.tsx
 */

import { useSyncExternalStore, useCallback } from "react";

// ============================================================
// 1. 타입 안전한 외부 저장소 구현
// ============================================================

/**
 * createStore - Redux와 유사한 외부 저장소를 생성합니다.
 *
 * useSyncExternalStore와 함께 사용할 수 있도록
 * subscribe, getSnapshot 인터페이스를 제공합니다.
 *
 * 핵심: getSnapshot이 참조 동일성(referential equality)을 보장해야
 * 불필요한 리렌더링을 방지할 수 있습니다.
 */
interface Store<T> {
  getSnapshot: () => T;
  subscribe: (listener: () => void) => () => void;
  setState: (updater: (prev: T) => T) => void;
  getState: () => T;
  destroy: () => void;
}

function createStore<T>(initialState: T): Store<T> {
  let state = initialState;
  const listeners = new Set<() => void>();

  return {
    getSnapshot: () => state,
    getState: () => state,

    subscribe: (listener: () => void) => {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },

    setState: (updater: (prev: T) => T) => {
      const nextState = updater(state);
      // 참조가 같으면 리스너를 호출하지 않음 (최적화)
      if (Object.is(state, nextState)) return;
      state = nextState;
      // 모든 리스너에게 변경 알림
      listeners.forEach((listener) => listener());
    },

    destroy: () => {
      listeners.clear();
    },
  };
}

/**
 * useStore - 외부 저장소의 전체 상태를 구독합니다.
 */
function useStore<T>(store: Store<T>): T {
  return useSyncExternalStore(store.subscribe, store.getSnapshot);
}

/**
 * useStoreSelector - 외부 저장소의 특정 부분만 선택적으로 구독합니다.
 *
 * selector 함수가 반환하는 값이 변경될 때만 리렌더링됩니다.
 * 이는 Redux의 useSelector와 동일한 패턴입니다.
 *
 * 주의: selector가 매번 새 객체를 반환하면 무한 리렌더링 발생!
 *       원시값이나 안정적인 참조를 반환해야 합니다.
 */
function useStoreSelector<T, S>(
  store: Store<T>,
  selector: (state: T) => S
): S {
  const getSnapshot = useCallback(() => selector(store.getState()), [store, selector]);
  return useSyncExternalStore(store.subscribe, getSnapshot);
}

// ============================================================
// 2. Undo/Redo 히스토리 저장소
// ============================================================

interface HistoryState<T> {
  past: T[];
  present: T;
  future: T[];
}

interface HistoryStore<T> extends Store<HistoryState<T>> {
  undo: () => void;
  redo: () => void;
  push: (value: T) => void;
  canUndo: () => boolean;
  canRedo: () => boolean;
}

/**
 * createHistoryStore - Undo/Redo를 지원하는 히스토리 저장소
 *
 * 시간 여행(time travel) 디버깅의 기초가 되는 패턴입니다.
 * 모든 상태 변경을 기록하여 이전/이후 상태로 이동할 수 있습니다.
 */
function createHistoryStore<T>(
  initialValue: T,
  maxHistory: number = 50
): HistoryStore<T> {
  const store = createStore<HistoryState<T>>({
    past: [],
    present: initialValue,
    future: [],
  });

  return {
    ...store,

    push: (value: T) => {
      store.setState((state) => ({
        past: [...state.past.slice(-maxHistory), state.present],
        present: value,
        future: [], // 새 변경 시 future 초기화
      }));
    },

    undo: () => {
      store.setState((state) => {
        if (state.past.length === 0) return state;
        const previous = state.past[state.past.length - 1];
        return {
          past: state.past.slice(0, -1),
          present: previous,
          future: [state.present, ...state.future],
        };
      });
    },

    redo: () => {
      store.setState((state) => {
        if (state.future.length === 0) return state;
        const next = state.future[0];
        return {
          past: [...state.past, state.present],
          present: next,
          future: state.future.slice(1),
        };
      });
    },

    canUndo: () => store.getState().past.length > 0,
    canRedo: () => store.getState().future.length > 0,
  };
}

// ============================================================
// 3. 브라우저 API 연동 예시 (선언적)
// ============================================================

/**
 * 온라인/오프라인 상태 구독 (useSyncExternalStore 패턴)
 *
 * 이 패턴의 장점: 브라우저 이벤트를 선언적 React 상태로 변환
 */
function subscribeToOnlineStatus(callback: () => void): () => void {
  window.addEventListener("online", callback);
  window.addEventListener("offline", callback);
  return () => {
    window.removeEventListener("online", callback);
    window.removeEventListener("offline", callback);
  };
}

function getOnlineSnapshot(): boolean {
  return navigator.onLine;
}

function getServerOnlineSnapshot(): boolean {
  return true; // SSR에서는 항상 온라인으로 가정
}

// React 컴포넌트에서 사용:
// const isOnline = useSyncExternalStore(
//   subscribeToOnlineStatus,
//   getOnlineSnapshot,
//   getServerOnlineSnapshot
// );

/**
 * 화면 크기 구독 (useSyncExternalStore 패턴)
 */
interface WindowSize {
  width: number;
  height: number;
}

let cachedWindowSize: WindowSize = { width: 0, height: 0 };

function subscribeToWindowSize(callback: () => void): () => void {
  const handler = () => {
    // 새 객체를 생성하되, 캐시하여 getSnapshot의 참조 안정성 유지
    cachedWindowSize = {
      width: window.innerWidth,
      height: window.innerHeight,
    };
    callback();
  };
  window.addEventListener("resize", handler);
  return () => window.removeEventListener("resize", handler);
}

function getWindowSizeSnapshot(): WindowSize {
  return cachedWindowSize;
}

// React 컴포넌트에서 사용:
// const windowSize = useSyncExternalStore(
//   subscribeToWindowSize,
//   getWindowSizeSnapshot
// );

// ============================================================
// 4. Node.js 환경 데모
// ============================================================

console.log("╔══════════════════════════════════════════════╗");
console.log("║ useSyncExternalStore 패턴 데모               ║");
console.log("╚══════════════════════════════════════════════╝\n");

// --- 기본 Store 테스트 ---
console.log("=== 1. 기본 Store ===\n");

interface TodoState {
  todos: { id: number; text: string; done: boolean }[];
  filter: "all" | "active" | "done";
}

const todoStore = createStore<TodoState>({
  todos: [],
  filter: "all",
});

// 리스너 등록
const unsubscribe = todoStore.subscribe(() => {
  console.log("  [리스너] 상태 변경 감지:", JSON.stringify(todoStore.getSnapshot()));
});

console.log("초기 상태:", JSON.stringify(todoStore.getSnapshot()));

todoStore.setState((prev) => ({
  ...prev,
  todos: [...prev.todos, { id: 1, text: "React 학습", done: false }],
}));

todoStore.setState((prev) => ({
  ...prev,
  todos: [...prev.todos, { id: 2, text: "TypeScript 학습", done: true }],
}));

todoStore.setState((prev) => ({
  ...prev,
  filter: "active" as const,
}));

unsubscribe();
console.log("리스너 해제 후:");

todoStore.setState((prev) => ({
  ...prev,
  todos: prev.todos.map((t) => (t.id === 1 ? { ...t, done: true } : t)),
}));
console.log("  (리스너가 호출되지 않음)");
console.log("  현재 상태:", JSON.stringify(todoStore.getSnapshot()));

// --- Selector 패턴 시뮬레이션 ---
console.log("\n\n=== 2. Selector 패턴 ===\n");

// selector: 전체 상태에서 필요한 부분만 추출
const selectActiveTodos = (state: TodoState) =>
  state.todos.filter((t) => !t.done);

const selectDoneTodos = (state: TodoState) =>
  state.todos.filter((t) => t.done);

const selectTodoCount = (state: TodoState) => state.todos.length;

console.log("활성 할일:", JSON.stringify(selectActiveTodos(todoStore.getSnapshot())));
console.log("완료 할일:", JSON.stringify(selectDoneTodos(todoStore.getSnapshot())));
console.log("전체 개수:", selectTodoCount(todoStore.getSnapshot()));

// --- History Store 테스트 ---
console.log("\n\n=== 3. Undo/Redo 히스토리 Store ===\n");

const textStore = createHistoryStore<string>("초기 텍스트");

console.log("초기:", textStore.getSnapshot().present);

textStore.push("첫 번째 수정");
console.log("수정 1:", textStore.getSnapshot().present);

textStore.push("두 번째 수정");
console.log("수정 2:", textStore.getSnapshot().present);

textStore.push("세 번째 수정");
console.log("수정 3:", textStore.getSnapshot().present);

console.log(`\ncanUndo: ${textStore.canUndo()}, canRedo: ${textStore.canRedo()}`);

console.log("\n--- Undo 실행 ---");
textStore.undo();
console.log("Undo 1:", textStore.getSnapshot().present);

textStore.undo();
console.log("Undo 2:", textStore.getSnapshot().present);

console.log(`canUndo: ${textStore.canUndo()}, canRedo: ${textStore.canRedo()}`);

console.log("\n--- Redo 실행 ---");
textStore.redo();
console.log("Redo 1:", textStore.getSnapshot().present);

console.log("\n히스토리 상태:");
const historyState = textStore.getSnapshot();
console.log("  past:", JSON.stringify(historyState.past));
console.log("  present:", historyState.present);
console.log("  future:", JSON.stringify(historyState.future));

// 새 변경을 push하면 future가 초기화됨
textStore.push("새로운 분기");
console.log("\n새 변경 후 (future 초기화):");
const afterNewChange = textStore.getSnapshot();
console.log("  past:", JSON.stringify(afterNewChange.past));
console.log("  present:", afterNewChange.present);
console.log("  future:", JSON.stringify(afterNewChange.future));

// --- 사용법 요약 ---
console.log("\n\n=== React 컴포넌트에서의 사용법 ===\n");
console.log(`
// 1. Store 생성 (컴포넌트 외부)
const store = createStore({ count: 0, name: '' });

// 2. 전체 상태 구독
function App() {
  const state = useStore(store);
  return <div>{state.count}</div>;
}

// 3. 선택적 구독 (count만)
function Counter() {
  const count = useStoreSelector(store, (s) => s.count);
  return <div>{count}</div>;
}

// 4. 브라우저 API 연동
function OnlineStatus() {
  const isOnline = useSyncExternalStore(
    subscribeToOnlineStatus,
    getOnlineSnapshot,
    getServerOnlineSnapshot
  );
  return <div>{isOnline ? '온라인' : '오프라인'}</div>;
}

// 5. Undo/Redo
function Editor() {
  const state = useStore(historyStore);
  return (
    <div>
      <textarea value={state.present} />
      <button onClick={historyStore.undo} disabled={!historyStore.canUndo()}>
        실행 취소
      </button>
    </div>
  );
}
`);

console.log("✅ 외부 저장소 패턴 데모 완료!");

export {
  createStore,
  useStore,
  useStoreSelector,
  createHistoryStore,
  Store,
  HistoryStore,
};
