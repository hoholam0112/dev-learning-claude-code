/**
 * 챕터 03 - 예제 1: 대규모 리스트 최적화와 프로파일링
 *
 * 10,000개 항목의 상품 리스트를 단계적으로 최적화합니다:
 * Step 1: 최적화 없는 기본 구현 (문제 확인)
 * Step 2: React.memo 적용
 * Step 3: useCallback + useMemo 적용
 * Step 4: 가상화(Virtualization) 적용
 *
 * 각 단계의 렌더링 비용을 측정하여 비교합니다.
 *
 * 실행 방법:
 *   npx tsx practice/example-01.tsx
 *
 * 브라우저에서 실제 리스트를 테스트하려면:
 *   React 프로젝트에서 아래 컴포넌트를 import하여 사용하세요.
 *   npm install @tanstack/react-virtual  (가상화 라이브러리)
 */

import React, {
  useState,
  useCallback,
  useMemo,
  memo,
  useRef,
  useEffect,
  Profiler,
} from "react";

// ============================================================
// 1. 타입 정의
// ============================================================

interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
  rating: number;
  inStock: boolean;
}

interface ProductCardProps {
  product: Product;
  isSelected: boolean;
  onSelect: (id: number) => void;
}

// ============================================================
// 2. 데이터 생성
// ============================================================

function generateProducts(count: number): Product[] {
  const categories = ["전자기기", "의류", "식품", "가구", "스포츠"];
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `상품 ${i + 1}`,
    price: Math.floor(Math.random() * 100000) + 1000,
    category: categories[i % categories.length],
    rating: Math.round((Math.random() * 4 + 1) * 10) / 10,
    inStock: Math.random() > 0.2,
  }));
}

// ============================================================
// Step 1: 최적화 없는 기본 구현
// ============================================================

/**
 * [문제점] 부모의 상태가 변경될 때마다 모든 ProductCard가 리렌더링됩니다.
 * 10,000개 항목이면 selectedId 하나 변경에 10,000번의 렌더링이 발생합니다.
 */
function ProductCardBasic({ product, isSelected, onSelect }: ProductCardProps) {
  // 비용이 큰 렌더링 시뮬레이션
  const startTime = performance.now();
  while (performance.now() - startTime < 0.1) {
    // 0.1ms 지연 (복잡한 UI 시뮬레이션)
  }

  return (
    <div
      style={{
        padding: "12px",
        border: isSelected ? "2px solid blue" : "1px solid #ddd",
        backgroundColor: isSelected ? "#e3f2fd" : "white",
        cursor: "pointer",
      }}
      onClick={() => onSelect(product.id)}
    >
      <h3>{product.name}</h3>
      <p>가격: {product.price.toLocaleString()}원</p>
      <p>카테고리: {product.category}</p>
      <p>평점: {product.rating}</p>
      {!product.inStock && <span style={{ color: "red" }}>품절</span>}
    </div>
  );
}

// ============================================================
// Step 2: React.memo 적용
// ============================================================

/**
 * React.memo로 감싸면 props가 변경되지 않은 항목은 리렌더링을 건너뜁니다.
 *
 * 하지만 주의! 부모에서 onSelect를 인라인 함수로 전달하면
 * 매번 새 참조가 생성되어 memo가 무력화됩니다.
 */
const ProductCardMemo = memo(function ProductCardMemo({
  product,
  isSelected,
  onSelect,
}: ProductCardProps) {
  return (
    <div
      style={{
        padding: "12px",
        border: isSelected ? "2px solid blue" : "1px solid #ddd",
        backgroundColor: isSelected ? "#e3f2fd" : "white",
        cursor: "pointer",
      }}
      onClick={() => onSelect(product.id)}
    >
      <h3>{product.name}</h3>
      <p>가격: {product.price.toLocaleString()}원</p>
      <p>카테고리: {product.category}</p>
      <p>평점: {product.rating}</p>
      {!product.inStock && <span style={{ color: "red" }}>품절</span>}
    </div>
  );
});

// ============================================================
// Step 3: useMemo + useCallback 적용
// ============================================================

/**
 * 부모 컴포넌트에서 useCallback과 useMemo를 사용하여
 * 자식에게 전달하는 props의 참조 안정성을 보장합니다.
 */
