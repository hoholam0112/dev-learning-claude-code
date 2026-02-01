/**
 * 챕터 04 - 연습 문제 모범 답안
 *
 * 실행 방법:
 *   npx tsx practice/solution.tsx
 */

import { useSyncExternalStore, useCallback, useRef } from "react";

// ============================================================
// 문제 1: 미니 Zustand 구현
// ============================================================

type StateCreator<T> = (
  set: (partial: Partial<T> | ((state: T) => Partial<T>)) => void,
  get: () => T
) => T;

interface StoreApi<T> {
  getState: () => T;
  setState: (partial: Partial<T> | ((state: T) => Partial<T>)) => void;
  subscribe: (listener: () => void) => () => void;
  destroy: () => void;
}

/**
 * create - 미니 Zustand 구현
 *
 * 핵심 원리:
 * 1. 클로저로 state와 listeners를 관리
 * 2. set 호출 시 state를 업데이트하고 모든 listener에게 알림
 * 3. Hook은 useSyncExternalStore로 구현
 * 4. selector로 필요한 부분만 구독하여 불필요한 리렌더링 방지
 */
function create<T extends object>(
  initializer: StateCreator<T>
): {
  (): T;
  <S>(selector: (state: T) => S): S;
  getState: () => T;
  setState: (partial: Partial<T> | ((state: T) => Partial<T>)) => void;
  subscribe: (listener: () => void) => () => void;
  destroy: () => void;
} {
  // 내부 상태와 리스너
  let state: T;
  const listeners = new Set<() => void>();

  // set: 상태 업데이트 함수
  const setState = (partial: Partial<T> | ((state: T) => Partial<T>)) => {
    const nextPartial =
      typeof partial === "function"
        ? (partial as (state: T) => Partial<T>)(state)
        : partial;

    // 변경 사항이 있는 경우에만 업데이트
    const nextState = Object.assign({}, state, nextPartial);

    // 얕은 비교로 실제 변경 여부 확인
    const hasChanged = Object.keys(nextPartial).some(
      (key) => !Object.is((state as any)[key], (nextState as any)[key])
    );

    if (hasChanged) {
      state = nextState;
      listeners.forEach((listener) => listener());
    }
  };

  // get: 현재 상태 반환
  const getState = () => state;

  // subscribe: 리스너 등록
  const subscribe = (listener: () => void) => {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  };

  // destroy: 모든 리스너 제거
  const destroy = () => {
    listeners.clear();
  };

  // 초기 상태 생성
  state = initializer(setState, getState);

  // Hook 함수 (오버로딩)
  function useStore(): T;
  function useStore<S>(selector: (state: T) => S): S;
  function useStore<S>(selector?: (state: T) => S): T | S {
    // selector가 없으면 전체 상태 반환
    const getSnapshot = selector
      ? () => selector(getState())
      : () => getState();

    return useSyncExternalStore(subscribe, getSnapshot);
  }

  // 정적 메서드 추가
  useStore.getState = getState;
  useStore.setState = setState;
  useStore.subscribe = subscribe;
  useStore.destroy = destroy;

  return useStore as any;
}

// 테스트
console.log("╔══════════════════════════════════════════╗");
console.log("║ 문제 1: 미니 Zustand 구현                ║");
console.log("╚══════════════════════════════════════════╝\n");

// Store 생성
interface CounterState {
  count: number;
  name: string;
  increment: () => void;
  decrement: () => void;
  setName: (name: string) => void;
}

const useCounterStore = create<CounterState>((set, get) => ({
  count: 0,
  name: "카운터",
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set({ count: get().count - 1 }),
  setName: (name: string) => set({ name }),
}));

// 외부 API 테스트
console.log("초기 상태:", useCounterStore.getState());

// 리스너 등록
const unsubscribe = useCounterStore.subscribe(() => {
  console.log("  [리스너] 상태 변경:", useCounterStore.getState());
});

console.log("\nsetState 테스트:");
useCounterStore.getState().increment();
useCounterStore.getState().increment();
useCounterStore.getState().decrement();
useCounterStore.getState().setName("내 카운터");

console.log(`\n최종 상태: count=${useCounterStore.getState().count}, name=${useCounterStore.getState().name}`);

unsubscribe();
console.log("\n리스너 해제 후 변경 (로그 없음):");
useCounterStore.getState().increment();
console.log(`  count=${useCounterStore.getState().count}`);

