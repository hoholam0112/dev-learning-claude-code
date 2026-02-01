# 챕터 05 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 온라인 상태 감지 Hook (난이도: ⭐⭐)

### 설명
사용자의 인터넷 연결 상태를 감지하는 `useOnlineStatus` 커스텀 Hook을 만드세요.

### 요구 사항
- `useOnlineStatus` 커스텀 Hook을 만드세요
  - `navigator.onLine`으로 초기값 설정
  - `window`의 `online`/`offline` 이벤트를 감지
  - 클린업에서 이벤트 리스너를 해제하세요
  - `isOnline` (불리언) 값을 반환
- `OnlineIndicator` 컴포넌트를 만드세요
  - `useOnlineStatus` Hook을 사용
  - 온라인이면 초록색 "온라인" 표시
  - 오프라인이면 빨간색 "오프라인" 표시
- `SaveButton` 컴포넌트를 만드세요
  - `useOnlineStatus` Hook을 재사용
  - 온라인일 때만 "저장" 버튼 활성화
  - 오프라인이면 "연결 대기 중..." 표시와 함께 버튼 비활성화

### 힌트
<details><summary>힌트 보기</summary>

- 온라인 이벤트: `window.addEventListener("online", handler)`
- 오프라인 이벤트: `window.addEventListener("offline", handler)`
- 테스트: 브라우저 개발자 도구 > Network 탭에서 "Offline" 체크박스로 테스트
- 같은 커스텀 Hook을 두 컴포넌트에서 독립적으로 사용할 수 있습니다

</details>

---

## 문제 2: 스톱워치 앱 (난이도: ⭐⭐)

### 설명
시작/정지/랩 기능이 있는 스톱워치를 만드세요. useEffect와 useRef를 활용합니다.

### 요구 사항
- `StopWatch` 컴포넌트를 만드세요
- 기능:
  - **시작**: 10ms 단위로 시간 측정 시작
  - **정지**: 시간 측정 일시 정지
  - **초기화**: 시간을 0으로 리셋하고 랩 기록 삭제
  - **랩(Lap)**: 현재 시간을 랩 기록 목록에 추가
- 시간 표시 형식: `MM:SS.ms` (분:초.밀리초)
- 랩 기록을 리스트로 표시하세요 (최신순)
- 랩 기록 중 가장 빠른 것과 가장 느린 것을 다른 색으로 표시하세요
- `useRef`를 사용하여:
  - `setInterval`의 ID를 저장하세요
  - 시작 시점을 저장하세요
- `useEffect`를 사용하여:
  - 컴포넌트 언마운트 시 타이머를 정리하세요

### 힌트
<details><summary>힌트 보기</summary>

- 시간 측정: `setInterval(() => { ... }, 10)` (10ms 간격)
- 시간 포맷: `const mins = Math.floor(time / 60000)`, `const secs = Math.floor((time % 60000) / 1000)`, `const ms = Math.floor((time % 1000) / 10)`
- 랩 간 시간 계산: 현재 시간 - 마지막 랩 시간
- 가장 빠른/느린 랩: `Math.min(...laps)` / `Math.max(...laps)`
- useRef로 intervalId 저장: `intervalRef.current = setInterval(...)`

</details>

---

## 문제 3: 데이터 페칭 Hook (useFetch) (난이도: ⭐⭐⭐)

### 설명
범용적으로 사용할 수 있는 데이터 페칭 커스텀 Hook `useFetch`를 만들고, 이를 활용하는 컴포넌트를 구현하세요.

### 요구 사항
- `useFetch` 커스텀 Hook을 만드세요
  - 매개변수: `url` (문자열)
  - 반환값: `{ data, loading, error, refetch }`
    - `data`: 응답 데이터 (초기값 null)
    - `loading`: 로딩 상태 (불리언)
    - `error`: 에러 메시지 (문자열 또는 null)
    - `refetch`: 다시 요청하는 함수
  - `url`이 변경되면 자동으로 새 요청을 보내세요
  - 컴포넌트 언마운트 시 진행 중인 요청을 무시하세요 (isCancelled 패턴)
- `PostViewer` 컴포넌트를 만드세요
  - JSONPlaceholder API 사용: `https://jsonplaceholder.typicode.com/posts`
  - 게시물 목록 표시 (제목만, 최대 10개)
  - 게시물을 클릭하면 해당 게시물의 상세 내용 표시
    - URL: `https://jsonplaceholder.typicode.com/posts/{id}`
  - 로딩 중, 에러, 데이터 세 가지 상태에 대한 UI 표시
  - "새로고침" 버튼으로 `refetch` 호출

### 힌트
<details><summary>힌트 보기</summary>

- `isCancelled` 패턴: useEffect 안에서 `let isCancelled = false` 선언, 클린업에서 `true`로 변경
- `refetch` 구현: 별도의 `trigger` 상태를 만들고, refetch 시 trigger를 변경하여 useEffect를 재실행
- JSONPlaceholder API는 실제 작동하는 무료 API입니다
- 상세 보기 URL이 변경되면 useFetch가 자동으로 새 요청을 보냅니다

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요.
> useEffect의 클린업 함수를 반드시 작성하여 메모리 누수를 방지하세요.
> 커스텀 Hook의 이름은 반드시 `use`로 시작해야 합니다.
