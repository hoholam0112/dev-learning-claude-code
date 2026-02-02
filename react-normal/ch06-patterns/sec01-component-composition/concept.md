# 섹션 01: 컴포넌트 분리와 합성

## 학습 목표

- 컴포넌트를 분리해야 하는 시점과 기준을 이해한다
- 상속 대신 합성(Composition)을 사용하는 이유를 안다
- `children` prop을 활용한 유연한 레이아웃 패턴을 익힌다
- 상태 끌어올리기(Lifting State Up) 패턴을 이해한다
- Container/Presentational 패턴의 기본 개념을 안다
- Prop Drilling 문제와 해결 방향을 파악한다

---

## 핵심 개념

### 1. 컴포넌트 분리 기준 (단일 책임 원칙)

컴포넌트는 **하나의 역할**만 담당해야 합니다. 소프트웨어 설계의 단일 책임 원칙(Single Responsibility Principle)을 React에 적용한 것입니다.

**분리가 필요한 신호들:**

- 컴포넌트 코드가 50줄을 넘기기 시작할 때
- 하나의 컴포넌트가 2개 이상의 역할을 수행할 때
- 같은 UI 패턴이 여러 곳에서 반복될 때
- 컴포넌트 이름이 너무 포괄적일 때 (예: `Dashboard`, `Page`)

**나쁜 예 - 하나의 컴포넌트에 모든 것을 넣음:**

```jsx
// 역할이 너무 많은 컴포넌트
function UserDashboard() {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState({});

  // 사용자 정보 로딩 로직...
  // 주문 목록 로딩 로직...
  // 통계 계산 로직...

  return (
    <div>
      {/* 사용자 프로필 영역 */}
      <div className="profile">...</div>
      {/* 주문 목록 영역 */}
      <div className="orders">...</div>
      {/* 통계 차트 영역 */}
      <div className="stats">...</div>
    </div>
  );
}
```

**좋은 예 - 역할별로 분리:**

```jsx
// 각 컴포넌트가 하나의 역할만 담당
function UserDashboard() {
  return (
    <div>
      <UserProfile />
      <OrderList />
      <StatsChart />
    </div>
  );
}

function UserProfile() {
  const [user, setUser] = useState(null);
  // 사용자 관련 로직만 처리
  return <div className="profile">...</div>;
}

function OrderList() {
  const [orders, setOrders] = useState([]);
  // 주문 관련 로직만 처리
  return <div className="orders">...</div>;
}
```

### 2. 합성(Composition) vs 상속(Inheritance)

React에서는 **상속보다 합성을 권장**합니다. React 공식 문서에서도 상속이 필요한 경우를 찾지 못했다고 말합니다.

**상속 방식 (비추천):**

상속은 "is-a" 관계를 만듭니다. `FancyButton`은 `Button`이다. 이 방식은 클래스 기반이며 React의 함수형 컴포넌트와 맞지 않습니다.

**합성 방식 (추천):**

합성은 "has-a" 관계를 만듭니다. `FancyButton`은 `Button`을 포함한다.

```jsx
// 합성: 작은 컴포넌트를 조합하여 복잡한 컴포넌트를 만듦
function FancyButton({ children, icon }) {
  return (
    <button className="fancy-button">
      {icon && <span className="icon">{icon}</span>}
      {children}
    </button>
  );
}

// 사용
<FancyButton icon="★">클릭하세요</FancyButton>
```

합성의 장점:
- 더 유연하고 예측 가능한 코드
- 컴포넌트 간 결합도가 낮음
- 테스트하기 쉬움

### 3. children 패턴 (유연한 레이아웃)

`children`은 React에서 가장 중요한 합성 도구입니다. 컴포넌트 태그 사이에 넣는 모든 것이 `children` prop으로 전달됩니다.

**기본 사용법:**

```jsx
// 카드 레이아웃 컴포넌트
function Card({ title, children }) {
  return (
    <div className="card">
      <h2 className="card-title">{title}</h2>
      <div className="card-body">
        {children}  {/* 어떤 내용이든 들어올 수 있음 */}
      </div>
    </div>
  );
}

// 다양한 내용을 Card 안에 넣을 수 있음
<Card title="사용자 정보">
  <p>이름: 홍길동</p>
  <p>나이: 25</p>
</Card>

<Card title="주문 목록">
  <OrderTable data={orders} />
</Card>
```

**슬롯 패턴 (여러 children):**

하나의 `children`으로 부족할 때, 이름이 있는 prop으로 여러 영역을 나눌 수 있습니다.

