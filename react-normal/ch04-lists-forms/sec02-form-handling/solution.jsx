// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 폼 상태 관리 객체 만들기 =====
// React의 useState + 객체 state 패턴을 시뮬레이션합니다.
// 실제 React에서는 이렇게 사용합니다:
//   const [formData, setFormData] = useState({ username: "", email: "" });
//   formData.username → getValue("username")
//   setFormData({...formData, username: "값"}) → setValue("username", "값")
function createFormState(fields) {
  // 내부 상태 객체 (React의 state에 해당)
  // 클로저를 이용하여 외부에서 직접 접근 불가 (캡슐화)
  let state = {};

  // 각 필드를 빈 문자열로 초기화
  fields.forEach((field) => {
    state[field] = "";
  });

  return {
    // 특정 필드의 현재 값을 읽기 (React에서 state.fieldName에 해당)
    getValue(fieldName) {
      return state[fieldName];
    },

    // 특정 필드의 값을 설정 (React에서 setState에 해당)
    // React의 제어 컴포넌트에서 onChange 핸들러가 하는 역할
    setValue(fieldName, value) {
      state = { ...state, [fieldName]: value };
    },

    // 모든 필드의 현재 값을 객체로 반환 (폼 제출 시 사용)
    getAll() {
      return { ...state };
    },

    // 모든 필드를 초기값(빈 문자열)으로 리셋
    // React에서 setFormData({ username: "", email: "" })에 해당
    reset() {
      fields.forEach((field) => {
        state[field] = "";
      });
    },
  };
}

// ===== 문제 2: 폼 유효성 검사 =====
// React에서 폼 제출(onSubmit) 시 입력값을 검증하는 패턴입니다.
// 실제 React에서는 이 결과로 errors state를 업데이트하여 오류 메시지를 표시합니다.
// 예: setErrors(validateForm(formData, rules).errors);
function validateForm(data, rules) {
  const errors = {};

  // 각 필드의 규칙을 순회하며 검증
  for (const fieldName in rules) {
    const fieldRules = rules[fieldName];
    const value = data[fieldName] || "";

    // 규칙 우선순위: required → minLength → pattern
    // 첫 번째 실패한 규칙의 메시지만 반환 (중복 방지)

    // 1. 필수 입력 검사
    if (fieldRules.required && !value.trim()) {
      errors[fieldName] = "필수 입력 항목입니다";
      continue; // 다음 필드로 이동 (이미 오류 발생)
    }

    // 2. 최소 길이 검사
    if (fieldRules.minLength && value.length < fieldRules.minLength) {
      errors[fieldName] = `최소 ${fieldRules.minLength}자 이상 입력하세요`;
      continue;
    }

    // 3. 패턴(정규식) 검사
    if (fieldRules.pattern && !fieldRules.pattern.test(value)) {
      errors[fieldName] = "올바른 형식이 아닙니다";
      continue;
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

// ===== 문제 3: 폼 제출 처리 =====
// React 폼의 onSubmit 핸들러 흐름을 시뮬레이션합니다.
// 실제 React에서의 흐름:
//   1. e.preventDefault() — 페이지 새로고침 방지
//   2. validateForm() — 유효성 검사
//   3. 성공 시 → API 호출 등 제출 로직 실행
//   4. 실패 시 → setErrors()로 오류 메시지 표시
function handleFormSubmit(formData, validationRules) {
  // 유효성 검사 수행 (validateForm 함수 재사용)
  const validationResult = validateForm(formData, validationRules);

  if (validationResult.isValid) {
    // 검증 성공: 데이터와 함께 성공 결과 반환
    // 실제 React에서는 여기서 API 호출(fetch)을 수행합니다
    return {
      success: true,
      data: { ...formData },
    };
  } else {
    // 검증 실패: 오류 정보와 함께 실패 결과 반환
    // 실제 React에서는 setErrors(validationResult.errors)로 오류를 표시합니다
    return {
      success: false,
      errors: validationResult.errors,
    };
  }
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 폼 상태 관리 테스트 ===");
const form = createFormState(["username", "email", "password"]);

// 초기값 확인
console.assert(form.getValue("username") === "", "초기값은 빈 문자열이어야 합니다");
console.assert(form.getValue("email") === "", "초기값은 빈 문자열이어야 합니다");

// 값 설정
form.setValue("username", "김철수");
form.setValue("email", "kim@example.com");
console.assert(form.getValue("username") === "김철수", "setValue 후 getValue 실패");
console.assert(form.getValue("email") === "kim@example.com", "setValue 후 getValue 실패");

// 전체 값 조회
const allValues = form.getAll();
console.assert(allValues.username === "김철수", "getAll() username 실패");
console.assert(allValues.email === "kim@example.com", "getAll() email 실패");
console.assert(allValues.password === "", "getAll() password 실패");

// 리셋
form.reset();
console.assert(form.getValue("username") === "", "reset 후 값이 비어있어야 합니다");
console.assert(form.getValue("email") === "", "reset 후 값이 비어있어야 합니다");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 폼 유효성 검사 테스트 ===");
const rules = {
  username: { required: true, minLength: 2 },
  email: { required: true, pattern: /@/ },
  password: { required: true, minLength: 8 },
};

// 유효한 데이터
const validResult = validateForm(
  { username: "김철수", email: "kim@example.com", password: "12345678" },
  rules
);
console.assert(validResult.isValid === true, "유효한 데이터가 검증 실패");
console.assert(Object.keys(validResult.errors).length === 0, "오류가 없어야 합니다");

// 빈 데이터
const emptyResult = validateForm(
  { username: "", email: "", password: "" },
  rules
);
console.assert(emptyResult.isValid === false, "빈 데이터가 검증 통과");
console.assert(emptyResult.errors.username === "필수 입력 항목입니다", "username 오류 메시지 실패");
console.assert(emptyResult.errors.email === "필수 입력 항목입니다", "email 오류 메시지 실패");

// 최소 길이 검사
const shortResult = validateForm(
  { username: "김", email: "kim@test.com", password: "1234" },
  rules
);
console.assert(shortResult.isValid === false, "짧은 데이터가 검증 통과");
console.assert(shortResult.errors.username === "최소 2자 이상 입력하세요", "minLength 오류 메시지 실패");
console.assert(shortResult.errors.password === "최소 8자 이상 입력하세요", "minLength 오류 메시지 실패");

// 패턴 검사
const patternResult = validateForm(
  { username: "김철수", email: "invalid-email", password: "12345678" },
  rules
);
console.assert(patternResult.isValid === false, "잘못된 이메일이 검증 통과");
console.assert(patternResult.errors.email === "올바른 형식이 아닙니다", "pattern 오류 메시지 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 폼 제출 처리 테스트 ===");
const submitRules = {
  username: { required: true, minLength: 2 },
  email: { required: true, pattern: /@/ },
};

// 성공 케이스
const successResult = handleFormSubmit(
  { username: "김철수", email: "kim@example.com" },
  submitRules
);
console.assert(successResult.success === true, "유효한 제출이 실패");
console.assert(successResult.data.username === "김철수", "제출 데이터 확인 실패");
console.assert(successResult.data.email === "kim@example.com", "제출 데이터 확인 실패");

// 실패 케이스
const failResult = handleFormSubmit(
  { username: "", email: "invalid" },
  submitRules
);
console.assert(failResult.success === false, "무효한 제출이 성공");
console.assert(failResult.errors.username === "필수 입력 항목입니다", "제출 오류 확인 실패");
console.assert(failResult.errors.email === "올바른 형식이 아닙니다", "제출 오류 확인 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n모든 테스트를 통과했습니다!");
