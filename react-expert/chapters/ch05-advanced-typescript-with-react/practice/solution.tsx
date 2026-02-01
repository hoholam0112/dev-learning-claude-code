/**
 * 챕터 05 - 연습 문제 모범 답안
 *
 * 실행 방법:
 *   npx tsx practice/solution.tsx
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useState,
  useEffect,
  useRef,
  useSyncExternalStore,
  useCallback,
} from "react";

// ============================================================
// 문제 1: 타입 안전한 이벤트 에미터
// ============================================================

/**
 * TypedEventEmitter - 완전한 타입 안전성을 가진 이벤트 에미터
 *
 * EventMap의 키가 이벤트 이름, 값이 페이로드 타입으로 사용됩니다.
 * on/emit/off 모든 메서드에서 이벤트 이름과 페이로드 타입이 검증됩니다.
 */
class TypedEventEmitter<EventMap extends Record<string, any>> {
  private handlers = new Map<keyof EventMap, Set<(payload: any) => void>>();

  /**
   * 이벤트 리스너 등록
   * K가 EventMap의 키로 제한되므로, handler의 payload 타입이 자동 추론됩니다.
   */
  on<K extends keyof EventMap>(
    event: K,
    handler: (payload: EventMap[K]) => void
  ): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);

    // unsubscribe 함수 반환
    return () => this.off(event, handler);
  }

  /** 한 번만 실행되는 리스너 */
  once<K extends keyof EventMap>(
    event: K,
    handler: (payload: EventMap[K]) => void
  ): () => void {
    const wrappedHandler = (payload: EventMap[K]) => {
      handler(payload);
      this.off(event, wrappedHandler);
    };
    return this.on(event, wrappedHandler);
  }

  /** 특정 리스너 제거 */
  off<K extends keyof EventMap>(
    event: K,
    handler: (payload: EventMap[K]) => void
  ): void {
    this.handlers.get(event)?.delete(handler);
  }

  /**
   * 이벤트 발행
   * event와 payload의 타입이 EventMap에 의해 강제됩니다.
   */
  emit<K extends keyof EventMap>(event: K, payload: EventMap[K]): void {
    const eventHandlers = this.handlers.get(event);
    if (eventHandlers) {
      eventHandlers.forEach((handler) => handler(payload));
    }
  }

  /** 리스너 전체 제거 */
  removeAllListeners<K extends keyof EventMap>(event?: K): void {
    if (event) {
      this.handlers.delete(event);
    } else {
      this.handlers.clear();
    }
  }

  /** 리스너 수 조회 */
  listenerCount<K extends keyof EventMap>(event: K): number {
    return this.handlers.get(event)?.size ?? 0;
  }
}

/**
 * useEvent - React Hook으로 이벤트 구독
 *
 * 컴포넌트 언마운트 시 자동으로 리스너를 정리합니다.
 * 마지막으로 받은 페이로드를 상태로 유지합니다.
 */
function useEvent<
  EventMap extends Record<string, any>,
  K extends keyof EventMap
>(
  emitter: TypedEventEmitter<EventMap>,
  event: K
): EventMap[K] | null {
  const [lastPayload, setLastPayload] = useState<EventMap[K] | null>(null);

  useEffect(() => {
    const unsubscribe = emitter.on(event, (payload) => {
      setLastPayload(payload);
    });

    return unsubscribe;
  }, [emitter, event]);

  return lastPayload;
}

// 테스트
console.log("╔══════════════════════════════════════════╗");
console.log("║ 문제 1: 타입 안전한 이벤트 에미터         ║");
console.log("╚══════════════════════════════════════════╝\n");

interface AppEvents {
  "user:login": { userId: string; timestamp: number };
  "user:logout": { userId: string };
  "cart:add": { productId: string; quantity: number };
  "cart:remove": { productId: string };
  notification: { message: string; type: "info" | "error" | "success" };
}

const emitter = new TypedEventEmitter<AppEvents>();