```jsx
// 여러 슬롯을 가진 레이아웃
function PageLayout({ header, sidebar, children, footer }) {
  return (
    <div className="page">
      <header>{header}</header>
      <div className="content">
        <aside>{sidebar}</aside>
        <main>{children}</main>
      </div>
      <footer>{footer}</footer>
    </div>
  );
}

// 사용: 각 영역에 다른 컴포넌트를 전달
<PageLayout
  header={<Navigation />}
  sidebar={<Sidebar />}
  footer={<Footer />}
>
  <MainContent />
</PageLayout>
```

### 4. 상태 끌어올리기 (Lifting State Up)

두 개 이상의 컴포넌트가 같은 데이터를 공유해야 할 때, 그 상태를 **가장 가까운 공통 부모**로 올리는 패턴입니다.

**문제 상황:**

```jsx
// TemperatureInput이 두 개 있고, 서로의 값을 알아야 함
function TemperatureInput() {
  // 각자 독립적인 상태 - 서로 동기화 불가!
  const [temp, setTemp] = useState('');
  return <input value={temp} onChange={e => setTemp(e.target.value)} />;
}
```

**해결: 상태를 부모로 끌어올리기**

```jsx
// 부모 컴포넌트에서 상태를 관리
function TemperatureCalculator() {
  const [celsius, setCelsius] = useState('');

  // 섭씨에서 화씨를 계산
  const fahrenheit = celsius ? (parseFloat(celsius) * 9/5 + 32).toString() : '';

  return (
    <div>
      {/* 부모의 상태와 변경 함수를 자식에게 전달 */}
      <TemperatureInput
        label="섭씨"
        value={celsius}
        onChange={setCelsius}
      />
      <TemperatureInput
        label="화씨"
        value={fahrenheit}
        onChange={(f) => setCelsius(((parseFloat(f) - 32) * 5/9).toString())}
      />
    </div>
  );
}

// 자식은 상태를 소유하지 않음 - 제어 컴포넌트
function TemperatureInput({ label, value, onChange }) {
  return (
    <label>
      {label}:
      <input value={value} onChange={e => onChange(e.target.value)} />
    </label>
  );
}
```

**핵심 원칙:**
- 상태를 가능한 한 아래쪽(사용하는 컴포넌트 가까이)에 두되
- 여러 컴포넌트가 공유하는 상태는 공통 부모로 올림
- 부모 → 자식 방향으로 데이터가 흐름 (단방향 데이터 흐름)

### 5. Container/Presentational 패턴 (간소화)

이 패턴은 **로직(데이터 처리)**과 **표현(UI 렌더링)**을 분리하는 설계 방법입니다. 과거 클래스 컴포넌트 시대에 매우 인기 있었고, 커스텀 Hook이 등장한 후에는 엄격하게 따르지 않아도 되지만 개념 자체는 여전히 유용합니다.

```jsx
// Container: 데이터를 가져오고 로직을 처리
function UserListContainer() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers().then(data => {
      setUsers(data);
      setLoading(false);
    });
  }, []);

  // Presentational 컴포넌트에 데이터만 전달
  return <UserList users={users} loading={loading} />;
}

// Presentational: 데이터를 받아서 보여주기만 함
function UserList({ users, loading }) {
  if (loading) return <p>로딩 중...</p>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

**현대적 대안 - 커스텀 Hook:**

```jsx
// 커스텀 Hook으로 로직 분리 (sec02에서 자세히 다룸)
function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers().then(data => {
      setUsers(data);
      setLoading(false);
    });
  }, []);

  return { users, loading };
}

