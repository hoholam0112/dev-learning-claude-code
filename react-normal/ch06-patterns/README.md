# 챕터 06: 컴포넌트 설계 패턴

## 개요

React 앱이 커지면 컴포넌트를 잘 설계하는 것이 중요해집니다. 컴포넌트 합성(Composition)은 작은 컴포넌트를 조합하여 복잡한 UI를 만드는 React의 핵심 패턴이며, 커스텀 Hook은 로직을 재사용 가능한 함수로 추출하는 강력한 방법입니다.

## 왜 중요한가?

- 잘 분리된 컴포넌트는 **재사용성**과 **유지보수성**을 높입니다
- 커스텀 Hook으로 **중복 로직을 제거**하고 코드를 깔끔하게 유지합니다
- 적절한 설계 패턴은 팀 협업을 원활하게 합니다

## 포함된 섹션

| 섹션 | 제목 | 설명 |
|------|------|------|
| sec01-component-composition | 컴포넌트 분리와 합성 | 컴포넌트 분리 기준, children, 합성 패턴 |
| sec02-custom-hooks | 커스텀 Hook 만들기 | Hook 규칙, 커스텀 Hook 작성, 재사용 패턴 |

## 학습 순서

1. **sec01-component-composition** → 컴포넌트를 잘 나누고 조합하는 방법
2. **sec02-custom-hooks** → 공통 로직을 Hook으로 추출하는 방법

## 선수 지식

- Props, State, 이벤트 처리 (ch03)
- Hooks 기초: useEffect, useRef (ch05)
