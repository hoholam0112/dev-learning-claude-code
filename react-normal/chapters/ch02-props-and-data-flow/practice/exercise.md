# 챕터 02 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 재사용 가능한 Badge 컴포넌트 (난이도: ⭐)

### 설명
다양한 상태를 표시할 수 있는 Badge(뱃지) 컴포넌트를 만들어보세요. Props를 통해 텍스트, 색상, 크기를 외부에서 지정할 수 있어야 합니다.

### 요구 사항
- `Badge` 컴포넌트를 만드세요
- 다음 props를 받아야 합니다:
  - `text` (문자열): 뱃지에 표시할 텍스트
  - `color` (문자열): 배경 색상 (`"green"`, `"red"`, `"blue"`, `"gray"` 중 하나)
  - `size` (문자열): 크기 (`"small"`, `"medium"`, `"large"`)
- 구조 분해 할당을 사용하세요
- `color`의 기본값은 `"gray"`, `size`의 기본값은 `"medium"`으로 설정하세요
- App 컴포넌트에서 다양한 조합으로 Badge를 5개 이상 렌더링하세요

### 힌트
<details><summary>힌트 보기</summary>

- 색상 매핑 객체를 만들면 편리합니다: `{ green: { bg: '#dcfce7', text: '#166534' }, ... }`
- 기본값 설정: `function Badge({ text, color = "gray", size = "medium" })`
- 사이즈별 padding과 fontSize를 객체로 관리하세요

</details>

---

## 문제 2: 상품 카드 시스템 (난이도: ⭐⭐)

### 설명
온라인 쇼핑몰의 상품 카드를 컴포넌트로 구현해보세요. 하나의 `ProductCard` 컴포넌트를 만들고, 다양한 상품 데이터를 props로 전달하여 여러 카드를 표시합니다.

### 요구 사항
- `ProductCard` 컴포넌트를 만드세요
- 다음 props를 받아야 합니다:
  - `name` (문자열): 상품명
  - `price` (숫자): 가격
  - `discount` (숫자, 선택): 할인율 (0~100, 기본값 0)
  - `imageUrl` (문자열): 상품 이미지 URL
  - `tags` (문자열 배열, 선택): 태그 목록 (기본값 빈 배열)
  - `inStock` (불리언, 선택): 재고 여부 (기본값 true)
- 할인가를 계산하여 표시하세요: `할인가 = price * (1 - discount / 100)`
- 원래 가격에 취소선을 적용하고 할인가를 강조하세요 (할인이 있을 때만)
- 재고가 없을 때(`inStock={false}`) "품절" 표시를 하고 카드를 흐리게(opacity) 처리하세요
- `toLocaleString()`을 사용하여 가격에 콤마를 표시하세요
- App 컴포넌트에서 최소 4개의 상품 카드를 렌더링하세요

### 힌트
<details><summary>힌트 보기</summary>

- 할인가 계산: `Math.round(price * (1 - discount / 100))`
- 취소선 스타일: `textDecoration: "line-through"`
- 품절 처리: `opacity: inStock ? 1 : 0.5`
- 조건부 렌더링: `{discount > 0 && <span>할인가</span>}`

</details>

---

## 문제 3: children을 활용한 탭 UI (난이도: ⭐⭐)

### 설명
children prop을 활용하여 유연한 탭 패널(TabPanel) 컴포넌트를 만들어보세요. 레이아웃 컴포넌트 패턴을 연습합니다.

### 요구 사항
- 다음 컴포넌트들을 만드세요:
  1. `TabPanel` - 탭의 내용을 감싸는 컨테이너 (title prop + children)
  2. `TabContainer` - 여러 TabPanel을 감싸는 상위 컴포넌트 (children)
  3. `InfoBox` - 정보를 표시하는 범용 박스 (variant prop + children)
- `TabPanel`은 `title` prop과 `children`을 받아, 제목이 있는 패널을 렌더링합니다
- `InfoBox`는 `variant` prop(`"tip"`, `"note"`, `"warning"`)에 따라 다른 스타일을 적용하고, `children`으로 내용을 받습니다
- `TabContainer`안에 3개의 `TabPanel`을 배치하고, 각 탭 내부에 `InfoBox`를 활용하세요
- 아직 상태(state)를 배우지 않았으므로, 탭 전환 기능은 구현하지 않아도 됩니다. 모든 탭이 동시에 보여도 괜찮습니다.

### 힌트
<details><summary>힌트 보기</summary>

- `TabPanel`의 구조: 제목 영역 + `{children}` 영역
- `InfoBox`의 variant별 색상을 객체로 매핑하세요
- children 안에 다양한 JSX를 넣을 수 있습니다 (텍스트, 리스트, 이미지 등)
- 모든 탭이 세로로 나열되는 형태로 만드세요

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요.
> props의 기본값 설정과 구조 분해 할당을 적극 활용하세요.
