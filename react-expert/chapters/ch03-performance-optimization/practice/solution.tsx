/**
 * 챕터 03 - 연습 문제 모범 답안
 *
 * 실행 방법:
 *   npx tsx practice/solution.tsx
 */

import React, {
  useState,
  useMemo,
  useCallback,
  useRef,
  useEffect,
  memo,
  Profiler,
} from "react";

// ============================================================
// 문제 1: 렌더링 최적화 진단 및 수정
// ============================================================

interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
}

interface UserListProps {
  users: User[];
  searchQuery: string;
}

// 상수 스타일: 컴포넌트 외부에 선언하여 참조 안정성 보장
const HEADER_STYLE: React.CSSProperties = {
  padding: "16px",
  backgroundColor: "#f5f5f5",
};

const CARD_STYLE: React.CSSProperties = {
  margin: "8px",
};

/**
 * [최적화된 UserCard]
 * - React.memo로 불필요한 리렌더링 방지
 * - 모든 props의 참조가 안정적이어야 효과 발휘
 */
const UserCardOptimized = memo(function UserCard({
  user,
  isSelected,
  onToggle,
}: {
  user: User;
  isSelected: boolean;
  onToggle: (id: number) => void;
}) {
  return (
    <div style={CARD_STYLE} onClick={() => onToggle(user.id)}>
      <span>{user.name}</span>
      <span>{user.email}</span>
      {isSelected && <span> [Check]</span>}
    </div>
  );
});

/**
 * [최적화된 UserList]
 *
 * 수정 사항:
 * 1. useMemo로 필터링/정렬 결과 캐싱 (deps: users, searchQuery, sortField)
 * 2. useMemo로 통계 계산 캐싱 (deps: filteredUsers, selectedIds)
 * 3. useCallback으로 handleToggle 참조 안정화
 * 4. 스타일 객체를 컴포넌트 외부 상수로 분리
 * 5. UserCard에 React.memo 적용
 */
