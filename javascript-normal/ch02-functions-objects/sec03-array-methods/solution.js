// 실행: node solution.js
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 데이터 변환 =====
function getDiscountedProducts(products) {
  // map()으로 각 상품을 이름+할인가 객체로 변환
  return products.map((p) => ({
    name: p.name,
    // 할인가 계산: 원래가격 * (1 - 할인율)
    salePrice: p.price * (1 - p.discountRate),
  }));
}

// ===== 문제 2: 필터링과 변환 조합 =====
function getPassedStudentNames(students) {
  return students
    // 60점 이상 필터링
    .filter((s) => s.score >= 60)
    // 이름만 추출
    .map((s) => s.name)
    // 오름차순 정렬 (문자열 기본 정렬)
    .sort();
}

// ===== 문제 3: reduce로 통계 계산 =====
function getStats(numbers) {
  // 빈 배열 처리
  if (numbers.length === 0) {
    return { sum: 0, average: 0, min: 0, max: 0 };
  }

  // reduce로 합계, 최솟값, 최댓값을 한 번에 계산
  const result = numbers.reduce(
    (acc, num) => ({
      sum: acc.sum + num,
      min: Math.min(acc.min, num),
      max: Math.max(acc.max, num),
    }),
    { sum: 0, min: Infinity, max: -Infinity }
  );

  // 평균 계산 추가
  return {
    ...result,
    average: result.sum / numbers.length,
  };
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