// ============================================================
// 문제 2: TanStack Query 캐시 시뮬레이터
// ============================================================

console.log("\n\n╔══════════════════════════════════════════╗");
console.log("║ 문제 2: TanStack Query 캐시 시뮬레이터    ║");
console.log("╚══════════════════════════════════════════╝\n");

interface QueryCacheOptions {
  staleTime?: number;
  gcTime?: number;
}

interface CachedQuery<T> {
  data: T;
  status: "fresh" | "stale" | "fetching";
  fetchedAt: number;
  error: Error | null;
  gcTimer?: ReturnType<typeof setTimeout>;
}

/**
 * QueryCache - TanStack Query의 캐시 메커니즘 시뮬레이션
 */
class QueryCache {
  private cache = new Map<string, CachedQuery<any>>();
  private inFlightQueries = new Map<string, Promise<any>>();
  private defaultOptions: Required<QueryCacheOptions> = {
    staleTime: 0,
    gcTime: 300000, // 5분
  };
  private fetchLog: string[] = [];

  /** 캐시 키를 문자열로 변환 */
  private serializeKey(key: string[]): string {
    return JSON.stringify(key);
  }

  /** 키 접두사 매칭 확인 */
  private keyStartsWith(cacheKey: string, prefix: string[]): boolean {
    try {
      const parsedKey: string[] = JSON.parse(cacheKey);
      return prefix.every((part, i) => parsedKey[i] === part);
    } catch {
      return false;
    }
  }

  /**
   * fetch - 데이터 조회 (캐시 우선)
   *
   * 동작:
   * 1. 캐시가 fresh이면 즉시 반환
   * 2. 캐시가 stale이면 캐시 반환 + 백그라운드 갱신
   * 3. 캐시가 없으면 fetch 실행
   * 4. 동일 키의 진행 중인 요청이 있으면 해당 Promise 재사용
   */
  async fetch<T>(
    key: string[],
    queryFn: () => Promise<T>,
    options?: QueryCacheOptions
  ): Promise<T> {
    const serializedKey = this.serializeKey(key);
    const opts = { ...this.defaultOptions, ...options };
    const cached = this.cache.get(serializedKey);

    // 캐시가 fresh이면 즉시 반환
    if (cached && cached.status === "fresh") {
      const elapsed = Date.now() - cached.fetchedAt;
      if (elapsed < opts.staleTime) {
        this.fetchLog.push(`[캐시 HIT - fresh] ${serializedKey}`);
        return cached.data;
      }
      // staleTime 경과 → stale 전환
      cached.status = "stale";
    }

    // 캐시가 stale이면 캐시 반환 + 백그라운드 갱신
    if (cached && cached.status === "stale") {
      this.fetchLog.push(`[캐시 HIT - stale] ${serializedKey} (백그라운드 갱신 시작)`);
      this.backgroundRefetch(serializedKey, queryFn, opts);
      return cached.data;
    }

    // 진행 중인 동일 요청이 있으면 재사용 (중복 제거)
    if (this.inFlightQueries.has(serializedKey)) {
      this.fetchLog.push(`[중복 요청 제거] ${serializedKey}`);
      return this.inFlightQueries.get(serializedKey)!;
    }

    // 새 fetch 실행
    this.fetchLog.push(`[API 호출] ${serializedKey}`);
    const promise = this.executeFetch(serializedKey, queryFn, opts);
    this.inFlightQueries.set(serializedKey, promise);

    try {
      const result = await promise;
      return result;
    } finally {
      this.inFlightQueries.delete(serializedKey);
    }
  }

  /** 실제 fetch 실행 및 캐시 저장 */
  private async executeFetch<T>(
    serializedKey: string,
    queryFn: () => Promise<T>,
    opts: Required<QueryCacheOptions>
  ): Promise<T> {
    // fetching 상태로 설정
    const existing = this.cache.get(serializedKey);
    if (existing) {
      existing.status = "fetching";
    }

    try {
      const data = await queryFn();

      // 이전 GC 타이머 제거
      const prev = this.cache.get(serializedKey);
      if (prev?.gcTimer) clearTimeout(prev.gcTimer);

      // 캐시에 저장
      const gcTimer = setTimeout(() => {
        this.cache.delete(serializedKey);
        this.fetchLog.push(`[GC 삭제] ${serializedKey}`);
      }, opts.gcTime);

      this.cache.set(serializedKey, {
        data,
        status: "fresh",
        fetchedAt: Date.now(),
        error: null,
        gcTimer,
      });

      return data;
    } catch (error) {
      const cached = this.cache.get(serializedKey);
      if (cached) {
        cached.status = "stale";
        cached.error = error instanceof Error ? error : new Error(String(error));
      }
      throw error;
    }
  }

