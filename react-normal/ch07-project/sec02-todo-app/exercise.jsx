// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과

// ===== Todo 앱 상태 관리 =====
// React의 useState를 시뮬레이션하여 Todo 앱의 핵심 로직을 구현하세요.

// createTodoApp() → { getTodos, addTodo, toggleTodo, deleteTodo, getFilteredTodos }
function createTodoApp() {
  // TODO: 여기에 코드를 작성하세요
  // 내부 상태: todos 배열 [{ id, text, completed }]
  // 내부 상태: nextId (자동 증가)

  // addTodo(text): 새 할 일 추가, { id: nextId++, text, completed: false }
  // toggleTodo(id): 해당 id의 completed를 토글
  // deleteTodo(id): 해당 id의 할 일 삭제
  // getTodos(): 전체 할 일 배열 반환
  // getFilteredTodos(filter): "all", "active", "completed" 필터링
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== Todo 앱 테스트 ===");
const app = createTodoApp();

// 추가 테스트
app.addTodo("React 공부하기");
app.addTodo("운동하기");
app.addTodo("책 읽기");
console.assert(app.getTodos().length === 3, "추가 테스트 실패");
console.assert(app.getTodos()[0].text === "React 공부하기", "첫 번째 할 일 테스트 실패");
console.assert(app.getTodos()[0].completed === false, "초기 completed 테스트 실패");
console.log("추가 테스트 통과!");

// 토글 테스트
const firstId = app.getTodos()[0].id;
app.toggleTodo(firstId);
console.assert(app.getTodos()[0].completed === true, "토글 테스트 실패");
app.toggleTodo(firstId);
console.assert(app.getTodos()[0].completed === false, "재토글 테스트 실패");
console.log("토글 테스트 통과!");

// 삭제 테스트
const secondId = app.getTodos()[1].id;
app.deleteTodo(secondId);
console.assert(app.getTodos().length === 2, "삭제 테스트 실패");
console.assert(app.getTodos().every(t => t.id !== secondId), "삭제 확인 실패");
console.log("삭제 테스트 통과!");

// 필터링 테스트
app.toggleTodo(firstId); // 첫 번째를 completed로
const all = app.getFilteredTodos("all");
const active = app.getFilteredTodos("active");
const completed = app.getFilteredTodos("completed");
console.assert(all.length === 2, "전체 필터 테스트 실패");
console.assert(active.length === 1, "활성 필터 테스트 실패");
console.assert(completed.length === 1, "완료 필터 테스트 실패");
console.assert(completed[0].text === "React 공부하기", "완료 항목 테스트 실패");
console.log("필터링 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
