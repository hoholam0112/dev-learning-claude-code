# 섹션 01: ES6+ 핵심 문법

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: 함수, 객체, 배열 (ch01-ch02)

---

## 학습 목표

이 섹션을 마치면 다음을 할 수 있습니다:

- 구조 분해 할당으로 객체/배열의 값을 추출할 수 있다
- 스프레드 연산자와 나머지 매개변수를 구분하여 사용할 수 있다
- 옵셔널 체이닝과 널 병합 연산자를 활용할 수 있다
- 단축 평가를 이해하고 사용할 수 있다

---

## 핵심 개념

### 구조 분해 할당 (Destructuring)

객체나 배열에서 값을 꺼내 변수에 할당하는 간결한 문법입니다.

#### 객체 구조 분해

```javascript
const user = { name: "김철수", age: 28, email: "kim@example.com" };

// 기존 방식
const name1 = user.name;
const age1 = user.age;

// 구조 분해 할당
const { name, age, email } = user;
console.log(name);  // "김철수"
console.log(age);   // 28

// 이름 변경
const { name: userName, age: userAge } = user;
console.log(userName); // "김철수"

// 기본값 설정
const { name: n, role = "회원" } = user;
console.log(role); // "회원" (user에 role이 없으므로 기본값 사용)
```

> 💡 **React 연관**: 컴포넌트에서 props를 받을 때 구조 분해 할당을 사용합니다.
> `function UserCard({ name, age }) { return <div>{name}</div>; }`

#### 배열 구조 분해

```javascript
const colors = ["빨강", "초록", "파랑"];

// 배열 구조 분해
const [first, second, third] = colors;
console.log(first);  // "빨강"
console.log(second); // "초록"

// 특정 요소 건너뛰기
const [, , blue] = colors;
console.log(blue); // "파랑"

// 기본값 설정
const [a, b, c, d = "노랑"] = colors;
console.log(d); // "노랑"
```

> 💡 **React 연관**: `useState`가 배열 구조 분해를 사용합니다.
> `const [count, setCount] = useState(0);`

### 스프레드 연산자 (Spread) vs 나머지 매개변수 (Rest)

`...` 문법은 사용 위치에 따라 다른 역할을 합니다:

```javascript
// 스프레드: 펼치기 (배열/객체를 개별 요소로)
const arr1 = [1, 2, 3];
const arr2 = [...arr1, 4, 5]; // [1, 2, 3, 4, 5]

const obj1 = { a: 1, b: 2 };
const obj2 = { ...obj1, c: 3 }; // { a: 1, b: 2, c: 3 }

// 나머지: 모으기 (여러 요소를 배열/객체로)
const { a, ...rest } = { a: 1, b: 2, c: 3 };
console.log(a);    // 1
console.log(rest); // { b: 2, c: 3 }

const [first2, ...others] = [10, 20, 30, 40];
console.log(first2); // 10
console.log(others); // [20, 30, 40]
```

### 옵셔널 체이닝 (?.)

중첩된 객체의 속성에 안전하게 접근합니다:

```javascript
const user = {
  name: "김철수",
  address: {
    city: "서울",
  },
};

// 옵셔널 체이닝 없이 — 에러 위험
// console.log(user.company.name); // TypeError!

// 옵셔널 체이닝으로 안전하게 접근
console.log(user.company?.name); // undefined (에러 없음)
console.log(user.address?.city); // "서울"
```

### 널 병합 연산자 (??)

`null` 또는 `undefined`일 때만 기본값을 사용합니다:

```javascript
const value1 = null ?? "기본값";
console.log(value1); // "기본값"

const value2 = 0 ?? "기본값";
console.log(value2); // 0 (0은 null/undefined가 아니므로)

// || 와의 차이: ||는 falsy 값(0, "", false)에도 기본값 적용
const value3 = 0 || "기본값";
console.log(value3); // "기본값" (0이 falsy이므로)
```

### 단축 평가 (Short-circuit Evaluation)

```javascript
// && — 왼쪽이 truthy이면 오른쪽 반환
const greeting = true && "안녕하세요";
console.log(greeting); // "안녕하세요"

const noGreeting = false && "안녕하세요";
console.log(noGreeting); // false

// || — 왼쪽이 falsy이면 오른쪽 반환
const name = "" || "익명";
console.log(name); // "익명"
```

> 💡 **React 연관**: 조건부 렌더링에서 `&&`를 자주 사용합니다.
> `{isLoggedIn && <UserProfile />}`

---

## 코드로 이해하기

### 예제: 사용자 데이터 가공

```javascript
const apiResponse = {
  status: "success",
  data: {
    user: { name: "이영희", age: 25 },
    posts: [
      { id: 1, title: "첫 글" },
      { id: 2, title: "두 번째 글" },
    ],
  },
};

// 구조 분해 + 옵셔널 체이닝으로 데이터 추출
const { data: { user, posts } } = apiResponse;
const { name, age, role = "일반" } = user;
const [firstPost, ...otherPosts] = posts;

console.log(`${name} (${age}세, ${role})`);
console.log(`첫 글: ${firstPost.title}`);
console.log(`나머지 글: ${otherPosts.length}개`);
```

**실행 방법**:
```bash
node exercise.js
```

---

## 주의 사항

- ⚠️ 구조 분해 시 변수명은 객체의 키 이름과 일치해야 합니다 (이름 변경은 `:` 사용)
- ⚠️ 스프레드로 복사한 것은 **얕은 복사(shallow copy)**입니다. 중첩 객체는 참조가 공유됩니다.
- ⚠️ `??`와 `||`의 차이를 주의하세요. `0`, `""`, `false`를 유효한 값으로 다루려면 `??`를 사용하세요.
- 💡 구조 분해와 기본값을 함께 사용하면 코드가 매우 간결해집니다.

---

## 정리

| 개념 | 설명 | 예제 |
|------|------|------|
| 객체 구조 분해 | 객체에서 값 추출 | `const { a, b } = obj` |
| 배열 구조 분해 | 배열에서 값 추출 | `const [x, y] = arr` |
| 스프레드 | 펼치기 | `{ ...obj, key: val }` |
| 나머지 | 모으기 | `const { a, ...rest } = obj` |
| 옵셔널 체이닝 | 안전한 속성 접근 | `obj?.nested?.prop` |
| 널 병합 | null/undefined 기본값 | `value ?? "default"` |

---

## 다음 단계

- ✅ `exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 섹션: **sec02-async: 비동기 프로그래밍**
- 🔗 참고 자료: [MDN - 구조 분해 할당](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment)
