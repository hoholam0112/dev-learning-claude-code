# React 용어 사전 (Expert - 고급)

> 알파벳 순서로 정리되어 있습니다. 한국어 번역과 함께 표기합니다.
> Normal 버전 용어 사전에 추가로, 고급 개념 위주로 정리합니다.

---

## A

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Abstract Syntax Tree (AST) | 추상 구문 트리 | 소스 코드의 구조를 트리 형태로 표현한 자료구조 |
| Atomic Design | 아토믹 디자인 | UI를 원자(Atom) 단위부터 페이지까지 계층적으로 설계하는 방법론 |

## B

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Batching | 배칭 | 여러 상태 업데이트를 하나로 묶어 리렌더링을 최소화하는 React의 최적화 기법 |
| Boundary (Error/Suspense) | 경계 | 에러 또는 비동기 로딩 상태를 포착하는 컴포넌트 경계 |
| Bundle Splitting | 번들 분리 | 빌드 결과물을 여러 파일로 나누어 초기 로딩 성능을 개선하는 기법 |

## C

| 영어 | 한국어 | 설명 |
|------|--------|------|
| CI/CD | 지속적 통합/지속적 배포 | 코드 변경을 자동으로 빌드, 테스트, 배포하는 파이프라인 |
| Client Component | 클라이언트 컴포넌트 | 브라우저에서 실행되는 React 컴포넌트 (`'use client'` 지시어) |
| Code Splitting | 코드 스플리팅 | 코드를 청크 단위로 분리하여 필요 시 로드하는 기법 |
| Commit Phase | 커밋 단계 | React가 계산된 변경사항을 실제 DOM에 반영하는 단계 |
| Compound Component | 복합 컴포넌트 | 관련 컴포넌트들이 암시적으로 상태를 공유하는 패턴 |
| Concurrent Mode | 동시성 모드 | React가 여러 작업을 동시에 처리하여 UI 응답성을 높이는 기능 |
| Conditional Type | 조건부 타입 | TypeScript에서 조건에 따라 타입을 결정하는 `T extends U ? X : Y` 문법 |

## D

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Debounce | 디바운스 | 연속적인 이벤트 발생 시 마지막 이벤트만 처리하는 기법 |
| Derived State | 파생 상태 | 다른 상태나 props로부터 계산되는 값 |
| Discriminated Union | 판별 유니온 | TypeScript에서 공통 속성으로 타입을 구분하는 유니온 타입 패턴 |

## E

| 영어 | 한국어 | 설명 |
|------|--------|------|
| E2E Test | 엔드투엔드 테스트 | 사용자 관점에서 전체 기능 흐름을 검증하는 테스트 |
| Error Boundary | 에러 바운더리 | 자식 컴포넌트의 렌더링 에러를 포착하여 대체 UI를 보여주는 컴포넌트 |

## F

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Feature-Sliced Design (FSD) | 기능 분할 설계 | 기능(Feature) 단위로 코드를 조직하는 프론트엔드 아키텍처 방법론 |
| Fiber | 파이버 | React의 내부 재조정 엔진, 작업을 작은 단위로 분할하여 처리 |
| Forwarded Ref | 전달된 Ref | `forwardRef`로 부모에서 자식 DOM 요소로 ref를 전달하는 패턴 |

## G

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Generic Component | 제네릭 컴포넌트 | TypeScript 제네릭을 사용하여 다양한 타입에 대응하는 컴포넌트 |

## H

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Higher-Order Component (HOC) | 고차 컴포넌트 | 컴포넌트를 받아 새로운 컴포넌트를 반환하는 함수 패턴 |
| Hydration | 하이드레이션 | 서버에서 렌더링된 HTML에 클라이언트 이벤트를 연결하는 과정 |

## I

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Integration Test | 통합 테스트 | 여러 모듈/컴포넌트의 상호작용을 검증하는 테스트 |
| Intersection Observer | 인터섹션 옵저버 | 요소의 뷰포트 진입/이탈을 감지하는 브라우저 API |
| Inversion of Control | 제어의 역전 | 실행 흐름의 제어권을 프레임워크/라이브러리에 위임하는 설계 원칙 |

## L

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Lazy Loading | 지연 로딩 | 컴포넌트를 필요한 시점에 동적으로 불러오는 기법 (`React.lazy`) |

## M

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Memoization | 메모이제이션 | 이전 계산 결과를 캐시하여 불필요한 재계산을 방지하는 최적화 기법 |
| Middleware | 미들웨어 | 요청과 응답 사이에서 추가 로직을 수행하는 중간 처리 계층 |
| Mock Service Worker (MSW) | 모의 서비스 워커 | Service Worker를 이용하여 API 요청을 가로채 모의 응답을 제공하는 라이브러리 |
| Monorepo | 모노레포 | 여러 프로젝트를 하나의 저장소에서 관리하는 구조 |

