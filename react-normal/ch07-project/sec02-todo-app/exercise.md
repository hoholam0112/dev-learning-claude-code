# 섹션 02: Todo 앱 만들기 - 연습문제

## 실행 방법

```bash
node exercise.jsx
```

## 문제: Todo 앱 상태 관리

React의 `useState`를 사용하지 않고, 클로저를 활용하여 Todo 앱의 핵심 CRUD 로직을 구현하세요. 이 연습을 통해 상태 업데이트 로직 자체에 집중할 수 있습니다.

### 구현할 함수: `createTodoApp()`

`createTodoApp()`은 다음 메서드를 포함한 객체를 반환해야 합니다:

### 메서드 설명

#### `getTodos()`
- 전체 할 일 배열을 반환합니다

#### `addTodo(text)`
- 새 할 일을 추가합니다
- 할 일 구조: `{ id: 자동증가, text: 입력값, completed: false }`
- id는 1부터 시작하여 추가할 때마다 1씩 증가합니다

#### `toggleTodo(id)`
- 해당 id의 할 일의 `completed` 값을 반전시킵니다
- `true` → `false`, `false` → `true`
- **불변 업데이트**: `map`을 사용하여 새 배열을 만드세요

#### `deleteTodo(id)`
- 해당 id의 할 일을 목록에서 제거합니다
- **불변 업데이트**: `filter`를 사용하여 새 배열을 만드세요

#### `getFilteredTodos(filter)`
- `filter` 값에 따라 필터링된 할 일 배열을 반환합니다
- `"all"`: 전체 할 일 반환
- `"active"`: `completed`가 `false`인 항목만 반환
- `"completed"`: `completed`가 `true`인 항목만 반환

### 힌트

- 클로저를 사용하여 `todos` 배열과 `nextId`를 내부 변수로 관리하세요
- 추가: `[...todos, newTodo]`
- 수정: `todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t)`
- 삭제: `todos.filter(t => t.id !== id)`

---

## 기대 출력

```
=== Todo 앱 테스트 ===
추가 테스트 통과!
토글 테스트 통과!
삭제 테스트 통과!
필터링 테스트 통과!

🎉 모든 테스트를 통과했습니다!
```
