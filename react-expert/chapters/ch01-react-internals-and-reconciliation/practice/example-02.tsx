/**
 * 챕터 01 - 예제 2: 재조정 과정 시각화
 *
 * React의 재조정 알고리즘이 어떻게 이전 트리와 새 트리를
 * 비교하는지 단계별 로그로 확인합니다.
 *
 * 이 예제는 순수 TypeScript로 작성되어 Node.js에서 바로 실행 가능합니다.
 * DOM API 없이 재조정 로직만 분리하여 동작을 관찰합니다.
 *
 * 실행 방법:
 *   npx tsx practice/example-02.tsx
 */

// ============================================================
// 1. 타입 정의
// ============================================================

interface VNode {
  type: string;
  key: string | null;
  props: Record<string, any>;
  children: VNode[];
}

interface DiffResult {
  action: "CREATE" | "UPDATE" | "DELETE" | "MOVE";
  path: string;
  oldNode?: VNode;
  newNode?: VNode;
  details?: string;
}

// ============================================================
// 2. 가상 노드 생성 헬퍼
// ============================================================

function h(
  type: string,
  props: Record<string, any> & { key?: string } = {},
  ...children: (VNode | string)[]
): VNode {
  const { key = null, ...restProps } = props;
  return {
    type,
    key,
    props: restProps,
    children: children.map((child) =>
      typeof child === "string"
        ? { type: "TEXT", key: null, props: { value: child }, children: [] }
        : child
    ),
  };
}

// ============================================================
// 3. Diff 알고리즘 구현
// ============================================================

/**
 * 두 가상 DOM 트리를 비교하여 차이점(DiffResult) 목록을 생성합니다.
 * React의 재조정 알고리즘과 동일한 가정을 사용합니다:
 * - 다른 타입의 노드는 완전히 다른 트리로 간주
 * - key를 사용한 자식 비교 최적화
 */
function diff(
  oldNode: VNode | null,
  newNode: VNode | null,
  path: string = "root"
): DiffResult[] {
  const results: DiffResult[] = [];

  // 케이스 1: 이전 노드가 없음 → 새로 생성
  if (!oldNode && newNode) {
    results.push({
      action: "CREATE",
      path,
      newNode,
      details: `<${newNode.type}> 노드를 생성합니다.`,
    });
    return results;
  }

  // 케이스 2: 새 노드가 없음 → 삭제
  if (oldNode && !newNode) {
    results.push({
      action: "DELETE",
      path,
      oldNode,
      details: `<${oldNode.type}> 노드를 삭제합니다.`,
    });
    return results;
  }

  if (!oldNode || !newNode) return results;

  // 케이스 3: 타입이 다름 → 전체 교체 (삭제 + 생성)
  if (oldNode.type !== newNode.type) {
    results.push({
      action: "DELETE",
      path,
      oldNode,
      details: `타입 변경 감지: <${oldNode.type}> → <${newNode.type}>. 기존 서브트리를 제거합니다.`,
    });
    results.push({
      action: "CREATE",
      path,
      newNode,
      details: `새 타입 <${newNode.type}>의 서브트리를 생성합니다.`,
    });
    return results;
  }

  // 케이스 4: 같은 타입 → 속성 비교
  const propsChanged = diffProps(oldNode.props, newNode.props);
  if (propsChanged.length > 0) {
    results.push({
      action: "UPDATE",
      path,
      oldNode,
      newNode,
      details: `<${newNode.type}> 속성 업데이트: ${propsChanged.join(", ")}`,
    });
  }

  // 케이스 5: 자식 비교
  const childResults = diffChildren(oldNode.children, newNode.children, path);
  results.push(...childResults);

  return results;
}

/** props 차이 확인 */
function diffProps(
  oldProps: Record<string, any>,
  newProps: Record<string, any>
): string[] {
  const changes: string[] = [];
  const allKeys = new Set([...Object.keys(oldProps), ...Object.keys(newProps)]);

  for (const key of allKeys) {
    if (oldProps[key] !== newProps[key]) {
      if (!(key in oldProps)) {
        changes.push(`${key} 추가(=${JSON.stringify(newProps[key])})`);
      } else if (!(key in newProps)) {
        changes.push(`${key} 제거`);
      } else {
        changes.push(
          `${key}: ${JSON.stringify(oldProps[key])} → ${JSON.stringify(newProps[key])}`
        );
      }
    }
  }

  return changes;
}

/**
 * 자식 노드 비교 - key 유무에 따라 다른 전략 사용
 */
function diffChildren(
  oldChildren: VNode[],
  newChildren: VNode[],
  parentPath: string
): DiffResult[] {
  const results: DiffResult[] = [];
  const hasKeys = newChildren.some((c) => c.key !== null);

  if (hasKeys) {
    // key 기반 비교
    results.push(...diffChildrenWithKeys(oldChildren, newChildren, parentPath));
  } else {
    // 인덱스 기반 비교
    results.push(
      ...diffChildrenByIndex(oldChildren, newChildren, parentPath)
    );
  }

  return results;
}

