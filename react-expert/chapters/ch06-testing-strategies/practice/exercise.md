# 챕터 06 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: 장바구니 컴포넌트 통합 테스트 (⭐⭐⭐⭐)

### 설명

온라인 쇼핑몰의 장바구니 컴포넌트를 테스트합니다. 이 컴포넌트는 다음 기능을 갖습니다:
- API (`GET /api/cart`)에서 장바구니 항목을 조회
- 수량 변경 (`PATCH /api/cart/:id`)
- 항목 삭제 (`DELETE /api/cart/:id`)
- 총 금액 자동 계산

### 요구 사항

1. MSW 핸들러를 작성하여 세 가지 API 엔드포인트를 모킹하세요.
2. 다음 테스트 케이스를 작성하세요:
   - 장바구니 항목이 올바르게 표시되는지 확인
   - 수량 증가/감소 시 총 금액이 업데이트되는지 확인
   - 항목 삭제 후 목록에서 제거되는지 확인
   - API 오류 시 에러 메시지가 표시되는지 확인
3. 모든 요소 탐색에 접근성 쿼리(`getByRole`, `getByLabelText` 등)를 사용하세요.
4. `userEvent`를 사용하여 사용자 상호작용을 시뮬레이션하세요.

### 힌트

<details><summary>힌트 보기</summary>

- MSW의 `http.patch`와 `http.delete` 핸들러를 작성하세요.
- 수량 변경 시 `waitFor`를 사용하여 UI 업데이트를 기다리세요.
- 버튼의 접근성 이름을 `aria-label`로 명시하면 `getByRole('button', { name: ... })`으로 정확히 선택할 수 있습니다.
- `within()`을 사용하면 특정 영역 내에서만 요소를 탐색할 수 있습니다.

</details>

---

## 문제 2: useInfiniteScroll 커스텀 훅 테스트 (⭐⭐⭐⭐)

### 설명

무한 스크롤을 구현하는 `useInfiniteScroll` 훅을 테스트합니다. 이 훅은 다음을 관리합니다:
- 페이지 단위 데이터 로딩
- Intersection Observer로 스크롤 감지
- 로딩/에러/더 불러올 데이터 여부 상태

### 요구 사항

1. `renderHook`을 사용하여 훅을 독립적으로 테스트하세요.
2. `IntersectionObserver`를 모킹하여 스크롤 이벤트를 시뮬레이션하세요.
3. 다음 테스트 케이스를 작성하세요:
   - 초기 데이터를 성공적으로 로드하는지 확인
   - 스크롤 시 다음 페이지를 자동으로 로드하는지 확인
   - 마지막 페이지에 도달하면 더 이상 요청하지 않는지 확인
   - 로딩 중 중복 요청을 방지하는지 확인
   - 에러 발생 시 재시도할 수 있는지 확인

### 힌트

<details><summary>힌트 보기</summary>

- `IntersectionObserver`를 `vi.fn()`으로 모킹하고, 콜백을 수동으로 호출하세요:
  ```tsx
  const mockObserve = vi.fn();
  const mockUnobserve = vi.fn();
  let observerCallback: IntersectionObserverCallback;

  global.IntersectionObserver = vi.fn((callback) => {
    observerCallback = callback;
    return { observe: mockObserve, unobserve: mockUnobserve, disconnect: vi.fn() };
  }) as any;
  ```
- `act()` 내에서 `observerCallback`을 호출하여 교차(intersection)를 시뮬레이션하세요.
- MSW와 함께 사용하여 페이지네이션 API를 모킹하세요.

</details>

---

## 문제 3: 접근성 준수 폼 컴포넌트 테스트 (⭐⭐⭐⭐⭐)

### 설명

회원가입 폼의 접근성을 종합적으로 테스트합니다. 폼에는 다음이 포함됩니다:
- 이메일, 비밀번호, 비밀번호 확인 필드
- 실시간 유효성 검사 메시지
- 에러/성공 토스트 알림
- 비밀번호 강도 표시기

### 요구 사항

1. `vitest-axe`를 사용하여 다음 상태별 접근성을 검증하세요:
   - 초기 렌더링 상태
   - 유효성 검사 에러가 표시된 상태
   - 성공적인 제출 후 상태
2. 키보드만으로 전체 폼을 사용할 수 있는지 테스트하세요:
   - Tab으로 필드 간 이동
   - Enter로 제출
   - Escape로 토스트 닫기
3. 스크린 리더 호환성을 테스트하세요:
   - `aria-invalid`, `aria-errormessage` 연결 확인
   - `aria-live` 영역에 에러 메시지가 올바르게 전달되는지 확인
   - 비밀번호 강도 표시기에 `aria-valuenow`, `aria-valuetext` 확인

### 힌트

<details><summary>힌트 보기</summary>

- `userEvent.tab()`으로 탭 네비게이션을 테스트하세요.
- `userEvent.keyboard('{Enter}')`, `userEvent.keyboard('{Escape}')`로 키보드 이벤트를 시뮬레이션하세요.
- `toHaveAttribute('aria-invalid', 'true')`로 ARIA 속성을 검증하세요.
- 비밀번호 강도 표시기는 `role="meter"` 또는 `role="progressbar"`를 사용하세요.
- `expect(element).toHaveFocus()`로 포커스 위치를 확인하세요.

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 RTL의 쿼리 우선순위와 MSW 핸들러 작성법을 복습하세요.
