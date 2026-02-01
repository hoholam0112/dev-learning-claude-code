# 챕터 02 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: 상태 머신 기반 useReducer (⭐⭐⭐)

### 설명

유한 상태 머신(Finite State Machine) 패턴을 활용한 `useStateMachine` Hook을 구현하세요. 이 Hook은 `useReducer`를 기반으로 하되, 현재 상태에서 허용되는 전이(transition)만 실행할 수 있도록 타입 레벨에서 강제합니다.

### 요구 사항

1. `createStateMachine<States, Events>(config)` 함수를 구현하세요.
2. 상태 머신 설정(config)은 다음 형태입니다:

```tsx
interface StateMachineConfig<S extends string, E extends string> {
  initial: S;
  states: {
    [state in S]: {
      on: {
        [event in E]?: {
          target: S;
          action?: (context: any) => any;
        };
      };
    };
  };
}
```

3. `useStateMachine(machine)` Hook은 다음을 반환합니다:
   - `state`: 현재 상태
   - `send(event)`: 이벤트 전송
   - `can(event)`: 현재 상태에서 해당 이벤트가 허용되는지 확인
   - `context`: 상태 머신의 확장 데이터

4. 허용되지 않는 전이는 무시되어야 합니다.

### 테스트 케이스

```tsx
// 네트워크 요청 상태 머신
const fetchMachine = createStateMachine({
  initial: 'idle' as const,
  states: {
    idle: {
      on: {
        FETCH: { target: 'loading' as const },
      },
    },
    loading: {
      on: {
        SUCCESS: { target: 'success' as const },
        ERROR: { target: 'error' as const },
      },
    },
    success: {
      on: {
        RESET: { target: 'idle' as const },
        FETCH: { target: 'loading' as const },
      },
    },
    error: {
      on: {
        RETRY: { target: 'loading' as const },
        RESET: { target: 'idle' as const },
      },
    },
  },
});

// 사용
const { state, send, can } = useStateMachine(fetchMachine);
// state === 'idle'
// can('FETCH') === true
// can('SUCCESS') === false  (idle에서 SUCCESS는 불가)
send('FETCH');  // state → 'loading'
send('RESET');  // 무시됨 (loading에서 RESET은 불가)
```

### 힌트
<details><summary>힌트 보기</summary>

- `useReducer`의 reducer 함수에서 현재 상태의 `on` 객체를 확인하여 전이 가능 여부를 판단하세요.
- TypeScript의 `Record` 타입과 제네릭을 활용하면 타입 안전성을 확보할 수 있습니다.
- `send`는 `dispatch`의 래퍼이며, 안정적인 참조를 가집니다.
</details>

---

## 문제 2: useSyncExternalStore로 반응형 LocalStorage Hook (⭐⭐⭐)

### 설명

`useSyncExternalStore`를 사용하여 여러 탭/윈도우에서 동기화되는 `useSharedLocalStorage` Hook을 구현하세요. 한 탭에서 값을 변경하면 다른 탭에서도 즉시 반영되어야 합니다.

### 요구 사항

1. `useSharedLocalStorage<T>(key, initialValue)` Hook을 구현하세요.
2. `useSyncExternalStore`를 반드시 사용해야 합니다 (useState로 직접 구현 금지).
3. 다음 기능을 지원해야 합니다:
   - 값 읽기/쓰기 (JSON 직렬화/역직렬화)
   - 다른 탭에서 변경 시 자동 동기화 (`storage` 이벤트)
   - 같은 탭 내에서의 변경도 구독자에게 알림
   - SSR 호환 (`getServerSnapshot` 제공)
   - 타입 안전성 (제네릭)

4. 반환값: `[value, setValue, removeValue]` 튜플

### 테스트 케이스

```tsx
// 탭 A
const [theme, setTheme] = useSharedLocalStorage('theme', 'light');
setTheme('dark');

// 탭 B (자동으로 동기화)
const [theme] = useSharedLocalStorage('theme', 'light');
// theme === 'dark'
```

### 힌트
<details><summary>힌트 보기</summary>

- `window.addEventListener('storage', callback)`으로 다른 탭의 변경을 감지할 수 있습니다.
- 같은 탭 내 변경은 `storage` 이벤트가 발생하지 않으므로, 커스텀 이벤트나 내부 구독 시스템이 필요합니다.
- `getSnapshot`은 매번 새 객체를 반환하면 안 됩니다. 캐시를 사용하세요.
- `subscribe` 함수는 `unsubscribe`를 반환해야 합니다.
</details>

---

## 문제 3: Hook 합성 — useInfiniteScroll (⭐⭐⭐⭐)

### 설명

무한 스크롤 기능을 구현하는 `useInfiniteScroll` Hook을 만드세요. 여러 기본 Hook과 유틸리티 Hook을 합성하여 구현합니다.

### 요구 사항

1. `useInfiniteScroll<T>(fetchPage, options)` Hook을 구현하세요.

```tsx
interface UseInfiniteScrollOptions {
  threshold?: number;       // 하단으로부터의 거리 (px), 기본값 200
  initialPage?: number;     // 초기 페이지, 기본값 1
  enabled?: boolean;        // 활성화 여부, 기본값 true
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
  sentinelRef: React.RefObject<HTMLElement>;  // 감시 대상 요소 ref
  retry: () => void;
  reset: () => void;
}
```

2. 사용할 내부 Hook/기술:
   - `useReducer`: 페이지네이션 상태 관리 (items, page, loading, error, hasMore)
   - `useRef`: sentinel 요소 참조
   - `useCallback`: 페이지 로딩 함수 메모이제이션
   - `useEffect` + IntersectionObserver: sentinel 요소가 뷰포트에 들어올 때 감지
   - `useRef`로 중복 요청 방지 (debounce 또는 lock)

3. 엣지 케이스 처리:
   - 컴포넌트 언마운트 시 진행 중인 요청 취소
   - 로딩 중 중복 요청 방지
   - 에러 발생 시 retry 가능
   - reset으로 초기 상태로 돌아가기

### 테스트 케이스

```tsx
// 사용 예시
function ProductList() {
  const {
    items,
    loading,
    error,
    hasMore,
    sentinelRef,
    retry,
  } = useInfiniteScroll<Product>(
    async (page: number) => {
      const res = await fetch(`/api/products?page=${page}`);
      const data = await res.json();
      return {
        data: data.products,
        hasMore: data.hasMore,
        nextPage: page + 1,
      };
    },
    { threshold: 300 }
  );

  return (
    <div>
      {items.map((item) => <ProductCard key={item.id} product={item} />)}
      {loading && <Spinner />}
      {error && <button onClick={retry}>재시도</button>}
      {hasMore && <div ref={sentinelRef} />}
    </div>
  );
}
```

### 힌트
<details><summary>힌트 보기</summary>

- IntersectionObserver를 useEffect에서 생성하고, cleanup에서 disconnect하세요.
- sentinel 요소가 뷰포트에 들어오면(`isIntersecting === true`) 다음 페이지를 로드합니다.
- `useReducer`의 상태에 `page` 번호를 포함시키면 페이지네이션 로직이 깔끔해집니다.
- AbortController를 사용하면 fetch 취소가 가능합니다.
- loading 중에는 추가 fetch를 하지 않도록 lock을 사용하세요.
</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 Hook 합성 패턴의 계층 구조를 이해하면 문제 3이 쉬워집니다.
