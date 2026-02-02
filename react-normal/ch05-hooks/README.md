# 챕터 05: Hooks 기초

## 개요

React Hooks는 함수 컴포넌트에서 **상태 관리와 생명주기 기능**을 사용할 수 있게 해주는 함수들입니다. 이전 챕터에서 배운 `useState`에 이어, 이 챕터에서는 **사이드 이펙트를 관리하는 `useEffect`**와 **DOM 참조 및 값 저장을 위한 `useRef`**를 학습합니다.

`useEffect`는 컴포넌트가 렌더링된 후 실행해야 하는 작업(데이터 가져오기, 타이머 설정, 이벤트 리스너 등록 등)을 처리합니다. `useRef`는 렌더링에 영향을 주지 않으면서 값을 기억하거나 DOM 요소에 직접 접근할 때 사용합니다.

## 왜 중요한가?

- **useEffect**: 실제 애플리케이션은 순수한 렌더링만으로 이루어지지 않습니다. 서버에서 데이터를 가져오고, 타이머를 설정하고, 외부 라이브러리와 연동하는 등의 **사이드 이펙트(부수 효과)**가 반드시 필요합니다. useEffect를 올바르게 사용해야 메모리 누수, 무한 루프 등의 버그를 방지할 수 있습니다.
- **useRef**: DOM 요소에 직접 접근해야 하는 경우(포커스 설정, 스크롤, 외부 라이브러리 연동)나 렌더링과 무관한 값을 저장해야 하는 경우에 useRef가 필수적입니다. state와 달리 ref 변경은 리렌더링을 유발하지 않습니다.

## 포함된 섹션

| 섹션 | 제목 | 설명 |
|------|------|------|
| sec01-useeffect | useEffect | 사이드 이펙트 관리, 의존성 배열, 클린업 함수 |
| sec02-useref-other-hooks | useRef와 기타 Hooks | DOM 참조, 값 저장, useMemo, useCallback 기초 |

## 학습 순서

1. **sec01-useeffect** → 사이드 이펙트의 개념과 useEffect 사용법을 학습합니다
2. **sec02-useref-other-hooks** → useRef, useMemo, useCallback의 기초를 학습합니다

## 선수 지식

- React 기초 (JSX, 컴포넌트, props, state)
- JavaScript 비동기 처리 (Promise, async/await)
- 리스트 렌더링과 이벤트 핸들링
