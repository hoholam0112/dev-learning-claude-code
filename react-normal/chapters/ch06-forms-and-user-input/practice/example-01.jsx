/**
 * 챕터 06 - 예제 01: 제어 컴포넌트 기반 회원가입 폼
 *
 * 핵심 개념:
 * - 제어 컴포넌트 패턴 (value + onChange)
 * - 단일 state 객체로 다중 필드 관리
 * - 실시간 유효성 검사
 * - 폼 제출 처리
 *
 * 실행 방법:
 *   npx create-react-app form-demo
 *   cd form-demo
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 *   // 브라우저에서 http://localhost:3000 확인
 */

import React, { useState } from 'react';

// ──────────────────────────────────────────────
// 유효성 검사 유틸리티 함수들
// ──────────────────────────────────────────────

/**
 * 각 필드에 대한 유효성 검사를 수행한다.
 * 에러가 있으면 해당 필드명을 키로, 에러 메시지를 값으로 하는 객체를 반환한다.
 */
function validateForm(formData) {
  const errors = {};

  // 사용자명 검사
  if (!formData.username.trim()) {
    errors.username = '사용자명을 입력해주세요';
  } else if (formData.username.length < 2) {
    errors.username = '사용자명은 최소 2자 이상이어야 합니다';
  }

  // 이메일 검사
  if (!formData.email.trim()) {
    errors.email = '이메일을 입력해주세요';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = '올바른 이메일 형식이 아닙니다';
  }

  // 비밀번호 검사
  if (!formData.password) {
    errors.password = '비밀번호를 입력해주세요';
  } else if (formData.password.length < 8) {
    errors.password = '비밀번호는 최소 8자 이상이어야 합니다';
  } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
    errors.password = '비밀번호는 영문자와 숫자를 포함해야 합니다';
  }

  // 비밀번호 확인 검사
  if (!formData.confirmPassword) {
    errors.confirmPassword = '비밀번호 확인을 입력해주세요';
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = '비밀번호가 일치하지 않습니다';
  }

  return errors;
}

// ──────────────────────────────────────────────
// 메인 컴포넌트: SignUpForm (회원가입 폼)
// ──────────────────────────────────────────────

