# 챕터 05 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: 타입 안전한 이벤트 에미터 (⭐⭐⭐⭐)

### 설명

TypeScript의 제네릭과 매핑 타입을 활용하여 완전한 타입 안전성을 가진 이벤트 에미터를 구현하세요. 이벤트 이름과 페이로드 타입이 컴파일 타임에 검증되어야 합니다.

### 요구 사항

1. `TypedEventEmitter<EventMap>` 클래스를 구현하세요:

```tsx
// 이벤트 맵 타입 정의
interface AppEvents {
  'user:login': { userId: string; timestamp: number };
  'user:logout': { userId: string };
  'cart:add': { productId: string; quantity: number };
  'cart:remove': { productId: string };
  'notification': { message: string; type: 'info' | 'error' | 'success' };
}

// 사용법
const emitter = new TypedEventEmitter<AppEvents>();

// 타입 안전한 이벤트 발행/구독
emitter.on('user:login', (payload) => {
  // payload의 타입이 { userId: string; timestamp: number }로 자동 추론
  console.log(payload.userId);
});

emitter.emit('user:login', { userId: '123', timestamp: Date.now() });
// emitter.emit('user:login', { userId: 123 }); // 컴파일 에러!
// emitter.emit('unknown', {}); // 컴파일 에러!
```

2. 구현할 메서드:
   - `on<K>(event, handler)`: 이벤트 리스너 등록, unsubscribe 함수 반환
   - `once<K>(event, handler)`: 한 번만 실행되는 리스너
   - `off<K>(event, handler)`: 특정 리스너 제거
   - `emit<K>(event, payload)`: 이벤트 발행
   - `removeAllListeners(event?)`: 리스너 전체 제거
   - `listenerCount(event)`: 특정 이벤트의 리스너 수

3. 추가: `useEvent<K>(emitter, event)` React Hook도 구현하세요.
   - 이벤트를 구독하고, 컴포넌트 언마운트 시 자동 정리
   - 마지막으로 받은 페이로드를 반환

### 힌트
<details><summary>힌트 보기</summary>

- `EventMap`의 키(`keyof EventMap`)를 이벤트 이름 타입으로 사용합니다.
- `on<K extends keyof EventMap>(event: K, handler: (payload: EventMap[K]) => void)` 형태입니다.
- 핸들러는 `Map<keyof EventMap, Set<Function>>`으로 저장합니다.
- `useEvent` Hook은 `useEffect`에서 `on`을 호출하고, cleanup에서 `off`를 호출합니다.
</details>

---

## 문제 2: 제네릭 API 클라이언트 (⭐⭐⭐⭐)

### 설명

REST API의 엔드포인트 정의에서 요청/응답 타입을 자동으로 추론하는 타입 안전한 API 클라이언트를 구현하세요.

### 요구 사항

1. API 엔드포인트를 타입으로 정의하세요:

```tsx
interface ApiEndpoints {
  'GET /users': {
    params: { page?: number; limit?: number };
    response: { users: User[]; total: number };
  };
  'GET /users/:id': {
    params: { id: string };
    response: User;
  };
  'POST /users': {
    body: Omit<User, 'id'>;
    response: User;
  };
  'PUT /users/:id': {
    params: { id: string };
    body: Partial<Omit<User, 'id'>>;
    response: User;
  };
  'DELETE /users/:id': {
    params: { id: string };
    response: { success: boolean };
  };
}
```

2. `createApiClient<Endpoints>()` 함수를 구현하세요:

```tsx
const api = createApiClient<ApiEndpoints>({
  baseUrl: 'https://api.example.com',
});

// 타입 안전한 API 호출
const { users, total } = await api.request('GET /users', {
  params: { page: 1, limit: 10 },
});
// users: User[], total: number (자동 추론)

const user = await api.request('GET /users/:id', {
  params: { id: '123' },
});
// user: User (자동 추론)

const newUser = await api.request('POST /users', {
  body: { name: '김개발', email: 'kim@dev.com' },
});
// newUser: User (자동 추론)
```

3. 추가 기능:
   - URL 파라미터 자동 치환 (`:id` → 실제 값)
   - HTTP 메서드 자동 결정 (`GET /users` → GET 요청)
   - 요청/응답 인터셉터
   - 타입 안전한 에러 처리

### 힌트
<details><summary>힌트 보기</summary>

- Template Literal Type으로 HTTP 메서드를 추출하세요: `'GET /users'` → `'GET'`
- URL에서 경로 파라미터를 추출하는 타입: `'/users/:id'` → `{ id: string }`
- `request<K extends keyof Endpoints>(endpoint: K, options: RequestOptions<Endpoints[K]>)` 형태입니다.
- `infer`를 활용하여 `'GET /users'`에서 메서드와 경로를 분리합니다.
</details>

---

## 문제 3: 타입 안전한 React Context 팩토리 (⭐⭐⭐⭐)

### 설명

Context 생성, Provider, Hook을 하나의 함수 호출로 만들어주는 타입 안전한 팩토리를 구현하세요. Context의 기본값이 `null`이 아니어도 되며, Hook 사용 시 null 체크가 필요 없어야 합니다.

### 요구 사항

1. `createSafeContext<T>(name)` 함수를 구현하세요:

```tsx
const [ThemeProvider, useTheme] = createSafeContext<ThemeContextType>('Theme');

// Provider 없이 사용하면 의미 있는 에러 메시지
function App() {
  return (
    <ThemeProvider value={{ mode: 'dark', primary: '#007bff' }}>
      <Page />
    </ThemeProvider>
  );
}

function Page() {
  const theme = useTheme(); // ThemeContextType (null이 아님!)
  return <div style={{ color: theme.primary }}>{theme.mode}</div>;
}
```

2. `createReducerContext<State, Action>(name, reducer, initialState)` 함수도 구현하세요:

```tsx
const [CounterProvider, useCounterState, useCounterDispatch] =
  createReducerContext<CounterState, CounterAction>(
    'Counter',
    counterReducer,
    { count: 0 }
  );

function App() {
  return (
    <CounterProvider>
      <Counter />
    </CounterProvider>
  );
}

function Counter() {
  const { count } = useCounterState();      // CounterState
  const dispatch = useCounterDispatch();     // Dispatch<CounterAction>
  return (
    <button onClick={() => dispatch({ type: 'INCREMENT' })}>
      {count}
    </button>
  );
}
```

3. `createSelectorContext<State>(name, initialState)` - selector 패턴 지원:

```tsx
const [StoreProvider, useStoreSelector] =
  createSelectorContext<AppState>('Store', initialState);

function UserName() {
  // name이 변경될 때만 리렌더링 (selector 최적화)
  const name = useStoreSelector((state) => state.user.name);
  return <span>{name}</span>;
}
```

### 힌트
<details><summary>힌트 보기</summary>

- `React.createContext<T | null>(null)`로 생성하고, Hook에서 null 체크합니다.
- null이면 `throw new Error('${name}Provider 없이 사용할 수 없습니다')`
- 반환 타입을 튜플로: `[Provider, useValue]` 또는 `[Provider, useState, useDispatch]`
- selector 패턴은 `useSyncExternalStore`를 활용하면 리렌더링 최적화가 가능합니다.
- 컴포넌트 이름은 DevTools에서 표시되도록 `displayName`을 설정하세요.
</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 Template Literal Type과 조건부 타입의 `infer` 키워드를 이해하면 문제 2가 쉬워집니다.
