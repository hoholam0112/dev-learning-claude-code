/**
 * 챕터 06 - 연습 문제 모범 답안
 *
 * 이 파일에는 exercise.md의 3개 문제에 대한 모범 답안이 포함되어 있습니다.
 * 각 문제의 답안은 독립적인 컴포넌트로 구현되어 있으며,
 * App 컴포넌트에서 탭으로 전환하여 확인할 수 있습니다.
 *
 * 실행 방법:
 *   npx create-react-app ch06-solutions
 *   cd ch06-solutions
 *   // src/App.js 내용을 이 파일로 교체
 *   npm start
 */

import React, { useState, useRef, useEffect } from 'react';

// ══════════════════════════════════════════════
// 문제 1 답안: 프로필 수정 폼
// ══════════════════════════════════════════════

// 초기값을 상수로 분리 (초기화 시 재사용)
const INITIAL_PROFILE = {
  nickname: '리액트러버',
  bio: '안녕하세요!',
  interest: '프론트엔드',
  newsletter: true,
};

function ProfileEditForm() {
  const [formData, setFormData] = useState({ ...INITIAL_PROFILE });

  // 단일 핸들러로 모든 필드 처리
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSave = () => {
    console.log('저장된 프로필:', formData);
    alert('프로필이 저장되었습니다! (콘솔 확인)');
  };

  const handleReset = () => {
    setFormData({ ...INITIAL_PROFILE });
  };

  return (
    <div style={styles.card}>
      <h2>프로필 수정</h2>

      <div style={styles.fieldGroup}>
        <label style={styles.label}>닉네임</label>
        <input
          type="text"
          name="nickname"
          value={formData.nickname}
          onChange={handleChange}
          style={styles.input}
        />
      </div>

      <div style={styles.fieldGroup}>
        <label style={styles.label}>자기소개</label>
        <textarea
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          rows={3}
          style={{ ...styles.input, resize: 'vertical' }}
        />
      </div>

      <div style={styles.fieldGroup}>
        <label style={styles.label}>관심 분야</label>
        <select
          name="interest"
          value={formData.interest}
          onChange={handleChange}
          style={styles.input}
        >
          <option value="프론트엔드">프론트엔드</option>
          <option value="백엔드">백엔드</option>
          <option value="풀스택">풀스택</option>
        </select>
      </div>

      <div style={styles.checkboxGroup}>
        <input
          type="checkbox"
          name="newsletter"
          checked={formData.newsletter}
          onChange={handleChange}
          id="newsletter"
        />
        <label htmlFor="newsletter">뉴스레터 수신 동의</label>
      </div>

      <div style={styles.buttonGroup}>
        <button onClick={handleSave} style={styles.primaryButton}>저장</button>
        <button onClick={handleReset} style={styles.secondaryButton}>초기화</button>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════
// 문제 2 답안: 실시간 검색 필터
// ══════════════════════════════════════════════

const FRUIT_LIST = [
  '사과', '바나나', '포도', '딸기', '수박',
  '참외', '복숭아', '키위', '망고', '블루베리',
];

function FruitSearch() {
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);

  // 컴포넌트 마운트 시 입력란에 자동 포커스
  useEffect(() => {
    inputRef.current.focus();
  }, []);

  // 검색어로 필터링된 목록
  const filteredFruits = FRUIT_LIST.filter((fruit) =>
    fruit.includes(query)
  );

  const handleClear = () => {
    setQuery('');
    inputRef.current.focus(); // 초기화 후 다시 포커스
  };

  return (
    <div style={styles.card}>
      <h2>과일 검색</h2>

      <div style={styles.searchBox}>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="과일 이름을 검색하세요"
          style={{ ...styles.input, flex: 1 }}
        />
        {query && (
          <button onClick={handleClear} style={styles.clearButton}>
            초기화
          </button>
        )}
      </div>

      <p style={styles.resultCount}>
        {filteredFruits.length}개의 결과
      </p>

      {filteredFruits.length > 0 ? (
        <ul style={styles.list}>
          {filteredFruits.map((fruit) => (
            <li key={fruit} style={styles.listItem}>
              {/* 검색어 하이라이트 */}
              {query ? (
                <>
                  {fruit.split(query).map((part, i, arr) => (
                    <React.Fragment key={i}>
                      {part}
                      {i < arr.length - 1 && (
                        <mark style={styles.highlight}>{query}</mark>
                      )}
                    </React.Fragment>
                  ))}
                </>
              ) : (
                fruit
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p style={styles.noResult}>검색 결과가 없습니다</p>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════
// 문제 3 답안: 다단계 설문조사 폼
// ══════════════════════════════════════════════

function SurveyForm() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    language: 'JavaScript',
    experience: '',
  });
  const [errors, setErrors] = useState({});
  const [isComplete, setIsComplete] = useState(false);

  const totalSteps = 3;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // 입력 시 해당 필드 에러 제거
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // 단계별 유효성 검사
  const validateStep = (step) => {
    const newErrors = {};

    if (step === 1) {
      if (!formData.name.trim()) newErrors.name = '이름을 입력해주세요';
      if (!formData.age) {
        newErrors.age = '나이를 입력해주세요';
      } else if (Number(formData.age) < 1 || Number(formData.age) > 150) {
        newErrors.age = '올바른 나이를 입력해주세요';
      }
    }

    if (step === 2) {
      if (!formData.experience) newErrors.experience = '경력을 선택해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, totalSteps));
    }
  };

  const handlePrev = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
    setErrors({});
  };

  const handleSubmit = () => {
    console.log('설문 결과:', formData);
    setIsComplete(true);
  };

  const handleRestart = () => {
    setFormData({ name: '', age: '', language: 'JavaScript', experience: '' });
    setCurrentStep(1);
    setErrors({});
    setIsComplete(false);
  };

  // 완료 화면
  if (isComplete) {
    return (
      <div style={styles.card}>
        <div style={styles.completeBox}>
          <h2>제출 완료!</h2>
          <p>설문에 참여해 주셔서 감사합니다.</p>
          <button onClick={handleRestart} style={styles.primaryButton}>
            다시 시작
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.card}>
      <h2>설문조사</h2>

      {/* 진행률 표시 */}
      <div style={styles.progressContainer}>
        <div style={styles.progressBar}>
          <div
            style={{
              ...styles.progressFill,
              width: `${(currentStep / totalSteps) * 100}%`,
            }}
          />
        </div>
        <span style={styles.stepText}>{currentStep}단계 / {totalSteps}단계</span>
      </div>

      {/* 1단계: 기본 정보 */}
      {currentStep === 1 && (
        <div style={styles.stepContent}>
          <h3>1단계: 기본 정보</h3>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>이름 *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="이름을 입력하세요"
              style={styles.input}
            />
            {errors.name && <span style={styles.error}>{errors.name}</span>}
          </div>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>나이 *</label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder="나이를 입력하세요"
              min="1"
              max="150"
              style={styles.input}
            />
            {errors.age && <span style={styles.error}>{errors.age}</span>}
          </div>
        </div>
      )}

      {/* 2단계: 개발 정보 */}
      {currentStep === 2 && (
        <div style={styles.stepContent}>
          <h3>2단계: 개발 정보</h3>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>좋아하는 프로그래밍 언어</label>
            <select
              name="language"
              value={formData.language}
              onChange={handleChange}
              style={styles.input}
            >
              <option value="JavaScript">JavaScript</option>
              <option value="Python">Python</option>
              <option value="Java">Java</option>
              <option value="기타">기타</option>
            </select>
          </div>
          <div style={styles.fieldGroup}>
            <label style={styles.label}>경력 *</label>
            <div style={styles.radioGroup}>
              {['학생', '1~3년', '3년 이상'].map((option) => (
                <label key={option} style={styles.radioLabel}>
                  <input
                    type="radio"
                    name="experience"
                    value={option}
                    checked={formData.experience === option}
                    onChange={handleChange}
                  />
                  {option}
                </label>
              ))}
            </div>
            {errors.experience && (
              <span style={styles.error}>{errors.experience}</span>
            )}
          </div>
        </div>
      )}

      {/* 3단계: 확인 및 제출 */}
      {currentStep === 3 && (
        <div style={styles.stepContent}>
          <h3>3단계: 입력 내용 확인</h3>
          <table style={styles.summaryTable}>
            <tbody>
              <tr>
                <td style={styles.summaryLabel}>이름</td>
                <td>{formData.name}</td>
              </tr>
              <tr>
                <td style={styles.summaryLabel}>나이</td>
                <td>{formData.age}세</td>
              </tr>
              <tr>
                <td style={styles.summaryLabel}>프로그래밍 언어</td>
                <td>{formData.language}</td>
              </tr>
              <tr>
                <td style={styles.summaryLabel}>경력</td>
                <td>{formData.experience}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* 네비게이션 버튼 */}
      <div style={styles.buttonGroup}>
        {currentStep > 1 && (
          <button onClick={handlePrev} style={styles.secondaryButton}>
            {currentStep === 3 ? '수정하기' : '이전'}
          </button>
        )}
        {currentStep < totalSteps ? (
          <button onClick={handleNext} style={styles.primaryButton}>
            다음
          </button>
        ) : (
          <button onClick={handleSubmit} style={styles.submitButton}>
            제출하기
          </button>
        )}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════
// 메인 App: 탭으로 문제 전환
// ══════════════════════════════════════════════

function App() {
  const [activeTab, setActiveTab] = useState(1);

  const tabs = [
    { id: 1, label: '문제 1: 프로필 수정', component: <ProfileEditForm /> },
    { id: 2, label: '문제 2: 과일 검색', component: <FruitSearch /> },
    { id: 3, label: '문제 3: 설문조사', component: <SurveyForm /> },
  ];

  return (
    <div style={styles.container}>
      <h1>챕터 06 연습 문제 답안</h1>

      {/* 탭 네비게이션 */}
      <div style={styles.tabBar}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...styles.tab,
              ...(activeTab === tab.id ? styles.activeTab : {}),
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 선택된 탭의 컴포넌트 렌더링 */}
      {tabs.find((tab) => tab.id === activeTab)?.component}
    </div>
  );
}

// ──────────────────────────────────────────────
// 스타일 객체
// ──────────────────────────────────────────────

const styles = {
  container: {
    maxWidth: '600px',
    margin: '20px auto',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  card: {
    padding: '24px',
    border: '1px solid #e0e0e0',
    borderRadius: '12px',
    backgroundColor: '#fff',
  },
  tabBar: {
    display: 'flex',
    gap: '8px',
    marginBottom: '20px',
    flexWrap: 'wrap',
  },
  tab: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    borderRadius: '20px',
    backgroundColor: '#f5f5f5',
    cursor: 'pointer',
    fontSize: '13px',
  },
  activeTab: {
    backgroundColor: '#1976d2',
    color: 'white',
    borderColor: '#1976d2',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    marginBottom: '16px',
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
  error: {
    color: '#f44336',
    fontSize: '12px',
  },
  checkboxGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '16px',
  },
  radioGroup: {
    display: 'flex',
    gap: '16px',
    marginTop: '4px',
  },
  radioLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '14px',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    marginTop: '16px',
  },
  primaryButton: {
    flex: 1,
    padding: '10px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '15px',
    cursor: 'pointer',
  },
  secondaryButton: {
    flex: 1,
    padding: '10px',
    backgroundColor: '#757575',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '15px',
    cursor: 'pointer',
  },
  submitButton: {
    flex: 1,
    padding: '10px',
    backgroundColor: '#4caf50',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '15px',
    cursor: 'pointer',
  },
  searchBox: {
    display: 'flex',
    gap: '8px',
    marginBottom: '12px',
  },
  clearButton: {
    padding: '10px 16px',
    backgroundColor: '#f44336',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  resultCount: {
    fontSize: '13px',
    color: '#666',
    marginBottom: '8px',
  },
  list: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  listItem: {
    padding: '8px 12px',
    borderBottom: '1px solid #eee',
    fontSize: '14px',
  },
  highlight: {
    backgroundColor: '#fff3e0',
    padding: '0 2px',
    borderRadius: '2px',
  },
  noResult: {
    textAlign: 'center',
    color: '#999',
    padding: '20px',
  },
  progressContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '20px',
  },
  progressBar: {
    flex: 1,
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#1976d2',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
  },
  stepText: {
    fontSize: '13px',
    color: '#666',
    whiteSpace: 'nowrap',
  },
  stepContent: {
    minHeight: '200px',
  },
  summaryTable: {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '12px',
  },
  summaryLabel: {
    fontWeight: 'bold',
    padding: '8px 12px',
    borderBottom: '1px solid #eee',
    width: '40%',
    fontSize: '14px',
  },
  completeBox: {
    textAlign: 'center',
    padding: '40px 20px',
  },
};

export default App;
