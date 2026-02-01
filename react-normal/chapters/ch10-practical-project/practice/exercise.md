# 챕터 10 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 검색 기능 추가 (⭐⭐)

### 설명
기존 할 일 목록에 **텍스트 검색 기능**을 추가하세요. 할 일 내용에서 키워드를 검색할 수 있어야 합니다.

### 요구 사항
- 할 일 목록 상단에 검색 입력란 추가
- 검색어 입력 시 실시간으로 목록 필터링 (기존 필터와 함께 동작)
- 검색어 하이라이트 표시 (해당 부분을 bold 또는 배경색으로 강조)
- "검색어 지우기" 버튼 (X 버튼)
- 검색 결과 개수 표시

### 힌트
<details><summary>힌트 보기</summary>

- `useState`로 검색어를 관리합니다 (전역 state가 아닌 로컬 state로 충분)
- 기존 `filteredTodos`에 추가로 검색어 필터를 적용합니다:
  ```jsx
  const searchedTodos = filteredTodos.filter(todo =>
    todo.text.toLowerCase().includes(searchQuery.toLowerCase())
  );
  ```
- 하이라이트는 `String.split()`과 `map()`으로 구현할 수 있습니다

</details>

---

## 문제 2: 드래그 없는 정렬 기능 (⭐⭐)

### 설명
할 일 목록을 다양한 기준으로 **정렬**할 수 있는 기능을 추가하세요.

### 요구 사항
- 정렬 옵션: 최신순(기본값), 오래된 순, 우선순위 높은순, 우선순위 낮은순, 카테고리순
- 정렬 셀렉트 박스 또는 버튼 그룹으로 UI 구현
- 정렬과 필터가 동시에 적용되어야 함 (예: "진행중" 필터 + "우선순위 높은순" 정렬)
- 현재 정렬 기준을 표시

### 힌트
<details><summary>힌트 보기</summary>

- 정렬은 `Array.sort()`를 사용하되, 원본 배열을 변경하지 않도록 `[...arr].sort()`를 사용합니다
- 우선순위 정렬을 위한 매핑 객체:
  ```jsx
  const priorityOrder = { high: 3, medium: 2, low: 1 };
  ```
- 정렬 state는 리듀서에 추가하거나 로컬 state로 관리합니다

</details>

---

## 문제 3: 마감일(Due Date) 기능 (⭐⭐⭐)

### 설명
할 일에 **마감일**을 설정할 수 있는 기능을 추가하세요. 마감일이 지난 항목은 시각적으로 경고를 표시합니다.

### 요구 사항
- TodoForm에 날짜 입력 필드 추가 (`<input type="date">`)
- 마감일은 선택사항 (없을 수도 있음)
- 할 일 항목에 마감일 표시 (예: "D-3", "D-Day", "D+2")
- 마감일이 지난 미완료 항목은 빨간색 배경 또는 테두리로 강조
- 마감일이 오늘인 항목은 노란색으로 강조
- "기한 임박순" 정렬 옵션 추가
- 통계 페이지에 "기한 지난 항목 수" 추가

### 힌트
<details><summary>힌트 보기</summary>

- D-Day 계산:
  ```jsx
  const today = new Date().setHours(0, 0, 0, 0);
  const dueDate = new Date(todo.dueDate).setHours(0, 0, 0, 0);
  const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
  // diffDays > 0: "D-3", diffDays === 0: "D-Day", diffDays < 0: "D+2"
  ```
- 리듀서의 `ADD_TODO`와 `EDIT_TODO`에 `dueDate` 필드를 추가합니다
- `<input type="date">`의 값은 "YYYY-MM-DD" 형식의 문자열입니다

</details>

---

## 문제 4: 다크 모드 구현 (⭐⭐⭐)

### 설명
앱 전체에 **다크 모드** 토글 기능을 추가하세요. Context를 사용하여 테마 상태를 전역으로 관리합니다.

### 요구 사항
- `ThemeContext`와 `ThemeProvider`를 별도로 구현
- 다크 모드/라이트 모드 전환 버튼을 헤더에 추가
- 다크 모드 시 배경색, 텍스트 색, 카드 색, 버튼 색 등이 모두 변경
- 테마 설정을 로컬 스토리지에 저장하여 새로고침 후에도 유지
- 시스템 다크 모드 설정을 감지하여 초기값으로 사용 (선택사항)
- `useTheme()` 커스텀 훅 제공

### 힌트
<details><summary>힌트 보기</summary>

- 시스템 다크 모드 감지:
  ```jsx
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  ```
- 테마별 색상 객체를 정의하고, 컴포넌트에서 `colors.bg`, `colors.text` 등으로 접근합니다
- 로컬 스토리지에 'theme' 키로 'dark' 또는 'light'를 저장합니다

</details>

---

## 문제 5: 종합 개선 - 서브태스크와 진행률 (⭐⭐⭐)

### 설명
할 일에 **서브태스크(하위 작업)**를 추가할 수 있는 기능을 구현하세요. 서브태스크의 완료 상태에 따라 메인 할 일의 진행률을 표시합니다.

### 요구 사항
- 각 할 일에 서브태스크 배열 추가: `subtasks: [{ id, text, completed }]`
- 할 일 항목을 클릭하면 확장되어 서브태스크 목록이 표시됨
- 서브태스크 추가/삭제/완료 토글 가능
- 서브태스크가 있는 경우 메인 할 일에 진행률 표시 (예: "2/5 완료")
- 서브태스크 전체가 완료되면 메인 할 일도 자동 완료 (선택사항)
- 리듀서에 서브태스크 관련 액션 추가:
  - `ADD_SUBTASK`
  - `DELETE_SUBTASK`
  - `TOGGLE_SUBTASK`
- 통계 페이지에 전체 서브태스크 완료율 추가

### 힌트
<details><summary>힌트 보기</summary>

- 서브태스크 리듀서 액션 예시:
  ```jsx
  case 'ADD_SUBTASK': {
    return {
      ...state,
      todos: state.todos.map(todo =>
        todo.id === action.payload.todoId
          ? {
              ...todo,
              subtasks: [...(todo.subtasks || []), {
                id: Date.now(),
                text: action.payload.text,
                completed: false,
              }],
            }
          : todo
      ),
    };
  }
  ```
- 확장/축소는 각 TodoItem 내에서 `useState`로 `isExpanded`를 관리합니다
- 진행률 계산: `subtasks.filter(s => s.completed).length / subtasks.length * 100`

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 한 번에 모든 문제를 풀려고 하지 마세요.
> 문제 1부터 순서대로 기능을 추가해 나가면, 점진적으로 앱이 완성됩니다.
> 각 문제를 풀 때마다 `example-01.jsx`의 코드를 기반으로 확장하세요.