// on 테스트
const unsubLogin = emitter.on("user:login", (payload) => {
  // payload 타입: { userId: string; timestamp: number }
  console.log(`  [로그인] userId: ${payload.userId}, time: ${payload.timestamp}`);
});

emitter.on("notification", (payload) => {
  // payload 타입: { message: string; type: 'info' | 'error' | 'success' }
  console.log(`  [알림] [${payload.type}] ${payload.message}`);
});

// once 테스트
emitter.once("cart:add", (payload) => {
  console.log(`  [장바구니-once] ${payload.productId} x${payload.quantity}`);
});

console.log("이벤트 발행 테스트:");
emitter.emit("user:login", { userId: "u123", timestamp: Date.now() });
emitter.emit("notification", { message: "환영합니다!", type: "success" });
emitter.emit("cart:add", { productId: "p1", quantity: 2 });
emitter.emit("cart:add", { productId: "p2", quantity: 1 }); // once이므로 출력 안 됨

console.log(`\n리스너 수: user:login=${emitter.listenerCount("user:login")}, cart:add=${emitter.listenerCount("cart:add")}`);

unsubLogin();
console.log("user:login 리스너 해제 후:");
emitter.emit("user:login", { userId: "u456", timestamp: Date.now() });
console.log("  (출력 없음)");

// ============================================================
// 문제 2: 제네릭 API 클라이언트
// ============================================================

console.log("\n\n╔══════════════════════════════════════════╗");
console.log("║ 문제 2: 제네릭 API 클라이언트              ║");
console.log("╚══════════════════════════════════════════╝\n");

/**
 * HTTP 메서드 추출 타입
 */
type ExtractMethod<T extends string> = T extends `${infer M} ${string}`
  ? M
  : never;

/**
 * URL 경로 추출 타입
 */
type ExtractPath<T extends string> = T extends `${string} ${infer P}`
  ? P
  : never;

/**
 * URL 경로에서 파라미터 추출
 * '/users/:id/posts/:postId' → { id: string; postId: string }
 */
type ExtractPathParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? { [K in Param]: string } & ExtractPathParams<`/${Rest}`>
    : T extends `${string}:${infer Param}`
      ? { [K in Param]: string }
      : {};

/**
 * 요청 옵션 타입 결정
 */
type RequestOptions<Endpoint> = Endpoint extends { params: infer P; body: infer B }
  ? { params: P; body: B }
  : Endpoint extends { params: infer P }
    ? { params: P }
    : Endpoint extends { body: infer B }
      ? { body: B }
      : {};

type ResponseType<Endpoint> = Endpoint extends { response: infer R } ? R : never;

/** API 엔드포인트 정의 */
interface User {
  id: string;
  name: string;
  email: string;
}

interface ApiEndpoints {
  "GET /users": {
    params: { page?: number; limit?: number };
    response: { users: User[]; total: number };
  };
  "GET /users/:id": {
    params: { id: string };
    response: User;
  };
  "POST /users": {
    body: Omit<User, "id">;
    response: User;
  };
  "PUT /users/:id": {
    params: { id: string };
    body: Partial<Omit<User, "id">>;
    response: User;
  };
  "DELETE /users/:id": {
    params: { id: string };
    response: { success: boolean };
  };
}

/**
 * createApiClient - 타입 안전한 API 클라이언트
 */
interface ApiClientConfig {
  baseUrl: string;
  headers?: Record<string, string>;
  onRequest?: (url: string, init: RequestInit) => RequestInit;
  onResponse?: (response: Response) => Response;
}

interface ApiClient<Endpoints extends Record<string, any>> {
  request<K extends keyof Endpoints & string>(
    endpoint: K,
    options?: RequestOptions<Endpoints[K]>
  ): Promise<ResponseType<Endpoints[K]>>;
}

