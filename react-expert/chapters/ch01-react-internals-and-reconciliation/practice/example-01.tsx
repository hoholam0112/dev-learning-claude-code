/**
 * 챕터 01 - 예제 1: 미니 React 렌더러 구현
 *
 * React의 핵심 동작 원리를 이해하기 위한 간소화된 렌더러입니다.
 * 실제 React의 Fiber 아키텍처를 모방하여 다음을 구현합니다:
 * 1. createElement - React Element(가상 DOM 노드) 생성
 * 2. Fiber 트리 구축 - Element를 Fiber 노드로 변환
 * 3. 재조정(Reconciliation) - 이전/새 트리 비교
 * 4. 커밋(Commit) - 실제 DOM에 변경 적용
 *
 * 실행 방법:
 *   1. 이 파일을 HTML에서 사용하려면:
 *      - index.html을 만들고 <div id="root"></div>를 추가
 *      - npx vite 로 개발 서버 실행
 *   2. Node.js 환경에서 로직만 테스트하려면:
 *      - npx tsx practice/example-01.tsx
 *      (DOM API가 없으므로 renderToDOM 부분은 주석 처리 필요)
 */

// ============================================================
// 1. 타입 정의
// ============================================================

/** 미니 React Element 타입 */
interface MElement {
  type: string | Function;
  props: {
    children: MElement[];
    [key: string]: any;
  };
}

/** 미니 Fiber 노드 타입 */
interface MFiber {
  type: string | Function;
  props: {
    children: MElement[];
    [key: string]: any;
  };
  dom: HTMLElement | Text | null;
  parent: MFiber | null;
  child: MFiber | null;
  sibling: MFiber | null;
  alternate: MFiber | null;
  effectTag?: "PLACEMENT" | "UPDATE" | "DELETION";
  hooks?: MHook[];
}

/** Hook 상태 타입 */
interface MHook {
  state: any;
  queue: Array<(prev: any) => any>;
}

// ============================================================
// 2. Element 생성 (React.createElement 역할)
// ============================================================

/**
 * JSX가 컴파일되면 호출되는 함수.
 * React Element 객체를 생성합니다.
 */
function createElement(
  type: string | Function,
  props: Record<string, any> | null,
  ...children: any[]
): MElement {
  return {
    type,
    props: {
      ...props,
      children: children.map((child) =>
        typeof child === "object" ? child : createTextElement(child)
      ),
    },
  };
}

/** 텍스트 노드를 위한 특수 Element 생성 */
function createTextElement(text: string | number): MElement {
  return {
    type: "TEXT_ELEMENT",
    props: {
      nodeValue: String(text),
      children: [],
    },
  };
}

// ============================================================
// 3. DOM 생성 및 업데이트
// ============================================================

/** Fiber에서 실제 DOM 노드를 생성 */
function createDom(fiber: MFiber): HTMLElement | Text {
  const dom =
    fiber.type === "TEXT_ELEMENT"
      ? document.createTextNode("")
      : document.createElement(fiber.type as string);

  updateDom(dom, { children: [] } as any, fiber.props);
  return dom;
}

/** 이벤트 리스너 판별 */
const isEvent = (key: string) => key.startsWith("on");
/** 일반 속성 판별 (children, 이벤트 제외) */
const isProperty = (key: string) => key !== "children" && !isEvent(key);
/** 이전 값과 다른지 비교 */
const isNew =
  (prev: Record<string, any>, next: Record<string, any>) => (key: string) =>
    prev[key] !== next[key];
/** 새 props에 없는지 확인 */
const isGone =
  (_prev: Record<string, any>, next: Record<string, any>) => (key: string) =>
    !(key in next);

/** DOM 노드의 속성과 이벤트 리스너를 업데이트 */
function updateDom(
  dom: HTMLElement | Text,
  prevProps: Record<string, any>,
  nextProps: Record<string, any>
): void {
  // 이전 이벤트 리스너 제거 (변경되었거나 삭제된 것)
  Object.keys(prevProps)
    .filter(isEvent)
    .filter((key) => !(key in nextProps) || isNew(prevProps, nextProps)(key))
    .forEach((name) => {
      const eventType = name.toLowerCase().substring(2);
      (dom as HTMLElement).removeEventListener(eventType, prevProps[name]);
    });

  // 삭제된 속성 제거
  Object.keys(prevProps)
    .filter(isProperty)
    .filter(isGone(prevProps, nextProps))
    .forEach((name) => {
      (dom as any)[name] = "";
    });

  // 새로운/변경된 속성 설정
  Object.keys(nextProps)
    .filter(isProperty)
    .filter(isNew(prevProps, nextProps))
    .forEach((name) => {
      (dom as any)[name] = nextProps[name];
    });

  // 새로운 이벤트 리스너 추가
  Object.keys(nextProps)
    .filter(isEvent)
    .filter(isNew(prevProps, nextProps))
    .forEach((name) => {
      const eventType = name.toLowerCase().substring(2);
      (dom as HTMLElement).addEventListener(eventType, nextProps[name]);
    });
}

// ============================================================
// 4. 재조정(Reconciliation) 엔진
// ============================================================

