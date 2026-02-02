# 섹션 02: 커스텀 Hook 만들기

## 학습 목표

- 커스텀 Hook이 무엇이고 왜 필요한지 이해한다
- Hook의 규칙 두 가지를 확실히 안다
- 자주 사용하는 커스텀 Hook 패턴을 익힌다 (useToggle, useLocalStorage, useWindowSize)
- 컴포넌트에서 로직을 Hook으로 추출하는 방법을 배운다
- 커스텀 Hook을 테스트하는 기본 방법을 안다

---

## 핵심 개념

### 1. 커스텀 Hook이란?

커스텀 Hook은 **"use"로 시작하는 함수**로, 내부에서 다른 Hook을 사용하여 **재사용 가능한 로직**을 캡슐화합니다. 컴포넌트의 UI가 아니라 **로직(상태 관리, 부수 효과 등)**을 재사용하는 것이 목적입니다.

```jsx
// 커스텀 Hook: 반드시 "use"로 시작
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  // 토글 로직을 캡슐화
  const toggle = () => setValue(prev => !prev);
  const setOn = () => setValue(true);
  const setOff = () => setValue(false);

  return { value, toggle, setOn, setOff };
}
```

**커스텀 Hook은 일반 함수와 다릅니다:**

| 구분 | 일반 함수 | 커스텀 Hook |
|------|----------|------------|
| 이름 규칙 | 자유 | 반드시 `use`로 시작 |
| Hook 사용 | 불가능 | useState, useEffect 등 사용 가능 |
| 호출 위치 | 어디서든 | React 컴포넌트 또는 다른 Hook 내부에서만 |
| 상태 공유 | 해당 없음 | 각 호출마다 독립적인 상태 생성 |

**중요:** 같은 커스텀 Hook을 두 컴포넌트에서 사용해도 상태는 **완전히 독립**입니다. Hook은 로직을 공유하지, 상태를 공유하지 않습니다.

### 2. Hook의 규칙

React Hook에는 반드시 지켜야 하는 **두 가지 규칙**이 있습니다.

#### 규칙 1: 최상위에서만 호출

Hook은 반복문, 조건문, 중첩 함수 안에서 호출하면 안 됩니다. 컴포넌트 함수의 최상위 레벨에서만 호출해야 합니다.

```jsx
// 잘못된 사용 - 조건문 안에서 Hook 호출
function MyComponent({ showName }) {
  if (showName) {
    const [name, setName] = useState('');  // 절대 안 됨!
  }
  // React는 Hook 호출 순서로 상태를 추적하므로
  // 조건에 따라 Hook 호출이 달라지면 상태가 꼬임
}

// 올바른 사용 - 최상위에서 호출
function MyComponent({ showName }) {
  const [name, setName] = useState('');  // 항상 호출됨

  // 조건부 로직은 Hook 호출 후에
  if (!showName) return null;
  return <p>{name}</p>;
}
```

#### 규칙 2: React 함수에서만 호출

Hook은 React 함수 컴포넌트 또는 커스텀 Hook 내부에서만 호출할 수 있습니다. 일반 JavaScript 함수에서는 사용할 수 없습니다.

```jsx
// 잘못된 사용 - 일반 함수에서 Hook 호출
function fetchUserData() {
  const [data, setData] = useState(null);  // 안 됨!
}

// 올바른 사용 - 커스텀 Hook에서 호출
function useFetchUser() {
  const [data, setData] = useState(null);  // OK!
  useEffect(() => { /* ... */ }, []);
  return data;
}
```

**ESLint 플러그인:** `eslint-plugin-react-hooks` 패키지를 사용하면 이 규칙들을 자동으로 검사할 수 있습니다.

### 3. 자주 사용하는 커스텀 Hook 패턴

#### useToggle - 불리언 토글

모달 열기/닫기, 다크모드 전환 등에 유용합니다.

```jsx
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = () => setValue(prev => !prev);
  const setOn = () => setValue(true);
  const setOff = () => setValue(false);

  return { value, toggle, setOn, setOff };
}

// 사용 예시
function ModalExample() {
  const { value: isOpen, toggle, setOff } = useToggle(false);

  return (
    <div>
      <button onClick={toggle}>모달 열기/닫기</button>
      {isOpen && (
        <div className="modal">
          <p>모달 내용</p>
          <button onClick={setOff}>닫기</button>
        </div>
      )}
    </div>
  );
}
```