/** 인덱스 기반 자식 비교 (key 없는 경우) */
function diffChildrenByIndex(
  oldChildren: VNode[],
  newChildren: VNode[],
  parentPath: string
): DiffResult[] {
  const results: DiffResult[] = [];
  const maxLen = Math.max(oldChildren.length, newChildren.length);

  console.log(`  📋 인덱스 기반 비교 (${parentPath}): ${oldChildren.length}개 → ${newChildren.length}개`);

  for (let i = 0; i < maxLen; i++) {
    const childPath = `${parentPath}/[${i}]`;
    results.push(...diff(oldChildren[i] ?? null, newChildren[i] ?? null, childPath));
  }

  return results;
}

/** key 기반 자식 비교 (key가 있는 경우) */
function diffChildrenWithKeys(
  oldChildren: VNode[],
  newChildren: VNode[],
  parentPath: string
): DiffResult[] {
  const results: DiffResult[] = [];

  console.log(`  🔑 Key 기반 비교 (${parentPath}): ${oldChildren.length}개 → ${newChildren.length}개`);

  // 이전 자식을 key로 인덱싱
  const oldKeyMap = new Map<string, VNode>();
  oldChildren.forEach((child) => {
    if (child.key) oldKeyMap.set(child.key, child);
  });

  const usedKeys = new Set<string>();

  // 새 자식 순회
  newChildren.forEach((newChild, index) => {
    const childPath = `${parentPath}/[key=${newChild.key}]`;

    if (newChild.key && oldKeyMap.has(newChild.key)) {
      // 기존 key에 매칭되는 노드 존재 → 재사용
      const oldChild = oldKeyMap.get(newChild.key)!;
      usedKeys.add(newChild.key);

      const oldIndex = oldChildren.indexOf(oldChild);
      if (oldIndex !== index) {
        results.push({
          action: "MOVE",
          path: childPath,
          oldNode: oldChild,
          newNode: newChild,
          details: `key="${newChild.key}" 노드를 인덱스 ${oldIndex} → ${index}로 이동`,
        });
      }

      // 이동 여부와 관계없이 내용 비교
      results.push(...diff(oldChild, newChild, childPath));
    } else {
      // 새 노드
      results.push({
        action: "CREATE",
        path: childPath,
        newNode: newChild,
        details: `key="${newChild.key}" 새 <${newChild.type}> 노드를 인덱스 ${index}에 삽입`,
      });
    }
  });

  // 매칭되지 않은 이전 노드 삭제
  oldChildren.forEach((oldChild) => {
    if (oldChild.key && !usedKeys.has(oldChild.key)) {
      results.push({
        action: "DELETE",
        path: `${parentPath}/[key=${oldChild.key}]`,
        oldNode: oldChild,
        details: `key="${oldChild.key}" <${oldChild.type}> 노드가 새 트리에 없어 삭제`,
      });
    }
  });

  return results;
}

// ============================================================
// 4. 시각화 출력
// ============================================================

function printTree(node: VNode, indent: string = ""): void {
  const keyStr = node.key ? ` key="${node.key}"` : "";
  const propsStr = Object.entries(node.props)
    .filter(([k]) => k !== "value")
    .map(([k, v]) => `${k}="${v}"`)
    .join(" ");
  const text = node.type === "TEXT" ? ` "${node.props.value}"` : "";

  console.log(`${indent}<${node.type}${keyStr}${propsStr ? " " + propsStr : ""}>${text}`);

  for (const child of node.children) {
    printTree(child, indent + "  ");
  }
}

