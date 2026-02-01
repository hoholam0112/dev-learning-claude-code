# 챕터 04 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: 미니 Zustand 구현 (⭐⭐⭐⭐)

### 설명

Zustand의 핵심 기능을 직접 구현하세요. `useSyncExternalStore`를 기반으로 한 미니 상태 관리 라이브러리를 만듭니다.

### 요구 사항

1. `create<T>(initializer)` 함수를 구현하세요:

```tsx
type StateCreator<T> = (
  set: (partial: Partial<T> | ((state: T) => Partial<T>)) => void,
  get: () => T
) => T;

function create<T>(initializer: StateCreator<T>): UseStore<T>;
```

2. 반환되는 `useStore` Hook은:
   - 인자 없이 호출: 전체 상태 반환
   - selector 함수와 호출: 선택된 값만 반환, 해당 값이 변경될 때만 리렌더링

```tsx
const useStore = create<CounterState>((set, get) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set({ count: get().count - 1 }),
}));

// 사용
const count = useStore((state) => state.count);        // count만 구독
const increment = useStore((state) => state.increment); // increment만 구독
const state = useStore();                               // 전체 상태 구독
```

3. 추가 요구 사항:
   - `useStore.getState()`: 구독 없이 현재 상태 반환
   - `useStore.setState()`: 외부에서 상태 변경
   - `useStore.subscribe()`: 상태 변경 리스너 등록

### 힌트
<details><summary>힌트 보기</summary>

- `useSyncExternalStore(subscribe, getSnapshot)`을 사용하세요.
- selector가 있을 때의 getSnapshot은 `() => selector(state)`입니다.
- selector의 반환값이 이전과 같으면(`Object.is`) 이전 캐시를 반환하여 리렌더링을 방지합니다.
- `set`은 부분 업데이트(Partial)를 지원해야 합니다: `Object.assign({}, state, partial)`.
</details>

---

## 문제 2: TanStack Query 캐시 시뮬레이터 (⭐⭐⭐⭐)

### 설명

TanStack Query의 핵심 캐싱 메커니즘을 순수 TypeScript로 시뮬레이션하세요. `staleTime`, `gcTime`(가비지 컬렉션 타임), 자동 갱신 로직을 구현합니다.

### 요구 사항

1. `QueryCache` 클래스를 구현하세요:

```tsx
interface QueryCacheOptions {
  staleTime?: number;  // fresh → stale 전환 시간 (ms), 기본값: 0
  gcTime?: number;     // 캐시 제거 시간 (ms), 기본값: 300000 (5분)
}

interface CachedQuery<T> {
  data: T;
  status: 'fresh' | 'stale' | 'fetching';
  fetchedAt: number;
  error: Error | null;
}

class QueryCache {
  fetch<T>(key: string[], queryFn: () => Promise<T>, options?: QueryCacheOptions): Promise<T>;
  invalidate(key: string[]): void;
  invalidateAll(keyPrefix: string[]): void;
  getQueryData<T>(key: string[]): T | undefined;
  setQueryData<T>(key: string[], data: T): void;
  getStatus(key: string[]): CachedQuery<any>['status'] | 'idle';
  clear(): void;
}
```

2. 캐싱 동작:
   - 같은 키로 `fetch`를 호출하면 캐시된 데이터 반환 (fresh 상태일 때)
   - stale 상태이면 캐시를 반환하면서 백그라운드에서 갱신 (stale-while-revalidate)
   - 중복 요청 제거: 같은 키로 동시에 여러 fetch가 호출되면 하나만 실행
   - `gcTime` 경과 후 비활성 캐시 자동 제거

3. `invalidate`/`invalidateAll` 동작:
   - `invalidate(['users', '1'])`: 정확히 일치하는 키의 캐시를 stale로 전환
   - `invalidateAll(['users'])`: `['users']`로 시작하는 모든 키의 캐시를 stale로 전환

### 테스트 케이스

