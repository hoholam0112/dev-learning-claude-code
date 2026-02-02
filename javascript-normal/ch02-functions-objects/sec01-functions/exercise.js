// 실행: node exercise.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 온도 변환 =====
// 섭씨 → 화씨: F = C × 9/5 + 32
// 화씨 → 섭씨: C = (F - 32) × 5/9
// 화살표 함수로 작성하세요.

// TODO: celsiusToFahrenheit 화살표 함수를 작성하세요

// TODO: fahrenheitToCelsius 화살표 함수를 작성하세요

// ===== 문제 2: 계산기 함수 =====
// 연산자("+", "-", "*", "/")와 두 수를 받아 결과를 반환하세요.
// 0으로 나누기: "0으로 나눌 수 없습니다" 반환
// 잘못된 연산자: "지원하지 않는 연산자입니다" 반환

function calculate(operator, a, b) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 배열 처리 함수 =====
// Array.prototype.map과 동일한 동작을 하는 myMap 함수를 작성하세요.
// 내장 map 메서드를 사용하지 않고 구현합니다.
// 콜백에 (요소, 인덱스)를 전달합니다.

function myMap(arr, callback) {
  // TODO: 여기에 코드를 작성하세요
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
