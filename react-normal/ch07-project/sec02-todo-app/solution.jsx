// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

function createTodoApp() {
  let todos = [];
  let nextId = 1;

  return {
    getTodos() {
      return todos;
    },

    addTodo(text) {
      // 불변 업데이트: 새 배열을 만들어 할 일 추가
      // React에서: setTodos(prev => [...prev, newTodo])
      const newTodo = { id: nextId++, text, completed: false };
      todos = [...todos, newTodo];
    },

    toggleTodo(id) {
      // 불변 업데이트: map으로 새 배열을 만들어 해당 항목만 변경
      // React에서: setTodos(prev => prev.map(t => t.id === id ? {...t, completed: !t.completed} : t))
      todos = todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      );
    },

    deleteTodo(id) {
      // 불변 업데이트: filter로 해당 항목을 제외한 새 배열 생성
      // React에서: setTodos(prev => prev.filter(t => t.id !== id))
      todos = todos.filter((todo) => todo.id !== id);
    },

    getFilteredTodos(filter) {
      switch (filter) {
        case "active":
          return todos.filter((todo) => !todo.completed);
        case "completed":
          return todos.filter((todo) => todo.completed);
        case "all":
        default:
          return todos;
      }
    },
  };
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== Todo 앱 테스트 ===");
const app = createTodoApp();

app.addTodo("React 공부하기");
app.addTodo("운동하기");
app.addTodo("책 읽기");
console.assert(app.getTodos().length === 3, "추가 테스트 실패");
console.assert(app.getTodos()[0].text === "React 공부하기", "첫 번째 할 일 테스트 실패");
console.assert(app.getTodos()[0].completed === false, "초기 completed 테스트 실패");
console.log("추가 테스트 통과!");

const firstId = app.getTodos()[0].id;
app.toggleTodo(firstId);
console.assert(app.getTodos()[0].completed === true, "토글 테스트 실패");
app.toggleTodo(firstId);
console.assert(app.getTodos()[0].completed === false, "재토글 테스트 실패");
console.log("토글 테스트 통과!");

const secondId = app.getTodos()[1].id;
app.deleteTodo(secondId);
console.assert(app.getTodos().length === 2, "삭제 테스트 실패");
console.assert(app.getTodos().every(t => t.id !== secondId), "삭제 확인 실패");
console.log("삭제 테스트 통과!");

app.toggleTodo(firstId);
const all = app.getFilteredTodos("all");
const active = app.getFilteredTodos("active");
const completed = app.getFilteredTodos("completed");
console.assert(all.length === 2, "전체 필터 테스트 실패");
console.assert(active.length === 1, "활성 필터 테스트 실패");
console.assert(completed.length === 1, "완료 필터 테스트 실패");
console.assert(completed[0].text === "React 공부하기", "완료 항목 테스트 실패");
console.log("필터링 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
