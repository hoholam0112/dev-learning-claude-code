/**
 * 챕터 08 - 예제 01: Compound Components 패턴 - 아코디언 & 탭 컴포넌트
 *
 * 이 예제는 Compound Components 패턴을 사용하여
 * 선언적이고 유연한 API를 가진 UI 컴포넌트를 구현합니다.
 *
 * 실행 방법:
 *   1. 프로젝트 생성:
 *      npm create vite@latest patterns-demo -- --template react-ts
 *      cd patterns-demo
 *
 *   2. 이 파일을 src/components/Accordion.tsx로 복사
 *
 *   3. App.tsx에서 import하여 사용:
 *      import { Accordion } from './components/Accordion';
 *
 *   4. 개발 서버 실행:
 *      npm run dev
 */

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useId,
  useMemo,
  type ReactNode,
} from 'react';

// ============================================================
// 1. Compound Components: Accordion
// ============================================================

// --- 타입 정의 ---

type AccordionType = 'single' | 'multiple';

interface AccordionContextValue {
  type: AccordionType;
  openItems: Set<string>;
  toggle: (value: string) => void;
}

interface AccordionItemContextValue {
  value: string;
  isOpen: boolean;
  triggerId: string;
  contentId: string;
}

interface AccordionProps {
  /** 단일 선택 또는 다중 선택 모드 */
  type?: AccordionType;
  /** 초기 열린 항목 (단일) */
  defaultValue?: string;
  /** 초기 열린 항목 (다중) */
  defaultValues?: string[];
  /** 외부 제어 모드 */
  value?: string | string[];
  /** 변경 콜백 */
  onValueChange?: (value: string | string[]) => void;
  children: ReactNode;
  className?: string;
}

interface AccordionItemProps {
  value: string;
  children: ReactNode;
  disabled?: boolean;
  className?: string;
}

interface AccordionTriggerProps {
  children: ReactNode;
  className?: string;
}

interface AccordionContentProps {
  children: ReactNode;
  className?: string;
}

// --- Context 생성 ---

const AccordionContext = createContext<AccordionContextValue | null>(null);
const AccordionItemContext = createContext<AccordionItemContextValue | null>(null);

/** Accordion Context 훅 */
function useAccordionContext(): AccordionContextValue {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error(
      'Accordion 하위 컴포넌트는 <Accordion> 내부에서 사용해야 합니다.'
    );
  }
  return context;
}

/** AccordionItem Context 훅 */
function useAccordionItemContext(): AccordionItemContextValue {
  const context = useContext(AccordionItemContext);
  if (!context) {
    throw new Error(
      'Accordion.Trigger/Content는 <Accordion.Item> 내부에서 사용해야 합니다.'
    );
  }
  return context;
}

// --- 메인 컴포넌트 ---

/**
 * Accordion 루트 컴포넌트
 *
 * 상태 관리를 담당하며 Context를 통해 하위 컴포넌트에 상태를 전달합니다.
 * 비제어(uncontrolled)와 제어(controlled) 모드를 모두 지원합니다.
 */
function AccordionRoot({
  type = 'single',
  defaultValue,
  defaultValues = [],
  value: controlledValue,
  onValueChange,
  children,
  className,
}: AccordionProps) {
  // 내부 상태 (비제어 모드)
  const [internalOpen, setInternalOpen] = useState<Set<string>>(() => {
    if (defaultValue) return new Set([defaultValue]);
    if (defaultValues.length > 0) return new Set(defaultValues);
    return new Set();
  });

  // 제어 모드 vs 비제어 모드
  const isControlled = controlledValue !== undefined;
  const openItems = isControlled
    ? new Set(Array.isArray(controlledValue) ? controlledValue : [controlledValue])
    : internalOpen;

  const toggle = useCallback(
    (itemValue: string) => {
      const newSet = new Set(openItems);

      if (newSet.has(itemValue)) {
        newSet.delete(itemValue);
      } else {
        if (type === 'single') {
          newSet.clear();
        }
        newSet.add(itemValue);
      }

      if (!isControlled) {
        setInternalOpen(newSet);
      }

      if (onValueChange) {
        const newValue = Array.from(newSet);
        onValueChange(type === 'single' ? newValue[0] ?? '' : newValue);
      }
    },
    [openItems, type, isControlled, onValueChange]
  );

  const contextValue = useMemo(
    () => ({ type, openItems, toggle }),
    [type, openItems, toggle]
  );

  return (
    <AccordionContext.Provider value={contextValue}>
      <div className={className} data-accordion-type={type}>
        {children}
      </div>
    </AccordionContext.Provider>
  );
}