/** 전역 상태 */
let nextUnitOfWork: MFiber | null = null;
let currentRoot: MFiber | null = null;
let wipRoot: MFiber | null = null;
let deletions: MFiber[] = [];
let wipFiber: MFiber | null = null;
let hookIndex: number = 0;

/**
 * Commit 단계: 수집된 효과(effect)를 실제 DOM에 적용합니다.
 * 이 단계는 동기적으로 수행되며 중단될 수 없습니다.
 */
function commitRoot(): void {
  // 삭제 대상 먼저 처리
  deletions.forEach(commitWork);
  // Fiber 트리를 순회하며 DOM에 반영
  if (wipRoot?.child) {
    commitWork(wipRoot.child);
  }
  // 현재 트리를 업데이트 (더블 버퍼링 스왑)
  currentRoot = wipRoot;
  wipRoot = null;
}

/** 개별 Fiber의 효과를 DOM에 적용 */
function commitWork(fiber: MFiber | null): void {
  if (!fiber) return;

  // 함수형 컴포넌트는 DOM이 없으므로 부모를 거슬러 올라감
  let domParentFiber = fiber.parent;
  while (domParentFiber && !domParentFiber.dom) {
    domParentFiber = domParentFiber.parent;
  }
  const domParent = domParentFiber?.dom;

  if (fiber.effectTag === "PLACEMENT" && fiber.dom != null) {
    // 새 노드 삽입
    domParent?.appendChild(fiber.dom);
    console.log(`[COMMIT] PLACEMENT: <${fiber.type}>`);
  } else if (fiber.effectTag === "UPDATE" && fiber.dom != null) {
    // 기존 노드 업데이트
    updateDom(fiber.dom, fiber.alternate?.props ?? { children: [] }, fiber.props);
    console.log(`[COMMIT] UPDATE: <${fiber.type}>`);
  } else if (fiber.effectTag === "DELETION") {
    // 노드 삭제
    commitDeletion(fiber, domParent as HTMLElement);
    console.log(`[COMMIT] DELETION: <${fiber.type}>`);
    return; // 삭제 시 자식은 재귀하지 않음
  }

  commitWork(fiber.child);
  commitWork(fiber.sibling);
}

/** 삭제 시 DOM 노드가 있는 자식을 찾아서 제거 */
function commitDeletion(fiber: MFiber, domParent: HTMLElement): void {
  if (fiber.dom) {
    domParent.removeChild(fiber.dom);
  } else if (fiber.child) {
    commitDeletion(fiber.child, domParent);
  }
}

/**
 * 작업 루프: requestIdleCallback을 사용하여
 * 브라우저가 유휴 상태일 때 Fiber 작업을 처리합니다.
 */
function workLoop(deadline: IdleDeadline): void {
  let shouldYield = false;

  while (nextUnitOfWork && !shouldYield) {
    // 다음 작업 단위(Fiber) 처리
    nextUnitOfWork = performUnitOfWork(nextUnitOfWork);
    // 남은 시간이 1ms 미만이면 브라우저에 제어권 반환
    shouldYield = deadline.timeRemaining() < 1;
  }

  // 모든 작업이 완료되면 커밋 단계 실행
  if (!nextUnitOfWork && wipRoot) {
    commitRoot();
  }

  requestIdleCallback(workLoop);
}

// 작업 루프 시작 (브라우저 환경에서만)
if (typeof requestIdleCallback !== "undefined") {
  requestIdleCallback(workLoop);
}

/**
 * 개별 Fiber 작업 단위 처리 (beginWork + completeWork)
 * 반환값: 다음에 처리할 Fiber 노드
 */
function performUnitOfWork(fiber: MFiber): MFiber | null {
  const isFunctionComponent = fiber.type instanceof Function;

  if (isFunctionComponent) {
    updateFunctionComponent(fiber);
  } else {
    updateHostComponent(fiber);
  }

  // 다음 작업 단위 결정: child → sibling → uncle
  if (fiber.child) {
    return fiber.child;
  }

  let nextFiber: MFiber | null = fiber;
  while (nextFiber) {
    if (nextFiber.sibling) {
      return nextFiber.sibling;
    }
    nextFiber = nextFiber.parent;
  }

  return null;
}

/** 함수형 컴포넌트 처리 */
function updateFunctionComponent(fiber: MFiber): void {
  wipFiber = fiber;
  hookIndex = 0;
  wipFiber.hooks = [];

  // 함수형 컴포넌트 실행 → children 획득
  const children = [(fiber.type as Function)(fiber.props)];
  reconcileChildren(fiber, children);
}

/** 호스트(DOM) 컴포넌트 처리 */
function updateHostComponent(fiber: MFiber): void {
  if (!fiber.dom) {
    fiber.dom = createDom(fiber);
  }
  reconcileChildren(fiber, fiber.props.children);
}

/**
 * 재조정 핵심 로직:
 * 이전 Fiber 트리(alternate)와 새 Element를 비교하여
 * effectTag를 설정합니다.
 */