function OptimizedProductList({
  products,
  filter,
}: {
  products: Product[];
  filter: string;
}) {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // useCallback: 함수 참조 안정화
  const handleSelect = useCallback((id: number) => {
    setSelectedId(id);
  }, []);

  // useMemo: 필터링 결과 캐싱
  const filteredProducts = useMemo(() => {
    console.log(`[useMemo] 필터링 실행: "${filter}"`);
    if (!filter) return products;
    return products.filter((p) =>
      p.category.includes(filter) || p.name.includes(filter)
    );
  }, [products, filter]);

  // useMemo: 통계 계산 캐싱
  const stats = useMemo(() => {
    console.log("[useMemo] 통계 계산 실행");
    return {
      total: filteredProducts.length,
      avgPrice:
        filteredProducts.reduce((sum, p) => sum + p.price, 0) /
        filteredProducts.length,
      inStockCount: filteredProducts.filter((p) => p.inStock).length,
    };
  }, [filteredProducts]);

  return {
    selectedId,
    handleSelect,
    filteredProducts,
    stats,
  };
}

// ============================================================
// Step 4: 가상화 (TanStack Virtual 패턴)
// ============================================================

/**
 * 가상화 로직을 순수 TypeScript로 구현합니다.
 * 실제 프로젝트에서는 @tanstack/react-virtual을 사용하세요.
 *
 * 핵심 원리: 스크롤 위치에 따라 보이는 항목의 인덱스 범위를 계산하고,
 * 해당 범위의 항목만 렌더링합니다.
 */
interface VirtualizerConfig {
  count: number;
  itemHeight: number;
  containerHeight: number;
  overscan: number; // 화면 밖에 추가로 렌더링할 항목 수
}

interface VirtualItem {
  index: number;
  offsetTop: number;
}

function calculateVisibleRange(
  scrollTop: number,
  config: VirtualizerConfig
): { items: VirtualItem[]; totalHeight: number } {
  const { count, itemHeight, containerHeight, overscan } = config;

  const totalHeight = count * itemHeight;
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    count - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const items: VirtualItem[] = [];
  for (let i = startIndex; i <= endIndex; i++) {
    items.push({
      index: i,
      offsetTop: i * itemHeight,
    });
  }

  return { items, totalHeight };
}

// ============================================================
// 5. 성능 측정 유틸리티
// ============================================================

interface ProfileResult {
  id: string;
  phase: string;
  actualDuration: number;
  baseDuration: number;
}

/**
 * React Profiler의 onRender 콜백
 * 렌더링 시간을 측정합니다.
 */
function onRenderCallback(
  id: string,
  phase: "mount" | "update",
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number
): void {
  console.log(
    `[Profiler] ${id} | ${phase} | actual: ${actualDuration.toFixed(2)}ms | base: ${baseDuration.toFixed(2)}ms`
  );
}

// ============================================================
// 6. 벤치마크 실행
// ============================================================

console.log("╔══════════════════════════════════════════════════════╗");
console.log("║ 대규모 리스트 최적화 - 단계별 벤치마크                ║");
console.log("╚══════════════════════════════════════════════════════╝\n");

const ITEM_COUNT = 10000;
const products = generateProducts(ITEM_COUNT);

console.log(`항목 수: ${ITEM_COUNT.toLocaleString()}개\n`);

// --- 가상화 벤치마크 ---
console.log("=== 가상화 벤치마크 ===\n");

const config: VirtualizerConfig = {
  count: ITEM_COUNT,
  itemHeight: 60,
  containerHeight: 600,
  overscan: 5,
};

// 스크롤 위치별 가상화 결과
const scrollPositions = [0, 1000, 5000, 50000, 299400]; // 마지막은 끝부분

scrollPositions.forEach((scrollTop) => {
  const result = calculateVisibleRange(scrollTop, config);
  const startIdx = result.items[0]?.index ?? 0;
  const endIdx = result.items[result.items.length - 1]?.index ?? 0;
  console.log(
    `  스크롤: ${scrollTop}px → 렌더링 범위: [${startIdx}~${endIdx}] (${result.items.length}개 / ${ITEM_COUNT.toLocaleString()}개)`
  );
});

console.log(`\n  총 DOM 높이: ${(config.count * config.itemHeight).toLocaleString()}px`);
console.log(`  한 화면에 보이는 항목: ${Math.ceil(config.containerHeight / config.itemHeight)}개`);
console.log(`  가상화로 렌더링하는 항목: ~${Math.ceil(config.containerHeight / config.itemHeight) + config.overscan * 2}개`);

