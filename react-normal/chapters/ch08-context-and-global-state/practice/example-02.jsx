/**
 * 챕터 08 - 예제 02: useReducer로 장바구니 구현
 *
 * 핵심 개념:
 * - useReducer로 복잡한 상태(장바구니) 관리
 * - Context + useReducer 결합 패턴
 * - 액션 타입별 상태 업데이트 로직
 * - 파생 상태(총 금액, 총 수량) 계산
 *
 * 실행 방법:
 *   npx create-react-app cart-demo
 *   cd cart-demo
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 */

import React, { createContext, useContext, useReducer } from 'react';

// ══════════════════════════════════════════════
// 1. 상품 데이터 (실제로는 API에서 가져옴)
// ══════════════════════════════════════════════

const PRODUCTS = [
  { id: 1, name: 'React 완벽 가이드', price: 35000, category: '도서' },
  { id: 2, name: 'JavaScript 딥다이브', price: 42000, category: '도서' },
  { id: 3, name: '무선 마우스', price: 25000, category: '전자기기' },
  { id: 4, name: '기계식 키보드', price: 89000, category: '전자기기' },
  { id: 5, name: '노트북 스탠드', price: 45000, category: '액세서리' },
  { id: 6, name: 'USB-C 허브', price: 32000, category: '액세서리' },
];

// ══════════════════════════════════════════════
// 2. 장바구니 리듀서 (상태 업데이트 로직 집중)
// ══════════════════════════════════════════════

/**
 * cartReducer: 장바구니의 모든 상태 변경을 처리하는 리듀서 함수
 *
 * state 구조: { items: [{ product, quantity }] }
 *
 * 지원하는 액션:
 * - ADD_ITEM: 상품 추가 (이미 있으면 수량+1)
 * - REMOVE_ITEM: 상품 제거
 * - UPDATE_QUANTITY: 수량 변경
 * - CLEAR_CART: 장바구니 비우기
 */
function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingIndex = state.items.findIndex(
        (item) => item.product.id === action.payload.id
      );

      if (existingIndex >= 0) {
        // 이미 있는 상품이면 수량만 증가
        const updatedItems = state.items.map((item, index) =>
          index === existingIndex
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
        return { ...state, items: updatedItems };
      }

      // 새 상품 추가
      return {
        ...state,
        items: [...state.items, { product: action.payload, quantity: 1 }],
      };
    }

    case 'REMOVE_ITEM': {
      return {
        ...state,
        items: state.items.filter(
          (item) => item.product.id !== action.payload
        ),
      };
    }

    case 'UPDATE_QUANTITY': {
      const { productId, quantity } = action.payload;

      if (quantity <= 0) {
        // 수량이 0 이하면 제거
        return {
          ...state,
          items: state.items.filter(
            (item) => item.product.id !== productId
          ),
        };
      }

      return {
        ...state,
        items: state.items.map((item) =>
          item.product.id === productId
            ? { ...item, quantity }
            : item
        ),
      };
    }

    case 'CLEAR_CART': {
      return { ...state, items: [] };
    }

    default:
      throw new Error(`알 수 없는 액션 타입: ${action.type}`);
  }
}

// ══════════════════════════════════════════════
// 3. Cart Context + Provider
// ══════════════════════════════════════════════

const CartContext = createContext();

