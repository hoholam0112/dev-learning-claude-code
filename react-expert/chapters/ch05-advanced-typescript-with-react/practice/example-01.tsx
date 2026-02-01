/**
 * 챕터 05 - 예제 1: 제네릭 컴포넌트 라이브러리
 *
 * 타입 안전하면서도 유연한 제네릭 컴포넌트들을 구현합니다.
 * 각 컴포넌트는 제네릭 타입 T를 통해 다양한 데이터 타입과 함께 사용됩니다.
 *
 * 실행 방법:
 *   npx tsx practice/example-01.tsx
 */

import React from "react";

// ============================================================
// 1. 제네릭 List 컴포넌트
// ============================================================

/**
 * List<T> - 어떤 타입의 배열이든 렌더링할 수 있는 범용 리스트
 *
 * 핵심: T가 items에서 추론되면, renderItem과 keyExtractor의
 * 매개변수 타입도 자동으로 T가 됩니다.
 */
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string | number;
  onItemClick?: (item: T) => void;
  emptyMessage?: string;
  className?: string;
}

function List<T>({
  items,
  renderItem,
  keyExtractor,
  onItemClick,
  emptyMessage = "항목이 없습니다.",
}: ListProps<T>): React.ReactElement {
  if (items.length === 0) {
    return React.createElement("p", null, emptyMessage);
  }

  return React.createElement(
    "ul",
    null,
    items.map((item, index) =>
      React.createElement(
        "li",
        {
          key: keyExtractor(item),
          onClick: () => onItemClick?.(item),
        },
        renderItem(item, index)
      )
    )
  );
}

// ============================================================
// 2. 제네릭 DataTable 컴포넌트
// ============================================================

/**
 * DataTable<T> - 타입 안전한 테이블
 *
 * 핵심: Column의 key가 T의 키로 제한되고,
 * render 함수의 value 매개변수가 해당 키의 값 타입으로 추론됩니다.
 */
