# 챕터 07 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 온라인 상태 감지기 (⭐⭐)

### 설명
브라우저의 온라인/오프라인 상태를 실시간으로 감지하여 표시하는 컴포넌트를 구현하세요. `navigator.onLine` 속성과 `online`/`offline` 이벤트를 활용합니다.

### 요구 사항
- `useEffect`에서 `window`의 `online`과 `offline` 이벤트를 구독할 것
- 온라인일 때 초록색 배지 + "온라인" 텍스트, 오프라인일 때 빨간색 배지 + "오프라인" 텍스트
- 상태 변경 이력을 시간과 함께 기록할 것 (예: "14:30:25 - 오프라인으로 전환")
- 컴포넌트 언마운트 시 이벤트 리스너를 **반드시** 정리(클린업)할 것

### 힌트
<details><summary>힌트 보기</summary>

- `navigator.onLine`으로 초기 온라인 상태를 확인할 수 있습니다
- `window.addEventListener('online', handler)`와 `window.addEventListener('offline', handler)`를 사용합니다
- 클린업에서 `removeEventListener`를 호출해야 합니다
- 개발자 도구 > Network 탭에서 "Offline" 체크박스로 테스트할 수 있습니다

</details>

---

## 문제 2: 디바운스 검색 + API 호출 (⭐⭐)

### 설명
JSONPlaceholder API의 포스트 목록(`https://jsonplaceholder.typicode.com/posts`)을 검색하는 컴포넌트를 구현하세요. 사용자가 타이핑을 멈춘 후 500ms 뒤에 API를 호출하는 디바운스 패턴을 적용합니다.

### 요구 사항
- 검색어 입력 시 500ms 디바운스를 적용하여 API 호출
- 로딩 중일 때 "검색 중..." 표시
- 에러 발생 시 에러 메시지와 "재시도" 버튼 표시
- 검색 결과는 제목(title)과 내용(body) 일부를 카드 형태로 표시
- 빈 검색어일 때는 API를 호출하지 않고 "검색어를 입력하세요" 안내 표시
- 클린업 함수로 이전 디바운스 타이머를 정리할 것

### 힌트
<details><summary>힌트 보기</summary>

- API 필터링은 클라이언트 측에서 수행합니다:
  ```jsx
  const filtered = posts.filter(post =>
    post.title.toLowerCase().includes(query.toLowerCase())
  );
  ```
- 또는 쿼리 파라미터를 활용할 수 있습니다: `?q=검색어`
- `isCancelled` 플래그 패턴으로 언마운트 후 state 업데이트를 방지합니다:
  ```jsx
  useEffect(() => {
    let isCancelled = false;
    // fetch...
    if (!isCancelled) setData(result);
    return () => { isCancelled = true; };
  }, [query]);
  ```

</details>

---

## 문제 3: 카운트다운 타이머 (⭐⭐⭐)

### 설명
사용자가 시간(분, 초)을 설정하고 시작하면 카운트다운이 진행되는 타이머를 구현하세요. 0초에 도달하면 알림을 표시합니다.

### 요구 사항
- 분(0~59)과 초(0~59)를 입력할 수 있는 폼
- "시작" 버튼으로 카운트다운 시작, "일시정지" 버튼으로 일시정지, "초기화" 버튼으로 리셋
- 남은 시간을 MM:SS 형식으로 크게 표시
- 남은 시간이 10초 이하일 때 빨간색으로 변경 (시각적 경고)
- 0초 도달 시 `alert('타이머 종료!')`와 함께 `document.title`을 "타이머 종료!"로 변경
- `document.title`에 남은 시간을 실시간 표시 (예: "남은 시간: 02:30")
- 컴포넌트 언마운트 시 `document.title`을 원래대로 복원 (클린업)
- `setInterval`의 클린업을 올바르게 처리할 것

### 힌트
<details><summary>힌트 보기</summary>

- 전체 시간을 초 단위로 변환하여 관리하면 편합니다: `minutes * 60 + seconds`
- `setInterval` 내에서 함수형 업데이트를 사용하세요:
  ```jsx
  setRemainingSeconds(prev => {
    if (prev <= 1) {
      setIsRunning(false);
      return 0;
    }
    return prev - 1;
  });
  ```
- `useEffect` 하나에서 타이머를, 다른 하나에서 `document.title`을 관리하면 관심사 분리가 됩니다
- 0초 도달 확인은 별도의 `useEffect`에서 `remainingSeconds`를 의존성으로 감시합니다

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
> 특히 "의존성 배열"과 "클린업 함수"의 동작 방식을 정확히 이해하는 것이 중요합니다.
