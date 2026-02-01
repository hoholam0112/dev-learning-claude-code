/**
 * 챕터 01 - 연습 문제 모범 답안
 *
 * 실행 방법:
 *   npx tsx practice/solution.tsx
 */

// ============================================================
// 문제 1: Fiber 트리 직렬화
// ============================================================

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
  phase: "begin" | "complete";
}

/**
 * Element 트리를 Fiber 트리로 변환합니다.
 * 핵심: 자식들은 child → sibling 체인으로 연결됩니다.
 */
function buildFiberTree(
  element: SimpleElement,
  parentFiber: SimpleFiber | null = null
): SimpleFiber {
  const fiber: SimpleFiber = {
    type: element.type,
    child: null,
    sibling: null,
    return: parentFiber,
  };

  // 자식 Element들을 Fiber로 변환하고 연결
  let prevChildFiber: SimpleFiber | null = null;

  for (const childElement of element.children) {
    const childFiber = buildFiberTree(childElement, fiber);

    if (prevChildFiber === null) {
      // 첫 번째 자식 → parent.child로 연결
      fiber.child = childFiber;
    } else {
      // 나머지 자식 → 이전 형제의 sibling으로 연결
      prevChildFiber.sibling = childFiber;
    }

    prevChildFiber = childFiber;
  }

  return fiber;
}

/**
 * Fiber 트리를 React의 작업 루프(performUnitOfWork)와
 * 동일한 순서로 순회합니다.
 *
 * 순회 알고리즘:
 * 1. 현재 노드 begin
 * 2. child가 있으면 child로 이동
 * 3. child가 없으면 현재 노드 complete
 * 4. sibling이 있으면 sibling으로 이동 (1번으로)
 * 5. sibling이 없으면 parent로 올라가서 complete (4번 반복)
 */
function traverseFiber(root: SimpleFiber): TraversalStep[] {
  const steps: TraversalStep[] = [];
  let current: SimpleFiber | null = root;
  let depth = 0;

  // begin: 루트 노드
  steps.push({ type: root.type, depth: 0, phase: "begin" });

  while (current !== null) {
    // child가 있으면 child로 이동
    if (current.child) {
      current = current.child;
      depth++;
      steps.push({ type: current.type, depth, phase: "begin" });
      continue;
    }

    // 루트에 도달하면 루트 complete 후 종료
    if (current === root) {
      steps.push({ type: current.type, depth, phase: "complete" });
      break;
    }

    // child가 없으면 complete
    steps.push({ type: current.type, depth, phase: "complete" });

    // sibling이 있으면 sibling으로 이동
    while (current !== null && current !== root && !current.sibling) {
      current = current.return;
      depth--;
      if (current && current !== root) {
        steps.push({ type: current.type, depth, phase: "complete" });
      }
    }

    if (current === root) {
      steps.push({ type: current.type, depth, phase: "complete" });
      break;
    }

    if (current?.sibling) {
      current = current.sibling;
      steps.push({ type: current.type, depth, phase: "begin" });
    }
  }

  return steps;
}

// 테스트
console.log("╔══════════════════════════════════════════╗");
console.log("║ 문제 1: Fiber 트리 직렬화               ║");
console.log("╚══════════════════════════════════════════╝\n");

const testElement: SimpleElement = {
  type: "App",
  children: [
    {
      type: "Header",
      children: [{ type: "Logo", children: [] }],
    },
    {
      type: "Main",
      children: [
        { type: "Article", children: [] },
        { type: "Sidebar", children: [] },
      ],
    },
    {
      type: "Footer",
      children: [],
    },
  ],
};

const fiberTree = buildFiberTree(testElement);
const steps = traverseFiber(fiberTree);

console.log("순회 결과:");
steps.forEach((step) => {
  const indent = "  ".repeat(step.depth);
  const arrow = step.phase === "begin" ? "▶" : "◀";
  console.log(`  ${arrow} ${indent}${step.type} (${step.phase})`);
});

// ============================================================
// 문제 2: Key 기반 리스트 Diff 최적화
// ============================================================

interface ListItem {
  key: string;
  value: string;
}