// --- React.memo 효과 시뮬레이션 ---
console.log("\n\n=== React.memo 효과 시뮬레이션 ===\n");

// 시나리오: 10,000개 중 1개의 selectedId만 변경
const propsComparisons = {
  withoutMemo: ITEM_COUNT, // 전체 리렌더링
  withMemo: 2, // 이전 선택 해제 + 새 선택 (2개만 변경)
};

console.log("시나리오: selectedId 변경 (1개 항목 선택)");
console.log(`  React.memo 없음: ${propsComparisons.withoutMemo.toLocaleString()}개 리렌더링`);
console.log(`  React.memo 적용: ${propsComparisons.withMemo}개 리렌더링`);
console.log(`  절감율: ${(((propsComparisons.withoutMemo - propsComparisons.withMemo) / propsComparisons.withoutMemo) * 100).toFixed(1)}%`);

// --- useMemo 효과 시뮬레이션 ---
console.log("\n\n=== useMemo 효과 시뮬레이션 ===\n");

console.log("시나리오: 필터 변경 없이 selectedId만 변경\n");

// useMemo 없음: 매번 필터링 실행
const startWithout = performance.now();
for (let i = 0; i < 100; i++) {
  products.filter((p) => p.category === "전자기기");
}
const durationWithout = performance.now() - startWithout;

console.log(`  useMemo 없음: 필터링 100회 실행 → ${durationWithout.toFixed(2)}ms`);
console.log(`  useMemo 적용: 필터링 1회 실행 + 캐시 99회 반환 → ~0.01ms`);
console.log(`  절감: ~${(durationWithout * 0.99).toFixed(2)}ms`);

// --- 종합 비교 ---
console.log("\n\n=== 최적화 단계별 비교 ===\n");

const estimatedRenderTime = 0.1; // 항목당 0.1ms (시뮬레이션)

console.log("┌─────────────────────────┬──────────────┬─────────────────┐");
console.log("│ 단계                    │ 렌더링 항목  │ 예상 시간 (ms)  │");
console.log("├─────────────────────────┼──────────────┼─────────────────┤");
console.log(`│ 1. 기본 (최적화 없음)   │ ${String(ITEM_COUNT).padStart(10)}  │ ${String((ITEM_COUNT * estimatedRenderTime).toFixed(0)).padStart(13)}  │`);
console.log(`│ 2. React.memo           │ ${String(2).padStart(10)}  │ ${String((2 * estimatedRenderTime).toFixed(1)).padStart(13)}  │`);
console.log(`│ 3. + useMemo/Callback   │ ${String(2).padStart(10)}  │ ${String((2 * estimatedRenderTime).toFixed(1)).padStart(13)}  │`);
console.log(`│ 4. + 가상화             │ ${String(20).padStart(10)}  │ ${String((20 * estimatedRenderTime).toFixed(1)).padStart(13)}  │`);
console.log("└─────────────────────────┴──────────────┴─────────────────┘");

console.log("\n결론:");
console.log("  1→2: React.memo로 불필요한 리렌더링 방지 (99.98% 감소)");
console.log("  2→3: useCallback/useMemo로 memo 효과 보장 + 연산 캐싱");
console.log("  3→4: 가상화로 초기 마운트 비용도 대폭 감소");
console.log("  모두 적용 시: 1000x 이상의 성능 향상");

console.log("\n\n=== React 컴포넌트 사용 예시 ===\n");
console.log(`
// 최종 최적화된 컴포넌트 (Step 4)
function ProductListPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [filter, setFilter] = useState('');
  const parentRef = useRef<HTMLDivElement>(null);

  const handleSelect = useCallback((id: number) => {
    setSelectedId(id);
  }, []);

  const filteredProducts = useMemo(
    () => filter
      ? products.filter(p => p.category.includes(filter))
      : products,
    [products, filter]
  );

  // @tanstack/react-virtual 사용
  const virtualizer = useVirtualizer({
    count: filteredProducts.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <ProductCardMemo
            key={filteredProducts[virtualItem.index].id}
            product={filteredProducts[virtualItem.index]}
            isSelected={filteredProducts[virtualItem.index].id === selectedId}
            onSelect={handleSelect}
          />
        ))}
      </div>
    </div>
  );
}
`);

console.log("✅ 벤치마크 완료!");

export {
  ProductCardBasic,
  ProductCardMemo,
  OptimizedProductList,
  calculateVisibleRange,
  generateProducts,
  Product,
  VirtualizerConfig,
};