// 하나의 컴포넌트에서 Hook을 사용
function UserList() {
  const { users, loading } = useUsers();
  if (loading) return <p>로딩 중...</p>;
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### 6. Prop Drilling 문제와 해결 방향

**Prop Drilling**이란 깊이 중첩된 컴포넌트에 데이터를 전달하기 위해 중간 컴포넌트들이 사용하지도 않는 prop을 계속 전달하는 현상입니다.

```jsx
// Prop Drilling 예시 - theme이 3단계를 거쳐 전달됨
function App() {
  const [theme, setTheme] = useState("dark");
  return <Layout theme={theme} />;        // Layout은 theme을 사용하지 않음
}

function Layout({ theme }) {
  return <Sidebar theme={theme} />;       // Sidebar도 theme을 사용하지 않음
}

function Sidebar({ theme }) {
  return <ThemeButton theme={theme} />;   // 실제 사용하는 곳
}

function ThemeButton({ theme }) {
  return <button className={theme}>테마 변경</button>;
}
```

**문제점:**
- 중간 컴포넌트들이 불필요한 prop을 전달해야 함
- prop 이름이 바뀌면 모든 중간 컴포넌트를 수정해야 함
- 코드가 복잡해지고 유지보수가 어려워짐

**해결 방향 (미리보기):**
- **컴포넌트 합성**: children을 활용하여 중간 단계를 줄임
- **Context API**: React 내장 기능으로 전역 상태 전달 (이후 챕터에서 학습)
- **상태 관리 라이브러리**: Redux, Zustand 등 (이후 챕터에서 학습)

합성으로 Prop Drilling을 줄이는 예:

```jsx
// 합성으로 개선 - children을 통해 직접 전달
function App() {
  const [theme, setTheme] = useState("dark");
  return (
    <Layout>
      <Sidebar>
        <ThemeButton theme={theme} />  {/* 직접 전달! */}
      </Sidebar>
    </Layout>
  );
}

function Layout({ children }) {
  return <div className="layout">{children}</div>;
}

function Sidebar({ children }) {
  return <aside className="sidebar">{children}</aside>;
}
```

---

## 코드로 이해하기

아래는 위 개념들을 종합적으로 활용한 예시입니다.

```jsx
// 종합 예제: 상품 목록 앱

// 1. Presentational 컴포넌트: UI만 담당
function ProductCard({ product, onAddToCart }) {
  return (
    <Card title={product.name}>
      <p>가격: {product.price}원</p>
      <button onClick={() => onAddToCart(product.id)}>
        장바구니 담기
      </button>
    </Card>
  );
}

// 2. 재사용 가능한 레이아웃 컴포넌트
function Card({ title, children }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <div className="card-content">{children}</div>
    </div>
  );
}

// 3. 상태 끌어올리기: 부모에서 장바구니 상태 관리
function ProductPage() {
  const [cart, setCart] = useState([]);
  const [products] = useState([
    { id: 1, name: "노트북", price: 1200000 },
    { id: 2, name: "마우스", price: 35000 },
  ]);

  const handleAddToCart = (productId) => {
    setCart(prev => [...prev, productId]);
  };

  return (
    <PageLayout
      header={<h1>쇼핑몰</h1>}
      sidebar={<CartSummary count={cart.length} />}
    >
      {products.map(p => (
        <ProductCard
          key={p.id}
          product={p}
          onAddToCart={handleAddToCart}
        />
      ))}
    </PageLayout>
  );
}
```

---

## 주의 사항

| 항목 | 설명 |
|------|------|
| 과도한 분리 주의 | 너무 작게 쪼개면 오히려 코드 추적이 어려워짐. 의미 있는 단위로 분리할 것 |
| 성급한 추상화 금지 | 처음부터 완벽한 구조를 만들려 하지 말 것. 반복이 보일 때 리팩토링 |
| children 타입 주의 | children에는 문자열, JSX, 배열, null 등 다양한 값이 올 수 있음 |
| 상태 위치 신중하게 | 상태를 너무 위로 올리면 불필요한 리렌더링 발생. 필요한 만큼만 올릴 것 |
| Prop Drilling 2~3단계는 OK | 모든 prop 전달을 문제로 볼 필요 없음. 3단계 이상일 때 개선 고려 |

---

## 정리

| 패턴 | 핵심 | 사용 시점 |
|------|------|----------|
| 컴포넌트 분리 | 단일 책임 원칙 적용 | 역할이 2개 이상이거나 코드가 길어질 때 |
| 합성 (Composition) | 작은 컴포넌트를 조합 | 상속 대신 항상 사용 |
| children 패턴 | 동적 내용 삽입 | 레이아웃, 래퍼 컴포넌트 |
| 상태 끌어올리기 | 공유 상태를 부모로 이동 | 형제 컴포넌트 간 데이터 공유 |
| Container/Presentational | 로직과 UI 분리 | 복잡한 데이터 처리가 있는 컴포넌트 |
| Prop Drilling 해결 | 합성, Context, 상태 관리 | 3단계 이상 prop 전달 시 |

---

## 다음 단계

다음 섹션 **sec02-custom-hooks**에서는 컴포넌트 로직을 재사용 가능한 Hook으로 추출하는 방법을 배웁니다. Container/Presentational 패턴의 현대적 대안인 커스텀 Hook을 깊이 있게 다룹니다.