type Operation =
  | { type: "INSERT"; key: string; value: string; index: number }
  | { type: "DELETE"; key: string }
  | { type: "MOVE"; key: string; fromIndex: number; toIndex: number }
  | { type: "UPDATE"; key: string; oldValue: string; newValue: string };

/**
 * 두 리스트를 비교하여 최소한의 DOM 조작 명령어를 생성합니다.
 *
 * 알고리즘:
 * 1. 이전 리스트를 key 기반 Map으로 인덱싱
 * 2. 새 리스트를 순회하며 매칭/삽입 결정
 * 3. 매칭되지 않은 이전 항목은 삭제
 * 4. 위치 변경이 필요한 항목은 이동
 */
function diffList(oldList: ListItem[], newList: ListItem[]): Operation[] {
  const operations: Operation[] = [];

  // 이전 리스트 인덱싱
  const oldMap = new Map<string, { value: string; index: number }>();
  oldList.forEach((item, index) => {
    oldMap.set(item.key, { value: item.value, index });
  });

  // 새 리스트에서 사용된 key 추적
  const usedKeys = new Set<string>();

  // 새 리스트 순회
  newList.forEach((newItem, newIndex) => {
    usedKeys.add(newItem.key);

    const oldEntry = oldMap.get(newItem.key);

    if (!oldEntry) {
      // 이전 리스트에 없는 key → INSERT
      operations.push({
        type: "INSERT",
        key: newItem.key,
        value: newItem.value,
        index: newIndex,
      });
    } else {
      // 이전 리스트에 있는 key
      // 값이 변경되었으면 UPDATE
      if (oldEntry.value !== newItem.value) {
        operations.push({
          type: "UPDATE",
          key: newItem.key,
          oldValue: oldEntry.value,
          newValue: newItem.value,
        });
      }

      // 위치가 다르면 MOVE
      if (oldEntry.index !== newIndex) {
        operations.push({
          type: "MOVE",
          key: newItem.key,
          fromIndex: oldEntry.index,
          toIndex: newIndex,
        });
      }
    }
  });

  // 이전 리스트에만 있는 항목 → DELETE
  oldList.forEach((oldItem) => {
    if (!usedKeys.has(oldItem.key)) {
      operations.push({
        type: "DELETE",
        key: oldItem.key,
      });
    }
  });

  return operations;
}

// 테스트
console.log("\n\n╔══════════════════════════════════════════╗");
console.log("║ 문제 2: Key 기반 리스트 Diff             ║");
console.log("╚══════════════════════════════════════════╝\n");

const oldList: ListItem[] = [
  { key: "a", value: "Apple" },
  { key: "b", value: "Banana" },
  { key: "c", value: "Cherry" },
  { key: "d", value: "Date" },
];

const newList: ListItem[] = [
  { key: "c", value: "Cherry Updated" },
  { key: "a", value: "Apple" },
  { key: "e", value: "Elderberry" },
  { key: "d", value: "Date" },
];

const ops = diffList(oldList, newList);

console.log("이전 리스트:", oldList.map((i) => `${i.key}:${i.value}`).join(", "));
console.log("새 리스트:  ", newList.map((i) => `${i.key}:${i.value}`).join(", "));
console.log("\nDiff 결과:");

const opEmoji: Record<string, string> = {
  INSERT: "🟢 INSERT",
  DELETE: "🔴 DELETE",
  MOVE: "🔵 MOVE  ",
  UPDATE: "🟡 UPDATE",
};

ops.forEach((op) => {
  switch (op.type) {
    case "INSERT":
      console.log(
        `  ${opEmoji.INSERT} key="${op.key}" value="${op.value}" → 인덱스 ${op.index}`
      );
      break;
    case "DELETE":
      console.log(`  ${opEmoji.DELETE} key="${op.key}"`);
      break;
    case "MOVE":
      console.log(
        `  ${opEmoji.MOVE} key="${op.key}" 인덱스 ${op.fromIndex} → ${op.toIndex}`
      );
      break;
    case "UPDATE":
      console.log(
        `  ${opEmoji.UPDATE} key="${op.key}" "${op.oldValue}" → "${op.newValue}"`
      );
      break;
  }
});

