# 챕터 03 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: 렌더링 최적화 진단 및 수정 (⭐⭐⭐)

### 설명

아래 코드에는 여러 가지 성능 문제가 있습니다. 각 문제를 식별하고 최적화하세요.

```tsx
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface UserListProps {
  users: User[];
  searchQuery: string;
}

function UserList({ users, searchQuery }: UserListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [sortField, setSortField] = useState<keyof User>('name');

  // 문제 1: 매 렌더링마다 필터링 + 정렬 실행
  const filteredUsers = users
    .filter(u => u.name.includes(searchQuery) || u.email.includes(searchQuery))
    .sort((a, b) => String(a[sortField]).localeCompare(String(b[sortField])));

  // 문제 2: 매 렌더링마다 새 객체 생성
  const stats = {
    total: filteredUsers.length,
    admins: filteredUsers.filter(u => u.role === 'admin').length,
    selected: selectedIds.size,
  };

  // 문제 3: 매 렌더링마다 새 함수 생성
  const handleToggle = (id: number) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // 문제 4: 매 렌더링마다 새 스타일 객체 생성
  const headerStyle = { padding: '16px', backgroundColor: '#f5f5f5' };

  return (
    <div>
      <div style={headerStyle}>
        <span>총 {stats.total}명 (관리자: {stats.admins}명, 선택: {stats.selected}명)</span>
      </div>
      <div>
        {filteredUsers.map(user => (
          <UserCard
            key={user.id}
            user={user}
            isSelected={selectedIds.has(user.id)}
            onToggle={handleToggle}
            style={{ margin: '8px' }}
          />
        ))}
      </div>
    </div>
  );
}

function UserCard({ user, isSelected, onToggle, style }: {
  user: User;
  isSelected: boolean;
  onToggle: (id: number) => void;
  style: React.CSSProperties;
}) {
  // 비용이 큰 렌더링 (아바타 생성 등)
  return (
    <div style={style} onClick={() => onToggle(user.id)}>
      <span>{user.name}</span>
      <span>{user.email}</span>
      {isSelected && <span>✓</span>}
    </div>
  );
}
```

### 요구 사항

1. 위 코드의 성능 문제 4가지 이상을 식별하세요.
2. 각 문제에 대해 최적화된 코드를 작성하세요.
3. 최적화 전후의 리렌더링 횟수를 비교 분석하세요.
4. `UserCard`에 `React.memo`를 적용하되, 모든 props의 참조 안정성을 보장하세요.

### 힌트
<details><summary>힌트 보기</summary>

- `useMemo`로 필터링/정렬 결과와 통계를 캐싱하세요.
- `useCallback`으로 `handleToggle` 함수의 참조를 안정화하세요.
- 스타일 객체는 컴포넌트 외부에 상수로 선언하거나 `useMemo`를 사용하세요.
- `UserCard`를 `React.memo`로 감싸세요.
- 인라인 스타일 `{{ margin: '8px' }}`도 매번 새 객체를 생성합니다.
</details>

---

## 문제 2: 가상 스크롤러 구현 (⭐⭐⭐⭐)

### 설명

`@tanstack/react-virtual` 같은 외부 라이브러리 없이, 기본적인 가상 스크롤러를 직접 구현하세요. 고정 높이 항목을 지원하며, 스크롤 위치에 따라 보이는 항목만 렌더링합니다.

### 요구 사항

1. `useVirtualScroll<T>(options)` Hook을 구현하세요:

```tsx
interface VirtualScrollOptions<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  overscan?: number;  // 기본값: 3
}

interface VirtualScrollResult<T> {
  virtualItems: Array<{
    index: number;
    item: T;
    style: React.CSSProperties;
  }>;
  totalHeight: number;
  containerProps: {
    onScroll: (e: React.UIEvent<HTMLDivElement>) => void;
    style: React.CSSProperties;
  };
  innerProps: {
    style: React.CSSProperties;
  };
  scrollToIndex: (index: number, align?: 'start' | 'center' | 'end') => void;
}
```