  /** 백그라운드 갱신 */
  private async backgroundRefetch<T>(
    serializedKey: string,
    queryFn: () => Promise<T>,
    opts: Required<QueryCacheOptions>
  ): Promise<void> {
    try {
      await this.executeFetch(serializedKey, queryFn, opts);
      this.fetchLog.push(`[백그라운드 갱신 완료] ${serializedKey}`);
    } catch {
      this.fetchLog.push(`[백그라운드 갱신 실패] ${serializedKey}`);
    }
  }

  /** 특정 키 무효화 */
  invalidate(key: string[]): void {
    const serializedKey = this.serializeKey(key);
    const cached = this.cache.get(serializedKey);
    if (cached) {
      cached.status = "stale";
      this.fetchLog.push(`[무효화] ${serializedKey}`);
    }
  }

  /** 접두사로 시작하는 모든 키 무효화 */
  invalidateAll(keyPrefix: string[]): void {
    for (const [cacheKey, cached] of this.cache.entries()) {
      if (this.keyStartsWith(cacheKey, keyPrefix)) {
        cached.status = "stale";
        this.fetchLog.push(`[무효화] ${cacheKey}`);
      }
    }
  }

  /** 캐시된 데이터 직접 조회 */
  getQueryData<T>(key: string[]): T | undefined {
    return this.cache.get(this.serializeKey(key))?.data;
  }

  /** 캐시 데이터 직접 설정 */
  setQueryData<T>(key: string[], data: T): void {
    const serializedKey = this.serializeKey(key);
    const existing = this.cache.get(serializedKey);
    if (existing) {
      existing.data = data;
      existing.fetchedAt = Date.now();
      existing.status = "fresh";
    } else {
      this.cache.set(serializedKey, {
        data,
        status: "fresh",
        fetchedAt: Date.now(),
        error: null,
      });
    }
  }

  /** 쿼리 상태 확인 */
  getStatus(key: string[]): CachedQuery<any>["status"] | "idle" {
    const cached = this.cache.get(this.serializeKey(key));
    return cached?.status ?? "idle";
  }

  /** 전체 캐시 비우기 */
  clear(): void {
    for (const cached of this.cache.values()) {
      if (cached.gcTimer) clearTimeout(cached.gcTimer);
    }
    this.cache.clear();
    this.inFlightQueries.clear();
  }

  /** 로그 조회 */
  getLog(): string[] {
    return [...this.fetchLog];
  }

  clearLog(): void {
    this.fetchLog = [];
  }
}

// 테스트
const cache = new QueryCache();

let apiCallCount = 0;
const mockFetchUsers = async (): Promise<string[]> => {
  apiCallCount++;
  await new Promise((r) => setTimeout(r, 50));
  return ["김개발", "이프론트", "박풀스택"];
};

