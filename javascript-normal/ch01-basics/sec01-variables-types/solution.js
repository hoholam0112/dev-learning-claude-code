// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 변수 선언과 출력 =====
// 이름과 이메일은 변경되지 않으므로 const 사용
const userName = "홍길동";
// 나이는 변할 수 있으므로 let 사용
let userAge = 25;
const userEmail = "hong@example.com";

// 템플릿 리터럴을 사용하여 변수를 문자열에 삽입
console.log(`이름: ${userName}, 나이: ${userAge}, 이메일: ${userEmail}`);

// ===== 문제 2: 타입 검사 함수 =====
function getTypeInKorean(value) {
  // typeof로 타입을 확인하고 한국어로 매핑
  const typeMap = {
    string: "문자열",
    number: "숫자",
    boolean: "불리언",
  };

  const type = typeof value;
  // typeMap에 해당 타입이 있으면 반환, 없으면 "기타"
  return typeMap[type] || "기타";
}

// ===== 문제 3: 타입 변환 =====
function sumStrings(strings) {
  let sum = 0;
  for (let i = 0; i < strings.length; i++) {
    // Number()로 문자열을 숫자로 변환
    const num = Number(strings[i]);
    // isNaN으로 변환 실패 여부 확인, NaN이면 0으로 처리
    if (!isNaN(num)) {
      sum += num;
    }
  }
  return sum;
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1 테스트 ===");
console.log(`이름: ${userName}, 나이: ${userAge}, 이메일: ${userEmail}`);

console.log("\n=== 문제 2 테스트 ===");
console.assert(getTypeInKorean("hello") === "문자열", "문자열 테스트 실패");
console.assert(getTypeInKorean(42) === "숫자", "숫자 테스트 실패");
console.assert(getTypeInKorean(true) === "불리언", "불리언 테스트 실패");
console.assert(getTypeInKorean(null) === "기타", "기타 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3 테스트 ===");
console.assert(sumStrings(["1", "2", "3"]) === 6, "기본 테스트 실패");
console.assert(sumStrings(["10", "abc", "20"]) === 30, "NaN 처리 테스트 실패");
console.assert(sumStrings([]) === 0, "빈 배열 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
