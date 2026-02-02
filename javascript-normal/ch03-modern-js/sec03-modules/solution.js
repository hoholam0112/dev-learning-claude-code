// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 수학 모듈 만들기 =====
function createMathModule() {
  // 각 연산 함수를 정의하고 객체로 묶어 반환
  // 실제 모듈이라면 각 함수를 export하는 것과 같은 패턴
  const add = (a, b) => a + b;
  const subtract = (a, b) => a - b;
  const multiply = (a, b) => a * b;
  const divide = (a, b) => {
    // 0으로 나누기 방지
    if (b === 0) return null;
    return a / b;
  };

  // 단축 속성으로 내보내기 (export와 유사)
  return { add, subtract, multiply, divide };
}

// ===== 문제 2: 문자열 모듈 만들기 =====
function createStringModule() {
  // 첫 글자를 대문자로 변환
  const capitalize = (str) => {
    if (str.length === 0) return "";
    return str[0].toUpperCase() + str.slice(1);
  };

  // 문자열 뒤집기
  const reverse = (str) => {
    let result = "";
    for (let i = str.length - 1; i >= 0; i--) {
      result += str[i];
    }
    return result;
  };

  // 지정 길이로 자르기, 초과 시 "..." 추가
  const truncate = (str, maxLength) => {
    if (str.length <= maxLength) return str;
    return str.slice(0, maxLength) + "...";
  };

  return { capitalize, reverse, truncate };
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