```tsx
const cache = new QueryCache();

// 첫 번째 호출: API 실행
const users = await cache.fetch(
  ['users'],
  () => fetchUsers(),
  { staleTime: 5000 }
);

// 즉시 두 번째 호출: 캐시 반환 (5초 이내이므로 fresh)
const cachedUsers = await cache.fetch(['users'], () => fetchUsers());
// API 호출 없이 캐시된 데이터 반환

// 5초 후: stale 상태 → 캐시 반환 + 백그라운드 갱신
// ...

// 캐시 무효화
cache.invalidateAll(['users']); // users로 시작하는 모든 쿼리 무효화
```

### 힌트
<details><summary>힌트 보기</summary>

- 캐시 키는 배열이므로 `JSON.stringify(key)`로 문자열 키로 변환하세요.
- `invalidateAll`은 키 접두사 매칭입니다: 캐시 키가 접두사로 시작하는지 확인하세요.
- 중복 요청 제거: 진행 중인 Promise를 Map에 저장하고, 같은 키의 요청은 기존 Promise를 반환합니다.
- `stale-while-revalidate`: 캐시 데이터를 즉시 반환하고, 새 데이터가 도착하면 캐시를 업데이트합니다.
</details>

---

## 문제 3: 낙관적 업데이트(Optimistic Update) 시스템 (⭐⭐⭐⭐)

### 설명

서버 응답을 기다리지 않고 즉시 UI를 업데이트하는 **낙관적 업데이트** 시스템을 구현하세요. 서버 요청이 실패하면 자동으로 롤백합니다.

### 요구 사항

1. `OptimisticUpdater<T>` 클래스를 구현하세요:

```tsx
interface OptimisticUpdateOptions<T> {
  mutationFn: () => Promise<any>;       // 실제 서버 요청
  optimisticData: T;                     // 낙관적으로 표시할 데이터
  rollbackData: T;                       // 실패 시 롤백할 데이터
  onSuccess?: (serverData: any) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  maxRetries?: number;                   // 자동 재시도 횟수
}

class OptimisticUpdater<T> {
  constructor(
    private getState: () => T,
    private setState: (data: T) => void
  );

  async execute(options: OptimisticUpdateOptions<T>): Promise<void>;
  getPendingUpdates(): number;
  cancelAll(): void;
}
```

2. 실행 흐름:
   1. `optimisticData`로 즉시 상태 업데이트
   2. `mutationFn()` 실행
   3. 성공: `onSuccess` 호출
   4. 실패: `rollbackData`로 상태 복원, 재시도 또는 `onError` 호출

3. 추가 요구 사항:
   - 여러 낙관적 업데이트가 동시에 진행될 수 있어야 합니다
   - 앞선 업데이트가 실패하면 이후 업데이트도 올바르게 롤백
   - 경쟁 조건(race condition) 처리

### 테스트 케이스

```tsx
// 할일 목록의 완료 토글
const updater = new OptimisticUpdater(
  () => todoStore.getState().todos,
  (todos) => todoStore.setState({ todos })
);

await updater.execute({
  mutationFn: () => api.updateTodo(1, { done: true }),
  optimisticData: todos.map(t => t.id === 1 ? { ...t, done: true } : t),
  rollbackData: todos, // 현재 상태
  onError: (err) => toast.error('업데이트 실패: ' + err.message),
});
```

### 힌트
<details><summary>힌트 보기</summary>

- 낙관적 업데이트 스택을 유지하세요. 여러 업데이트가 쌓일 수 있습니다.
- 실패 시 롤백할 때, 이후에 적용된 다른 낙관적 업데이트도 고려해야 합니다.
- `AbortController`로 취소 기능을 구현할 수 있습니다.
- 동시 업데이트 시 순서가 중요합니다. 큐를 사용하거나 버전 번호를 관리하세요.
</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 Zustand의 내부 원리(useSyncExternalStore)와 TanStack Query의 캐시 생명주기를 이해하면 문제가 쉬워집니다.