function createApiClient<Endpoints extends Record<string, any>>(
  config: ApiClientConfig
): ApiClient<Endpoints> {
  return {
    async request<K extends keyof Endpoints & string>(
      endpoint: K,
      options?: RequestOptions<Endpoints[K]>
    ): Promise<ResponseType<Endpoints[K]>> {
      // HTTP 메서드와 경로 분리
      const [method, ...pathParts] = endpoint.split(" ");
      let path = pathParts.join(" ");

      // URL 파라미터 치환
      const params = (options as any)?.params;
      if (params) {
        for (const [key, value] of Object.entries(params)) {
          path = path.replace(`:${key}`, String(value));
        }

        // 나머지 params는 쿼리 스트링으로
        const queryParams: Record<string, string> = {};
        for (const [key, value] of Object.entries(params)) {
          if (!path.includes(`:${key}`) && value !== undefined) {
            queryParams[key] = String(value);
          }
        }
        const queryString = new URLSearchParams(queryParams).toString();
        if (queryString) path += `?${queryString}`;
      }

      const url = `${config.baseUrl}${path}`;
      let init: RequestInit = {
        method,
        headers: {
          "Content-Type": "application/json",
          ...config.headers,
        },
      };

      // body 추가
      const body = (options as any)?.body;
      if (body) {
        init.body = JSON.stringify(body);
      }

      // 요청 인터셉터
      if (config.onRequest) {
        init = config.onRequest(url, init);
      }

      console.log(`  [API] ${method} ${url}`);
      if (body) console.log(`    body: ${JSON.stringify(body)}`);

      // 시뮬레이션: 실제 fetch 대신 모의 응답 반환
      return { _mock: true, endpoint, method, path, params, body } as any;
    },
  };
}

// 테스트
const api = createApiClient<ApiEndpoints>({
  baseUrl: "https://api.example.com",
  headers: { Authorization: "Bearer token123" },
});

async function runApiTest() {
  console.log("API 호출 시뮬레이션:\n");

  // GET /users with query params
  await api.request("GET /users", {
    params: { page: 1, limit: 10 },
  });

  // GET /users/:id with path param
  await api.request("GET /users/:id", {
    params: { id: "user-123" },
  });

  // POST /users with body
  await api.request("POST /users", {
    body: { name: "김개발", email: "kim@dev.com" },
  });

  // PUT /users/:id with params and body
  await api.request("PUT /users/:id", {
    params: { id: "user-123" },
    body: { name: "김시니어" },
  });

  // DELETE /users/:id
  await api.request("DELETE /users/:id", {
    params: { id: "user-123" },
  });

  console.log("\n타입 추론 검증:");
  console.log("  GET /users → response: { users: User[]; total: number }");
  console.log("  GET /users/:id → response: User");
  console.log("  POST /users → body: Omit<User, 'id'>, response: User");
  console.log("  PUT /users/:id → body: Partial<Omit<User, 'id'>>, response: User");
  console.log("  DELETE /users/:id → response: { success: boolean }");
}

// ============================================================
// 문제 3: 타입 안전한 React Context 팩토리
// ============================================================

/**
 * createSafeContext - null 체크 없는 안전한 Context
 */
function createSafeContext<T>(
  name: string
): [React.FC<{ value: T; children: React.ReactNode }>, () => T] {
  const Context = createContext<T | null>(null);
  Context.displayName = name;

  function Provider({
    value,
    children,
  }: {
    value: T;
    children: React.ReactNode;
  }) {
    return React.createElement(Context.Provider, { value }, children);
  }
  Provider.displayName = `${name}Provider`;

  function useSafeContext(): T {
    const context = useContext(Context);
    if (context === null) {
      throw new Error(
        `use${name}()은 <${name}Provider> 내부에서만 사용할 수 있습니다.`
      );
    }
    return context;
  }

  return [Provider, useSafeContext];
}

/**
 * createReducerContext - Reducer 기반 Context
 *
 * State와 Dispatch를 분리하여 불필요한 리렌더링을 방지합니다.
 */