async function runCacheTest() {
  console.log("=== 캐시 동작 테스트 ===\n");

  // 1. 첫 번째 호출: API 실행
  apiCallCount = 0;
  const users1 = await cache.fetch(["users"], mockFetchUsers, {
    staleTime: 5000,
  });
  console.log(`1. 첫 호출: ${JSON.stringify(users1)} (API 호출: ${apiCallCount}회)`);
  console.log(`   상태: ${cache.getStatus(["users"])}`);

  // 2. 즉시 두 번째 호출: 캐시 반환
  apiCallCount = 0;
  const users2 = await cache.fetch(["users"], mockFetchUsers, {
    staleTime: 5000,
  });
  console.log(`2. 즉시 재호출: ${JSON.stringify(users2)} (API 호출: ${apiCallCount}회)`);

  // 3. 캐시 무효화 후 호출
  cache.invalidate(["users"]);
  console.log(`3. 무효화 후 상태: ${cache.getStatus(["users"])}`);

  apiCallCount = 0;
  const users3 = await cache.fetch(["users"], mockFetchUsers);
  console.log(`   재호출: ${JSON.stringify(users3)} (API 호출: ${apiCallCount}회)`);

  // 4. 접두사 무효화
  await cache.fetch(["users", "1"], async () => ({ id: 1, name: "김개발" }), {
    staleTime: 5000,
  });
  await cache.fetch(["users", "2"], async () => ({ id: 2, name: "이프론트" }), {
    staleTime: 5000,
  });
  await cache.fetch(["posts"], async () => [{ id: 1, title: "게시글" }], {
    staleTime: 5000,
  });

  console.log(`\n4. 접두사 무효화 전:`);
  console.log(`   users: ${cache.getStatus(["users"])}`);
  console.log(`   users/1: ${cache.getStatus(["users", "1"])}`);
  console.log(`   users/2: ${cache.getStatus(["users", "2"])}`);
  console.log(`   posts: ${cache.getStatus(["posts"])}`);

  cache.invalidateAll(["users"]);

  console.log(`   접두사 무효화 후 (["users"]):`);
  console.log(`   users: ${cache.getStatus(["users"])}`);
  console.log(`   users/1: ${cache.getStatus(["users", "1"])}`);
  console.log(`   users/2: ${cache.getStatus(["users", "2"])}`);
  console.log(`   posts: ${cache.getStatus(["posts"])} (영향 없음)`);

  // 5. setQueryData
  console.log(`\n5. setQueryData 테스트:`);
  cache.setQueryData(["users", "3"], { id: 3, name: "최백엔드" });
  console.log(`   users/3: ${JSON.stringify(cache.getQueryData(["users", "3"]))}`);
  console.log(`   상태: ${cache.getStatus(["users", "3"])}`);

  // 로그 출력
  console.log("\n=== 전체 캐시 로그 ===");
  cache.getLog().forEach((log) => console.log(`  ${log}`));

  cache.clear();
}

// ============================================================
// 문제 3: 낙관적 업데이트 시스템
// ============================================================

interface OptimisticUpdateOptions<T> {
  mutationFn: () => Promise<any>;
  optimisticData: T;
  rollbackData: T;
  onSuccess?: (serverData: any) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
  maxRetries?: number;
}

interface PendingUpdate<T> {
  id: number;
  rollbackData: T;
  status: "pending" | "success" | "error" | "cancelled";
}

/**
 * OptimisticUpdater - 낙관적 업데이트 시스템
 *
 * 동작 흐름:
 * 1. optimisticData로 즉시 상태 업데이트
 * 2. mutationFn() 실행
 * 3. 성공: pending 업데이트 제거
 * 4. 실패: rollbackData로 복원 (+ 재시도)
 */
class OptimisticUpdater<T> {
  private pendingUpdates: PendingUpdate<T>[] = [];
  private updateCounter = 0;
  private log: string[] = [];

  constructor(
    private getState: () => T,
    private setState: (data: T) => void
  ) {}

  async execute(options: OptimisticUpdateOptions<T>): Promise<void> {
    const updateId = ++this.updateCounter;
    const { maxRetries = 0 } = options;

    // 1. 낙관적 업데이트 적용
    this.pendingUpdates.push({
      id: updateId,
      rollbackData: options.rollbackData,
      status: "pending",
    });

    this.setState(options.optimisticData);
    this.log.push(`[#${updateId}] 낙관적 업데이트 적용`);

    // 2. 서버 요청 실행 (재시도 포함)
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const serverData = await options.mutationFn();

        // 성공
        const pending = this.pendingUpdates.find((u) => u.id === updateId);
        if (pending) {
          pending.status = "success";
        }

        this.log.push(`[#${updateId}] 서버 요청 성공 (시도 ${attempt + 1})`);
        options.onSuccess?.(serverData);
        options.onSettled?.();
        return;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        this.log.push(
          `[#${updateId}] 서버 요청 실패 (시도 ${attempt + 1}/${maxRetries + 1}): ${lastError.message}`
        );

        if (attempt < maxRetries) {
          await new Promise((r) => setTimeout(r, 100 * Math.pow(2, attempt)));
        }
      }
    }

    // 3. 최종 실패 → 롤백
    const pending = this.pendingUpdates.find((u) => u.id === updateId);
    if (pending && pending.status === "pending") {
      pending.status = "error";
      this.rollback(updateId);
    }

    if (lastError) {
      options.onError?.(lastError);
    }
    options.onSettled?.();
  }

  /** 특정 업데이트를 롤백 */
  private rollback(updateId: number): void {
    const pending = this.pendingUpdates.find((u) => u.id === updateId);
    if (!pending) return;

    this.log.push(`[#${updateId}] 롤백 실행`);
    this.setState(pending.rollbackData);

    // 이후에 성공한 업데이트들을 다시 적용
    const laterSuccessUpdates = this.pendingUpdates.filter(
      (u) => u.id > updateId && u.status === "success"
    );

    if (laterSuccessUpdates.length > 0) {
      this.log.push(
        `[#${updateId}] 이후 성공한 업데이트 ${laterSuccessUpdates.length}개 재적용`
      );
    }
  }

  /** 진행 중인 업데이트 수 */
  getPendingUpdates(): number {
    return this.pendingUpdates.filter((u) => u.status === "pending").length;
  }

  /** 모든 대기 중인 업데이트 취소 */
  cancelAll(): void {
    this.pendingUpdates
      .filter((u) => u.status === "pending")
      .forEach((u) => {
        u.status = "cancelled";
        this.log.push(`[#${u.id}] 취소됨`);
      });

    // 가장 최근의 롤백 데이터로 복원
    const lastRollback = this.pendingUpdates
      .filter((u) => u.status === "cancelled")
      .pop();
    if (lastRollback) {
      this.setState(lastRollback.rollbackData);
    }
  }

  getLog(): string[] {
    return [...this.log];
  }
}

