# 챕터 01 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: Fiber 트리 직렬화 (⭐⭐⭐)

### 설명

주어진 React Element 트리를 Fiber 트리로 변환하고, 이를 순회하여 직렬화(serialize)하는 함수를 구현하세요. Fiber 트리는 `child`, `sibling`, `return` 포인터로 연결된 연결 리스트 구조이며, 이를 **DFS(깊이 우선 탐색)** 순서로 방문하여 각 노드의 정보를 배열로 반환해야 합니다.

### 요구 사항

1. `buildFiberTree(element: SimpleElement): SimpleFiber` 함수를 구현하세요.
   - `SimpleElement`를 받아 `SimpleFiber` 트리를 구축합니다.
   - `child`, `sibling`, `return` 포인터를 올바르게 연결해야 합니다.

2. `traverseFiber(root: SimpleFiber): TraversalStep[]` 함수를 구현하세요.
   - Fiber 트리를 React의 작업 루프와 동일한 순서(child → sibling → return)로 순회합니다.
   - 각 방문 노드의 `{ type, depth, phase }` 정보를 배열로 반환합니다.
   - `phase`는 `'begin'`(처음 방문) 또는 `'complete'`(자식 처리 완료 후)입니다.

```tsx
interface SimpleElement {
  type: string;
  children: SimpleElement[];
}

interface SimpleFiber {
  type: string;
  child: SimpleFiber | null;
  sibling: SimpleFiber | null;
  return: SimpleFiber | null;
}

interface TraversalStep {
  type: string;
  depth: number;
  phase: 'begin' | 'complete';
}
```

### 테스트 케이스

```tsx
const element: SimpleElement = {
  type: 'App',
  children: [
    {
      type: 'Header',
      children: [{ type: 'Logo', children: [] }],
    },
    {
      type: 'Main',
      children: [
        { type: 'Article', children: [] },
        { type: 'Sidebar', children: [] },
      ],
    },
    {
      type: 'Footer',
      children: [],
    },
  ],
};

// 예상 순회 결과 (일부):
// { type: 'App', depth: 0, phase: 'begin' }
// { type: 'Header', depth: 1, phase: 'begin' }
// { type: 'Logo', depth: 2, phase: 'begin' }
// { type: 'Logo', depth: 2, phase: 'complete' }
// { type: 'Header', depth: 1, phase: 'complete' }
// { type: 'Main', depth: 1, phase: 'begin' }
// ...
```

### 힌트
<details><summary>힌트 보기</summary>

- Fiber의 순회 순서는 다음과 같습니다:
  1. 현재 노드 방문 (begin)
  2. child가 있으면 child로 이동
  3. child가 없으면 complete 후 sibling으로 이동
  4. sibling도 없으면 return으로 올라가서 complete
- `while` 루프로 구현하면 재귀 없이 순회할 수 있습니다.
</details>

---

## 문제 2: Key 기반 리스트 Diff 최적화 (⭐⭐⭐⭐)

### 설명

리스트의 이전 상태와 새 상태를 비교하여 **최소한의 DOM 조작 명령어**를 생성하는 `diffList` 함수를 구현하세요. 이 함수는 React의 재조정 알고리즘 중 리스트 비교 부분을 모방합니다.

### 요구 사항

1. `diffList(oldList, newList)` 함수를 구현하세요.
2. 각 항목은 `{ key: string, value: string }` 형태입니다.
3. 반환값은 `Operation[]` 배열이며, 순서대로 실행하면 `oldList`가 `newList`로 변환됩니다.

```tsx
type Operation =
  | { type: 'INSERT'; key: string; value: string; index: number }
  | { type: 'DELETE'; key: string }
  | { type: 'MOVE'; key: string; fromIndex: number; toIndex: number }
  | { type: 'UPDATE'; key: string; oldValue: string; newValue: string };
```

4. 최적화 기준:
   - key가 동일한 항목은 재사용 (이동으로 처리)
   - value가 변경된 항목은 UPDATE
   - 없어진 항목은 DELETE
   - 새로 추가된 항목은 INSERT

### 테스트 케이스