function createReducerContext<State, Action>(
  name: string,
  reducer: (state: State, action: Action) => State,
  initialState: State
): [
  React.FC<{ children: React.ReactNode }>,
  () => State,
  () => React.Dispatch<Action>
] {
  const StateContext = createContext<State | null>(null);
  const DispatchContext = createContext<React.Dispatch<Action> | null>(null);

  StateContext.displayName = `${name}State`;
  DispatchContext.displayName = `${name}Dispatch`;

  function Provider({ children }: { children: React.ReactNode }) {
    const [state, dispatch] = useReducer(reducer, initialState);
    return React.createElement(
      StateContext.Provider,
      { value: state },
      React.createElement(
        DispatchContext.Provider,
        { value: dispatch },
        children
      )
    );
  }
  Provider.displayName = `${name}Provider`;

  function useStateContext(): State {
    const context = useContext(StateContext);
    if (context === null) {
      throw new Error(
        `use${name}State()는 <${name}Provider> 내부에서만 사용할 수 있습니다.`
      );
    }
    return context;
  }

  function useDispatchContext(): React.Dispatch<Action> {
    const context = useContext(DispatchContext);
    if (context === null) {
      throw new Error(
        `use${name}Dispatch()는 <${name}Provider> 내부에서만 사용할 수 있습니다.`
      );
    }
    return context;
  }

  return [Provider, useStateContext, useDispatchContext];
}

/**
 * createSelectorContext - Selector 패턴 지원 Context
 *
 * useSyncExternalStore를 활용하여
 * selector의 반환값이 변경될 때만 리렌더링합니다.
 */
function createSelectorContext<State>(
  name: string,
  initialState: State
): [
  React.FC<{ children: React.ReactNode }>,
  <S>(selector: (state: State) => S) => S,
  () => (updater: (prev: State) => State) => void
] {
  let state = initialState;
  const listeners = new Set<() => void>();

  function subscribe(listener: () => void): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  }

  function getState(): State {
    return state;
  }

  function setState(updater: (prev: State) => State): void {
    state = updater(state);
    listeners.forEach((l) => l());
  }

  const Context = createContext<boolean>(false); // Provider 존재 확인용

  function Provider({ children }: { children: React.ReactNode }) {
    return React.createElement(
      Context.Provider,
      { value: true },
      children
    );
  }
  Provider.displayName = `${name}Provider`;

  function useSelector<S>(selector: (state: State) => S): S {
    const isInProvider = useContext(Context);
    if (!isInProvider) {
      throw new Error(
        `use${name}Selector()는 <${name}Provider> 내부에서만 사용할 수 있습니다.`
      );
    }

    const getSnapshot = useCallback(
      () => selector(getState()),
      [selector]
    );

    return useSyncExternalStore(subscribe, getSnapshot);
  }

  function useUpdater(): (updater: (prev: State) => State) => void {
    const isInProvider = useContext(Context);
    if (!isInProvider) {
      throw new Error(
        `use${name}Updater()는 <${name}Provider> 내부에서만 사용할 수 있습니다.`
      );
    }
    return setState;
  }

  return [Provider, useSelector, useUpdater];
}

