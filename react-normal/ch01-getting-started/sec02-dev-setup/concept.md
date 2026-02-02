# 섹션 02: 개발 환경 설정

> **난이도**: ⭐ (1/5)
> **선수 지식**: Node.js 설치, 터미널 기본 사용법

---

## 학습 목표

이 섹션을 마치면 다음을 할 수 있습니다:

- Vite를 사용하여 React 프로젝트를 생성할 수 있다
- 프로젝트 구조를 이해할 수 있다
- 개발 서버를 실행하고 코드 변경을 확인할 수 있다

---

## 핵심 개념

### Vite란?

Vite는 **빠른 프론트엔드 빌드 도구**입니다. React 프로젝트를 쉽게 만들고 개발할 수 있게 해줍니다.

### 프로젝트 생성

```bash
# React 프로젝트 생성
npm create vite@latest my-react-app -- --template react

# 프로젝트 디렉토리로 이동
cd my-react-app

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

브라우저에서 `http://localhost:5173`으로 접속하면 React 앱을 볼 수 있습니다.

### 프로젝트 구조

```
my-react-app/
  node_modules/        # 설치된 패키지들
  public/              # 정적 파일 (이미지 등)
  src/                 # 소스 코드 (여기서 코딩)
    App.jsx            # 메인 컴포넌트
    App.css            # 스타일
    main.jsx           # 앱의 시작점 (엔트리 포인트)
    index.css          # 전역 스타일
  index.html           # HTML 파일
  package.json         # 프로젝트 설정
  vite.config.js       # Vite 설정
```

### 핵심 파일 이해

**main.jsx** — 앱의 시작점:
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// 'root' DOM 요소에 React 앱을 렌더링
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**App.jsx** — 메인 컴포넌트:
```jsx
function App() {
  return (
    <div>
      <h1>안녕하세요, React!</h1>
    </div>
  )
}

export default App
```

### Hot Module Replacement (HMR)

Vite는 **HMR** 기능을 제공합니다:
- 코드를 수정하면 브라우저가 **자동으로 새로고침** 됩니다
- 전체 페이지를 다시 로드하지 않고 **변경된 부분만** 업데이트합니다
- 매우 빠른 개발 경험을 제공합니다

---

## 코드로 이해하기

### 예제: 첫 컴포넌트 수정

```jsx
// src/App.jsx
function App() {
  const name = "학습자";
  const today = new Date().toLocaleDateString("ko-KR");

  return (
    <div>
      <h1>안녕하세요, {name}님!</h1>
      <p>오늘 날짜: {today}</p>
      <p>React 학습을 시작합니다! 🎉</p>
    </div>
  );
}

export default App;
```

**실행 방법**:
```bash
npm run dev
```

---

## 주의 사항

- ⚠️ Node.js 18 이상이 설치되어 있어야 합니다 (`node -v`로 확인)
- ⚠️ `npm run dev`는 개발 서버를 실행합니다. 배포용 빌드는 `npm run build`를 사용합니다.
- 💡 VS Code 사용 시 "ES7+ React/Redux/React-Native snippets" 확장을 설치하면 편리합니다.

---

## 정리

| 개념 | 설명 |
|------|------|
| Vite | 빠른 React 프로젝트 빌드 도구 |
| `npm create vite` | 새 프로젝트 생성 명령어 |
| `npm run dev` | 개발 서버 실행 |
| `src/` | 소스 코드를 작성하는 디렉토리 |
| `main.jsx` | 앱의 시작점 |
| HMR | 코드 변경 시 자동 브라우저 업데이트 |

---

## 다음 단계

- ✅ `exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 챕터: **ch02-jsx-components: JSX와 컴포넌트**
- 🔗 참고 자료: [Vite 공식 문서](https://vite.dev/)