#### useLocalStorage - 로컬 스토리지 동기화

브라우저를 새로고침해도 상태가 유지되어야 할 때 사용합니다.

```jsx
function useLocalStorage(key, initialValue) {
  // 초기값: localStorage에 저장된 값이 있으면 사용, 없으면 initialValue
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('localStorage 읽기 실패:', error);
      return initialValue;
    }
  });

  // 값 설정 시 localStorage에도 저장
  const setValue = (value) => {
    try {
      // 함수형 업데이트 지원
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('localStorage 쓰기 실패:', error);
    }
  };

  // 값 삭제
  const removeValue = () => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error('localStorage 삭제 실패:', error);
    }
  };

  return [storedValue, setValue, removeValue];
}

// 사용 예시
function ThemeSettings() {
  const [theme, setTheme, removeTheme] = useLocalStorage('theme', 'light');

  return (
    <div>
      <p>현재 테마: {theme}</p>
      <button onClick={() => setTheme('dark')}>다크 모드</button>
      <button onClick={() => setTheme('light')}>라이트 모드</button>
      <button onClick={removeTheme}>테마 초기화</button>
    </div>
  );
}
```

#### useWindowSize - 윈도우 크기 감지

반응형 레이아웃이나 크기 기반 조건부 렌더링에 사용합니다.

```jsx
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);

    // 클린업: 컴포넌트 언마운트 시 이벤트 제거
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return size;
}

// 사용 예시
function ResponsiveLayout() {
  const { width } = useWindowSize();

  return (
    <div>
      {width > 768 ? <DesktopLayout /> : <MobileLayout />}
      <p>현재 너비: {width}px</p>
    </div>
  );
}
```

### 4. 컴포넌트에서 Hook으로 로직 추출하기

커스텀 Hook의 가장 큰 장점은 **컴포넌트의 로직을 분리**하여 코드를 깔끔하게 만드는 것입니다.

**리팩토링 전 - 로직이 컴포넌트에 섞여 있음:**

```jsx
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(`/api/users/${userId}`)
      .then(res => {
        if (!res.ok) throw new Error('사용자를 찾을 수 없습니다');
        return res.json();
      })
      .then(data => {
        setUser(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <p>로딩 중...</p>;
  if (error) return <p>오류: {error}</p>;
  return <div>{user.name}</div>;
}
```

**리팩토링 후 - 로직을 Hook으로 추출:**

```jsx
// 커스텀 Hook: 데이터 가져오기 로직
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(url)
      .then(res => {
        if (!res.ok) throw new Error('요청 실패');
        return res.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [url]);

  return { data, loading, error };
}

// 컴포넌트: UI만 담당
function UserProfile({ userId }) {
  const { data: user, loading, error } = useFetch(`/api/users/${userId}`);

  if (loading) return <p>로딩 중...</p>;
  if (error) return <p>오류: {error}</p>;
  return <div>{user.name}</div>;
}

// 같은 Hook을 다른 컴포넌트에서 재사용!
function ProductDetail({ productId }) {
  const { data: product, loading, error } = useFetch(`/api/products/${productId}`);

  if (loading) return <p>로딩 중...</p>;
  if (error) return <p>오류: {error}</p>;
  return <div>{product.name} - {product.price}원</div>;
}
```

**추출 시점 판단 기준:**
- 같은 로직이 2개 이상의 컴포넌트에서 반복될 때
- 컴포넌트가 너무 길어져서 가독성이 떨어질 때
- 로직 자체를 독립적으로 테스트하고 싶을 때

### 5. 커스텀 Hook 테스트하기

커스텀 Hook은 일반 함수가 아니므로 React의 렌더링 환경이 필요합니다. `@testing-library/react-hooks` 또는 `@testing-library/react`의 `renderHook`을 사용합니다.

```jsx
import { renderHook, act } from '@testing-library/react';

// useToggle 테스트
describe('useToggle', () => {
  test('초기값이 올바르게 설정된다', () => {
    const { result } = renderHook(() => useToggle(false));
    expect(result.current.value).toBe(false);
  });

  test('toggle이 값을 반전시킨다', () => {
    const { result } = renderHook(() => useToggle(false));

    // act로 상태 변경을 감싸야 함
    act(() => {
      result.current.toggle();
    });

    expect(result.current.value).toBe(true);
  });

  test('setOn/setOff가 올바르게 동작한다', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => { result.current.setOn(); });
    expect(result.current.value).toBe(true);

    act(() => { result.current.setOff(); });
    expect(result.current.value).toBe(false);
  });
});
```

