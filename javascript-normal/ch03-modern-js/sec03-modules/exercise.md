# 섹션 03 연습 문제: 모듈 시스템

> **관련 개념**: `concept.md` 참조
> **코드 템플릿**: `exercise.js`
> **모범 답안**: `solution.js` 참조

---

## 문제 1: 모듈 개념 이해 (⭐⭐)

### 설명
모듈 시스템의 개념을 코드로 시뮬레이션합니다. 실제 파일 분리 대신 객체를 사용하여 모듈 패턴을 연습하세요.

### 요구 사항
- `createMathModule()`: add, subtract, multiply, divide 함수를 포함하는 객체 반환
- `createStringModule()`: capitalize, reverse, truncate 함수를 포함하는 객체 반환

### 힌트
<details>
<summary>힌트 보기</summary>

- 모듈 패턴: 함수들을 객체에 담아 반환합니다
- `return { add, subtract, ... }`

</details>

---

## 문제 2: import/export 문법 연습 (⭐⭐)

### 설명
주어진 코드 조각의 import/export 문법이 올바른지 판단하는 함수를 작성하세요.

### 요구 사항
- 올바른 import/export 패턴인지 판별합니다
- 기본 내보내기와 명명 내보내기의 규칙을 적용합니다

### 힌트
<details>
<summary>힌트 보기</summary>

- 기본 내보내기: 중괄호 없이 import
- 명명 내보내기: 중괄호로 import

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

---

> 💡 **팁**: 모듈 시스템은 React에서 컴포넌트를 분리할 때 필수적입니다.
> 모범 답안은 `solution.js`에 있지만, 먼저 스스로 풀어보는 것을 권장합니다.