/** 개별 아코디언 항목 */
function AccordionItem({
  value,
  children,
  disabled = false,
  className,
}: AccordionItemProps) {
  const { openItems } = useAccordionContext();
  const id = useId();
  const isOpen = openItems.has(value);

  const itemContext = useMemo(
    () => ({
      value,
      isOpen,
      triggerId: `${id}-trigger`,
      contentId: `${id}-content`,
    }),
    [value, isOpen, id]
  );

  return (
    <AccordionItemContext.Provider value={itemContext}>
      <div
        className={className}
        data-state={isOpen ? 'open' : 'closed'}
        data-disabled={disabled || undefined}
      >
        {children}
      </div>
    </AccordionItemContext.Provider>
  );
}

/** 아코디언 트리거 (토글 버튼) */
function AccordionTrigger({ children, className }: AccordionTriggerProps) {
  const { toggle } = useAccordionContext();
  const { value, isOpen, triggerId, contentId } = useAccordionItemContext();

  return (
    <h3>
      <button
        id={triggerId}
        type="button"
        className={className}
        onClick={() => toggle(value)}
        aria-expanded={isOpen}
        aria-controls={contentId}
        data-state={isOpen ? 'open' : 'closed'}
      >
        {children}
        <span aria-hidden="true">{isOpen ? '▲' : '▼'}</span>
      </button>
    </h3>
  );
}

/** 아코디언 콘텐츠 (접힘/펼침 영역) */
function AccordionContent({ children, className }: AccordionContentProps) {
  const { isOpen, triggerId, contentId } = useAccordionItemContext();

  return (
    <div
      id={contentId}
      role="region"
      className={className}
      aria-labelledby={triggerId}
      data-state={isOpen ? 'open' : 'closed'}
      hidden={!isOpen}
      style={{
        overflow: 'hidden',
        transition: 'max-height 0.3s ease',
        maxHeight: isOpen ? '500px' : '0',
      }}
    >
      <div style={{ padding: '16px' }}>{children}</div>
    </div>
  );
}

// --- Compound Component 합성 ---

/**
 * Accordion 최종 API
 *
 * 사용 예:
 * ```tsx
 * <Accordion type="single" defaultValue="item-1">
 *   <Accordion.Item value="item-1">
 *     <Accordion.Trigger>React란?</Accordion.Trigger>
 *     <Accordion.Content>
 *       UI를 구축하기 위한 JavaScript 라이브러리입니다.
 *     </Accordion.Content>
 *   </Accordion.Item>
 *   <Accordion.Item value="item-2">
 *     <Accordion.Trigger>TypeScript란?</Accordion.Trigger>
 *     <Accordion.Content>
 *       JavaScript에 타입 시스템을 추가한 언어입니다.
 *     </Accordion.Content>
 *   </Accordion.Item>
 * </Accordion>
 * ```
 */
export const Accordion = Object.assign(AccordionRoot, {
  Item: AccordionItem,
  Trigger: AccordionTrigger,
  Content: AccordionContent,
});

// ============================================================
// 2. Compound Components: Tabs
// ============================================================

// --- 타입 정의 ---

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (value: string) => void;
}

interface TabsProps {
  defaultValue: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: ReactNode;
  className?: string;
}

interface TabListProps {
  children: ReactNode;
  className?: string;
  'aria-label'?: string;
}

interface TabTriggerProps {
  value: string;
  children: ReactNode;
  disabled?: boolean;
  className?: string;
}

interface TabContentProps {
  value: string;
  children: ReactNode;
  className?: string;
}

// --- Context ---

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext(): TabsContextValue {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs 하위 컴포넌트는 <Tabs> 내부에서 사용해야 합니다.');
  }
  return context;
}

// --- 컴포넌트 ---

function TabsRoot({
  defaultValue,
  value: controlledValue,
  onValueChange,
  children,
  className,
}: TabsProps) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const isControlled = controlledValue !== undefined;
  const activeTab = isControlled ? controlledValue : internalValue;

  const setActiveTab = useCallback(
    (newValue: string) => {
      if (!isControlled) {
        setInternalValue(newValue);
      }
      onValueChange?.(newValue);
    },
    [isControlled, onValueChange]
  );

  const contextValue = useMemo(
    () => ({ activeTab, setActiveTab }),
    [activeTab, setActiveTab]
  );

  return (
    <TabsContext.Provider value={contextValue}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children, className, 'aria-label': ariaLabel }: TabListProps) {
  return (
    <div role="tablist" className={className} aria-label={ariaLabel}>
      {children}
    </div>
  );
}

function TabTrigger({
  value,
  children,
  disabled = false,
  className,
}: TabTriggerProps) {
  const { activeTab, setActiveTab } = useTabsContext();
  const isActive = activeTab === value;

  return (
    <button
      role="tab"
      type="button"
      className={className}
      aria-selected={isActive}
      aria-controls={`tabpanel-${value}`}
      id={`tab-${value}`}
      tabIndex={isActive ? 0 : -1}
      disabled={disabled}
      onClick={() => setActiveTab(value)}
      data-state={isActive ? 'active' : 'inactive'}
    >
      {children}
    </button>
  );
}

