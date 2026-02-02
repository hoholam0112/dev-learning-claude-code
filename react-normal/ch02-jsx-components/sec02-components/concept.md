# 섹션 02: 컴포넌트 만들기

> **난이도**: ⭐ (1/5)
> **선수 지식**: JSX 문법 (sec01)

---

## 학습 목표

이 섹션을 마치면 다음을 할 수 있습니다:

- 함수 컴포넌트를 정의하고 사용할 수 있다
- 컴포넌트를 별도 파일로 분리하고 import할 수 있다
- 컴포넌트를 중첩하고 합성할 수 있다

---

## 핵심 개념

### 함수 컴포넌트

React 컴포넌트는 **JSX를 반환하는 함수**입니다:

```jsx
// 컴포넌트 정의 — 함수 이름은 반드시 대문자로 시작
function Welcome() {
  return <h1>환영합니다!</h1>;
}

// 컴포넌트 사용 — HTML 태그처럼 사용
function App() {
  return (
    <div>
      <Welcome />
      <Welcome />
      <Welcome />
    </div>
  );
}
```

> ⚠️ 컴포넌트 이름은 반드시 **대문자**로 시작해야 합니다. 소문자로 시작하면 HTML 태그로 인식됩니다.

### 화살표 함수 컴포넌트

```jsx
const Welcome = () => {
  return <h1>환영합니다!</h1>;
};

// 한 줄이면 더 간결하게
const Welcome = () => <h1>환영합니다!</h1>;
```

### 컴포넌트 합성

작은 컴포넌트를 조합하여 복잡한 UI를 구성합니다:

```jsx
function Avatar() {
  return <img src="https://via.placeholder.com/50" alt="아바타" />;
}

function UserInfo() {
  return (
    <div>
      <h3>김철수</h3>
      <p>프론트엔드 개발자</p>
    </div>
  );
}

function UserCard() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
      <Avatar />
      <UserInfo />
    </div>
  );
}
```

### 파일 분리와 import/export

```jsx
// components/Button.jsx
export default function Button() {
  return <button>클릭하세요</button>;
}
```

```jsx
// App.jsx
import Button from "./components/Button";

function App() {
  return (
    <div>
      <h1>내 앱</h1>
      <Button />
    </div>
  );
}
```

### 여러 컴포넌트 내보내기

```jsx
// components/Icons.jsx
export function HomeIcon() {
  return <span>🏠</span>;
}

export function SettingsIcon() {
  return <span>⚙️</span>;
}
```

```jsx
// App.jsx — 명명 가져오기
import { HomeIcon, SettingsIcon } from "./components/Icons";
```

---

## 코드로 이해하기

### 예제: 카드 컴포넌트 조합

```jsx
function Badge({ text }) {
  return (
    <span style={{
      backgroundColor: "#e0f2fe",
      padding: "4px 8px",
      borderRadius: "4px",
      fontSize: "12px",
    }}>
      {text}
    </span>
  );
}

function ArticleCard() {
  return (
    <article style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "8px" }}>
      <h2>React 시작하기</h2>
      <p>React의 기본 개념을 알아봅시다.</p>
      <div style={{ display: "flex", gap: "8px" }}>
        <Badge text="React" />
        <Badge text="입문" />
        <Badge text="프론트엔드" />
      </div>
    </article>
  );
}
```

---

## 주의 사항

- ⚠️ 컴포넌트 이름은 **대문자**로 시작해야 합니다 (`Button` ✅, `button` ❌)
- ⚠️ 컴포넌트는 반드시 JSX를 **반환**해야 합니다 (`return` 필수)
- ⚠️ 하나의 파일에 너무 많은 컴포넌트를 넣지 마세요. 관련된 것끼리 분리하세요.
- 💡 컴포넌트가 점점 커지면 더 작은 컴포넌트로 분리하세요.

---

## 정리

| 개념 | 설명 | 예제 |
|------|------|------|
| 함수 컴포넌트 | JSX를 반환하는 함수 | `function App() { return <div/> }` |
| 컴포넌트 사용 | 태그처럼 사용 | `<App />` |
| 합성 | 컴포넌트 조합 | `<Card><Avatar /><Info /></Card>` |
| default export | 메인 컴포넌트 내보내기 | `export default function App()` |
| named export | 여러 컴포넌트 내보내기 | `export function Button()` |

---

## 다음 단계

- ✅ `exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 챕터: **ch03-props-state: Props와 State**
- 🔗 참고 자료: [React 공식 문서 - 첫 번째 컴포넌트](https://react.dev/learn/your-first-component)
