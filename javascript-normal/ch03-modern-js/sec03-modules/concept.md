# 섹션 03: 모듈 시스템

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: 함수, 객체 (ch02), ES6 문법 (sec01)

---

## 학습 목표

이 섹션을 마치면 다음을 할 수 있습니다:

- `export`와 `import`로 코드를 모듈로 분리할 수 있다
- 기본 내보내기와 명명 내보내기의 차이를 이해할 수 있다
- 모듈 패턴을 활용하여 코드를 구조화할 수 있다

---

## 핵심 개념

### 왜 모듈이 필요한가?

모든 코드를 하나의 파일에 작성하면 유지보수가 어려워집니다. 모듈 시스템을 사용하면:

- 코드를 기능별로 분리할 수 있습니다
- 이름 충돌을 방지할 수 있습니다
- 재사용성이 높아집니다

> 💡 **React 연관**: React에서 각 컴포넌트를 별도 파일로 분리하고 import합니다.
> `import App from './App';`

### 명명 내보내기 (Named Export)

여러 개의 값을 이름으로 내보내고 가져옵니다:

```javascript
// math.js — 여러 함수를 명명 내보내기
export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

export const PI = 3.14159;
```

```javascript
// app.js — 명명 가져오기 (중괄호 사용)
import { add, subtract, PI } from "./math.js";

console.log(add(3, 5));    // 8
console.log(PI);           // 3.14159
```

### 기본 내보내기 (Default Export)

모듈당 하나의 메인 값을 내보냅니다:

```javascript
// User.js — 기본 내보내기
export default function User(name) {
  return { name, createdAt: new Date() };
}
```

```javascript
// app.js — 기본 가져오기 (중괄호 없이, 이름 자유)
import User from "./User.js";
// import CreateUser from "./User.js"; // 다른 이름도 가능

const user = User("김철수");
```

### 혼합 사용

```javascript
// api.js
export default class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }
}

export function formatUrl(path) {
  return `https://api.example.com${path}`;
}

export const API_VERSION = "v2";
```

```javascript
// app.js — 기본 + 명명 가져오기 혼합
import ApiClient, { formatUrl, API_VERSION } from "./api.js";
```

### 전체 가져오기

```javascript
// 모든 명명 내보내기를 객체로 가져오기
import * as MathUtils from "./math.js";

console.log(MathUtils.add(3, 5));  // 8
console.log(MathUtils.PI);        // 3.14159
```

### 다시 내보내기 (Re-export)

```javascript
// index.js — 여러 모듈을 하나로 모아서 내보내기
export { add, subtract } from "./math.js";
export { default as User } from "./User.js";
export { formatUrl } from "./api.js";
```

---

## 코드로 이해하기

### 예제: 모듈 구조 설계

프로젝트에서 모듈을 어떻게 구성하는지 예시입니다:

```
project/
  utils/
    math.js        # 수학 유틸리티
    string.js      # 문자열 유틸리티
    index.js       # 모아서 내보내기
  models/
    user.js        # 사용자 모델
  app.js           # 메인 파일
```

```javascript
// utils/index.js
export { add, subtract } from "./math.js";
export { capitalize, truncate } from "./string.js";

// app.js
import { add, capitalize } from "./utils/index.js";
```

**실행 방법** (Node.js에서 ES 모듈 사용):
```bash
node --experimental-modules exercise.mjs
# 또는 package.json에 "type": "module" 추가 후
node exercise.js
```

---

## 주의 사항

- ⚠️ 기본 내보내기는 모듈당 **하나만** 가능합니다
- ⚠️ 명명 가져오기는 반드시 **중괄호 `{}`**를 사용합니다
- ⚠️ Node.js에서 ES 모듈을 사용하려면 파일 확장자를 `.mjs`로 하거나 `package.json`에 `"type": "module"`을 추가해야 합니다
- 💡 React 프로젝트는 빌드 도구가 모듈을 처리하므로 별도 설정 없이 import/export를 사용할 수 있습니다

---

## 정리

| 개념 | 설명 | 예제 |
|------|------|------|
| 명명 내보내기 | 이름으로 내보내기 | `export function add() {}` |
| 명명 가져오기 | 이름으로 가져오기 | `import { add } from "./mod"` |
| 기본 내보내기 | 메인 값 내보내기 | `export default function() {}` |
| 기본 가져오기 | 메인 값 가져오기 | `import Comp from "./mod"` |
| 전체 가져오기 | 모두 가져오기 | `import * as M from "./mod"` |

---

## 다음 단계

- ✅ `exercise.md`의 연습 문제를 풀어보세요.
- 🎉 JavaScript 기초 학습이 완료되었습니다!
- 📖 다음 단계: **`react-normal/` 디렉토리의 React 학습**으로 넘어가세요.
- 🔗 참고 자료: [MDN - JavaScript 모듈](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