function SignUpForm() {
  // 폼 데이터 state - 모든 필드를 하나의 객체로 관리
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  // 유효성 검사 에러 state
  const [errors, setErrors] = useState({});

  // 폼 제출 상태
  const [isSubmitted, setIsSubmitted] = useState(false);

  // 각 필드의 터치 여부 (포커스 후 이탈 시 에러 표시 용도)
  const [touched, setTouched] = useState({});

  /**
   * 모든 입력 필드에 대해 하나의 핸들러로 처리한다.
   * e.target.name으로 어떤 필드인지 구분한다.
   */
  const handleChange = (e) => {
    const { name, value } = e.target;

    // state 업데이트
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // 이미 터치된 필드라면 실시간 유효성 검사
    if (touched[name]) {
      const updatedData = { ...formData, [name]: value };
      const validationErrors = validateForm(updatedData);
      setErrors((prev) => ({
        ...prev,
        [name]: validationErrors[name] || '',
      }));
    }
  };

  /**
   * 필드에서 포커스가 빠져나갈 때(blur) 해당 필드를 '터치됨'으로 표시하고
   * 유효성 검사를 수행한다.
   */
  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));

    // 해당 필드만 유효성 검사
    const validationErrors = validateForm(formData);
    setErrors((prev) => ({
      ...prev,
      [name]: validationErrors[name] || '',
    }));
  };

  /**
   * 폼 제출 핸들러
   * e.preventDefault()로 기본 제출(페이지 새로고침) 방지
   */
  const handleSubmit = (e) => {
    e.preventDefault(); // 매우 중요! 이걸 빼면 페이지가 새로고침됨

    // 모든 필드를 터치됨으로 표시
    const allTouched = Object.keys(formData).reduce(
      (acc, key) => ({ ...acc, [key]: true }),
      {}
    );
    setTouched(allTouched);

    // 전체 유효성 검사
    const validationErrors = validateForm(formData);
    setErrors(validationErrors);

    // 에러가 없으면 제출 성공
    if (Object.keys(validationErrors).length === 0) {
      setIsSubmitted(true);
      console.log('회원가입 데이터:', formData);
    }
  };

  /**
   * 폼 초기화 핸들러
   */
  const handleReset = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    });
    setErrors({});
    setTouched({});
    setIsSubmitted(false);
  };

  // 비밀번호 강도 표시 (간단한 시각적 피드백)
  const getPasswordStrength = (password) => {
    if (!password) return { level: 0, text: '', color: '#ccc' };
    if (password.length < 6) return { level: 1, text: '약함', color: '#f44336' };
    if (password.length < 10) return { level: 2, text: '보통', color: '#ff9800' };
    if (/(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%])/.test(password)) {
      return { level: 3, text: '강함', color: '#4caf50' };
    }
    return { level: 2, text: '보통', color: '#ff9800' };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  // 제출 성공 화면
  if (isSubmitted) {
    return (
      <div style={styles.container}>
        <div style={styles.successCard}>
          <h2>회원가입 완료!</h2>
          <p>환영합니다, <strong>{formData.username}</strong>님!</p>
          <p>이메일: {formData.email}</p>
          <button onClick={handleReset} style={styles.button}>
            다시 시작
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h1>회원가입</h1>
      <form onSubmit={handleSubmit} style={styles.form}>
        {/* 사용자명 필드 */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>사용자명</label>
          <input
            type="text"
            name="username"
            value={formData.username}       // 제어 컴포넌트: state 값을 사용
            onChange={handleChange}          // 입력 시 state 업데이트
            onBlur={handleBlur}             // 포커스 이탈 시 검증
            placeholder="사용자명을 입력하세요"
            style={{
              ...styles.input,
              borderColor: touched.username && errors.username ? '#f44336' : '#ddd',
            }}
          />
          {touched.username && errors.username && (
            <span style={styles.error}>{errors.username}</span>
          )}
        </div>

        {/* 이메일 필드 */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>이메일</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="example@email.com"
            style={{
              ...styles.input,
              borderColor: touched.email && errors.email ? '#f44336' : '#ddd',
            }}
          />
          {touched.email && errors.email && (
            <span style={styles.error}>{errors.email}</span>
          )}
        </div>

        {/* 비밀번호 필드 */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>비밀번호</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="영문자 + 숫자 포함 8자 이상"
            style={{
              ...styles.input,
              borderColor: touched.password && errors.password ? '#f44336' : '#ddd',
            }}
          />
          {/* 비밀번호 강도 표시 바 */}
          {formData.password && (
            <div style={styles.strengthBar}>
              <div
                style={{
                  ...styles.strengthFill,
                  width: `${(passwordStrength.level / 3) * 100}%`,
                  backgroundColor: passwordStrength.color,
                }}
              />
              <span style={{ fontSize: '12px', color: passwordStrength.color }}>
                {passwordStrength.text}
              </span>
            </div>
          )}
          {touched.password && errors.password && (
            <span style={styles.error}>{errors.password}</span>
          )}
        </div>

        {/* 비밀번호 확인 필드 */}
        <div style={styles.fieldGroup}>
          <label style={styles.label}>비밀번호 확인</label>
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="비밀번호를 다시 입력하세요"
            style={{
              ...styles.input,
              borderColor:
                touched.confirmPassword && errors.confirmPassword ? '#f44336' : '#ddd',
            }}
          />
          {touched.confirmPassword && errors.confirmPassword && (
            <span style={styles.error}>{errors.confirmPassword}</span>
          )}
        </div>

        {/* 제출 버튼 */}
        <button type="submit" style={styles.button}>
          가입하기
        </button>
      </form>
    </div>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  container: {
    maxWidth: '400px',
    margin: '40px auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
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
    transition: 'border-color 0.2s',
  },
  error: {
    color: '#f44336',
    fontSize: '12px',
  },
  button: {
    padding: '12px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
    marginTop: '8px',
  },
  successCard: {
    textAlign: 'center',
    padding: '40px 20px',
    backgroundColor: '#e8f5e9',
    borderRadius: '12px',
  },
  strengthBar: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginTop: '4px',
  },
  strengthFill: {
    height: '4px',
    borderRadius: '2px',
    transition: 'width 0.3s, background-color 0.3s',
    flex: 1,
  },
};

export default SignUpForm;