2. `VirtualList` 컴포넌트를 구현하세요:

```tsx
interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  height: number;
  renderItem: (item: T, index: number) => React.ReactNode;
}
```

3. 다음 기능을 구현하세요:
   - 스크롤 위치에 따른 보이는 항목 계산
   - overscan으로 스크롤 시 깜빡임 방지
   - `scrollToIndex`로 프로그래밍 방식의 스크롤
   - 컨테이너와 내부 래퍼의 스타일 자동 계산

### 테스트 케이스

```tsx
// 10,000개 항목의 가상 리스트
const items = Array.from({ length: 10000 }, (_, i) => ({
  id: i,
  text: `항목 ${i + 1}`,
}));

function App() {
  return (
    <VirtualList
      items={items}
      itemHeight={40}
      height={400}
      renderItem={(item) => (
        <div style={{ padding: '8px' }}>{item.text}</div>
      )}
    />
  );
}
```

### 힌트
<details><summary>힌트 보기</summary>

- 컨테이너는 `overflow: auto`로 스크롤 가능하게 합니다.
- 내부 래퍼의 높이를 `items.length * itemHeight`로 설정하여 스크롤바 크기를 정확히 만듭니다.
- 각 항목은 `position: absolute`로 배치하고, `top` 값을 `index * itemHeight`로 설정합니다.
- `onScroll` 이벤트에서 `scrollTop`을 읽어 보이는 범위를 재계산합니다.
- `scrollToIndex`는 `containerRef.current.scrollTop = index * itemHeight`로 구현합니다.
</details>

---

## 문제 3: 성능 모니터링 대시보드 구현 (⭐⭐⭐⭐)

### 설명

React 앱의 렌더링 성능을 실시간으로 모니터링하는 `PerformanceMonitor` 컴포넌트와 관련 Hook을 구현하세요. React의 `<Profiler>` API를 활용합니다.

### 요구 사항

1. `useRenderCount()` Hook: 컴포넌트의 렌더링 횟수를 추적합니다.

```tsx
function MyComponent() {
  const renderCount = useRenderCount();
  // renderCount는 매 렌더링마다 1씩 증가
}
```

2. `useRenderTime()` Hook: 컴포넌트의 렌더링 시간을 측정합니다.

```tsx
function MyComponent() {
  const { lastRenderTime, averageRenderTime, maxRenderTime } = useRenderTime();
}
```

3. `useWhyDidYouRender(componentName, props)` Hook: 리렌더링의 원인을 분석합니다.

```tsx
function MyComponent(props: Props) {
  useWhyDidYouRender('MyComponent', props);
  // 콘솔에 출력: "[MyComponent] 리렌더링 원인: name 변경 ('old' → 'new')"
}
```

4. `PerformanceMonitor` 컴포넌트: 자식 컴포넌트 트리의 렌더링 성능을 시각화합니다.

```tsx
<PerformanceMonitor
  threshold={16}  // 16ms 이상이면 경고
  onSlowRender={(info) => console.warn('느린 렌더링:', info)}
>
  <App />
</PerformanceMonitor>
```

5. 모든 성능 데이터는 전역 저장소에 수집되어 대시보드로 표시할 수 있어야 합니다.

### 힌트
<details><summary>힌트 보기</summary>

- `useRenderCount`: `useRef`로 카운터를 유지하고, 매 렌더링마다 증가시킵니다.
- `useRenderTime`: `useRef`로 시작 시간을 기록하고, `useEffect`에서 경과 시간을 계산합니다.
- `useWhyDidYouRender`: `useRef`로 이전 props를 저장하고, 현재 props와 비교합니다.
- `<Profiler>`의 `onRender` 콜백에서 `actualDuration`, `baseDuration` 등을 수집합니다.
- `performance.now()`로 정밀한 시간 측정이 가능합니다.
</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 "메모이제이션은 공짜가 아닙니다" 섹션과 "언제 사용해야 하는가" 플로차트를 참고하세요.
