# 챕터 03: 모던 JavaScript

## 개요

ES6(ECMAScript 2015) 이후 JavaScript는 크게 발전했습니다. 구조 분해 할당, 스프레드 연산자, 비동기 처리, 모듈 시스템 등 현대적인 문법은 React 개발에서 필수적으로 사용됩니다.

이 챕터에서는 React를 배우기 전에 반드시 알아야 할 **모던 JavaScript 핵심 문법**을 학습합니다.

## 왜 중요한가?

- React에서 props를 받을 때 구조 분해 할당을 사용합니다: `function App({ name, age }) { ... }`
- 상태 업데이트에 스프레드 연산자를 사용합니다: `setState({ ...state, key: value })`
- API 호출에 async/await를 사용합니다: `const data = await fetch(url)`
- 컴포넌트를 모듈로 분리합니다: `import App from './App'`

## 포함된 섹션

| 섹션 | 제목 | 설명 |
|------|------|------|
| sec01-es6-syntax | ES6+ 핵심 문법 | 구조 분해 할당, 스프레드/나머지, 옵셔널 체이닝 |
| sec02-async | 비동기 프로그래밍 | 콜백, Promise, async/await |
| sec03-modules | 모듈 시스템 | import/export, 기본 내보내기, 명명 내보내기 |

## 학습 순서

1. **sec01-es6-syntax** → 최신 JavaScript 문법을 익힙니다
2. **sec02-async** → 비동기 처리 방법을 배웁니다
3. **sec03-modules** → 코드를 파일 단위로 분리하는 방법을 배웁니다

## 선수 지식

- 챕터 01-02의 모든 내용 (변수, 함수, 객체, 배열)

---

> 이 챕터를 마치면 React를 학습할 준비가 완료됩니다!
> 다음 단계: `react-normal/` 디렉토리의 React 학습으로 넘어가세요.