## N

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Normalization | 정규화 | 중첩된 데이터를 평평한 구조로 변환하여 관리하는 기법 |

## O

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Optimistic Update | 낙관적 업데이트 | 서버 응답 전에 UI를 먼저 업데이트하고, 실패 시 롤백하는 패턴 |

## P

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Partial Hydration | 부분 하이드레이션 | 페이지 전체가 아닌 필요한 컴포넌트만 하이드레이션하는 기법 |
| Payload | 페이로드 | 액션이나 API 응답에서 전달되는 실제 데이터 |
| Profiler | 프로파일러 | 컴포넌트 렌더링 성능을 측정하는 React 내장 도구 |

## R

| 영어 | 한국어 | 설명 |
|------|--------|------|
| React Compiler | React 컴파일러 | 메모이제이션을 자동으로 적용하는 빌드 타임 최적화 도구 |
| React Server Components (RSC) | React 서버 컴포넌트 | 서버에서만 실행되어 번들 크기를 줄이는 컴포넌트 아키텍처 |
| Reconciliation | 재조정 | 이전 트리와 새 트리를 비교하여 최소한의 DOM 업데이트를 결정하는 알고리즘 |
| Render Phase | 렌더 단계 | React가 컴포넌트를 호출하여 가상 DOM 변경사항을 계산하는 단계 |
| Render Props | 렌더 프롭스 | 함수를 prop으로 전달하여 렌더링 로직을 공유하는 패턴 |

## S

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Selective Hydration | 선택적 하이드레이션 | 우선순위에 따라 컴포넌트를 선택적으로 하이드레이션하는 기법 |
| Server Action | 서버 액션 | 클라이언트에서 호출하는 서버 측 함수 (`'use server'` 지시어) |
| Server-Side Rendering (SSR) | 서버 사이드 렌더링 | 서버에서 HTML을 생성하여 초기 로딩 성능을 개선하는 기법 |
| Stale-While-Revalidate | 만료-재검증 | 캐시된 데이터를 즉시 표시하고 백그라운드에서 최신 데이터를 가져오는 전략 |
| Static Site Generation (SSG) | 정적 사이트 생성 | 빌드 시 HTML을 미리 생성하는 렌더링 전략 |
| Streaming SSR | 스트리밍 SSR | HTML을 청크 단위로 점진적으로 전송하는 SSR 방식 |
| Suspense | 서스펜스 | 비동기 작업의 로딩 상태를 선언적으로 처리하는 React 컴포넌트 |

## T

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Test Pyramid | 테스트 피라미드 | 단위 > 통합 > E2E 순서로 테스트 비중을 구성하는 전략 |
| Throttle | 스로틀 | 일정 시간 간격으로 이벤트를 제한하여 처리하는 기법 |
| Transition | 트랜지션 | 긴급하지 않은 UI 업데이트를 표시하는 React의 동시성 기능 (`useTransition`) |
| Tree Shaking | 트리 쉐이킹 | 사용하지 않는 코드를 번들에서 제거하는 최적화 기법 |
| Type Guard | 타입 가드 | TypeScript에서 런타임 검사를 통해 타입을 좁히는 기법 |
| Type Inference | 타입 추론 | TypeScript가 명시적 타입 선언 없이 타입을 자동으로 결정하는 기능 |

## U

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Unit Test | 단위 테스트 | 개별 함수/컴포넌트의 동작을 격리하여 검증하는 테스트 |
| useCallback | useCallback | 함수를 메모이제이션하는 React Hook |
| useImperativeHandle | useImperativeHandle | ref로 노출되는 인스턴스 값을 커스터마이즈하는 Hook |
| useMemo | useMemo | 계산 결과를 메모이제이션하는 React Hook |
| useSyncExternalStore | useSyncExternalStore | 외부 저장소를 구독하는 React Hook |
| useTransition | useTransition | 비긴급 상태 업데이트를 트랜지션으로 표시하는 Hook |
| Utility Type | 유틸리티 타입 | TypeScript에서 기존 타입을 변환하는 내장 타입 (`Partial`, `Pick`, `Omit` 등) |

## V

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Virtualization | 가상화 | 화면에 보이는 항목만 렌더링하여 대규모 리스트 성능을 개선하는 기법 |

## W

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Web Worker | 웹 워커 | 메인 스레드와 별도로 백그라운드에서 스크립트를 실행하는 브라우저 기능 |

## Z

| 영어 | 한국어 | 설명 |
|------|--------|------|
| Zustand | Zustand (주스탄트) | 간결한 API를 제공하는 경량 상태 관리 라이브러리 |
