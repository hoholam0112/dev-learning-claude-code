// 실행: node exercise.js
// 기대 결과: 모든 테스트 통과

// 참고: 실제 모듈 시스템은 파일을 분리하여 사용하지만,
// 이 연습에서는 모듈 패턴(객체 반환)으로 개념을 연습합니다.

// ===== 문제 1: 수학 모듈 만들기 =====
// add, subtract, multiply, divide 함수를 포함하는 객체를 반환하세요.
// divide에서 0으로 나누면 null을 반환합니다.

function createMathModule() {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 문자열 모듈 만들기 =====
// capitalize: 첫 글자를 대문자로 ("hello" → "Hello")
// reverse: 문자열 뒤집기 ("hello" → "olleh")
// truncate: 지정 길이로 자르기, 초과 시 "..." 추가 ("hello world", 5 → "hello...")

function createStringModule() {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 수학 모듈 테스트 ===");
const math = createMathModule();
console.assert(math.add(3, 5) === 8, "add 테스트 실패");
console.assert(math.subtract(10, 4) === 6, "subtract 테스트 실패");
console.assert(math.multiply(3, 7) === 21, "multiply 테스트 실패");
console.assert(math.divide(15, 3) === 5, "divide 테스트 실패");
console.assert(math.divide(10, 0) === null, "divide by zero 테스트 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 문자열 모듈 테스트 ===");
const str = createStringModule();
console.assert(str.capitalize("hello") === "Hello", "capitalize 테스트 실패");
console.assert(str.capitalize("") === "", "빈 문자열 capitalize 테스트 실패");
console.assert(str.reverse("hello") === "olleh", "reverse 테스트 실패");
console.assert(str.truncate("hello world", 5) === "hello...", "truncate 초과 테스트 실패");
console.assert(str.truncate("hi", 5) === "hi", "truncate 미만 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
