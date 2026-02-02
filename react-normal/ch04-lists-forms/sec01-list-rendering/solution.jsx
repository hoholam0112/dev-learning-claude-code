// 실행: node solution.jsx
// 기대 결과: 모든 테스트 통과

// ===== 문제 1: 리스트 렌더링 함수 =====
// React에서 map()으로 배열을 JSX 요소로 변환하는 것과 동일한 패턴입니다.
// 실제 React에서는 문자열 대신 <li> 같은 JSX 요소를 반환합니다.
function renderList(items) {
  // map()을 사용하여 각 항목을 포맷된 문자열로 변환
  // React에서 items.map(item => <li>{item.name}</li>)과 동일한 개념
  return items.map((item) => {
    const status = item.active ? "활성" : "비활성";
    return `[${status}] ${item.name}`;
  });
}

// ===== 문제 2: 필터링 후 렌더링 =====
// React에서 렌더링 전에 filter()로 데이터를 걸러내는 패턴입니다.
// 예: todos.filter(t => !t.done).map(t => <TodoItem key={t.id} {...t} />)
function filterAndRender(items, condition) {
  // 1단계: 조건에 맞는 항목만 필터링 (React의 조건부 리스트 렌더링)
  // 2단계: 필터링된 결과를 포맷 (React의 map() 렌더링)
  return items
    .filter(condition)
    .map((item, index) => `${index + 1}. ${item.name} (${item.category})`);
}

// ===== 문제 3: 카테고리별 그룹화 =====
// React에서 중첩 리스트를 렌더링하기 전에 데이터를 가공하는 패턴입니다.
// 그룹화된 데이터는 Object.entries()와 map()을 중첩하여 렌더링합니다.
// 예:
// {Object.entries(grouped).map(([category, items]) => (
//   <section key={category}>
//     <h2>{category}</h2>
//     <ul>{items.map(item => <li key={item.id}>{item.name}</li>)}</ul>
//   </section>
// ))}
function groupByCategory(items) {
  // reduce()를 사용하여 카테고리별로 그룹화
  // 이 패턴은 React에서 데이터를 중첩 구조로 변환할 때 자주 사용됩니다
  return items.reduce((groups, item) => {
    // 해당 카테고리 키가 없으면 빈 배열로 초기화
    const category = item.category;
    if (!groups[category]) {
      groups[category] = [];
    }
    // 해당 카테고리에 항목 추가 (원래 순서 유지)
    groups[category].push(item);
    return groups;
  }, {});
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
