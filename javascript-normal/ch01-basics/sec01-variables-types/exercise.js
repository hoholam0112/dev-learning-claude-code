// 실행: node exercise.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 변수 선언과 출력 =====
// 다음 정보를 적절한 변수(const 또는 let)에 저장하세요.
// 이름: "홍길동", 나이: 25, 이메일: "hong@example.com"

// TODO: 여기에 변수를 선언하세요


// TODO: 템플릿 리터럴로 "이름: 홍길동, 나이: 25, 이메일: hong@example.com" 형식으로 출력하세요


// ===== 문제 2: 타입 검사 함수 =====
// 주어진 값의 타입을 한국어로 반환하는 함수를 작성하세요.
// "string" → "문자열", "number" → "숫자", "boolean" → "불리언", 그 외 → "기타"

function getTypeInKorean(value) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 타입 변환 =====
// 문자열 배열의 값을 숫자로 변환하여 합계를 구하는 함수를 작성하세요.
// 변환할 수 없는 값(NaN)은 0으로 처리합니다.

function sumStrings(strings) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
// 문제 1 테스트
console.log("=== 문제 1 테스트 ===");
console.log(`이름: ${userName}, 나이: ${userAge}, 이메일: ${userEmail}`);

// 문제 2 테스트
console.log("\n=== 문제 2 테스트 ===");
console.assert(getTypeInKorean("hello") === "문자열", "문자열 테스트 실패");
console.assert(getTypeInKorean(42) === "숫자", "숫자 테스트 실패");
console.assert(getTypeInKorean(true) === "불리언", "불리언 테스트 실패");
console.assert(getTypeInKorean(null) === "기타", "기타 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

// 문제 3 테스트
console.log("\n=== 문제 3 테스트 ===");
console.assert(sumStrings(["1", "2", "3"]) === 6, "기본 테스트 실패");
console.assert(sumStrings(["10", "abc", "20"]) === 30, "NaN 처리 테스트 실패");
console.assert(sumStrings([]) === 0, "빈 배열 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
