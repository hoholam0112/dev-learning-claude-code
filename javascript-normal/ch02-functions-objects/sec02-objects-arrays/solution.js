// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 사용자 프로필 생성 =====
function createProfile(name, age, hobbies) {
  return {
    // 단축 속성: 키와 변수명이 같으면 생략 가능
    name,
    age,
    hobbies,
    // 메서드 단축 문법
    introduce() {
      return `안녕하세요, ${this.name}입니다. ${this.age}살입니다.`;
    },
  };
}

// ===== 문제 2: 객체 병합 =====
function mergeObjects(obj1, obj2) {
  // 스프레드 연산자로 새 객체 생성
  // 뒤에 오는 obj2의 값이 obj1의 같은 키를 덮어씀
  return { ...obj1, ...obj2 };
}

// ===== 문제 3: 중첩 데이터 탐색 =====
function getTopStudents(students, minScore) {
  const result = [];
  for (const student of students) {
    // 기준 점수 이상인 학생의 이름만 추가
    if (student.score >= minScore) {
      result.push(student.name);
    }
  }
  return result;
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
