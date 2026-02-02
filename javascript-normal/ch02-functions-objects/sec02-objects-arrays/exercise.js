// 실행: node exercise.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 사용자 프로필 생성 =====
// 이름, 나이, 취미 배열을 받아 프로필 객체를 반환하세요.
// 객체에 introduce() 메서드를 포함합니다.
// introduce()는 "안녕하세요, {name}입니다. {age}살입니다." 형식의 문자열을 반환합니다.

function createProfile(name, age, hobbies) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 객체 병합 =====
// 두 객체를 병합하는 함수를 작성하세요.
// 두 번째 객체의 값이 우선합니다.
// 원본 객체를 변경하지 않아야 합니다.

function mergeObjects(obj1, obj2) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: 중첩 데이터 탐색 =====
// 학생 목록에서 기준 점수 이상인 학생의 이름 배열을 반환하세요.
// students: [{ name: "...", score: N }, ...]
// minScore: 기준 점수

function getTopStudents(students, minScore) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 프로필 생성 테스트 ===");
const profile = createProfile("홍길동", 30, ["독서", "코딩"]);
console.assert(profile.name === "홍길동", "이름 테스트 실패");
console.assert(profile.age === 30, "나이 테스트 실패");
console.assert(JSON.stringify(profile.hobbies) === '["독서","코딩"]', "취미 테스트 실패");
console.assert(profile.introduce() === "안녕하세요, 홍길동입니다. 30살입니다.", "소개 테스트 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 객체 병합 테스트 ===");
const obj1 = { a: 1, b: 2 };
const obj2 = { b: 3, c: 4 };
const merged = mergeObjects(obj1, obj2);
console.assert(merged.a === 1, "a 테스트 실패");
console.assert(merged.b === 3, "b 우선순위 테스트 실패");
console.assert(merged.c === 4, "c 테스트 실패");
console.assert(obj1.b === 2, "원본 변경 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 중첩 데이터 테스트 ===");
const students = [
  { name: "김철수", score: 85 },
  { name: "이영희", score: 92 },
  { name: "박지민", score: 78 },
  { name: "최수현", score: 95 },
];
const topStudents = getTopStudents(students, 90);
console.assert(JSON.stringify(topStudents) === '["이영희","최수현"]', "기본 테스트 실패");
const allStudents = getTopStudents(students, 0);
console.assert(allStudents.length === 4, "전체 테스트 실패");
const noStudents = getTopStudents(students, 100);
console.assert(noStudents.length === 0, "빈 결과 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
