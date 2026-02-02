// 실행: node exercise.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 데이터 변환 =====
// 상품 배열에서 이름과 할인가를 포함하는 새 배열을 만드세요.
// 할인가 = price * (1 - discountRate)
// map()을 사용하세요.

function getDiscountedProducts(products) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 필터링과 변환 조합 =====
// 점수가 60점 이상인 학생의 이름을 오름차순 정렬하여 반환하세요.
// filter(), map(), sort()를 체이닝하세요.

function getPassedStudentNames(students) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 3: reduce로 통계 계산 =====
// 숫자 배열의 통계(합계, 평균, 최솟값, 최댓값)를 객체로 반환하세요.
// 빈 배열이면 { sum: 0, average: 0, min: 0, max: 0 }을 반환합니다.

function getStats(numbers) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 할인가 테스트 ===");
const products = [
  { name: "노트북", price: 1000000, discountRate: 0.1 },
  { name: "마우스", price: 50000, discountRate: 0.2 },
  { name: "키보드", price: 80000, discountRate: 0.15 },
];
const discounted = getDiscountedProducts(products);
console.assert(discounted[0].name === "노트북", "이름 테스트 실패");
console.assert(discounted[0].salePrice === 900000, "노트북 할인가 테스트 실패");
console.assert(discounted[1].salePrice === 40000, "마우스 할인가 테스트 실패");
console.assert(discounted[2].salePrice === 68000, "키보드 할인가 테스트 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 합격자 테스트 ===");
const students = [
  { name: "Charlie", score: 75 },
  { name: "Alice", score: 55 },
  { name: "Bob", score: 82 },
  { name: "Diana", score: 90 },
];
const passed = getPassedStudentNames(students);
console.assert(JSON.stringify(passed) === '["Bob","Charlie","Diana"]', "합격자 테스트 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 통계 테스트 ===");
const stats = getStats([10, 20, 30, 40, 50]);
console.assert(stats.sum === 150, "합계 테스트 실패");
console.assert(stats.average === 30, "평균 테스트 실패");
console.assert(stats.min === 10, "최솟값 테스트 실패");
console.assert(stats.max === 50, "최댓값 테스트 실패");
const emptyStats = getStats([]);
console.assert(emptyStats.sum === 0 && emptyStats.average === 0, "빈 배열 테스트 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n🎉 모든 테스트를 통과했습니다!");