interface Column<T> {
  key: keyof T & string;
  header: string;
  width?: string;
  render?: (value: T[keyof T], item: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T extends Record<string, any>> {
  data: T[];
  columns: Column<T>[];
  keyField: keyof T & string;
  onRowClick?: (item: T) => void;
  sortBy?: keyof T & string;
  sortOrder?: "asc" | "desc";
  onSort?: (column: keyof T & string) => void;
}

function DataTable<T extends Record<string, any>>({
  data,
  columns,
  keyField,
  onRowClick,
  sortBy,
  sortOrder,
  onSort,
}: DataTableProps<T>): React.ReactElement {
  return React.createElement(
    "table",
    null,
    React.createElement(
      "thead",
      null,
      React.createElement(
        "tr",
        null,
        columns.map((col) =>
          React.createElement(
            "th",
            {
              key: col.key,
              onClick: col.sortable ? () => onSort?.(col.key) : undefined,
              style: { cursor: col.sortable ? "pointer" : "default", width: col.width },
            },
            col.header,
            sortBy === col.key ? (sortOrder === "asc" ? " ▲" : " ▼") : ""
          )
        )
      )
    ),
    React.createElement(
      "tbody",
      null,
      data.map((item) =>
        React.createElement(
          "tr",
          {
            key: String(item[keyField]),
            onClick: () => onRowClick?.(item),
          },
          columns.map((col) =>
            React.createElement(
              "td",
              { key: col.key },
              col.render
                ? col.render(item[col.key], item)
                : String(item[col.key])
            )
          )
        )
      )
    )
  );
}

// ============================================================
// 3. 제네릭 Select 컴포넌트
// ============================================================

/**
 * Select<T> - 타입 안전한 드롭다운 셀렉트
 *
 * 핵심: 선택된 값의 타입이 T로 보장됩니다.
 * onChange 콜백의 매개변수가 T 타입입니다.
 */
interface SelectProps<T> {
  options: T[];
  value: T | null;
  onChange: (value: T) => void;
  getLabel: (option: T) => string;
  getValue: (option: T) => string | number;
  placeholder?: string;
  disabled?: boolean;
}

function Select<T>({
  options,
  value,
  onChange,
  getLabel,
  getValue,
  placeholder = "선택하세요",
}: SelectProps<T>): React.ReactElement {
  const selectedValue = value ? getValue(value) : "";

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = options.find(
      (opt) => String(getValue(opt)) === e.target.value
    );
    if (selected) onChange(selected);
  };

  return React.createElement(
    "select",
    { value: String(selectedValue), onChange: handleChange },
    React.createElement("option", { value: "" }, placeholder),
    options.map((option) =>
      React.createElement(
        "option",
        { key: String(getValue(option)), value: String(getValue(option)) },
        getLabel(option)
      )
    )
  );
}

// ============================================================
// 4. 다형(Polymorphic) 컴포넌트
// ============================================================

/**
 * 다형 컴포넌트: "as" prop으로 렌더링할 HTML 요소를 지정
 *
 * <Button as="a" href="/home">홈</Button>  → <a> 렌더링, href prop 사용 가능
 * <Button as="button" type="submit">제출</Button> → <button> 렌더링
 */
type PolymorphicRef<E extends React.ElementType> =
  React.ComponentPropsWithRef<E>["ref"];

type PolymorphicComponentProps<
  E extends React.ElementType,
  Props = {}
> = Props &
  Omit<React.ComponentPropsWithoutRef<E>, keyof Props> & {
    as?: E;
  };

type PolymorphicComponentPropsWithRef<
  E extends React.ElementType,
  Props = {}
> = PolymorphicComponentProps<E, Props> & {
  ref?: PolymorphicRef<E>;
};

// Button 컴포넌트의 고유 props
interface ButtonOwnProps {
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

type ButtonProps<E extends React.ElementType = "button"> =
  PolymorphicComponentProps<E, ButtonOwnProps>;

/**
 * 다형 Button 컴포넌트
 *
 * 사용 예시:
 * <Button variant="primary">클릭</Button>                    → <button>
 * <Button as="a" href="/home" variant="secondary">홈</Button> → <a>
 * <Button as={Link} to="/dashboard">대시보드</Button>          → <Link>
 */
function Button<E extends React.ElementType = "button">({
  as,
  variant = "primary",
  size = "md",
  isLoading = false,
  children,
  ...restProps
}: ButtonProps<E>): React.ReactElement {
  const Component = as || "button";
  return React.createElement(
    Component,
    {
      ...restProps,
      "data-variant": variant,
      "data-size": size,
      disabled: isLoading || (restProps as any).disabled,
    },
    isLoading ? "로딩 중..." : children
  );
}

// ============================================================
// 5. 제네릭 Hook 패턴
// ============================================================

/**
 * useSelection<T> - 타입 안전한 단일/다중 선택 Hook
 */
interface UseSelectionOptions<T> {
  items: T[];
  keyExtractor: (item: T) => string | number;
  multiple?: boolean;
  initialSelection?: T[];
}

interface UseSelectionResult<T> {
  selectedItems: T[];
  selectedKeys: Set<string | number>;
  isSelected: (item: T) => boolean;
  toggle: (item: T) => void;
  select: (item: T) => void;
  deselect: (item: T) => void;
  selectAll: () => void;
  deselectAll: () => void;
}

function createSelection<T>(options: UseSelectionOptions<T>): UseSelectionResult<T> {
  const { items, keyExtractor, multiple = false, initialSelection = [] } = options;

  let selectedKeys = new Set<string | number>(
    initialSelection.map(keyExtractor)
  );

  const getSelectedItems = () =>
    items.filter((item) => selectedKeys.has(keyExtractor(item)));

  return {
    get selectedItems() {
      return getSelectedItems();
    },
    get selectedKeys() {
      return new Set(selectedKeys);
    },
    isSelected: (item: T) => selectedKeys.has(keyExtractor(item)),
    toggle: (item: T) => {
      const key = keyExtractor(item);
      if (selectedKeys.has(key)) {
        selectedKeys.delete(key);
      } else {
        if (!multiple) selectedKeys.clear();
        selectedKeys.add(key);
      }
    },
    select: (item: T) => {
      if (!multiple) selectedKeys.clear();
      selectedKeys.add(keyExtractor(item));
    },
    deselect: (item: T) => {
      selectedKeys.delete(keyExtractor(item));
    },
    selectAll: () => {
      if (multiple) {
        selectedKeys = new Set(items.map(keyExtractor));
      }
    },
    deselectAll: () => {
      selectedKeys.clear();
    },
  };
}

// ============================================================
// 6. 타입 레벨 유틸리티
// ============================================================

/**
 * 타입 레벨 유틸리티: React 컴포넌트 개발에 유용한 타입들
 */

// 컴포넌트의 props 타입 추출
type PropsOf<C extends React.ElementType> = React.ComponentPropsWithoutRef<C>;

// 이벤트 핸들러만 추출
type EventHandlers<T> = {
  [K in keyof T as K extends `on${string}` ? K : never]: T[K];
};

// 깊은 Readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// 특정 키만 필수로 변환
type RequireKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

// 특정 키만 Optional로 변환
type OptionalKeys<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// 객체의 값 타입 유니온
type ValueOf<T> = T[keyof T];

// ============================================================
// 7. 데모 실행
// ============================================================

console.log("╔══════════════════════════════════════════════════════════╗");
console.log("║ 제네릭 컴포넌트 라이브러리 - 타입 시스템 데모            ║");
console.log("╚══════════════════════════════════════════════════════════╝\n");

// --- 타입 추론 데모 ---
console.log("=== 1. 제네릭 타입 추론 ===\n");

interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user";
}

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
}

const users: User[] = [
  { id: 1, name: "김개발", email: "kim@dev.com", role: "admin" },
  { id: 2, name: "이프론트", email: "lee@front.com", role: "user" },
  { id: 3, name: "박풀스택", email: "park@full.com", role: "admin" },
];

