// 실행: node exercise.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 구조 분해 할당 =====
// API 응답에서 사용자 이름, 이메일, 역할(기본값: "user")을 추출하세요.
// 구조 분해 할당을 사용합니다.

function extractUserInfo(response) {
  // TODO: 구조 분해 할당으로 name, email, role(기본값 "user")을 추출하세요
  // response 구조: { data: { user: { name, email, role? } } }

  // TODO: 추출한 값을 객체로 반환하세요
  // return { name, email, role };
}

// ===== 문제 2: 불변 업데이트 =====
// 원본 객체를 변경하지 않고, updates의 내용을 반영한 새 객체를 반환하세요.
// 스프레드 연산자를 사용합니다.

function updateObject(original, updates) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 안전한 데이터 접근 =====
// 사용자 객체에서 도시 이름을 안전하게 추출하세요.
// address나 city가 없으면 기본값 "알 수 없음"을 반환합니다.
// 옵셔널 체이닝(?.)과 널 병합 연산자(??)를 사용합니다.

function getUserCity(user) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 구조 분해 할당 테스트 ===");
const response1 = { data: { user: { name: "김철수", email: "kim@test.com", role: "admin" } } };
const info1 = extractUserInfo(response1);
console.assert(info1.name === "김철수", "이름 테스트 실패");
console.assert(info1.email === "kim@test.com", "이메일 테스트 실패");
console.assert(info1.role === "admin", "역할 테스트 실패");

const response2 = { data: { user: { name: "이영희", email: "lee@test.com" } } };
const info2 = extractUserInfo(response2);
console.assert(info2.role === "user", "기본 역할 테스트 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 불변 업데이트 테스트 ===");
const original = { name: "김철수", age: 28, city: "서울" };
const updated = updateObject(original, { age: 29, city: "부산" });
console.assert(updated.name === "김철수", "유지된 속성 테스트 실패");
console.assert(updated.age === 29, "업데이트된 age 테스트 실패");
console.assert(updated.city === "부산", "업데이트된 city 테스트 실패");
console.assert(original.age === 28, "원본 불변 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 안전한 접근 테스트 ===");
console.assert(getUserCity({ address: { city: "서울" } }) === "서울", "정상 접근 테스트 실패");
console.assert(getUserCity({ address: {} }) === "알 수 없음", "city 없음 테스트 실패");
console.assert(getUserCity({}) === "알 수 없음", "address 없음 테스트 실패");
console.assert(getUserCity(null) === "알 수 없음", "null 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