function TabContent({ value, children, className }: TabContentProps) {
  const { activeTab } = useTabsContext();
  const isActive = activeTab === value;

  if (!isActive) return null;

  return (
    <div
      role="tabpanel"
      className={className}
      id={`tabpanel-${value}`}
      aria-labelledby={`tab-${value}`}
      tabIndex={0}
    >
      {children}
    </div>
  );
}

/**
 * Tabs 최종 API
 *
 * 사용 예:
 * ```tsx
 * <Tabs defaultValue="overview">
 *   <Tabs.List aria-label="프로젝트 정보">
 *     <Tabs.Trigger value="overview">개요</Tabs.Trigger>
 *     <Tabs.Trigger value="code">코드</Tabs.Trigger>
 *     <Tabs.Trigger value="settings">설정</Tabs.Trigger>
 *   </Tabs.List>
 *   <Tabs.Content value="overview">개요 내용...</Tabs.Content>
 *   <Tabs.Content value="code">코드 내용...</Tabs.Content>
 *   <Tabs.Content value="settings">설정 내용...</Tabs.Content>
 * </Tabs>
 * ```
 */
export const Tabs = Object.assign(TabsRoot, {
  List: TabList,
  Trigger: TabTrigger,
  Content: TabContent,
});

// ============================================================
// 3. 사용 예시 컴포넌트
// ============================================================

export function CompoundComponentsDemo() {
  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '24px' }}>
      <h1>Compound Components 패턴 데모</h1>

      {/* 아코디언 예시 */}
      <section>
        <h2>아코디언 (단일 선택)</h2>
        <Accordion type="single" defaultValue="react">
          <Accordion.Item value="react">
            <Accordion.Trigger>React란 무엇인가?</Accordion.Trigger>
            <Accordion.Content>
              React는 Facebook에서 만든 사용자 인터페이스 구축을 위한
              JavaScript 라이브러리입니다. 컴포넌트 기반 아키텍처와
              가상 DOM을 통해 효율적인 UI 업데이트를 제공합니다.
            </Accordion.Content>
          </Accordion.Item>
          <Accordion.Item value="typescript">
            <Accordion.Trigger>TypeScript의 장점은?</Accordion.Trigger>
            <Accordion.Content>
              TypeScript는 정적 타입 검사를 통해 런타임 에러를 사전에
              방지하고, IDE의 자동완성과 리팩토링 지원을 강화합니다.
            </Accordion.Content>
          </Accordion.Item>
          <Accordion.Item value="nextjs">
            <Accordion.Trigger>Next.js는 언제 사용하나?</Accordion.Trigger>
            <Accordion.Content>
              SSR, SSG, ISR 등이 필요한 프로덕션 React 애플리케이션에
              적합합니다. 파일 기반 라우팅과 최적화 기능을 기본 제공합니다.
            </Accordion.Content>
          </Accordion.Item>
        </Accordion>
      </section>

      <hr style={{ margin: '32px 0' }} />

      {/* 아코디언 예시 (다중 선택) */}
      <section>
        <h2>아코디언 (다중 선택)</h2>
        <Accordion type="multiple" defaultValues={['item-1']}>
          <Accordion.Item value="item-1">
            <Accordion.Trigger>첫 번째 항목</Accordion.Trigger>
            <Accordion.Content>
              여러 항목을 동시에 열 수 있습니다.
            </Accordion.Content>
          </Accordion.Item>
          <Accordion.Item value="item-2">
            <Accordion.Trigger>두 번째 항목</Accordion.Trigger>
            <Accordion.Content>
              이 항목도 함께 열 수 있습니다.
            </Accordion.Content>
          </Accordion.Item>
        </Accordion>
      </section>

      <hr style={{ margin: '32px 0' }} />

      {/* 탭 예시 */}
      <section>
        <h2>탭 컴포넌트</h2>
        <Tabs defaultValue="html">
          <Tabs.List aria-label="웹 기술">
            <Tabs.Trigger value="html">HTML</Tabs.Trigger>
            <Tabs.Trigger value="css">CSS</Tabs.Trigger>
            <Tabs.Trigger value="js">JavaScript</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="html">
            <p>HTML은 웹 페이지의 구조를 정의하는 마크업 언어입니다.</p>
          </Tabs.Content>
          <Tabs.Content value="css">
            <p>CSS는 웹 페이지의 스타일을 정의하는 스타일시트 언어입니다.</p>
          </Tabs.Content>
          <Tabs.Content value="js">
            <p>JavaScript는 웹 페이지에 동적 기능을 추가하는 프로그래밍 언어입니다.</p>
          </Tabs.Content>
        </Tabs>
      </section>
    </div>
  );
}

export default CompoundComponentsDemo;