// ============================================================
// 문제 3: useEffect 실행 시뮬레이터
// ============================================================

interface ComponentDef {
  name: string;
  children?: ComponentDef[];
  effects?: EffectDef[];
}

interface EffectDef {
  type: "effect" | "layoutEffect";
  deps?: string[];
}

interface EffectState {
  type: "effect" | "layoutEffect";
  deps?: string[];
  isSetup: boolean;
}

interface ComponentState {
  name: string;
  effects: EffectState[];
  children: string[];
  isMounted: boolean;
}

/**
 * React의 생명주기 실행 순서를 시뮬레이션합니다.
 *
 * 실행 순서:
 * 1. Render 단계: 모든 컴포넌트 render (DFS, top-down)
 * 2. Layout Effects: useLayoutEffect 콜백 (bottom-up)
 * 3. Browser Paint
 * 4. Passive Effects: useEffect 콜백 (bottom-up)
 */
class LifecycleSimulator {
  private log: string[] = [];
  private components = new Map<string, ComponentState>();
  private tree: ComponentDef[] = [];

  /** 마운트 시뮬레이션 */
  mount(componentTree: ComponentDef[]): void {
    this.tree = componentTree;
    this.log = [];

    // Phase 1: Render (DFS, top-down)
    this.renderPhase(componentTree);

    // Phase 2: Layout Effects (bottom-up)
    this.layoutEffectPhase(componentTree);

    // Phase 3: Paint
    this.log.push("[Paint]");

    // Phase 4: Passive Effects (bottom-up)
    this.passiveEffectPhase(componentTree);
  }

  /** 컴포넌트 업데이트 시뮬레이션 */
  update(componentName: string, _newProps?: any): void {
    const component = this.components.get(componentName);
    if (!component || !component.isMounted) {
      console.error(`컴포넌트 "${componentName}"가 마운트되지 않았습니다.`);
      return;
    }

    // Render
    this.log.push(`[Render] ${componentName}`);

    // 자식도 재렌더링
    const compDef = this.findComponentDef(this.tree, componentName);
    if (compDef?.children) {
      this.renderPhase(compDef.children);
    }

    // Layout Effect Cleanup → Setup (해당 컴포넌트만)
    component.effects
      .filter((e) => e.type === "layoutEffect")
      .forEach((effect) => {
        if (effect.isSetup && (!effect.deps || effect.deps === undefined)) {
          this.log.push(`[LayoutEffect Cleanup] ${componentName}`);
        }
        if (!effect.deps || effect.deps === undefined) {
          this.log.push(`[LayoutEffect] ${componentName}: setup`);
        }
      });

    // Paint
    this.log.push("[Paint]");

    // Passive Effect Cleanup → Setup
    component.effects
      .filter((e) => e.type === "effect")
      .forEach((effect) => {
        if (effect.isSetup && (!effect.deps || effect.deps === undefined)) {
          this.log.push(`[Effect Cleanup] ${componentName}`);
        }
        if (!effect.deps || effect.deps === undefined) {
          this.log.push(`[Effect] ${componentName}: setup`);
        }
      });
  }

  /** 컴포넌트 언마운트 시뮬레이션 */
  unmount(componentName: string): void {
    const component = this.components.get(componentName);
    if (!component) return;

    // 자식 먼저 언마운트 (bottom-up)
    const compDef = this.findComponentDef(this.tree, componentName);
    if (compDef?.children) {
      this.unmountChildren(compDef.children);
    }

    // Layout Effect Cleanup
    component.effects
      .filter((e) => e.type === "layoutEffect" && e.isSetup)
      .forEach(() => {
        this.log.push(`[LayoutEffect Cleanup] ${componentName}`);
      });

    // Passive Effect Cleanup
    component.effects
      .filter((e) => e.type === "effect" && e.isSetup)
      .forEach(() => {
        this.log.push(`[Effect Cleanup] ${componentName}`);
      });

    component.isMounted = false;
    this.log.push(`[Unmount] ${componentName}`);
  }

