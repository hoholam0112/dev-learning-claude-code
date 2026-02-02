// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: FizzBuzz =====
function fizzBuzz(n) {
  const result = [];
  for (let i = 1; i <= n; i++) {
    // 15의 배수를 먼저 검사해야 함 (3과 5의 공배수)
    if (i % 15 === 0) {
      result.push("FizzBuzz");
    } else if (i % 3 === 0) {
      result.push("Fizz");
    } else if (i % 5 === 0) {
      result.push("Buzz");
    } else {
      // 숫자 그대로 추가 (문자열이 아닌 number 타입)
      result.push(i);
    }
  }
  return result;
}

// ===== 문제 2: 배열에서 최댓값 찾기 =====
function findMax(numbers) {
  // 빈 배열 처리
  if (numbers.length === 0) {
    return null;
  }

  // 첫 번째 요소를 초기 최댓값으로 설정
  let max = numbers[0];
  // 두 번째 요소부터 비교 시작
  for (let i = 1; i < numbers.length; i++) {
    if (numbers[i] > max) {
      max = numbers[i];
    }
  }
  return max;
}

// ===== 문제 3: 문자열 뒤집기 =====
function reverseString(str) {
  let reversed = "";
  // 문자열의 끝에서부터 시작하여 역순으로 하나씩 추가
  for (let i = str.length - 1; i >= 0; i--) {
    reversed += str[i];
  }
  return reversed;
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: FizzBuzz 테스트 ===");
const result = fizzBuzz(15);
console.assert(result[0] === 1, "1 테스트 실패");
console.assert(result[2] === "Fizz", "Fizz 테스트 실패");
console.assert(result[4] === "Buzz", "Buzz 테스트 실패");
console.assert(result[14] === "FizzBuzz", "FizzBuzz 테스트 실패");
console.assert(result.length === 15, "길이 테스트 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 최댓값 테스트 ===");
console.assert(findMax([3, 7, 2, 9, 1]) === 9, "기본 테스트 실패");
console.assert(findMax([-5, -1, -10]) === -1, "음수 테스트 실패");
console.assert(findMax([42]) === 42, "단일 요소 테스트 실패");
console.assert(findMax([]) === null, "빈 배열 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 문자열 뒤집기 테스트 ===");
console.assert(reverseString("hello") === "olleh", "기본 테스트 실패");
console.assert(reverseString("abc") === "cba", "abc 테스트 실패");
console.assert(reverseString("a") === "a", "단일 문자 테스트 실패");
console.assert(reverseString("") === "", "빈 문자열 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