function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] });

  // 파생 상태: 총 수량
  const totalQuantity = state.items.reduce(
    (sum, item) => sum + item.quantity,
    0
  );

  // 파생 상태: 총 금액
  const totalPrice = state.items.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0
  );

  // 편의 함수들 (dispatch를 감싼 헬퍼 함수)
  const addItem = (product) => dispatch({ type: 'ADD_ITEM', payload: product });
  const removeItem = (productId) => dispatch({ type: 'REMOVE_ITEM', payload: productId });
  const updateQuantity = (productId, quantity) =>
    dispatch({ type: 'UPDATE_QUANTITY', payload: { productId, quantity } });
  const clearCart = () => dispatch({ type: 'CLEAR_CART' });

  return (
    <CartContext.Provider
      value={{
        items: state.items,
        totalQuantity,
        totalPrice,
        addItem,
        removeItem,
        updateQuantity,
        clearCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

// 커스텀 훅
function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart는 CartProvider 안에서만 사용할 수 있습니다');
  }
  return context;
}

// ══════════════════════════════════════════════
// 4. UI 컴포넌트들
// ══════════════════════════════════════════════

// 상품 카드
function ProductCard({ product }) {
  const { addItem, items } = useCart();
  const cartItem = items.find((item) => item.product.id === product.id);

  return (
    <div style={styles.productCard}>
      <div>
        <span style={styles.category}>{product.category}</span>
        <h3 style={styles.productName}>{product.name}</h3>
        <p style={styles.price}>{product.price.toLocaleString()}원</p>
      </div>
      <button
        onClick={() => addItem(product)}
        style={styles.addButton}
      >
        {cartItem ? `담기 (${cartItem.quantity}개)` : '장바구니 담기'}
      </button>
    </div>
  );
}

// 상품 목록
function ProductList() {
  return (
    <div>
      <h2>상품 목록</h2>
      <div style={styles.productGrid}>
        {PRODUCTS.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}

// 장바구니 아이템
function CartItem({ item }) {
  const { updateQuantity, removeItem } = useCart();

  return (
    <div style={styles.cartItem}>
      <div style={{ flex: 1 }}>
        <p style={{ margin: '0 0 4px 0', fontWeight: 'bold' }}>
          {item.product.name}
        </p>
        <p style={{ margin: 0, color: '#666', fontSize: '13px' }}>
          {item.product.price.toLocaleString()}원
        </p>
      </div>

      {/* 수량 조절 */}
      <div style={styles.quantityControl}>
        <button
          onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
          style={styles.quantityButton}
        >
          -
        </button>
        <span style={styles.quantityValue}>{item.quantity}</span>
        <button
          onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
          style={styles.quantityButton}
        >
          +
        </button>
      </div>

      {/* 소계 */}
      <p style={{ minWidth: '80px', textAlign: 'right', fontWeight: 'bold' }}>
        {(item.product.price * item.quantity).toLocaleString()}원
      </p>

      {/* 삭제 버튼 */}
      <button
        onClick={() => removeItem(item.product.id)}
        style={styles.removeButton}
      >
        삭제
      </button>
    </div>
  );
}

// 장바구니 패널
function CartPanel() {
  const { items, totalQuantity, totalPrice, clearCart } = useCart();

  return (
    <div style={styles.cartPanel}>
      <div style={styles.cartHeader}>
        <h2>장바구니 ({totalQuantity}개)</h2>
        {items.length > 0 && (
          <button onClick={clearCart} style={styles.clearButton}>
            전체 삭제
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <p style={styles.emptyCart}>장바구니가 비어 있습니다</p>
      ) : (
        <>
          {items.map((item) => (
            <CartItem key={item.product.id} item={item} />
          ))}

          {/* 합계 */}
          <div style={styles.totalSection}>
            <span style={{ fontSize: '18px' }}>총 합계</span>
            <span style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
              {totalPrice.toLocaleString()}원
            </span>
          </div>

          <button style={styles.checkoutButton}>주문하기</button>
        </>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// 5. 메인 App
// ══════════════════════════════════════════════

function AppContent() {
  return (
    <div style={styles.container}>
      <h1>Context + useReducer 장바구니</h1>
      <p style={styles.description}>
        상품을 장바구니에 담아보세요. 모든 상태는 useReducer로 관리됩니다.
      </p>

      <div style={styles.layout}>
        <div style={styles.mainArea}>
          <ProductList />
        </div>
        <div style={styles.sideArea}>
          <CartPanel />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <CartProvider>
      <AppContent />
    </CartProvider>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  container: {
    maxWidth: '900px',
    margin: '20px auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  description: {
    color: '#666',
    fontSize: '14px',
    marginBottom: '24px',
  },
  layout: {
    display: 'flex',
    gap: '24px',
    alignItems: 'flex-start',
  },
  mainArea: { flex: 2 },
  sideArea: { flex: 1, position: 'sticky', top: '20px' },
  productGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  productCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px',
    border: '1px solid #e0e0e0',
    borderRadius: '10px',
    backgroundColor: 'white',
  },
  category: {
    fontSize: '11px',
    color: '#999',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  productName: {
    margin: '4px 0',
    fontSize: '16px',
  },
  price: {
    margin: 0,
    color: '#1976d2',
    fontWeight: 'bold',
    fontSize: '15px',
  },
  addButton: {
    padding: '10px 20px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '13px',
    whiteSpace: 'nowrap',
  },
  cartPanel: {
    padding: '20px',
    border: '1px solid #e0e0e0',
    borderRadius: '12px',
    backgroundColor: 'white',
  },
  cartHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
  },
  clearButton: {
    padding: '6px 12px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  emptyCart: {
    textAlign: 'center',
    color: '#999',
    padding: '30px 0',
  },
  cartItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 0',
    borderBottom: '1px solid #f0f0f0',
  },
  quantityControl: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  quantityButton: {
    width: '28px',
    height: '28px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: '#f5f5f5',
    cursor: 'pointer',
    fontSize: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  quantityValue: {
    minWidth: '24px',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  removeButton: {
    padding: '4px 8px',
    backgroundColor: 'transparent',
    color: '#f44336',
    border: '1px solid #f44336',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  totalSection: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 0',
    marginTop: '12px',
    borderTop: '2px solid #333',
  },
  checkoutButton: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#4caf50',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    marginTop: '12px',
  },
};

export default App;
