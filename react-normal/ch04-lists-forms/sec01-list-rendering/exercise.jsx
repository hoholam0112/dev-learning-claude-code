// 실행: node exercise.jsx
// 기대 결과: 모든 테스트 통과
// 참고: 이 연습은 React의 리스트 렌더링 패턴을 JavaScript로 연습합니다.

// ===== 문제 1: 리스트 렌더링 함수 =====
// 배열의 각 항목을 포맷된 문자열로 변환하세요.
// active가 true이면 "[활성] 이름", false이면 "[비활성] 이름"
// 예: { id: 1, name: "김철수", active: true } → "[활성] 김철수"

function renderList(items) {
  // TODO: 여기에 코드를 작성하세요
}

// ===== 문제 2: 필터링 후 렌더링 =====
// 조건 함수로 필터링한 후, "인덱스. 이름 (카테고리)" 형태로 변환하세요.
// 인덱스는 필터링 후 기준으로 1부터 시작합니다.
// 예: { id: 1, name: "사과", category: "과일" } → "1. 사과 (과일)"

function filterAndRender(items, condition) {
  // TODO: 여기에 코드를 작성하세요
  // items: [{ id, name, category }, ...]
  // condition: (item) => boolean
}

// ===== 문제 3: 카테고리별 그룹화 =====
// 항목들을 category 속성을 기준으로 그룹화하세요.
// 반환: { 카테고리명: [항목, 항목, ...], ... }
// 예: [{ id: 1, name: "사과", category: "과일" }]
//   → { "과일": [{ id: 1, name: "사과", category: "과일" }] }

function groupByCategory(items) {
  // TODO: 여기에 코드를 작성하세요
}

// --- 테스트 (수정하지 마세요) ---
console.log("=== 문제 1: 리스트 렌더링 테스트 ===");
const listItems = [
  { id: 1, name: "김철수", active: true },
  { id: 2, name: "이영희", active: false },
  { id: 3, name: "박민수", active: true },
];
const rendered = renderList(listItems);
console.assert(rendered.length === 3, "3개의 항목이 반환되어야 합니다");
console.assert(rendered[0] === "[활성] 김철수", `첫 번째 항목 실패: ${rendered[0]}`);
console.assert(rendered[1] === "[비활성] 이영희", `두 번째 항목 실패: ${rendered[1]}`);
console.assert(rendered[2] === "[활성] 박민수", `세 번째 항목 실패: ${rendered[2]}`);

// 빈 배열 테스트
const emptyResult = renderList([]);
console.assert(emptyResult.length === 0, "빈 배열 처리 실패");
console.log("문제 1: 모든 테스트 통과!");

console.log("\n=== 문제 2: 필터링 후 렌더링 테스트 ===");
const products = [
  { id: 1, name: "사과", category: "과일" },
  { id: 2, name: "당근", category: "채소" },
  { id: 3, name: "바나나", category: "과일" },
  { id: 4, name: "시금치", category: "채소" },
  { id: 5, name: "오렌지", category: "과일" },
];
const fruitsOnly = filterAndRender(products, (item) => item.category === "과일");
console.assert(fruitsOnly.length === 3, `과일 개수 실패: ${fruitsOnly.length}`);
console.assert(fruitsOnly[0] === "1. 사과 (과일)", `첫 번째 과일 실패: ${fruitsOnly[0]}`);
console.assert(fruitsOnly[1] === "2. 바나나 (과일)", `두 번째 과일 실패: ${fruitsOnly[1]}`);
console.assert(fruitsOnly[2] === "3. 오렌지 (과일)", `세 번째 과일 실패: ${fruitsOnly[2]}`);

// 모두 필터링되는 경우
const noMatch = filterAndRender(products, (item) => item.category === "육류");
console.assert(noMatch.length === 0, "매칭 없음 처리 실패");
console.log("문제 2: 모든 테스트 통과!");

console.log("\n=== 문제 3: 카테고리별 그룹화 테스트 ===");
const mixedItems = [
  { id: 1, name: "사과", category: "과일" },
  { id: 2, name: "당근", category: "채소" },
  { id: 3, name: "바나나", category: "과일" },
  { id: 4, name: "시금치", category: "채소" },
  { id: 5, name: "우유", category: "유제품" },
];
const grouped = groupByCategory(mixedItems);
console.assert(Object.keys(grouped).length === 3, "3개의 카테고리가 있어야 합니다");
console.assert(grouped["과일"].length === 2, "과일 카테고리에 2개 항목");
console.assert(grouped["채소"].length === 2, "채소 카테고리에 2개 항목");
console.assert(grouped["유제품"].length === 1, "유제품 카테고리에 1개 항목");
console.assert(grouped["과일"][0].name === "사과", "그룹 내 순서 유지 확인");
console.assert(grouped["과일"][1].name === "바나나", "그룹 내 순서 유지 확인");

// 빈 배열 테스트
const emptyGrouped = groupByCategory([]);
console.assert(Object.keys(emptyGrouped).length === 0, "빈 배열 그룹화 실패");
console.log("문제 3: 모든 테스트 통과!");

console.log("\n모든 테스트를 통과했습니다!");
