// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 구조 분해 할당 =====
function extractUserInfo(response) {
  // 중첩 구조 분해로 user 객체 내의 값을 한 번에 추출
  // role에 기본값 "user" 설정
  const {
    data: {
      user: { name, email, role = "user" },
    },
  } = response;

  return { name, email, role };
}

// ===== 문제 2: 불변 업데이트 =====
function updateObject(original, updates) {
  // 스프레드로 원본을 복사하고, updates로 덮어쓰기
  // 원본 객체는 변경되지 않음
  return { ...original, ...updates };
}

// ===== 문제 3: 안전한 데이터 접근 =====
function getUserCity(user) {
  // 옵셔널 체이닝으로 안전하게 접근
  // null, undefined인 경우 에러 없이 undefined 반환
  // ?? 로 null/undefined일 때 기본값 사용
  return user?.address?.city ?? "알 수 없음";
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