  /** 실행 로그 반환 */
  getLog(): string[] {
    return [...this.log];
  }

  /** 로그 초기화 */
  clearLog(): void {
    this.log = [];
  }

  // --- Private 메서드 ---

  /** Render 단계: DFS top-down 순서로 컴포넌트 함수 실행 */
  private renderPhase(defs: ComponentDef[]): void {
    for (const def of defs) {
      this.log.push(`[Render] ${def.name}`);

      const state: ComponentState = {
        name: def.name,
        effects: (def.effects ?? []).map((e) => ({
          ...e,
          isSetup: false,
        })),
        children: (def.children ?? []).map((c) => c.name),
        isMounted: true,
      };
      this.components.set(def.name, state);

      if (def.children) {
        this.renderPhase(def.children);
      }
    }
  }

  /** Layout Effect 단계: bottom-up 순서 */
  private layoutEffectPhase(defs: ComponentDef[]): void {
    for (const def of defs) {
      // 먼저 자식의 layout effects 실행
      if (def.children) {
        this.layoutEffectPhase(def.children);
      }

      // 현재 컴포넌트의 layout effects
      const state = this.components.get(def.name);
      if (state) {
        state.effects
          .filter((e) => e.type === "layoutEffect")
          .forEach((effect) => {
            this.log.push(`[LayoutEffect] ${def.name}: setup`);
            effect.isSetup = true;
          });
      }
    }
  }

  /** Passive Effect 단계: bottom-up 순서 */
  private passiveEffectPhase(defs: ComponentDef[]): void {
    for (const def of defs) {
      // 먼저 자식의 passive effects 실행
      if (def.children) {
        this.passiveEffectPhase(def.children);
      }

      // 현재 컴포넌트의 passive effects
      const state = this.components.get(def.name);
      if (state) {
        state.effects
          .filter((e) => e.type === "effect")
          .forEach((effect) => {
            this.log.push(`[Effect] ${def.name}: setup`);
            effect.isSetup = true;
          });
      }
    }
  }

  /** 자식 컴포넌트 언마운트 */
  private unmountChildren(defs: ComponentDef[]): void {
    for (const def of defs) {
      this.unmount(def.name);
    }
  }

  /** 컴포넌트 정의 찾기 */
  private findComponentDef(
    defs: ComponentDef[],
    name: string
  ): ComponentDef | null {
    for (const def of defs) {
      if (def.name === name) return def;
      if (def.children) {
        const found = this.findComponentDef(def.children, name);
        if (found) return found;
      }
    }
    return null;
  }
}

// 테스트
console.log("\n\n╔══════════════════════════════════════════╗");
console.log("║ 문제 3: useEffect 실행 시뮬레이터        ║");
console.log("╚══════════════════════════════════════════╝\n");

const simulator = new LifecycleSimulator();

simulator.mount([
  {
    name: "App",
    effects: [{ type: "effect", deps: [] }],
    children: [
      {
        name: "Header",
        effects: [{ type: "layoutEffect" }],
      },
      {
        name: "Content",
        effects: [
          { type: "effect", deps: ["data"] },
          { type: "layoutEffect", deps: [] },
        ],
      },
    ],
  },
]);

console.log("=== 마운트 시 실행 순서 ===");
simulator.getLog().forEach((entry, i) => {
  console.log(`  ${String(i + 1).padStart(2)}. ${entry}`);
});

console.log("\n=== Content 업데이트 ===");
simulator.clearLog();
simulator.update("Content");
simulator.getLog().forEach((entry, i) => {
  console.log(`  ${String(i + 1).padStart(2)}. ${entry}`);
});

console.log("\n=== Header 언마운트 ===");
simulator.clearLog();
simulator.unmount("Header");
simulator.getLog().forEach((entry, i) => {
  console.log(`  ${String(i + 1).padStart(2)}. ${entry}`);
});

console.log("\n✅ 모든 테스트 완료!");

export {
  buildFiberTree,
  traverseFiber,
  diffList,
  LifecycleSimulator,
  SimpleElement,
  SimpleFiber,
  TraversalStep,
  ListItem,
  Operation,
  ComponentDef,
  EffectDef,
};
