/**
 * 챕터 06 - 예제 02: useRef를 활용한 비제어 컴포넌트와 포커스 관리
 *
 * 핵심 개념:
 * - 비제어 컴포넌트 패턴 (ref + defaultValue)
 * - useRef로 DOM 요소에 직접 접근
 * - 엔터키로 다음 필드 포커스 이동
 * - 파일 입력 처리 (비제어 컴포넌트 필수)
 *
 * 실행 방법:
 *   npx create-react-app ref-form-demo
 *   cd ref-form-demo
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 */

import React, { useRef, useState } from 'react';

// ──────────────────────────────────────────────
// 예시 A: 비제어 컴포넌트 기반 간단한 폼
// ──────────────────────────────────────────────

function UncontrolledForm() {
  // 각 입력 필드에 대한 ref 생성
  const nameRef = useRef(null);
  const emailRef = useRef(null);
  const messageRef = useRef(null);
  const fileRef = useRef(null);

  // 제출 결과를 표시하기 위한 state (화면 업데이트가 필요하므로 state 사용)
  const [result, setResult] = useState(null);

  /**
   * 엔터키를 누르면 다음 ref의 입력 필드로 포커스를 이동한다.
   * 비제어 컴포넌트에서도 ref를 통해 DOM 메서드를 직접 호출할 수 있다.
   */
  const handleKeyDown = (e, nextRef) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // 폼 제출 방지
      if (nextRef && nextRef.current) {
        nextRef.current.focus(); // 다음 필드로 포커스 이동
      }
    }
  };

  /**
   * 폼 제출 시 ref.current.value로 각 필드의 값을 읽어온다.
   * 이것이 비제어 컴포넌트의 핵심: state가 아닌 DOM에서 직접 값을 가져온다.
   */
  const handleSubmit = (e) => {
    e.preventDefault();

    // ref를 통해 DOM에서 직접 값을 읽어옴
    const formValues = {
      name: nameRef.current.value,
      email: emailRef.current.value,
      message: messageRef.current.value,
      file: fileRef.current.files[0]?.name || '파일 없음',
    };

    console.log('비제어 컴포넌트 폼 데이터:', formValues);
    setResult(formValues);
  };

  /**
   * 폼 초기화: ref를 통해 DOM 값을 직접 변경
   */
  const handleReset = () => {
    nameRef.current.value = '';
    emailRef.current.value = '';
    messageRef.current.value = '';
    fileRef.current.value = '';
    setResult(null);
    nameRef.current.focus(); // 첫 번째 필드로 포커스
  };

  return (
    <div style={styles.section}>
      <h2>비제어 컴포넌트 폼</h2>
      <p style={styles.description}>
        아래 폼은 <code>ref</code>를 사용하여 값을 관리합니다.
        <br />
        엔터키를 눌러 다음 필드로 이동할 수 있습니다.
      </p>

      <form onSubmit={handleSubmit} style={styles.form}>
        {/* 이름 필드 - defaultValue로 초기값 설정 */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>이름</label>
          <input
            ref={nameRef}
            type="text"
            defaultValue=""
            placeholder="이름을 입력하세요"
            onKeyDown={(e) => handleKeyDown(e, emailRef)}
            style={styles.input}
          />
        </div>

        {/* 이메일 필드 */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>이메일</label>
          <input
            ref={emailRef}
            type="email"
            defaultValue=""
            placeholder="이메일을 입력하세요"
            onKeyDown={(e) => handleKeyDown(e, messageRef)}
            style={styles.input}
          />
        </div>

        {/* 메시지 필드 (textarea) */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>메시지</label>
          <textarea
            ref={messageRef}
            defaultValue=""
            placeholder="메시지를 입력하세요"
            rows={4}
            style={{ ...styles.input, resize: 'vertical' }}
          />
        </div>

        {/* 파일 입력 - 반드시 비제어 컴포넌트여야 함 */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>파일 첨부</label>
          <input
            ref={fileRef}
            type="file"
            style={styles.input}
          />
          <span style={styles.hint}>
            파일 입력은 반드시 비제어 컴포넌트로 처리해야 합니다
          </span>
        </div>

        {/* 버튼 그룹 */}
        <div style={styles.buttonGroup}>
          <button type="submit" style={styles.submitButton}>
            제출하기
          </button>
          <button type="button" onClick={handleReset} style={styles.resetButton}>
            초기화
          </button>
        </div>
      </form>

      {/* 제출 결과 표시 */}
      {result && (
        <div style={styles.resultBox}>
          <h3>제출된 데이터</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// 예시 B: useRef로 렌더링 횟수 추적하기
// ──────────────────────────────────────────────

function RenderCounter() {
  const [inputValue, setInputValue] = useState('');

  // useRef는 리렌더링을 일으키지 않으면서 값을 보존한다
  const renderCount = useRef(0);

  // 매 렌더링마다 카운트 증가 (state가 아니므로 리렌더링 유발하지 않음)
  renderCount.current += 1;

  return (
    <div style={styles.section}>
      <h2>useRef로 렌더링 횟수 추적</h2>
      <p style={styles.description}>
        <code>useRef</code>는 값이 변경되어도 리렌더링을 일으키지 않습니다.
        <br />
        아래 입력란에 타이핑하면 state 변경으로 리렌더링이 발생하고,
        ref에 저장된 카운트가 증가합니다.
      </p>

      <input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="여기에 타이핑하세요"
        style={styles.input}
      />
      <p>
        현재 입력값: <strong>{inputValue || '(없음)'}</strong>
      </p>
      <p>
        렌더링 횟수: <strong>{renderCount.current}</strong>회
      </p>
    </div>
  );
}

// ──────────────────────────────────────────────
// 메인 App 컴포넌트
// ──────────────────────────────────────────────

function App() {
  return (
    <div style={styles.container}>
      <h1>useRef 활용 예제</h1>
      <UncontrolledForm />
      <hr style={styles.divider} />
      <RenderCounter />
    </div>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  container: {
    maxWidth: '500px',
    margin: '40px auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  section: {
    marginBottom: '30px',
  },
  description: {
    color: '#666',
    fontSize: '14px',
    lineHeight: '1.6',
    marginBottom: '16px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  label: {
    fontWeight: 'bold',
    fontSize: '14px',
  },
  input: {
    padding: '10px 12px',
    border: '2px solid #ddd',
    borderRadius: '6px',
    fontSize: '14px',
    outline: 'none',
  },
  hint: {
    fontSize: '11px',
    color: '#999',
    fontStyle: 'italic',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    marginTop: '8px',
  },
  submitButton: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  resetButton: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#757575',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  resultBox: {
    marginTop: '20px',
    padding: '16px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
    border: '1px solid #ddd',
  },
  divider: {
    border: 'none',
    borderTop: '2px solid #eee',
    margin: '30px 0',
  },
};

export default App;
