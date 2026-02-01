# 챕터 04 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 사용자 목록 대시보드 (난이도: ⭐⭐)

### 설명
사용자 목록을 표시하고, 상태(활성/비활성)에 따라 필터링할 수 있는 대시보드를 만드세요.

### 요구 사항
- 다음 데이터를 사용하세요:
  ```jsx
  const users = [
    { id: 1, name: "김철수", role: "관리자", isActive: true, lastLogin: "2024-01-15" },
    { id: 2, name: "이영희", role: "편집자", isActive: true, lastLogin: "2024-01-14" },
    { id: 3, name: "박민수", role: "뷰어", isActive: false, lastLogin: "2023-12-20" },
    { id: 4, name: "최지은", role: "편집자", isActive: true, lastLogin: "2024-01-15" },
    { id: 5, name: "정하나", role: "관리자", isActive: false, lastLogin: "2023-11-30" },
    { id: 6, name: "강동원", role: "뷰어", isActive: true, lastLogin: "2024-01-13" },
  ];
  ```
- 필터 버튼 3개: "전체", "활성", "비활성"
- 각 사용자 카드에 다음을 표시:
  - 이름, 역할
  - 활성/비활성 상태 뱃지 (색상 다르게)
  - 마지막 접속일
- 역할별 아이콘 또는 색상을 다르게 표시 (관리자/편집자/뷰어)
- 필터링된 사용자 수를 표시하세요
- 결과가 없을 때 빈 상태 메시지를 표시하세요

### 힌트
<details><summary>힌트 보기</summary>

- 필터 상태: `const [filter, setFilter] = useState("all")`
- 조건부 필터링: `users.filter(u => filter === "all" || (filter === "active" ? u.isActive : !u.isActive))`
- 역할별 색상 매핑: `{ "관리자": "#dc2626", "편집자": "#2563eb", "뷰어": "#6b7280" }`
- 빈 상태 체크: `{filteredUsers.length === 0 ? <Empty /> : <List />}`

</details>

---

## 문제 2: 영화 리뷰 게시판 (난이도: ⭐⭐)

### 설명
영화 리뷰를 추가하고 목록으로 표시하는 게시판을 만드세요. 조건부 렌더링과 리스트 렌더링을 종합적으로 활용합니다.

### 요구 사항
- 리뷰 데이터 구조: `{ id, title, rating (1-5), content, author, date }`
- 초기 리뷰 3개를 미리 설정하세요
- 새 리뷰 추가 기능:
  - 영화 제목, 평점(1~5 선택), 내용, 작성자 입력
  - "등록" 버튼으로 리스트에 추가
  - 등록 후 입력 폼 초기화
- 리뷰 목록 표시:
  - 평점을 별(★)로 표시하세요 (예: ★★★☆☆)
  - 평점 4 이상이면 "추천" 뱃지를 표시하세요
- 정렬 기능: "최신순" / "평점순"
- 리뷰가 없을 때 적절한 메시지를 표시하세요
- "삭제" 버튼으로 리뷰를 제거할 수 있어야 합니다

### 힌트
<details><summary>힌트 보기</summary>

- 별 표시: `"★".repeat(rating) + "☆".repeat(5 - rating)`
- 새 리뷰 id 생성: `Date.now()` 또는 별도 카운터 상태
- 정렬: `sort((a, b) => sortBy === "recent" ? b.id - a.id : b.rating - a.rating)`
- 입력 폼에 여러 상태를 사용하거나 객체 상태를 활용하세요

</details>

---

## 문제 3: 다단계 카테고리 네비게이션 (난이도: ⭐⭐⭐)

### 설명
카테고리를 선택하면 해당 카테고리의 항목들이 표시되는 2단계 네비게이션을 만드세요.

### 요구 사항
- 다음 데이터 구조를 사용하세요:
  ```jsx
  const categories = [
    {
      id: "food",
      name: "음식",
      items: [
        { id: 1, name: "비빔밥", description: "한국 전통 음식", popular: true },
        { id: 2, name: "파스타", description: "이탈리아 면 요리", popular: false },
        { id: 3, name: "초밥", description: "일본 전통 음식", popular: true },
        { id: 4, name: "타코", description: "멕시코 전통 음식", popular: false },
      ],
    },
    {
      id: "drink",
      name: "음료",
      items: [
        { id: 5, name: "아메리카노", description: "에스프레소 + 물", popular: true },
        { id: 6, name: "녹차라떼", description: "녹차 + 우유", popular: true },
        { id: 7, name: "스무디", description: "과일 혼합 음료", popular: false },
      ],
    },
    {
      id: "dessert",
      name: "디저트",
      items: [
        { id: 8, name: "티라미수", description: "이탈리아 디저트", popular: true },
        { id: 9, name: "마카롱", description: "프랑스 디저트", popular: false },
      ],
    },
  ];
  ```
- 카테고리 탭을 클릭하면 해당 카테고리의 항목 목록이 표시
- "인기" 필터 토글: 인기 항목만 보기
- 선택된 카테고리가 없을 때: "카테고리를 선택하세요" 메시지
- 필터링 결과가 없을 때: 적절한 빈 상태 메시지
- 각 항목 옆에 "인기" 뱃지를 조건부로 표시

### 힌트
<details><summary>힌트 보기</summary>

- 선택된 카테고리: `const [selectedCategoryId, setSelectedCategoryId] = useState(null)`
- 선택된 카테고리 데이터: `categories.find(c => c.id === selectedCategoryId)`
- 2단계 구조: 먼저 카테고리 탭을 map으로 렌더링, 선택된 카테고리의 items를 map으로 렌더링
- 조건부 렌더링을 3단계로: (1) 카테고리 선택 안 됨 (2) 필터링 결과 없음 (3) 항목 표시

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요.
> map()에서 key를 빠뜨리지 않도록 주의하고, 고유한 id를 key로 사용하세요.