```tsx
const oldList = [
  { key: 'a', value: 'Apple' },
  { key: 'b', value: 'Banana' },
  { key: 'c', value: 'Cherry' },
  { key: 'd', value: 'Date' },
];

const newList = [
  { key: 'c', value: 'Cherry Updated' },  // c가 맨 앞으로 이동 + 값 변경
  { key: 'a', value: 'Apple' },            // a 유지 (이동)
  { key: 'e', value: 'Elderberry' },       // e 새로 추가
  { key: 'd', value: 'Date' },             // d 유지 (이동)
];
// b는 삭제됨
```

### 힌트
<details><summary>힌트 보기</summary>

- 이전 리스트의 항목을 `Map<key, { value, index }>`로 인덱싱하세요.
- 새 리스트를 순회하며:
  - 이전에 있었던 key → MOVE (+ UPDATE if value changed)
  - 새로운 key → INSERT
- 이전 리스트에만 있는 key → DELETE
- 이동 최소화를 위해 LIS(Longest Increasing Subsequence)를 사용할 수 있지만, 기본 구현에서는 단순히 위치 비교로 충분합니다.
</details>

---

## 문제 3: useEffect 실행 시뮬레이터 (⭐⭐⭐⭐)

### 설명

React의 `useEffect`와 `useLayoutEffect`가 컴포넌트 생명주기에서 어떤 순서로 실행되는지를 시뮬레이션하는 시스템을 구현하세요. 실제 DOM이나 React 없이, 순수 TypeScript로 실행 순서를 재현합니다.

### 요구 사항

1. `LifecycleSimulator` 클래스를 구현하세요.
2. 다음 메서드를 포함해야 합니다:
   - `mount(componentTree: ComponentDef[])`: 초기 마운트 시뮬레이션
   - `update(componentName: string, newProps?: any)`: 특정 컴포넌트 업데이트
   - `unmount(componentName: string)`: 특정 컴포넌트 언마운트
   - `getLog(): string[]`: 실행 순서 로그 반환

3. 시뮬레이션해야 할 단계:
   - Render 단계: 컴포넌트 함수 실행 (출력: `"[Render] ComponentName"`)
   - Layout Effects: `useLayoutEffect` 콜백 (출력: `"[LayoutEffect] ComponentName: setup"`)
   - Paint: 브라우저 페인트 (출력: `"[Paint]"`)
   - Passive Effects: `useEffect` 콜백 (출력: `"[Effect] ComponentName: setup"`)
   - Cleanup: 이전 effect의 정리 함수 (출력: `"[Effect Cleanup] ComponentName"`)

```tsx
interface ComponentDef {
  name: string;
  children?: ComponentDef[];
  effects?: EffectDef[];
}

interface EffectDef {
  type: 'effect' | 'layoutEffect';
  deps?: string[]; // 의존성 (문자열 표현)
}
```

### 테스트 케이스

```tsx
const simulator = new LifecycleSimulator();

simulator.mount([
  {
    name: 'App',
    effects: [{ type: 'effect', deps: [] }],
    children: [
      {
        name: 'Header',
        effects: [{ type: 'layoutEffect' }],
      },
      {
        name: 'Content',
        effects: [
          { type: 'effect', deps: ['data'] },
          { type: 'layoutEffect', deps: [] },
        ],
      },
    ],
  },
]);

// 예상 로그:
// [Render] App
// [Render] Header
// [Render] Content
// [LayoutEffect] Header: setup
// [LayoutEffect] Content: setup
// [Paint]
// [Effect] App: setup
// [Effect] Content: setup
```

### 힌트
<details><summary>힌트 보기</summary>

- React의 실행 순서를 기억하세요:
  1. 모든 컴포넌트의 render가 먼저 실행 (DFS 순서)
  2. Layout effects는 자식 → 부모 순서 (bottom-up)
  3. 브라우저 페인트
  4. Passive effects (useEffect)는 자식 → 부모 순서
- Cleanup은 새 effect가 실행되기 전에 수행됩니다.
- `deps`가 빈 배열이면 마운트 시에만 실행, `undefined`면 매 렌더링마다 실행됩니다.
</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 Fiber 순회 순서와 Commit 단계의 세부 순서가 핵심입니다.