function printResults(results: DiffResult[]): void {
  console.log("\n" + "=".repeat(60));
  console.log("📊 Diff 결과:");
  console.log("=".repeat(60));

  if (results.length === 0) {
    console.log("  변경 사항 없음 ✓");
    return;
  }

  const actionEmoji: Record<string, string> = {
    CREATE: "🟢",
    UPDATE: "🟡",
    DELETE: "🔴",
    MOVE: "🔵",
  };

  results.forEach((result, i) => {
    const emoji = actionEmoji[result.action] || "⚪";
    console.log(`  ${i + 1}. ${emoji} [${result.action}] ${result.path}`);
    console.log(`     ${result.details}`);
  });

  console.log("\n📈 요약:");
  const counts = results.reduce(
    (acc, r) => {
      acc[r.action] = (acc[r.action] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );
  Object.entries(counts).forEach(([action, count]) => {
    console.log(`  ${action}: ${count}건`);
  });
}

// ============================================================
// 5. 시나리오 테스트
// ============================================================

console.log("╔══════════════════════════════════════════════════════════╗");
console.log("║  React 재조정(Reconciliation) 알고리즘 시각화           ║");
console.log("╚══════════════════════════════════════════════════════════╝\n");

// --- 시나리오 1: 속성 변경 ---
console.log("━━━ 시나리오 1: 속성만 변경 ━━━");
const scenario1Old = h("div", { className: "old" }, h("p", {}, "Hello"));
const scenario1New = h("div", { className: "new" }, h("p", {}, "Hello"));

console.log("\n이전 트리:");
printTree(scenario1Old);
console.log("\n새 트리:");
printTree(scenario1New);

const results1 = diff(scenario1Old, scenario1New);
printResults(results1);

// --- 시나리오 2: key 없는 리스트에 맨 앞에 항목 추가 ---
console.log("\n\n━━━ 시나리오 2: key 없는 리스트 (맨 앞에 추가) ━━━");
const scenario2Old = h(
  "ul",
  {},
  h("li", {}, "사과"),
  h("li", {}, "바나나")
);
const scenario2New = h(
  "ul",
  {},
  h("li", {}, "체리"),   // 새로 추가
  h("li", {}, "사과"),
  h("li", {}, "바나나")
);

console.log("\n이전 트리:");
printTree(scenario2Old);
console.log("\n새 트리:");
printTree(scenario2New);

const results2 = diff(scenario2Old, scenario2New);
printResults(results2);
console.log("\n⚠️ key가 없어서 3개 모두 변경/생성으로 처리됩니다!");

// --- 시나리오 3: key가 있는 리스트에 맨 앞에 항목 추가 ---
console.log("\n\n━━━ 시나리오 3: key가 있는 리스트 (맨 앞에 추가) ━━━");
const scenario3Old = h(
  "ul",
  {},
  h("li", { key: "apple" }, "사과"),
  h("li", { key: "banana" }, "바나나")
);
const scenario3New = h(
  "ul",
  {},
  h("li", { key: "cherry" }, "체리"),    // 새로 추가
  h("li", { key: "apple" }, "사과"),
  h("li", { key: "banana" }, "바나나")
);

console.log("\n이전 트리:");
printTree(scenario3Old);
console.log("\n새 트리:");
printTree(scenario3New);

const results3 = diff(scenario3Old, scenario3New);
printResults(results3);
console.log("\n✅ key 덕분에 기존 노드를 재사용하고, 새 항목만 삽입합니다!");

// --- 시나리오 4: 타입 변경 (전체 서브트리 교체) ---
console.log("\n\n━━━ 시나리오 4: 타입 변경 ━━━");
const scenario4Old = h(
  "div",
  {},
  h("span", { className: "tag" }, "태그"),
  h("p", {}, "내용")
);
const scenario4New = h(
  "div",
  {},
  h("a", { href: "/link", className: "tag" }, "태그"),  // span → a
  h("p", {}, "내용 수정됨")
);

console.log("\n이전 트리:");
printTree(scenario4Old);
console.log("\n새 트리:");
printTree(scenario4New);

const results4 = diff(scenario4Old, scenario4New);
printResults(results4);

// --- 시나리오 5: key 기반 재정렬 ---
console.log("\n\n━━━ 시나리오 5: key 기반 재정렬 ━━━");
const scenario5Old = h(
  "ul",
  {},
  h("li", { key: "a" }, "A"),
  h("li", { key: "b" }, "B"),
  h("li", { key: "c" }, "C"),
  h("li", { key: "d" }, "D")
);
const scenario5New = h(
  "ul",
  {},
  h("li", { key: "d" }, "D"),   // d가 맨 앞으로
  h("li", { key: "a" }, "A"),
  h("li", { key: "c" }, "C"),   // b 제거, c 유지
);

console.log("\n이전 트리:");
printTree(scenario5Old);
console.log("\n새 트리:");
printTree(scenario5New);

const results5 = diff(scenario5Old, scenario5New);
printResults(results5);
console.log("\n✅ key 기반으로 최소한의 이동/삭제만 수행합니다!");

// ============================================================
// 6. 성능 비교 요약
// ============================================================

console.log("\n\n" + "=".repeat(60));
console.log("📊 key 유무에 따른 비교 요약");
console.log("=".repeat(60));
console.log(`
┌─────────────────────┬──────────────────────┬──────────────────────┐
│ 시나리오            │ key 없음             │ key 있음             │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ 맨 앞에 추가        │ 모든 항목 업데이트   │ 새 항목만 삽입       │
│ 중간 삭제           │ 뒤쪽 항목 모두 갱신  │ 해당 항목만 삭제     │
│ 순서 변경           │ 모든 항목 업데이트   │ 이동만 수행          │
│ DOM 재사용          │ 불가능               │ 가능                 │
│ 상태 보존           │ 불가능               │ 가능                 │
└─────────────────────┴──────────────────────┴──────────────────────┘
`);

export { h, diff, VNode, DiffResult };