const products: Product[] = [
  { id: "p1", name: "키보드", price: 89000, category: "전자기기" },
  { id: "p2", name: "마우스", price: 65000, category: "전자기기" },
  { id: "p3", name: "모니터", price: 450000, category: "디스플레이" },
];

console.log("List<User>의 keyExtractor: (user) => user.id");
console.log("  user 매개변수가 User 타입으로 자동 추론됩니다.");
console.log("  user.id는 number, user.name은 string으로 추론됩니다.\n");

console.log("List<Product>의 renderItem: (product) => product.name");
console.log("  product 매개변수가 Product 타입으로 자동 추론됩니다.\n");

// --- DataTable 컬럼 정의 시 타입 안전성 ---
console.log("=== 2. DataTable 컬럼 타입 안전성 ===\n");

// Column<User>에서 key는 'id' | 'name' | 'email' | 'role'만 허용됨
const userColumns: Column<User>[] = [
  { key: "id", header: "ID", width: "60px" },
  { key: "name", header: "이름", sortable: true },
  { key: "email", header: "이메일" },
  {
    key: "role",
    header: "역할",
    render: (value) => (value === "admin" ? "[관리자]" : "[사용자]"),
  },
  // { key: 'nonExistent', header: '에러' },  // 컴파일 에러! User에 없는 키
];

console.log("User 테이블 컬럼:");
userColumns.forEach((col) =>
  console.log(`  key: "${col.key}", header: "${col.header}", sortable: ${col.sortable ?? false}`)
);

// Column<Product>에서 key는 'id' | 'name' | 'price' | 'category'만 허용됨
const productColumns: Column<Product>[] = [
  { key: "name", header: "상품명", sortable: true },
  {
    key: "price",
    header: "가격",
    sortable: true,
    render: (value) => `${Number(value).toLocaleString()}원`,
  },
  { key: "category", header: "카테고리" },
];

console.log("\nProduct 테이블 컬럼:");
productColumns.forEach((col) =>
  console.log(`  key: "${col.key}", header: "${col.header}"`)
);

// --- Select 컴포넌트 ---
console.log("\n\n=== 3. Select 타입 추론 ===\n");

// Select<User> → onChange의 value가 User 타입
console.log("Select<User>:");
console.log("  onChange: (user: User) => void  // User 전체 객체 전달");
console.log("  getLabel: (user: User) => string");
console.log("  getValue: (user: User) => string | number\n");

// --- 다형 컴포넌트 ---
console.log("=== 4. 다형 컴포넌트 타입 ===\n");

console.log("Button (기본):");
console.log("  렌더링: <button>");
console.log("  허용 props: variant, size, isLoading, onClick, type, disabled...\n");

console.log('Button as="a":');
console.log("  렌더링: <a>");
console.log("  허용 props: variant, size, isLoading, href, target, rel...\n");

console.log('Button as="a" href="/home" target="_blank":');
console.log("  href, target은 <a> 전용 props로 타입 체크됨\n");

// --- Selection Hook ---
console.log("=== 5. 제네릭 Selection 패턴 ===\n");

const selection = createSelection<User>({
  items: users,
  keyExtractor: (u) => u.id,
  multiple: true,
});

console.log("초기 선택:", selection.selectedItems.map((u) => u.name));

selection.select(users[0]);
selection.select(users[2]);
console.log("김개발, 박풀스택 선택:", selection.selectedItems.map((u) => u.name));

console.log("이프론트 선택 여부:", selection.isSelected(users[1]));
console.log("김개발 선택 여부:", selection.isSelected(users[0]));

selection.toggle(users[0]);
console.log("김개발 토글 후:", selection.selectedItems.map((u) => u.name));

selection.selectAll();
console.log("전체 선택:", selection.selectedItems.map((u) => u.name));

// --- 타입 유틸리티 ---
console.log("\n\n=== 6. 타입 레벨 유틸리티 ===\n");

console.log("type PropsOf<'button'>  → HTMLButtonElement의 모든 props");
console.log("type EventHandlers<ButtonHTMLAttributes>");
console.log("  → { onClick, onFocus, onBlur, ... } (이벤트 핸들러만 추출)");
console.log("type DeepReadonly<User> → 모든 속성이 재귀적으로 readonly");
console.log("type RequireKeys<User, 'email'> → email만 필수, 나머지 유지");
console.log("type OptionalKeys<User, 'id'> → id만 선택적, 나머지 유지");
console.log("type ValueOf<User> → number | string (값 타입의 유니온)");

console.log("\n✅ 제네릭 컴포넌트 라이브러리 데모 완료!");

export {
  List,
  DataTable,
  Select,
  Button,
  createSelection,
  ListProps,
  DataTableProps,
  Column,
  SelectProps,
  ButtonProps,
  PolymorphicComponentProps,
  PropsOf,
  EventHandlers,
  DeepReadonly,
  RequireKeys,
  OptionalKeys,
  ValueOf,
};
