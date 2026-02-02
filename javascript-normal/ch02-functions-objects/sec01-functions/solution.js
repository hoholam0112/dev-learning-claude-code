// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 온도 변환 =====
// 한 줄 화살표 함수: 본문이 표현식 하나면 중괄호와 return 생략 가능
const celsiusToFahrenheit = (celsius) => celsius * 9 / 5 + 32;
const fahrenheitToCelsius = (fahrenheit) => (fahrenheit - 32) * 5 / 9;

// ===== 문제 2: 계산기 함수 =====
function calculate(operator, a, b) {
  switch (operator) {
    case "+":
      return a + b;
    case "-":
      return a - b;
    case "*":
      return a * b;
    case "/":
      // 0으로 나누기 검사를 먼저 수행
      if (b === 0) return "0으로 나눌 수 없습니다";
      return a / b;
    default:
      // 지원하지 않는 연산자 처리
      return "지원하지 않는 연산자입니다";
  }
}

// ===== 문제 3: 배열 처리 함수 =====
function myMap(arr, callback) {
  const result = [];
  // 배열을 순회하며 콜백 적용
  for (let i = 0; i < arr.length; i++) {
    // 콜백에 요소와 인덱스를 전달하고 결과를 새 배열에 추가
    result.push(callback(arr[i], i));
  }
  return result;
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 온도 변환 테스트 ===");
console.assert(celsiusToFahrenheit(0) === 32, "0°C 테스트 실패");
console.assert(celsiusToFahrenheit(100) === 212, "100°C 테스트 실패");
console.assert(fahrenheitToCelsius(32) === 0, "32°F 테스트 실패");
console.assert(fahrenheitToCelsius(212) === 100, "212°F 테스트 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 계산기 테스트 ===");
console.assert(calculate("+", 3, 5) === 8, "덧셈 테스트 실패");
console.assert(calculate("-", 10, 4) === 6, "뺄셈 테스트 실패");
console.assert(calculate("*", 3, 7) === 21, "곱셈 테스트 실패");
console.assert(calculate("/", 15, 3) === 5, "나눗셈 테스트 실패");
console.assert(calculate("/", 10, 0) === "0으로 나눌 수 없습니다", "0 나눗셈 테스트 실패");
console.assert(calculate("%", 10, 3) === "지원하지 않는 연산자입니다", "잘못된 연산자 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: myMap 테스트 ===");
const doubled = myMap([1, 2, 3], (x) => x * 2);
console.assert(JSON.stringify(doubled) === "[2,4,6]", "두 배 테스트 실패");
const indexed = myMap(["a", "b", "c"], (val, idx) => `${idx}:${val}`);
console.assert(JSON.stringify(indexed) === '["0:a","1:b","2:c"]', "인덱스 테스트 실패");
const empty = myMap([], (x) => x);
console.assert(JSON.stringify(empty) === "[]", "빈 배열 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
