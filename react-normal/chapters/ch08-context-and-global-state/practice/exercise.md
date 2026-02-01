# 챕터 08 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 언어 설정 Context (⭐⭐)

### 설명
다국어(한국어/영어) 전환 기능을 Context로 구현하세요. 앱 전체에서 현재 언어에 맞는 텍스트를 표시합니다.

### 요구 사항
- `LanguageContext`를 생성하고 `LanguageProvider`에서 현재 언어(ko/en)와 전환 함수를 제공할 것
- 번역 데이터 객체를 만들어 언어에 따라 텍스트를 표시:
  ```js
  const translations = {
    ko: { greeting: '안녕하세요', welcome: '환영합니다', settings: '설정', language: '언어' },
    en: { greeting: 'Hello', welcome: 'Welcome', settings: 'Settings', language: 'Language' },
  };
  ```
- `useLanguage()` 커스텀 훅을 만들어 Context 접근을 편리하게 할 것
- 헤더, 메인 콘텐츠, 푸터 등 최소 3개의 컴포넌트에서 번역된 텍스트를 표시
- 언어 전환 버튼(또는 셀렉트)을 포함할 것

### 힌트
<details><summary>힌트 보기</summary>

- `translations[currentLang].greeting`으로 현재 언어의 텍스트에 접근합니다
- 편의를 위해 `t` 함수를 커스텀 훅에서 제공하면 좋습니다:
  ```jsx
  const t = (key) => translations[lang][key] || key;
  ```
- Provider에서 `lang`, `setLang`, `t` 함수를 모두 value로 전달하세요

</details>

---

## 문제 2: 알림(Notification) 시스템 (⭐⭐⭐)

### 설명
전역 알림 시스템을 Context + useReducer로 구현하세요. 앱 어디에서나 `addNotification`을 호출하여 알림을 표시하고, 일정 시간 후 자동으로 사라지게 합니다.

### 요구 사항
- `NotificationContext`와 `notificationReducer`를 구현할 것
- 알림 타입: `success`(녹색), `error`(빨간색), `info`(파란색)
- 리듀서 액션: `ADD_NOTIFICATION`, `REMOVE_NOTIFICATION`
- 각 알림은 고유 id, 메시지, 타입을 가짐
- 알림은 화면 상단에 표시되며, 3초 후 자동으로 사라짐 (`useEffect`+`setTimeout` 사용)
- 알림의 "X" 버튼을 클릭하여 수동으로 닫을 수도 있음
- 테스트용 버튼 3개를 만들어 각 타입의 알림을 발생시킬 것

### 힌트
<details><summary>힌트 보기</summary>

- 고유 id는 `Date.now()`를 사용하면 간단합니다
- 자동 제거는 각 알림 컴포넌트 내부에서 `useEffect`로 구현합니다:
  ```jsx
  useEffect(() => {
    const timer = setTimeout(() => {
      removeNotification(id);
    }, 3000);
    return () => clearTimeout(timer);
  }, [id]);
  ```
- 알림 목록은 position: fixed로 화면 상단에 고정합니다

</details>

---

## 문제 3: 미니 상태 관리 라이브러리 (⭐⭐⭐)

### 설명
범용적으로 사용할 수 있는 간단한 상태 관리 패턴을 만드세요. `createStore` 함수를 만들어 Context, Provider, 커스텀 훅을 한 번에 생성하는 유틸리티를 구현합니다.

### 요구 사항
- `createStore(reducer, initialState)` 함수를 만들 것
- 이 함수는 `{ Provider, useStore }` 객체를 반환
- `useStore()`는 `{ state, dispatch }` 를 반환
- 이 패턴을 사용하여 **카운터**와 **할 일 목록** 두 개의 독립적인 스토어를 생성
- 카운터 스토어: `INCREMENT`, `DECREMENT`, `RESET` 액션
- 할 일 스토어: `ADD_TODO`, `TOGGLE_TODO`, `DELETE_TODO` 액션
- 두 스토어가 서로 독립적으로 동작하는 것을 확인할 수 있는 UI

### 힌트
<details><summary>힌트 보기</summary>

- `createStore`는 함수 안에서 `createContext`, `useReducer`, `useContext`를 활용합니다:
  ```jsx
  function createStore(reducer, initialState) {
    const StoreContext = createContext();

    function Provider({ children }) {
      const [state, dispatch] = useReducer(reducer, initialState);
      return (
        <StoreContext.Provider value={{ state, dispatch }}>
          {children}
        </StoreContext.Provider>
      );
    }

    function useStore() {
      const context = useContext(StoreContext);
      if (!context) throw new Error('Provider 안에서 사용하세요');
      return context;
    }

    return { Provider, useStore };
  }
  ```
- 각 스토어를 별도의 변수에 저장: `const CounterStore = createStore(...)`

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요.
> 특히 "Context + useReducer 패턴"과 "커스텀 훅" 부분을 복습하면 도움이 됩니다.
