# 섹션 01: JSX 문법

> **난이도**: ⭐ (1/5)
> **선수 지식**: JavaScript 기초, React 소개 (ch01)

---

## 학습 목표

이 섹션을 마치면 다음을 할 수 있습니다:

- JSX가 무엇인지 이해하고 기본 문법을 사용할 수 있다
- JSX 안에서 JavaScript 표현식을 사용할 수 있다
- 조건부 렌더링을 구현할 수 있다
- 스타일을 적용할 수 있다

---

## 핵심 개념

### JSX란?

JSX는 **JavaScript XML**의 약자로, JavaScript 코드 안에서 HTML과 유사한 마크업을 작성할 수 있게 해줍니다.

```jsx
// JSX — JavaScript 안에 HTML 같은 코드
const element = <h1>안녕하세요!</h1>;

// JSX는 사실 JavaScript 함수 호출로 변환됩니다
// 위 코드는 아래와 동일:
// const element = React.createElement('h1', null, '안녕하세요!');
```

### JSX 규칙

#### 1. 하나의 루트 요소

JSX는 **하나의 루트 요소**로 감싸야 합니다:

```jsx
// ❌ 잘못된 예 — 여러 루트 요소
return (
  <h1>제목</h1>
  <p>내용</p>
);

// ✅ 올바른 예 — div로 감싸기
return (
  <div>
    <h1>제목</h1>
    <p>내용</p>
  </div>
);

// ✅ 올바른 예 — Fragment 사용 (불필요한 DOM 요소 없이)
return (
  <>
    <h1>제목</h1>
    <p>내용</p>
  </>
);
```

#### 2. 모든 태그 닫기

HTML과 달리 모든 태그를 반드시 닫아야 합니다:

```jsx
// ❌ 잘못된 예
<img src="photo.jpg">
<br>
<input type="text">

// ✅ 올바른 예
<img src="photo.jpg" />
<br />
<input type="text" />
```

#### 3. camelCase 속성

HTML 속성을 camelCase로 작성합니다:

```jsx
// HTML          → JSX
// class         → className
// for           → htmlFor
// tabindex      → tabIndex
// onclick       → onClick

<div className="container">
  <label htmlFor="name">이름</label>
  <input id="name" tabIndex={1} />
</div>
```

### JavaScript 표현식 삽입

중괄호 `{}`로 JavaScript 표현식을 JSX 안에 삽입합니다:

```jsx
function Greeting() {
  const name = "김철수";
  const age = 28;
  const isAdult = age >= 18;

  return (
    <div>
      {/* 변수 표시 */}
      <h1>안녕하세요, {name}님!</h1>

      {/* 표현식 계산 */}
      <p>태어난 해: {2024 - age}년</p>

      {/* 함수 호출 */}
      <p>이름 길이: {name.length}자</p>

      {/* 삼항 연산자 */}
      <p>구분: {isAdult ? "성인" : "미성년자"}</p>
    </div>
  );
}
```

### 조건부 렌더링

#### 삼항 연산자

```jsx
function StatusBadge({ isOnline }) {
  return (
    <span>{isOnline ? "🟢 온라인" : "⚫ 오프라인"}</span>
  );
}
```

#### && 연산자

조건이 true일 때만 렌더링합니다:

```jsx
function Notification({ count }) {
  return (
    <div>
      <h1>알림</h1>
      {count > 0 && <p>새 알림이 {count}개 있습니다.</p>}
    </div>
  );
}
```

#### 조기 반환

```jsx
function UserProfile({ user }) {
  if (!user) {
    return <p>사용자 정보가 없습니다.</p>;
  }

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

### 인라인 스타일

JSX에서 스타일은 **객체**로 전달합니다:

```jsx
function StyledBox() {
  const boxStyle = {
    backgroundColor: "#f0f0f0",  // kebab-case → camelCase
    padding: "20px",
    borderRadius: "8px",
    fontSize: "16px",
  };

  return <div style={boxStyle}>스타일이 적용된 박스</div>;
}
```

---

## 코드로 이해하기

### 예제: 프로필 카드

```jsx
function ProfileCard() {
  const user = {
    name: "이영희",
    role: "프론트엔드 개발자",
    avatar: "https://via.placeholder.com/100",
    isVerified: true,
    skills: ["React", "TypeScript", "CSS"],
  };

  return (
    <div style={{ border: "1px solid #ddd", padding: "20px", borderRadius: "8px" }}>
      <img src={user.avatar} alt={`${user.name} 프로필`} />
      <h2>
        {user.name} {user.isVerified && "✅"}
      </h2>
      <p>{user.role}</p>
      <div>
        {user.skills.map((skill) => (
          <span key={skill} style={{ marginRight: "8px" }}>
            #{skill}
          </span>
        ))}
      </div>
    </div>
  );
}
```

---

## 주의 사항

- ⚠️ `class` 대신 `className`을 사용합니다
- ⚠️ JSX에서 `{}`는 JavaScript 표현식만 넣을 수 있습니다 (if문, for문 등 문(statement)은 불가)
- ⚠️ `&&` 조건부 렌더링에서 왼쪽이 `0`이면 `0`이 화면에 렌더링됩니다. `count > 0 && ...`으로 사용하세요.
- 💡 여러 줄의 JSX는 `()`로 감싸면 가독성이 좋습니다

---

## 정리

| 개념 | 설명 | 예제 |
|------|------|------|
| JSX | JS 안의 마크업 | `<h1>Hello</h1>` |
| 표현식 삽입 | `{}`로 JS 삽입 | `{name}`, `{2+3}` |
| Fragment | 빈 래퍼 | `<>...</>` |
| className | CSS 클래스 | `<div className="box">` |
| 조건부 렌더링 | 조건에 따라 표시 | `{x && <p>...</p>}` |
| 인라인 스타일 | 객체로 스타일 | `style={{ color: "red" }}` |

---

## 다음 단계

- ✅ `exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 섹션: **sec02-components: 컴포넌트 만들기**
- 🔗 참고 자료: [React 공식 문서 - JSX로 마크업 작성하기](https://react.dev/learn/writing-markup-with-jsx)