**테스트 핵심 포인트:**
- `renderHook`으로 Hook을 독립적으로 실행
- 상태를 변경하는 코드는 `act()`로 감싸기
- `result.current`로 현재 반환값에 접근

---

## 코드로 이해하기

아래는 커스텀 Hook을 종합적으로 활용한 폼 관리 예시입니다.

```jsx
// 커스텀 Hook: 폼 필드 관리
function useFormField(initialValue, validator) {
  const [value, setValue] = useState(initialValue);
  const [error, setError] = useState('');
  const [touched, setTouched] = useState(false);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setValue(newValue);

    // 이미 터치된 필드만 실시간 유효성 검사
    if (touched && validator) {
      setError(validator(newValue));
    }
  };

  const handleBlur = () => {
    setTouched(true);
    if (validator) {
      setError(validator(value));
    }
  };

  const reset = () => {
    setValue(initialValue);
    setError('');
    setTouched(false);
  };

  return {
    value,
    error,
    touched,
    onChange: handleChange,
    onBlur: handleBlur,
    reset,
    isValid: !error && touched,
  };
}

// 사용: 깔끔한 폼 컴포넌트
function SignupForm() {
  const email = useFormField('', (val) =>
    !val.includes('@') ? '유효한 이메일을 입력하세요' : ''
  );
  const password = useFormField('', (val) =>
    val.length < 8 ? '비밀번호는 8자 이상이어야 합니다' : ''
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email.isValid && password.isValid) {
      console.log('가입:', email.value, password.value);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input type="email" placeholder="이메일" {...email} />
        {email.error && <span className="error">{email.error}</span>}
      </div>
      <div>
        <input type="password" placeholder="비밀번호" {...password} />
        {password.error && <span className="error">{password.error}</span>}
      </div>
      <button type="submit">가입</button>
    </form>
  );
}
```

---

## 주의 사항

| 항목 | 설명 |
|------|------|
| 이름 규칙 필수 | 반드시 `use`로 시작해야 React가 Hook으로 인식. `useXxx` 형태 사용 |
| 과도한 추출 주의 | 한 곳에서만 사용하는 로직을 Hook으로 빼면 오히려 코드 추적이 어려움 |
| 상태 공유 오해 | 같은 Hook을 쓰더라도 각 컴포넌트의 상태는 완전히 독립적 |
| 조건부 호출 금지 | if문이나 반복문 안에서 Hook을 호출하면 안 됨 |
| 의존성 배열 주의 | useEffect 안에서 외부 변수를 사용하면 의존성 배열에 포함해야 함 |
| 초기값 계산 | 무거운 초기값 계산은 `useState(() => heavyCompute())` 형태 사용 |

---

## 정리

| 개념 | 핵심 | 사용 시점 |
|------|------|----------|
| 커스텀 Hook | `use`로 시작하는 재사용 가능한 로직 함수 | 같은 로직이 반복될 때 |
| Hook 규칙 | 최상위 호출, React 함수 내에서만 | 항상 지켜야 함 |
| useToggle | 불리언 토글 | 모달, 드롭다운, 다크모드 등 |
| useLocalStorage | 브라우저 저장소 동기화 | 사용자 설정, 테마 등 영속 상태 |
| useWindowSize | 윈도우 크기 감지 | 반응형 레이아웃 |
| useFetch | 데이터 가져오기 | API 호출 패턴 재사용 |
| 로직 추출 | 컴포넌트에서 Hook으로 분리 | 컴포넌트가 복잡해질 때 |

---

## 다음 단계

이번 챕터에서 배운 컴포넌트 합성과 커스텀 Hook은 React 앱의 기초 설계 능력입니다. 이후 챕터에서는 **Context API**를 사용한 전역 상태 관리, **성능 최적화**(React.memo, useMemo, useCallback) 등 더 고급 패턴을 다룹니다. 잘 설계된 컴포넌트와 Hook 위에 이러한 기법을 쌓아 올리면 확장성 있는 React 앱을 만들 수 있습니다.
