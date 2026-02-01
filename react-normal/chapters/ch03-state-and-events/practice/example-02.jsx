/**
 * 챕터 03 - 예제 2: 폼 입력과 객체/배열 상태 관리
 *
 * 학습 포인트:
 * - 입력(input) 이벤트 처리와 제어 컴포넌트
 * - 객체 상태의 불변 업데이트 (spread 연산자)
 * - 배열 상태의 불변 업데이트 (concat, filter, map)
 * - 여러 상태를 조합한 복합 UI
 *
 * 실행 방법:
 * 1. npx create-react-app ch03-demo (이미 생성했다면 생략)
 * 2. cd ch03-demo
 * 3. src/App.js 파일을 이 파일의 내용으로 교체
 * 4. npm start
 * 5. 브라우저에서 http://localhost:3000 확인
 */

import React, { useState } from "react";

// --- 1. 제어 컴포넌트 (Controlled Component) ---
// input의 값을 React 상태로 관리합니다.
function ControlledInput() {
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");

  const containerStyle = {
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const inputStyle = {
    padding: "8px 12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "1rem",
    width: "100%",
    boxSizing: "border-box",
    marginBottom: "12px",
  };

  return (
    <div style={containerStyle}>
      <h2>제어 컴포넌트</h2>

      <label>
        이름:
        <input
          style={inputStyle}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="이름을 입력하세요"
        />
      </label>

      <label>
        메시지:
        <textarea
          style={{ ...inputStyle, minHeight: "80px", resize: "vertical" }}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="메시지를 입력하세요"
        />
      </label>

      {/* 입력값 실시간 미리보기 */}
      <div
        style={{
          padding: "12px",
          backgroundColor: "#f8fafc",
          borderRadius: "6px",
          marginTop: "8px",
        }}
      >
        <p style={{ margin: "0 0 4px 0", fontWeight: "bold" }}>미리보기:</p>
        <p style={{ margin: 0 }}>
          {name ? `${name}님이 말합니다:` : "(이름을 입력하세요)"}
        </p>
        <p style={{ margin: 0, color: "#4b5563" }}>
          {message || "(메시지를 입력하세요)"}
        </p>
      </div>

      <p style={{ fontSize: "0.85rem", color: "#9ca3af" }}>
        글자 수: 이름 {name.length}자 / 메시지 {message.length}자
      </p>
    </div>
  );
}

// --- 2. 객체 상태 관리 (회원가입 폼) ---
function RegistrationForm() {
  // 여러 필드를 하나의 객체 상태로 관리
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    agreeToTerms: false,
  });

  const [submitted, setSubmitted] = useState(false);

  // 범용 변경 핸들러: name 속성으로 어떤 필드인지 구분
  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;

    setFormData((prev) => ({
      ...prev, // 기존 값 복사
      // 체크박스는 checked, 나머지는 value 사용
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault(); // 페이지 새로고침 방지
    setSubmitted(true);
  };

  const containerStyle = {
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const inputStyle = {
    padding: "8px 12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "1rem",
    width: "100%",
    boxSizing: "border-box",
    marginBottom: "12px",
  };

  const buttonStyle = {
    padding: "10px 24px",
    backgroundColor: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    fontSize: "1rem",
    cursor: "pointer",
    width: "100%",
  };

  return (
    <div style={containerStyle}>
      <h2>회원가입 폼 (객체 상태)</h2>

      {submitted ? (
        <div style={{ textAlign: "center", padding: "20px" }}>
          <h3 style={{ color: "#22c55e" }}>가입 완료!</h3>
          <p>사용자명: {formData.username}</p>
          <p>이메일: {formData.email}</p>
          <button
            onClick={() => {
              setSubmitted(false);
              setFormData({
                username: "",
                email: "",
                password: "",
                agreeToTerms: false,
              });
            }}
            style={{ ...buttonStyle, backgroundColor: "#6b7280" }}
          >
            다시 입력
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <label>
            사용자명:
            <input
              style={inputStyle}
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="사용자명"
            />
          </label>

          <label>
            이메일:
            <input
              style={inputStyle}
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="email@example.com"
            />
          </label>

          <label>
            비밀번호:
            <input
              style={inputStyle}
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="비밀번호"
            />
          </label>

          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "16px",
            }}
          >
            <input
              name="agreeToTerms"
              type="checkbox"
              checked={formData.agreeToTerms}
              onChange={handleChange}
            />
            이용약관에 동의합니다
          </label>

          <button
            type="submit"
            style={{
              ...buttonStyle,
              opacity: formData.agreeToTerms ? 1 : 0.5,
              cursor: formData.agreeToTerms ? "pointer" : "not-allowed",
            }}
            disabled={!formData.agreeToTerms}
          >
            가입하기
          </button>
        </form>
      )}
    </div>
  );
}