function UserListOptimized({ users, searchQuery }: UserListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [sortField, setSortField] = useState<keyof User>("name");

  // [수정 1] useMemo로 필터링 + 정렬 캐싱
  const filteredUsers = useMemo(() => {
    const filtered = users.filter(
      (u) => u.name.includes(searchQuery) || u.email.includes(searchQuery)
    );
    return filtered.sort((a, b) =>
      String(a[sortField]).localeCompare(String(b[sortField]))
    );
  }, [users, searchQuery, sortField]);

  // [수정 2] useMemo로 통계 캐싱
  const stats = useMemo(
    () => ({
      total: filteredUsers.length,
      admins: filteredUsers.filter((u) => u.role === "admin").length,
      selected: selectedIds.size,
    }),
    [filteredUsers, selectedIds]
  );

  // [수정 3] useCallback으로 함수 참조 안정화
  const handleToggle = useCallback((id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  return {
    filteredUsers,
    stats,
    handleToggle,
    selectedIds,
    sortField,
    setSortField,
  };
}

// 테스트
console.log("╔══════════════════════════════════════════╗");
console.log("║ 문제 1: 렌더링 최적화 진단 및 수정       ║");
console.log("╚══════════════════════════════════════════╝\n");

console.log("=== 식별된 문제와 해결책 ===\n");

const issues = [
  {
    problem: "필터링/정렬이 매 렌더링마다 실행",
    solution: "useMemo(filterAndSort, [users, searchQuery, sortField])",
    impact: "selectedIds 변경 시 불필요한 재계산 방지",
  },
  {
    problem: "stats 객체가 매번 새로 생성",
    solution: "useMemo(computeStats, [filteredUsers, selectedIds])",
    impact: "props 비교 시 불필요한 리렌더링 방지",
  },
  {
    problem: "handleToggle 함수가 매번 새로 생성",
    solution: "useCallback(handleToggle, [])",
    impact: "React.memo된 UserCard의 리렌더링 방지",
  },
  {
    problem: "인라인 스타일 객체가 매번 새로 생성",
    solution: "컴포넌트 외부 상수로 분리",
    impact: "props 비교 시 참조 동일성 보장",
  },
  {
    problem: "UserCard에 React.memo 미적용",
    solution: "React.memo(UserCard)",
    impact: "변경되지 않은 카드의 리렌더링 방지",
  },
];

issues.forEach((issue, i) => {
  console.log(`${i + 1}. 문제: ${issue.problem}`);
  console.log(`   해결: ${issue.solution}`);
  console.log(`   효과: ${issue.impact}\n`);
});

// 리렌더링 비교 분석
console.log("=== 리렌더링 횟수 비교 (사용자 1명 선택 시) ===\n");
const userCount = 1000;
console.log(`사용자 ${userCount}명 기준:`);
console.log(`  최적화 전: UserList(1) + UserCard(${userCount}) = ${userCount + 1}회`);
console.log(`  최적화 후: UserList(1) + UserCard(2) = 3회`);
console.log(`  (선택 해제된 1개 + 새로 선택된 1개만 리렌더링)\n`);

// ============================================================
// 문제 2: 가상 스크롤러 구현
// ============================================================

console.log("\n╔══════════════════════════════════════════╗");
console.log("║ 문제 2: 가상 스크롤러 구현                ║");
console.log("╚══════════════════════════════════════════╝\n");

interface VirtualScrollOptions<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
}

interface VirtualItem<T> {
  index: number;
  item: T;
  style: React.CSSProperties;
}

interface VirtualScrollResult<T> {
  virtualItems: VirtualItem<T>[];
  totalHeight: number;
  visibleRange: { start: number; end: number };
  scrollToIndex: (index: number, align?: "start" | "center" | "end") => void;
}

/**
 * useVirtualScroll - 가상 스크롤 Hook
 *
 * 핵심 알고리즘:
 * 1. scrollTop에서 시작 인덱스 계산: Math.floor(scrollTop / itemHeight)
 * 2. containerHeight에서 보이는 항목 수 계산: Math.ceil(containerHeight / itemHeight)
 * 3. overscan 적용: 시작과 끝에 여분의 항목 추가
 * 4. 각 항목의 style 계산: position: absolute, top: index * itemHeight
 */
function useVirtualScroll<T>(
  options: VirtualScrollOptions<T>,
  scrollTop: number
): VirtualScrollResult<T> {
  const {
    items,
    itemHeight,
    containerHeight,
    overscan = 3,
  } = options;

  const totalHeight = items.length * itemHeight;

  // 보이는 범위 계산
  const startIndex = Math.max(
    0,
    Math.floor(scrollTop / itemHeight) - overscan
  );
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  // 가상 항목 생성
  const virtualItems: VirtualItem<T>[] = [];
  for (let i = startIndex; i <= endIndex; i++) {
    virtualItems.push({
      index: i,
      item: items[i],
      style: {
        position: "absolute" as const,
        top: i * itemHeight,
        height: itemHeight,
        left: 0,
        right: 0,
      },
    });
  }

  // scrollToIndex 구현
  const scrollToIndex = (
    index: number,
    align: "start" | "center" | "end" = "start"
  ): number => {
    const clampedIndex = Math.max(0, Math.min(items.length - 1, index));
    let targetScrollTop: number;

    switch (align) {
      case "start":
        targetScrollTop = clampedIndex * itemHeight;
        break;
      case "center":
        targetScrollTop =
          clampedIndex * itemHeight - containerHeight / 2 + itemHeight / 2;
        break;
      case "end":
        targetScrollTop =
          clampedIndex * itemHeight - containerHeight + itemHeight;
        break;
    }

    return Math.max(0, Math.min(targetScrollTop, totalHeight - containerHeight));
  };

  return {
    virtualItems,
    totalHeight,
    visibleRange: { start: startIndex, end: endIndex },
    scrollToIndex,
  };
}

// 테스트
const testItems = Array.from({ length: 10000 }, (_, i) => ({
  id: i,
  text: `항목 ${i + 1}`,
}));

const scrollConfig: VirtualScrollOptions<typeof testItems[0]> = {
  items: testItems,
  itemHeight: 40,
  containerHeight: 400,
  overscan: 3,
};

console.log("=== 가상 스크롤 테스트 ===\n");
console.log(`총 항목: ${testItems.length.toLocaleString()}개`);
console.log(`항목 높이: ${scrollConfig.itemHeight}px`);
console.log(`컨테이너 높이: ${scrollConfig.containerHeight}px`);
console.log(`overscan: ${scrollConfig.overscan}\n`);

const scrollTests = [0, 500, 2000, 10000, 396000];

scrollTests.forEach((scrollTop) => {
  const result = useVirtualScroll(scrollConfig, scrollTop);
  console.log(
    `  scrollTop=${String(scrollTop).padStart(6)}px → ` +
    `렌더링: [${result.visibleRange.start}~${result.visibleRange.end}] ` +
    `(${result.virtualItems.length}개 / ${testItems.length.toLocaleString()}개)`
  );
});

// scrollToIndex 테스트
console.log("\n=== scrollToIndex 테스트 ===\n");
const result0 = useVirtualScroll(scrollConfig, 0);

["start", "center", "end"].forEach((align) => {
  const targetScrollTop = result0.scrollToIndex(
    5000,
    align as "start" | "center" | "end"
  );
  console.log(
    `  scrollToIndex(5000, '${align}') → scrollTop: ${targetScrollTop}px`
  );
});

// ============================================================
// 문제 3: 성능 모니터링 대시보드
// ============================================================

console.log("\n\n╔══════════════════════════════════════════╗");
console.log("║ 문제 3: 성능 모니터링 대시보드             ║");
console.log("╚══════════════════════════════════════════╝\n");

/**
 * useRenderCount - 렌더링 횟수 추적
 * ref를 사용하여 리렌더링을 유발하지 않으면서 카운트합니다.
 */
function useRenderCount(): number {
  const countRef = useRef(0);
  countRef.current += 1;
  return countRef.current;
}

/**
 * useRenderTime - 렌더링 시간 측정
 *
 * 컴포넌트 본문에서 시작 시간을 기록하고,
 * useEffect에서 (렌더링 완료 후) 경과 시간을 계산합니다.
 */
interface RenderTimeStats {
  lastRenderTime: number;
  averageRenderTime: number;
  maxRenderTime: number;
  totalRenders: number;
}

function useRenderTime(): RenderTimeStats {
  const startTimeRef = useRef(performance.now());
  const statsRef = useRef({
    lastRenderTime: 0,
    averageRenderTime: 0,
    maxRenderTime: 0,
    totalRenders: 0,
    totalTime: 0,
  });

  // 렌더링 시작 시점 기록 (컴포넌트 본문에서 실행)
  startTimeRef.current = performance.now();

  useEffect(() => {
    const duration = performance.now() - startTimeRef.current;
    const stats = statsRef.current;

    stats.lastRenderTime = duration;
    stats.totalRenders += 1;
    stats.totalTime += duration;
    stats.averageRenderTime = stats.totalTime / stats.totalRenders;
    stats.maxRenderTime = Math.max(stats.maxRenderTime, duration);
  });

  return {
    lastRenderTime: statsRef.current.lastRenderTime,
    averageRenderTime: statsRef.current.averageRenderTime,
    maxRenderTime: statsRef.current.maxRenderTime,
    totalRenders: statsRef.current.totalRenders,
  };
}

/**
 * useWhyDidYouRender - 리렌더링 원인 분석
 *
 * 이전 props와 현재 props를 비교하여 변경된 prop을 식별합니다.
 */
interface RenderReason {
  prop: string;
  oldValue: any;
  newValue: any;
  isReferenceChange: boolean; // 값은 같지만 참조가 다른 경우
}

function useWhyDidYouRender<T extends Record<string, any>>(
  componentName: string,
  props: T
): RenderReason[] {
  const prevPropsRef = useRef<T | undefined>(undefined);
  const reasons: RenderReason[] = [];

  if (prevPropsRef.current !== undefined) {
    const prevProps = prevPropsRef.current;
    const allKeys = new Set([
      ...Object.keys(prevProps),
      ...Object.keys(props),
    ]);

    for (const key of allKeys) {
      const oldValue = prevProps[key];
      const newValue = props[key];

      if (!Object.is(oldValue, newValue)) {
        // 깊은 비교로 실제 값이 같은지 확인
        const isReferenceChange =
          typeof oldValue === "object" &&
          typeof newValue === "object" &&
          JSON.stringify(oldValue) === JSON.stringify(newValue);

        reasons.push({
          prop: key,
          oldValue,
          newValue,
          isReferenceChange,
        });
      }
    }

    if (reasons.length > 0) {
      console.log(`[WhyDidYouRender] ${componentName} 리렌더링 원인:`);
      reasons.forEach((reason) => {
        const refNote = reason.isReferenceChange
          ? " (참조만 변경, 값은 동일!)"
          : "";
        console.log(
          `  - ${reason.prop}: ${JSON.stringify(reason.oldValue)} → ${JSON.stringify(reason.newValue)}${refNote}`
        );
      });
    } else {
      console.log(
        `[WhyDidYouRender] ${componentName} 리렌더링됨 (부모 리렌더링, props 변경 없음)`
      );
    }
  }

  // 현재 props를 다음 비교를 위해 저장
  prevPropsRef.current = { ...props };

  return reasons;
}

/**
 * 성능 데이터 수집기
 */
interface PerformanceEntry {
  componentId: string;
  phase: "mount" | "update";
  actualDuration: number;
  baseDuration: number;
  timestamp: number;
}

class PerformanceCollector {
  private entries: PerformanceEntry[] = [];
  private threshold: number;

  constructor(threshold: number = 16) {
    this.threshold = threshold;
  }

  addEntry(entry: PerformanceEntry): void {
    this.entries.push(entry);

    if (entry.actualDuration > this.threshold) {
      console.warn(
        `[PerformanceMonitor] 느린 렌더링 감지: ${entry.componentId} ` +
        `(${entry.actualDuration.toFixed(2)}ms > ${this.threshold}ms 임계값)`
      );
    }
  }

  getStats(componentId?: string): {
    totalRenders: number;
    avgDuration: number;
    maxDuration: number;
    slowRenders: number;
  } {
    const filtered = componentId
      ? this.entries.filter((e) => e.componentId === componentId)
      : this.entries;

    if (filtered.length === 0) {
      return { totalRenders: 0, avgDuration: 0, maxDuration: 0, slowRenders: 0 };
    }

    const durations = filtered.map((e) => e.actualDuration);
    return {
      totalRenders: filtered.length,
      avgDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
      maxDuration: Math.max(...durations),
      slowRenders: durations.filter((d) => d > this.threshold).length,
    };
  }

  getReport(): string {
    const componentIds = [...new Set(this.entries.map((e) => e.componentId))];
    let report = "=== 성능 리포트 ===\n\n";

    componentIds.forEach((id) => {
      const stats = this.getStats(id);
      report += `${id}:\n`;
      report += `  총 렌더링: ${stats.totalRenders}회\n`;
      report += `  평균 시간: ${stats.avgDuration.toFixed(2)}ms\n`;
      report += `  최대 시간: ${stats.maxDuration.toFixed(2)}ms\n`;
      report += `  느린 렌더링: ${stats.slowRenders}회\n\n`;
    });

    return report;
  }

  clear(): void {
    this.entries = [];
  }
}

// 테스트

console.log("=== useRenderCount 시뮬레이션 ===\n");
let renderCount = 0;
for (let i = 0; i < 5; i++) {
  renderCount++;
  console.log(`  렌더링 ${i + 1}: count = ${renderCount}`);
}

console.log("\n=== useWhyDidYouRender 시뮬레이션 ===\n");

// 시뮬레이션: props 비교
const prevProps = {
  name: "홍길동",
  age: 30,
  style: { color: "red" },
  items: [1, 2, 3],
  onClick: () => {},
};

const nextProps = {
  name: "홍길동",
  age: 31,                    // 값 변경
  style: { color: "red" },    // 참조만 변경 (값은 동일)
  items: [1, 2, 3],           // 참조만 변경 (값은 동일)
  onClick: () => {},           // 참조 변경 (함수)
};

console.log("이전 props:", JSON.stringify(prevProps, null, 2));
console.log("현재 props:", JSON.stringify(nextProps, null, 2));
console.log();

const allKeys = new Set([...Object.keys(prevProps), ...Object.keys(nextProps)]);
for (const key of allKeys) {
  const old = (prevProps as any)[key];
  const curr = (nextProps as any)[key];
  const same = Object.is(old, curr);

  if (!same) {
    const isRefOnly =
      typeof old === "object" &&
      typeof curr === "object" &&
      old !== null &&
      curr !== null &&
      JSON.stringify(old) === JSON.stringify(curr);

    const note = isRefOnly ? " (참조만 변경!)" : "";
    console.log(`  변경됨: ${key}${note}`);
  }
}

console.log("\n=== PerformanceCollector 시뮬레이션 ===\n");

const collector = new PerformanceCollector(16);

// 시뮬레이션된 렌더링 데이터
const simulatedEntries: PerformanceEntry[] = [
  { componentId: "App", phase: "mount", actualDuration: 8.5, baseDuration: 12.0, timestamp: 1000 },
  { componentId: "UserList", phase: "mount", actualDuration: 25.3, baseDuration: 30.0, timestamp: 1001 },
  { componentId: "UserCard", phase: "mount", actualDuration: 2.1, baseDuration: 3.0, timestamp: 1002 },
  { componentId: "App", phase: "update", actualDuration: 5.2, baseDuration: 12.0, timestamp: 2000 },
  { componentId: "UserList", phase: "update", actualDuration: 18.7, baseDuration: 30.0, timestamp: 2001 },
  { componentId: "UserCard", phase: "update", actualDuration: 1.5, baseDuration: 3.0, timestamp: 2002 },
  { componentId: "UserList", phase: "update", actualDuration: 45.1, baseDuration: 30.0, timestamp: 3001 },
];

simulatedEntries.forEach((entry) => {
  collector.addEntry(entry);
});

console.log(collector.getReport());

console.log("✅ 모든 문제 풀이 완료!");

export {
  UserListOptimized,
  UserCardOptimized,
  useVirtualScroll,
  useRenderCount,
  useRenderTime,
  useWhyDidYouRender,
  PerformanceCollector,
  VirtualScrollOptions,
  RenderTimeStats,
  RenderReason,
};