function reconcileChildren(parentFiber: MFiber, elements: MElement[]): void {
  let index = 0;
  let oldFiber = parentFiber.alternate?.child ?? null;
  let prevSibling: MFiber | null = null;

  while (index < elements.length || oldFiber != null) {
    const element = elements[index];
    let newFiber: MFiber | null = null;

    // 타입이 같은지 비교
    const sameType = oldFiber && element && element.type === oldFiber.type;

    if (sameType && oldFiber) {
      // 같은 타입 → UPDATE (DOM 노드 재사용)
      newFiber = {
        type: oldFiber.type,
        props: element.props,
        dom: oldFiber.dom,
        parent: parentFiber,
        child: null,
        sibling: null,
        alternate: oldFiber,
        effectTag: "UPDATE",
      };
      console.log(`[RECONCILE] UPDATE: <${oldFiber.type}>`);
    }

    if (element && !sameType) {
      // 새 요소 → PLACEMENT
      newFiber = {
        type: element.type,
        props: element.props,
        dom: null,
        parent: parentFiber,
        child: null,
        sibling: null,
        alternate: null,
        effectTag: "PLACEMENT",
      };
      console.log(`[RECONCILE] PLACEMENT: <${element.type}>`);
    }

    if (oldFiber && !sameType) {
      // 이전 노드 삭제 → DELETION
      oldFiber.effectTag = "DELETION";
      deletions.push(oldFiber);
      console.log(`[RECONCILE] DELETION: <${oldFiber.type}>`);
    }

    // 이전 Fiber의 다음 형제로 이동
    if (oldFiber) {
      oldFiber = oldFiber.sibling;
    }

    // Fiber 트리 연결
    if (index === 0) {
      parentFiber.child = newFiber;
    } else if (element && prevSibling) {
      prevSibling.sibling = newFiber;
    }

    prevSibling = newFiber;
    index++;
  }
}

// ============================================================
// 5. 미니 useState Hook
// ============================================================

/**
 * 간소화된 useState 구현.
 * 실제 React의 Hook은 Fiber의 memoizedState에 연결 리스트로 저장됩니다.
 */
function useState<T>(initial: T): [T, (action: T | ((prev: T) => T)) => void] {
  const oldHook = wipFiber?.alternate?.hooks?.[hookIndex];

  const hook: MHook = {
    state: oldHook ? oldHook.state : initial,
    queue: [],
  };

  // 이전 렌더링에서 큐잉된 액션 실행
  const actions = oldHook ? oldHook.queue : [];
  actions.forEach((action) => {
    hook.state = action(hook.state);
  });

  const setState = (action: T | ((prev: T) => T)) => {
    const actionFn =
      typeof action === "function"
        ? (action as (prev: T) => T)
        : () => action;

    hook.queue.push(actionFn);

    // 새 렌더링 예약 (wipRoot 재설정)
    wipRoot = {
      type: currentRoot!.type,
      props: currentRoot!.props,
      dom: currentRoot!.dom,
      parent: null,
      child: null,
      sibling: null,
      alternate: currentRoot,
    };
    nextUnitOfWork = wipRoot;
    deletions = [];
  };

  wipFiber!.hooks!.push(hook);
  hookIndex++;
  return [hook.state, setState];
}

// ============================================================
// 6. render 함수 (ReactDOM.render 역할)
// ============================================================

function render(element: MElement, container: HTMLElement): void {
  wipRoot = {
    type: "ROOT",
    props: {
      children: [element],
    },
    dom: container,
    parent: null,
    child: null,
    sibling: null,
    alternate: currentRoot,
  };
  deletions = [];
  nextUnitOfWork = wipRoot;
}

// ============================================================
// 7. 사용 예시
// ============================================================

/**
 * 아래는 브라우저 환경에서 사용할 수 있는 예시입니다.
 * Node.js 환경에서는 DOM API가 없으므로 구조만 확인하세요.
 */

// 함수형 컴포넌트 예시
function Counter({ initialCount }: { initialCount: number; children: MElement[] }) {
  const [count, setCount] = useState(initialCount);

  return createElement(
    "div",
    { className: "counter" },
    createElement("h2", null, `카운트: ${count}`),
    createElement(
      "button",
      { onClick: () => setCount((c: number) => c + 1) },
      "증가"
    ),
    createElement(
      "button",
      { onClick: () => setCount((c: number) => c - 1) },
      "감소"
    )
  );
}

// 브라우저 환경에서 실행
if (typeof document !== "undefined") {
  const container = document.getElementById("root");
  if (container) {
    const app = createElement(
      "div",
      null,
      createElement("h1", null, "미니 React 렌더러"),
      createElement(Counter, { initialCount: 0 } as any)
    );
    render(app, container);
    console.log("미니 React 렌더러가 시작되었습니다!");
  }
}

// Node.js 환경에서의 구조 확인용
console.log("\n=== 미니 React Element 구조 ===");
const testElement = createElement(
  "div",
  { id: "app" },
  createElement("h1", null, "Hello"),
  createElement("p", null, "World")
);
console.log(JSON.stringify(testElement, null, 2));

// 내보내기 (모듈로 사용 시)
export { createElement, render, useState, MElement, MFiber };
