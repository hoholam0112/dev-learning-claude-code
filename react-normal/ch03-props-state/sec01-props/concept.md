# 섹션 01: Props로 데이터 전달

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: JSX, 컴포넌트 (ch02)

---

## 학습 목표

이 섹션을 마치면 다음을 할 수 있습니다:

- Props를 통해 부모에서 자식으로 데이터를 전달할 수 있다
- 구조 분해 할당으로 props를 받을 수 있다
- 기본값(default props)을 설정할 수 있다
- children prop을 이해하고 사용할 수 있다

---

## 핵심 개념

### Props란?

Props(properties)는 **부모 컴포넌트가 자식 컴포넌트에게 전달하는 데이터**입니다. HTML 속성처럼 전달합니다:

```jsx
// 부모 — props 전달
function App() {
  return <UserCard name="김철수" age={28} isAdmin={true} />;
}

// 자식 — props 받기
function UserCard(props) {
  return (
    <div>
      <h2>{props.name}</h2>
      <p>나이: {props.age}세</p>
      {props.isAdmin && <span>관리자</span>}
    </div>
  );
}
```

### 구조 분해 할당으로 props 받기

실무에서는 대부분 구조 분해 할당을 사용합니다:

```jsx
// 매개변수에서 바로 구조 분해
function UserCard({ name, age, isAdmin }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>나이: {age}세</p>
      {isAdmin && <span>관리자</span>}
    </div>
  );
}
```

### Props 규칙

1. **읽기 전용**: 자식 컴포넌트에서 props를 수정할 수 없습니다
2. **단방향**: 부모 → 자식으로만 전달합니다
3. **모든 타입 가능**: 문자열, 숫자, 배열, 객체, 함수 등

```jsx
// 다양한 타입의 props 전달
<Product
  name="노트북"              {/* 문자열 */}
  price={1200000}            {/* 숫자 */}
  tags={["전자", "컴퓨터"]}    {/* 배열 */}
  specs={{ ram: "16GB" }}     {/* 객체 */}
  onBuy={() => alert("구매")} {/* 함수 */}
/>
```

### 기본값 설정

```jsx
// 방법 1: 매개변수 기본값 (권장)
function Button({ text = "클릭", color = "blue", size = "medium" }) {
  return <button style={{ color }}>{text}</button>;
}

// 사용 — text만 전달하면 나머지는 기본값
<Button text="저장" />
```

### children Prop

컴포넌트 태그 사이의 내용은 `children` prop으로 전달됩니다:

```jsx
function Card({ children, title }) {
  return (
    <div style={{ border: "1px solid #ddd", padding: "16px" }}>
      <h3>{title}</h3>
      <div>{children}</div>
    </div>
  );
}

// 사용 — 태그 사이의 내용이 children
<Card title="공지사항">
  <p>오늘 서버 점검이 있습니다.</p>
  <p>22:00 ~ 24:00</p>
</Card>
```

### Props로 컴포넌트 재사용

```jsx
function Alert({ type = "info", message }) {
  const colors = { info: "#2196f3", warning: "#ff9800", error: "#f44336" };
  return (
    <div style={{ padding: "12px", backgroundColor: colors[type], color: "white" }}>
      {message}
    </div>
  );
}

// 같은 컴포넌트, 다른 데이터
<Alert type="info" message="정보입니다." />
<Alert type="warning" message="주의하세요!" />
<Alert type="error" message="오류가 발생했습니다." />
```

---

## 코드로 이해하기

### 예제: 상품 목록

```jsx
function ProductCard({ name, price, imageUrl, onSale = false }) {
  return (
    <div>
      <img src={imageUrl} alt={name} />
      <h3>{name}</h3>
      <p>{onSale ? `할인가: ${price * 0.8}원` : `${price}원`}</p>
      {onSale && <span style={{ color: "red" }}>20% 할인!</span>}
    </div>
  );
}
```

---

## 주의 사항

- ⚠️ props는 **읽기 전용**입니다. `props.name = "새 이름"` 같은 코드는 에러입니다.
- ⚠️ `key`는 특수한 prop으로 컴포넌트 내부에서 접근할 수 없습니다.
- 💡 props가 많아지면 객체로 묶어서 전달하는 것도 방법입니다: `<User {...userData} />`

---

## 정리

| 개념 | 설명 | 예제 |
|------|------|------|
| Props | 부모→자식 데이터 전달 | `<Comp name="값" />` |
| 구조 분해 | 간결한 props 받기 | `function Comp({ name })` |
| 기본값 | 전달되지 않은 props의 기본값 | `{ name = "기본" }` |
| children | 태그 사이 내용 | `<Card>내용</Card>` |

---

## 다음 단계

- ✅ `exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 섹션: **sec02-state-events: State와 이벤트 처리**
- 🔗 참고 자료: [React 공식 문서 - 컴포넌트에 props 전달하기](https://react.dev/learn/passing-props-to-a-component)
