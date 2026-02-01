/**
 * 챕터 04 - 예제 1: TanStack Query + Zustand 전자상거래 앱
 *
 * 서버 상태(TanStack Query)와 클라이언트 상태(Zustand)를
 * 명확히 분리하는 아키텍처를 보여줍니다.
 *
 * 실행 방법:
 *   npx tsx practice/example-01.tsx
 *
 * 브라우저 환경에서 실제 사용:
 *   npm install @tanstack/react-query zustand
 *   React 프로젝트에서 import하여 사용
 */

// ============================================================
// 1. 타입 정의
// ============================================================

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  imageUrl: string;
  stock: number;
}

interface CartItem {
  productId: string;
  quantity: number;
}

interface CartState {
  items: CartItem[];
  addItem: (productId: string, quantity?: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  getTotalItems: () => number;
  getTotalPrice: (products: Map<string, Product>) => number;
}

interface UIState {
  isSidebarOpen: boolean;
  isCartOpen: boolean;
  selectedCategory: string | null;
  sortBy: "price-asc" | "price-desc" | "name" | "newest";
  searchQuery: string;
  toggleSidebar: () => void;
  toggleCart: () => void;
  setCategory: (category: string | null) => void;
  setSortBy: (sort: UIState["sortBy"]) => void;
  setSearchQuery: (query: string) => void;
}

// ============================================================
// 2. Zustand Store 구현 (클라이언트 상태)
// ============================================================

/**
 * 장바구니 Store
 *
 * Zustand의 create 함수를 시뮬레이션합니다.
 * 실제 프로젝트에서는 zustand의 create를 사용합니다.
 */
function createCartStore(): CartState {
  let state: CartState;

  const listeners = new Set<() => void>();

  function notifyListeners() {
    listeners.forEach((l) => l());
  }

  state = {
    items: [],

    addItem: (productId: string, quantity: number = 1) => {
      const existing = state.items.find((item) => item.productId === productId);
      if (existing) {
        state.items = state.items.map((item) =>
          item.productId === productId
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        state.items = [...state.items, { productId, quantity }];
      }
      notifyListeners();
    },

    removeItem: (productId: string) => {
      state.items = state.items.filter((item) => item.productId !== productId);
      notifyListeners();
    },

    updateQuantity: (productId: string, quantity: number) => {
      if (quantity <= 0) {
        state.removeItem(productId);
        return;
      }
      state.items = state.items.map((item) =>
        item.productId === productId ? { ...item, quantity } : item
      );
      notifyListeners();
    },

    clearCart: () => {
      state.items = [];
      notifyListeners();
    },

    getTotalItems: () => {
      return state.items.reduce((sum, item) => sum + item.quantity, 0);
    },

    getTotalPrice: (products: Map<string, Product>) => {
      return state.items.reduce((sum, item) => {
        const product = products.get(item.productId);
        return sum + (product ? product.price * item.quantity : 0);
      }, 0);
    },
  };

  return state;
}

/**
 * UI 상태 Store
 */
function createUIStore(): UIState {
  const listeners = new Set<() => void>();
  function notifyListeners() {
    listeners.forEach((l) => l());
  }

  const state: UIState = {
    isSidebarOpen: true,
    isCartOpen: false,
    selectedCategory: null,
    sortBy: "newest",
    searchQuery: "",

    toggleSidebar: () => {
      state.isSidebarOpen = !state.isSidebarOpen;
      notifyListeners();
    },
    toggleCart: () => {
      state.isCartOpen = !state.isCartOpen;
      notifyListeners();
    },
    setCategory: (category) => {
      state.selectedCategory = category;
      notifyListeners();
    },
    setSortBy: (sort) => {
      state.sortBy = sort;
      notifyListeners();
    },
    setSearchQuery: (query) => {
      state.searchQuery = query;
      notifyListeners();
    },
  };

  return state;
}

// ============================================================
// 3. TanStack Query 시뮬레이션 (서버 상태)
// ============================================================

/**
 * 서버 API 시뮬레이션
 */
const mockProducts: Product[] = [
  { id: "1", name: "무선 키보드", price: 89000, category: "전자기기", imageUrl: "/kb.jpg", stock: 50 },
  { id: "2", name: "게이밍 마우스", price: 65000, category: "전자기기", imageUrl: "/mouse.jpg", stock: 30 },
  { id: "3", name: "USB-C 허브", price: 45000, category: "전자기기", imageUrl: "/hub.jpg", stock: 0 },
  { id: "4", name: "모니터 암", price: 120000, category: "가구", imageUrl: "/arm.jpg", stock: 15 },
  { id: "5", name: "스탠딩 데스크", price: 450000, category: "가구", imageUrl: "/desk.jpg", stock: 8 },
  { id: "6", name: "프로그래밍 서적", price: 35000, category: "도서", imageUrl: "/book.jpg", stock: 100 },
  { id: "7", name: "TypeScript 서적", price: 38000, category: "도서", imageUrl: "/ts.jpg", stock: 75 },
  { id: "8", name: "에르고노믹 의자", price: 680000, category: "가구", imageUrl: "/chair.jpg", stock: 5 },
];

async function fetchProducts(params: {
  category?: string | null;
  sort?: string;
  search?: string;
}): Promise<Product[]> {
  // 네트워크 지연 시뮬레이션
  await new Promise((resolve) => setTimeout(resolve, 100));

  let results = [...mockProducts];

  // 카테고리 필터
  if (params.category) {
    results = results.filter((p) => p.category === params.category);
  }

  // 검색
  if (params.search) {
    const query = params.search.toLowerCase();
    results = results.filter((p) => p.name.toLowerCase().includes(query));
  }

  // 정렬
  switch (params.sort) {
    case "price-asc":
      results.sort((a, b) => a.price - b.price);
      break;
    case "price-desc":
      results.sort((a, b) => b.price - a.price);
      break;
    case "name":
      results.sort((a, b) => a.name.localeCompare(b.name));
      break;
  }

  return results;
}

async function fetchProduct(id: string): Promise<Product | null> {
  await new Promise((resolve) => setTimeout(resolve, 50));
  return mockProducts.find((p) => p.id === id) ?? null;
}

/**
 * TanStack Query의 queryKey 설계 패턴
 *
 * 계층적 구조로 설계하면 캐시 무효화가 쉬워집니다:
 * ['products'] - 모든 상품 관련 쿼리 무효화
 * ['products', 'list', { category, sort }] - 특정 조건의 목록
 * ['products', 'detail', productId] - 특정 상품 상세
 */
interface QueryKeyFactory {
  all: readonly string[];
  lists: () => readonly string[];
  list: (params: Record<string, any>) => readonly (string | Record<string, any>)[];
  details: () => readonly string[];
  detail: (id: string) => readonly string[];
}

const productKeys: QueryKeyFactory = {
  all: ["products"] as const,
  lists: () => ["products", "list"] as const,
  list: (params) => ["products", "list", params] as const,
  details: () => ["products", "detail"] as const,
  detail: (id) => ["products", "detail", id] as const,
};

// ============================================================
// 4. React 컴포넌트에서의 사용 패턴 (의사 코드)
// ============================================================

/**
 * 실제 React 컴포넌트에서의 사용법을 보여주는 의사 코드입니다.
 *
 * ```tsx
 * // zustand store
 * const useCartStore = create<CartState>((set, get) => ({
 *   items: [],
 *   addItem: (productId, quantity = 1) => set((state) => ({
 *     items: state.items.some(i => i.productId === productId)
 *       ? state.items.map(i =>
 *           i.productId === productId
 *             ? { ...i, quantity: i.quantity + quantity }
 *             : i
 *         )
 *       : [...state.items, { productId, quantity }]
 *   })),
 *   // ...
 * }));
 *
 * // 컴포넌트
 * function ProductList() {
 *   // UI 상태 (Zustand)
 *   const category = useUIStore((s) => s.selectedCategory);
 *   const sortBy = useUIStore((s) => s.sortBy);
 *
 *   // 서버 상태 (TanStack Query)
 *   const { data: products, isLoading } = useQuery({
 *     queryKey: productKeys.list({ category, sortBy }),
 *     queryFn: () => fetchProducts({ category, sort: sortBy }),
 *     staleTime: 5 * 60 * 1000,
 *   });
 *
 *   // 클라이언트 액션 (Zustand)
 *   const addToCart = useCartStore((s) => s.addItem);
 *
 *   if (isLoading) return <Skeleton />;
 *
 *   return (
 *     <div>
 *       {products?.map((product) => (
 *         <ProductCard
 *           key={product.id}
 *           product={product}
 *           onAddToCart={() => addToCart(product.id)}
 *         />
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */

// ============================================================
// 5. 데모 실행
// ============================================================

console.log("╔══════════════════════════════════════════════════════════╗");
console.log("║ TanStack Query + Zustand 전자상거래 아키텍처             ║");
console.log("╚══════════════════════════════════════════════════════════╝\n");

// --- Store 생성 ---
const cartStore = createCartStore();
const uiStore = createUIStore();

// --- queryKey 패턴 ---
console.log("=== QueryKey 패턴 ===\n");
console.log("productKeys.all:", JSON.stringify(productKeys.all));
console.log("productKeys.lists():", JSON.stringify(productKeys.lists()));
console.log("productKeys.list({ category: '전자기기' }):", JSON.stringify(productKeys.list({ category: "전자기기" })));
console.log("productKeys.detail('1'):", JSON.stringify(productKeys.detail("1")));

console.log("\n캐시 무효화 시나리오:");
console.log("  상품 수정 후 → invalidateQueries({ queryKey: productKeys.all })");
console.log("  → ['products']로 시작하는 모든 쿼리가 무효화됩니다.");

// --- 서버 상태 테스트 ---
console.log("\n\n=== 서버 상태 (API 호출 시뮬레이션) ===\n");

async function runServerStateDemo() {
  console.log("1. 전체 상품 조회:");
  const allProducts = await fetchProducts({});
  allProducts.forEach((p) =>
    console.log(`   ${p.id}. ${p.name} - ${p.price.toLocaleString()}원 (${p.category})`)
  );

  console.log("\n2. 카테고리 필터 (전자기기):");
  const electronics = await fetchProducts({ category: "전자기기" });
  electronics.forEach((p) =>
    console.log(`   ${p.name} - ${p.price.toLocaleString()}원`)
  );

  console.log("\n3. 가격 오름차순 정렬:");
  const sorted = await fetchProducts({ sort: "price-asc" });
  sorted.forEach((p) =>
    console.log(`   ${p.name} - ${p.price.toLocaleString()}원`)
  );

  console.log("\n4. 검색 (서적):");
  const searchResults = await fetchProducts({ search: "서적" });
  searchResults.forEach((p) =>
    console.log(`   ${p.name} - ${p.price.toLocaleString()}원`)
  );
}

// --- 클라이언트 상태 테스트 ---
function runClientStateDemo() {
  console.log("\n\n=== 클라이언트 상태 (Zustand Store) ===\n");

  console.log("1. 장바구니에 상품 추가:");
  cartStore.addItem("1", 2);
  console.log(`   무선 키보드 x2 추가 → 장바구니: ${cartStore.getTotalItems()}개`);

  cartStore.addItem("5", 1);
  console.log(`   스탠딩 데스크 x1 추가 → 장바구니: ${cartStore.getTotalItems()}개`);

  cartStore.addItem("1", 1);
  console.log(`   무선 키보드 x1 추가 → 장바구니: ${cartStore.getTotalItems()}개 (기존 수량 증가)`);

  console.log("\n2. 장바구니 상태:");
  const productMap = new Map(mockProducts.map((p) => [p.id, p]));
  cartStore.items.forEach((item) => {
    const product = productMap.get(item.productId)!;
    console.log(
      `   ${product.name} x${item.quantity} = ${(product.price * item.quantity).toLocaleString()}원`
    );
  });
  console.log(`   총액: ${cartStore.getTotalPrice(productMap).toLocaleString()}원`);

  console.log("\n3. 수량 변경:");
  cartStore.updateQuantity("1", 1);
  console.log(
    `   무선 키보드 수량 → 1개, 총 ${cartStore.getTotalItems()}개`
  );

  console.log("\n4. UI 상태:");
  console.log(`   사이드바: ${uiStore.isSidebarOpen ? "열림" : "닫힘"}`);
  uiStore.toggleSidebar();
  console.log(`   사이드바 토글 → ${uiStore.isSidebarOpen ? "열림" : "닫힘"}`);

  uiStore.setCategory("전자기기");
  console.log(`   카테고리 설정 → ${uiStore.selectedCategory}`);

  uiStore.setSortBy("price-asc");
  console.log(`   정렬 설정 → ${uiStore.sortBy}`);
}

// --- 아키텍처 요약 ---
function printArchitectureSummary() {
  console.log("\n\n=== 아키텍처 요약 ===\n");
  console.log(`
┌──────────────────────────────────────────────────────────────┐
│                        컴포넌트 레이어                        │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐       │
│  │ ProductList  │  │  CartPanel   │  │   Checkout    │       │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘       │
│         │                │                   │               │
├─────────┼────────────────┼───────────────────┼───────────────┤
│         │                │                   │               │
│  ┌──────┴──────┐  ┌──────┴───────┐  ┌───────┴───────┐       │
│  │ useQuery    │  │ useCartStore │  │ useMutation   │       │
│  │ (서버 상태) │  │ (클라이언트) │  │ (서버 변경)   │       │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘       │
│         │                │                   │               │
├─────────┼────────────────┼───────────────────┼───────────────┤
│         │                │                   │               │
│  ┌──────┴──────────────┐ │ ┌─────────────────┴──────┐       │
│  │  TanStack Query     │ │ │  TanStack Query        │       │
│  │  캐시 레이어        │ │ │  Mutation + 캐시 무효화 │       │
│  └──────┬──────────────┘ │ └─────────────────┬──────┘       │
│         │          ┌─────┴──┐                │               │
│         │          │Zustand │                │               │
│         │          │ Store  │                │               │
│         │          └────────┘                │               │
├─────────┼────────────────────────────────────┼───────────────┤
│         │          네트워크 레이어            │               │
│  ┌──────┴────────────────────────────────────┴──────┐       │
│  │                  REST API / GraphQL                │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
`);
}

// 실행
runServerStateDemo().then(() => {
  runClientStateDemo();
  printArchitectureSummary();
  console.log("✅ 전자상거래 아키텍처 데모 완료!");
});

export {
  Product,
  CartItem,
  CartState,
  UIState,
  createCartStore,
  createUIStore,
  fetchProducts,
  fetchProduct,
  productKeys,
};