// 테스트
async function runContextTest() {
  console.log("\n\n╔══════════════════════════════════════════╗");
  console.log("║ 문제 3: 타입 안전한 Context 팩토리         ║");
  console.log("╚══════════════════════════════════════════╝\n");

  // --- createSafeContext ---
  console.log("=== createSafeContext ===\n");

  interface ThemeContext {
    mode: "light" | "dark";
    primary: string;
  }

  const [ThemeProvider, useTheme] = createSafeContext<ThemeContext>("Theme");

  console.log("생성됨: [ThemeProvider, useTheme]");
  console.log("  useTheme() → ThemeContext (null이 아닌 타입 보장)");
  console.log("  Provider 없이 사용 시 → Error: 'useTheme()은 <ThemeProvider> 내부에서만 사용할 수 있습니다.'");

  // --- createReducerContext ---
  console.log("\n\n=== createReducerContext ===\n");

  interface CounterState {
    count: number;
  }

  type CounterAction =
    | { type: "INCREMENT" }
    | { type: "DECREMENT" }
    | { type: "SET"; value: number };

  function counterReducer(
    state: CounterState,
    action: CounterAction
  ): CounterState {
    switch (action.type) {
      case "INCREMENT":
        return { count: state.count + 1 };
      case "DECREMENT":
        return { count: state.count - 1 };
      case "SET":
        return { count: action.value };
    }
  }

  const [CounterProvider, useCounterState, useCounterDispatch] =
    createReducerContext<CounterState, CounterAction>(
      "Counter",
      counterReducer,
      { count: 0 }
    );

  console.log("생성됨: [CounterProvider, useCounterState, useCounterDispatch]");
  console.log("  useCounterState() → CounterState (null이 아닌 타입 보장)");
  console.log("  useCounterDispatch() → Dispatch<CounterAction>");
  console.log("  State와 Dispatch가 분리되어 dispatch만 사용하는 컴포넌트는");
  console.log("  state 변경 시 리렌더링되지 않음");

  // Reducer 동작 시뮬레이션
  console.log("\n  Reducer 시뮬레이션:");
  let counterState: CounterState = { count: 0 };
  const actions: CounterAction[] = [
    { type: "INCREMENT" },
    { type: "INCREMENT" },
    { type: "SET", value: 10 },
    { type: "DECREMENT" },
  ];

  actions.forEach((action) => {
    counterState = counterReducer(counterState, action);
    console.log(`    dispatch(${JSON.stringify(action)}) → count: ${counterState.count}`);
  });

  // --- createSelectorContext ---
  console.log("\n\n=== createSelectorContext ===\n");

  interface AppState {
    user: { name: string; email: string };
    settings: { theme: "light" | "dark"; language: string };
    todos: { id: number; text: string; done: boolean }[];
  }

  const [StoreProvider, useStoreSelector, useStoreUpdater] =
    createSelectorContext<AppState>("Store", {
      user: { name: "김개발", email: "kim@dev.com" },
      settings: { theme: "light", language: "ko" },
      todos: [
        { id: 1, text: "React 학습", done: false },
        { id: 2, text: "TypeScript 학습", done: true },
      ],
    });

  console.log("생성됨: [StoreProvider, useStoreSelector, useStoreUpdater]");
  console.log("  useStoreSelector((s) => s.user.name) → string");
  console.log("  useStoreSelector((s) => s.settings) → { theme, language }");
  console.log("  selector의 반환값이 변경될 때만 리렌더링 (useSyncExternalStore)");

  console.log("\n  Selector 패턴의 장점:");
  console.log("  - UserName 컴포넌트: (s) => s.user.name만 구독");
  console.log("  - TodoList 컴포넌트: (s) => s.todos만 구독");
  console.log("  - todos가 변경되어도 UserName은 리렌더링 안 됨!");
}

// 실행
runApiTest().then(runContextTest).then(() => {
  // --- 최종 요약 ---
  console.log("\n\n=== 전체 타입 패턴 요약 ===\n");
  console.log(`
┌──────────────────────────┬─────────────────────────────────────┐
│ 타입 패턴                │ 사용 사례                            │
├──────────────────────────┼─────────────────────────────────────┤
│ 매핑 타입                │ EventMap → on/emit 메서드 타입        │
│ 조건부 타입 + infer      │ 'GET /users' → method, path 추출     │
│ Template Literal Type    │ URL 경로 파라미터 추출                │
│ 제네릭 클래스            │ TypedEventEmitter<EventMap>           │
│ 함수 오버로딩            │ createContext → 다양한 반환 타입      │
│ 판별 유니온              │ CounterAction의 type 기반 좁힘        │
│ 제네릭 제약              │ T extends Record<string, any>        │
│ 유틸리티 타입 조합       │ Omit + Partial + Pick 조합            │
└──────────────────────────┴─────────────────────────────────────┘
  `);

  console.log("✅ 모든 문제 풀이 완료!");
});

export {
  TypedEventEmitter,
  useEvent,
  createApiClient,
  createSafeContext,
  createReducerContext,
  createSelectorContext,
};