// --- 3. 배열 상태 관리 (할 일 목록) ---
function TodoList() {
  const [todos, setTodos] = useState([
    { id: 1, text: "React 공부하기", completed: false },
    { id: 2, text: "운동하기", completed: true },
  ]);
  const [newTodo, setNewTodo] = useState("");
  const [nextId, setNextId] = useState(3);

  // 추가: 새 배열을 생성 (concat 또는 spread)
  const handleAdd = () => {
    if (newTodo.trim() === "") return; // 빈 값 방지

    setTodos((prev) => [
      ...prev,
      { id: nextId, text: newTodo.trim(), completed: false },
    ]);
    setNextId((prev) => prev + 1);
    setNewTodo(""); // 입력 초기화
  };

  // 토글: map으로 해당 항목만 변경한 새 배열 생성
  const handleToggle = (id) => {
    setTodos((prev) =>
      prev.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  // 삭제: filter로 해당 항목을 제외한 새 배열 생성
  const handleDelete = (id) => {
    setTodos((prev) => prev.filter((todo) => todo.id !== id));
  };

  // Enter 키로 추가
  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      handleAdd();
    }
  };

  const containerStyle = {
    padding: "24px",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    margin: "16px 0",
    fontFamily: "sans-serif",
  };

  const inputRowStyle = {
    display: "flex",
    gap: "8px",
    marginBottom: "16px",
  };

  const inputStyle = {
    flex: 1,
    padding: "8px 12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "1rem",
  };

  const completedCount = todos.filter((t) => t.completed).length;

  return (
    <div style={containerStyle}>
      <h2>할 일 목록 (배열 상태)</h2>

      {/* 입력 영역 */}
      <div style={inputRowStyle}>
        <input
          style={inputStyle}
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="할 일을 입력하세요"
        />
        <button
          onClick={handleAdd}
          style={{
            padding: "8px 16px",
            backgroundColor: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          추가
        </button>
      </div>

      {/* 목록 */}
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {todos.map((todo) => (
          <li
            key={todo.id}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "10px 0",
              borderBottom: "1px solid #f3f4f6",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <input
                type="checkbox"
                checked={todo.completed}
                onChange={() => handleToggle(todo.id)}
              />
              <span
                style={{
                  textDecoration: todo.completed ? "line-through" : "none",
                  color: todo.completed ? "#9ca3af" : "#1f2937",
                }}
              >
                {todo.text}
              </span>
            </div>
            <button
              onClick={() => handleDelete(todo.id)}
              style={{
                padding: "4px 8px",
                backgroundColor: "#fef2f2",
                color: "#dc2626",
                border: "1px solid #fecaca",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "0.85rem",
              }}
            >
              삭제
            </button>
          </li>
        ))}
      </ul>

      {/* 통계 */}
      <p style={{ fontSize: "0.85rem", color: "#6b7280", marginTop: "12px" }}>
        총 {todos.length}개 중 {completedCount}개 완료
      </p>
    </div>
  );
}

// --- App 컴포넌트 ---
function App() {
  return (
    <div
      style={{
        padding: "24px",
        maxWidth: "600px",
        margin: "0 auto",
        fontFamily: "sans-serif",
      }}
    >
      <h1 style={{ textAlign: "center" }}>폼 입력과 상태 관리</h1>

      <ControlledInput />
      <RegistrationForm />
      <TodoList />
    </div>
  );
}

export default App;
