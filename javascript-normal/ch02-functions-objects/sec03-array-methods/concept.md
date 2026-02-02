# 섹션 03: 배열 메서드

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: 함수, 객체, 배열 (sec01, sec02)

---

## 학습 목표

이 섹션을 마치면 다음을 할 수 있습니다:

- `map()`으로 배열을 변환할 수 있다
- `filter()`로 조건에 맞는 요소를 걸러낼 수 있다
- `find()`와 `findIndex()`로 요소를 검색할 수 있다
- `reduce()`로 배열을 하나의 값으로 줄일 수 있다
- 메서드를 체이닝하여 사용할 수 있다

---

## 핵심 개념

### map() — 변환

배열의 각 요소를 변환하여 **새 배열**을 만듭니다:

```javascript
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map((num) => num * 2);
console.log(doubled); // [2, 4, 6, 8, 10]

// 객체 배열 변환
const users = [
  { name: "김철수", age: 28 },
  { name: "이영희", age: 25 },
];
const names = users.map((user) => user.name);
console.log(names); // ["김철수", "이영희"]
```

> 💡 **React 연관**: 리스트를 렌더링할 때 `map()`을 매우 자주 사용합니다.
> `{items.map(item => <li key={item.id}>{item.name}</li>)}`

### filter() — 필터링

조건을 만족하는 요소만 모아 **새 배열**을 만듭니다:

```javascript
const numbers = [1, 2, 3, 4, 5, 6];
const evens = numbers.filter((num) => num % 2 === 0);
console.log(evens); // [2, 4, 6]

// 특정 조건의 사용자 필터링
const users = [
  { name: "김철수", age: 28, isActive: true },
  { name: "이영희", age: 25, isActive: false },
  { name: "박지민", age: 32, isActive: true },
];
const activeUsers = users.filter((user) => user.isActive);
console.log(activeUsers.length); // 2
```

### find() / findIndex() — 검색

조건에 맞는 **첫 번째 요소**를 찾습니다:

```javascript
const users = [
  { id: 1, name: "김철수" },
  { id: 2, name: "이영희" },
  { id: 3, name: "박지민" },
];

const user = users.find((u) => u.id === 2);
console.log(user); // { id: 2, name: "이영희" }

const index = users.findIndex((u) => u.id === 2);
console.log(index); // 1

// 찾지 못하면 find는 undefined, findIndex는 -1 반환
const notFound = users.find((u) => u.id === 99);
console.log(notFound); // undefined
```

### reduce() — 축약

배열을 순회하며 **하나의 값으로 축약**합니다:

```javascript
const numbers = [1, 2, 3, 4, 5];

// 합계 구하기
const sum = numbers.reduce((acc, num) => acc + num, 0);
console.log(sum); // 15

// 최댓값 구하기
const max = numbers.reduce((acc, num) => (num > acc ? num : acc), numbers[0]);
console.log(max); // 5

// 객체로 그룹핑
const fruits = ["사과", "바나나", "사과", "체리", "바나나", "사과"];
const count = fruits.reduce((acc, fruit) => {
  acc[fruit] = (acc[fruit] || 0) + 1;
  return acc;
}, {});
console.log(count); // { 사과: 3, 바나나: 2, 체리: 1 }
```

### forEach() — 순회

배열의 각 요소에 대해 함수를 실행합니다 (반환값 없음):

```javascript
const items = ["사과", "바나나", "체리"];
items.forEach((item, index) => {
  console.log(`${index + 1}. ${item}`);
});
// 1. 사과
// 2. 바나나
// 3. 체리
```

### 메서드 체이닝

여러 메서드를 연결하여 사용합니다:

```javascript
const products = [
  { name: "노트북", price: 1200000, inStock: true },
  { name: "마우스", price: 35000, inStock: true },
  { name: "키보드", price: 89000, inStock: false },
  { name: "모니터", price: 450000, inStock: true },
];

// 재고 있는 상품의 이름만 추출하여 정렬
const available = products
  .filter((p) => p.inStock)
  .map((p) => p.name)
  .sort();

console.log(available); // ["노트북", "마우스", "모니터"]
```

---

## 코드로 이해하기

### 예제: 주문 데이터 분석

```javascript
const orders = [
  { item: "커피", price: 4500, quantity: 2 },
  { item: "케이크", price: 6000, quantity: 1 },
  { item: "쿠키", price: 2000, quantity: 3 },
];

// 총 매출 계산
const totalRevenue = orders.reduce(
  (sum, order) => sum + order.price * order.quantity,
  0
);
console.log(`총 매출: ${totalRevenue.toLocaleString()}원`); // 총 매출: 21,000원
```

**실행 방법**:
```bash
node exercise.js
```

---

## 주의 사항

- ⚠️ `map()`, `filter()`는 **새 배열을 반환**합니다. 원본 배열은 변경되지 않습니다.
- ⚠️ `forEach()`는 반환값이 없습니다. 변환이 필요하면 `map()`을 사용하세요.
- ⚠️ `reduce()`의 두 번째 인수(초기값)를 항상 지정하는 것이 안전합니다.
- 💡 `sort()`는 원본 배열을 변경합니다. 복사 후 정렬하려면 `[...arr].sort()`를 사용하세요.

---

## 정리

| 메서드 | 설명 | 반환 | 예제 |
|--------|------|------|------|
| `map()` | 각 요소 변환 | 새 배열 | `[1,2,3].map(x => x*2)` → `[2,4,6]` |
| `filter()` | 조건 필터링 | 새 배열 | `[1,2,3].filter(x => x>1)` → `[2,3]` |
| `find()` | 조건 검색 | 요소/undefined | `[1,2,3].find(x => x>1)` → `2` |
| `reduce()` | 축약 | 단일 값 | `[1,2,3].reduce((a,b) => a+b, 0)` → `6` |
| `forEach()` | 순회 실행 | undefined | `arr.forEach(x => console.log(x))` |

---

## 다음 단계

- ✅ `exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 챕터: **ch03-modern-js: 모던 JavaScript**
- 🔗 참고 자료: [MDN - Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
