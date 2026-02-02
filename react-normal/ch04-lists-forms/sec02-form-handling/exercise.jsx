// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과
// 참고: 이 연습은 React의 폼 처리 패턴을 JavaScript로 연습합니다.

// ===== 문제 1: 폼 상태 관리 객체 만들기 =====
// React의 제어 컴포넌트(Controlled Component) 패턴을 시뮬레이션합니다.
// 필드 이름 배열을 받아 상태 관리 객체를 반환하세요.
// 반환 객체:
//   getValue(fieldName) - 해당 필드의 현재 값 반환
//   setValue(fieldName, value) - 해당 필드의 값 설정
//   getAll() - 모든 필드의 현재 값을 객체로 반환
//   reset() - 모든 필드를 빈 문자열("")로 초기화

function createFormState(fields) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 폼 유효성 검사 =====
// 데이터와 규칙을 받아 검증 결과를 반환하세요.
// rules 형식: { 필드명: { required: true, minLength: 3, pattern: /정규식/ } }
// 반환: { isValid: boolean, errors: { 필드명: "오류 메시지" } }
// 규칙별 오류 메시지:
//   required → "필수 입력 항목입니다"
//   minLength → "최소 N자 이상 입력하세요" (N은 규칙값)
//   pattern → "올바른 형식이 아닙니다"

function validateForm(data, rules) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 폼 제출 처리 =====
// 유효성 검사 후 제출 결과를 반환하세요.
// 검증 성공: { success: true, data: formData }
// 검증 실패: { success: false, errors: { 필드명: "오류 메시지" } }

function handleFormSubmit(formData, validationRules) {
  // TODO: 여기에 코드를 작성하세요
  // 힌트: validateForm() 함수를 활용하세요
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