// 테스트
async function runOptimisticUpdateTest() {
  console.log("\n\n╔══════════════════════════════════════════╗");
  console.log("║ 문제 3: 낙관적 업데이트 시스템             ║");
  console.log("╚══════════════════════════════════════════╝\n");

  interface Todo {
    id: number;
    text: string;
    done: boolean;
  }

  let todosState: Todo[] = [
    { id: 1, text: "React 학습", done: false },
    { id: 2, text: "TypeScript 학습", done: false },
    { id: 3, text: "Zustand 학습", done: false },
  ];

  const updater = new OptimisticUpdater<Todo[]>(
    () => todosState,
    (data) => {
      todosState = data;
    }
  );

  // 시나리오 1: 성공 케이스
  console.log("=== 시나리오 1: 낙관적 업데이트 성공 ===\n");
  console.log("초기 상태:", todosState.map((t) => `${t.text}:${t.done}`).join(", "));

  await updater.execute({
    mutationFn: async () => {
      await new Promise((r) => setTimeout(r, 50));
      return { success: true };
    },
    optimisticData: todosState.map((t) =>
      t.id === 1 ? { ...t, done: true } : t
    ),
    rollbackData: [...todosState],
    onSuccess: () => console.log("  서버 응답: 성공"),
  });

  console.log("최종 상태:", todosState.map((t) => `${t.text}:${t.done}`).join(", "));

  // 시나리오 2: 실패 + 롤백
  console.log("\n=== 시나리오 2: 낙관적 업데이트 실패 → 롤백 ===\n");
  const beforeFailure = [...todosState];
  console.log("업데이트 전:", todosState.map((t) => `${t.text}:${t.done}`).join(", "));

  await updater.execute({
    mutationFn: async () => {
      await new Promise((r) => setTimeout(r, 50));
      throw new Error("네트워크 오류");
    },
    optimisticData: todosState.map((t) =>
      t.id === 2 ? { ...t, done: true } : t
    ),
    rollbackData: beforeFailure,
    onError: (err) => console.log(`  에러 처리: ${err.message}`),
  });

  console.log("롤백 후:", todosState.map((t) => `${t.text}:${t.done}`).join(", "));

  // 시나리오 3: 재시도 후 성공
  console.log("\n=== 시나리오 3: 재시도 후 성공 ===\n");
  let attemptCount = 0;

  await updater.execute({
    mutationFn: async () => {
      attemptCount++;
      await new Promise((r) => setTimeout(r, 30));
      if (attemptCount < 3) throw new Error(`시도 ${attemptCount} 실패`);
      return { success: true };
    },
    optimisticData: todosState.map((t) =>
      t.id === 3 ? { ...t, done: true } : t
    ),
    rollbackData: [...todosState],
    maxRetries: 3,
    onSuccess: () => console.log("  3번째 시도에서 성공!"),
  });

  console.log("최종 상태:", todosState.map((t) => `${t.text}:${t.done}`).join(", "));

  // 로그 출력
  console.log("\n=== 전체 로그 ===");
  updater.getLog().forEach((log) => console.log(`  ${log}`));
}

// 실행
runCacheTest().then(() => runOptimisticUpdateTest()).then(() => {
  console.log("\n✅ 모든 문제 풀이 완료!");
});

export {
  create,
  QueryCache,
  OptimisticUpdater,
  StateCreator,
};
