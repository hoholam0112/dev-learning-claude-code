# 챕터 08 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: Compound Components - Modal 시스템 (⭐⭐⭐⭐)

### 설명

재사용 가능한 Modal 컴포넌트 시스템을 Compound Components 패턴으로 구현하세요. HTML의 `<dialog>` 요소와 유사한 선언적 API를 가져야 합니다.

### 요구 사항

1. 다음 하위 컴포넌트를 구현하세요:
   - `Modal` (루트) - 포탈 렌더링, 배경 오버레이
   - `Modal.Trigger` - 모달 열기 트리거
   - `Modal.Content` - 모달 콘텐츠 영역
   - `Modal.Header` - 제목 + 닫기 버튼
   - `Modal.Body` - 본문 내용
   - `Modal.Footer` - 액션 버튼 영역
   - `Modal.Close` - 닫기 버튼 (어디서든 사용 가능)

2. 다음 기능을 지원하세요:
   - 비제어/제어(controlled/uncontrolled) 모드
   - Escape 키로 닫기
   - 배경 오버레이 클릭으로 닫기 (옵션)
   - 포커스 트래핑 (열린 동안 모달 내부에만 포커스)
   - 접근성: `role="dialog"`, `aria-modal`, `aria-labelledby`

3. 사용 API 예시:
   ```tsx
   <Modal>
     <Modal.Trigger asChild>
       <button>모달 열기</button>
     </Modal.Trigger>
     <Modal.Content>
       <Modal.Header>제목</Modal.Header>
       <Modal.Body>내용...</Modal.Body>
       <Modal.Footer>
         <Modal.Close asChild>
           <button>닫기</button>
         </Modal.Close>
         <button>확인</button>
       </Modal.Footer>
     </Modal.Content>
   </Modal>
   ```

### 힌트

<details><summary>힌트 보기</summary>

- `createPortal`을 사용하여 모달을 `document.body`에 렌더링하세요.
- 포커스 트래핑은 `MutationObserver`나 `querySelectorAll('button, input, ...')`로 구현합니다.
- `asChild` prop은 `React.cloneElement`로 구현할 수 있습니다. 자식 요소에 props를 병합합니다.
- Context로 `isOpen`, `open`, `close`를 공유합니다.

</details>

---

## 문제 2: Headless Component - useTable 훅 (⭐⭐⭐⭐⭐)

### 설명

테이블 로직을 캡슐화하는 Headless `useTable` 훅을 구현하세요. TanStack Table에서 영감을 받은 간소화 버전입니다.

### 요구 사항

1. 다음 기능을 지원하는 `useTable` 훅을 구현하세요:
   - 컬럼 정의 (`columns`)
   - 데이터 소스 (`data`)
   - 정렬 (단일 컬럼, 오름차순/내림차순)
   - 검색/필터링 (글로벌 검색)
   - 페이지네이션 (페이지 크기, 현재 페이지)
   - 행 선택 (체크박스)

2. Props 생성자를 제공하세요:
   - `getTableProps()` - `<table>` 요소용 props
   - `getHeaderProps(column)` - `<th>` 요소용 props (정렬 클릭 포함)
   - `getRowProps(row)` - `<tr>` 요소용 props
   - `getCellProps(cell)` - `<td>` 요소용 props

3. TypeScript 제네릭을 활용하여 타입 안전한 API를 제공하세요.

### 힌트

<details><summary>힌트 보기</summary>

- 컬럼 정의 타입:
  ```tsx
  interface ColumnDef<T> {
    id: string;
    header: string;
    accessorKey: keyof T;
    sortable?: boolean;
    cell?: (value: T[keyof T], row: T) => ReactNode;
  }
  ```
- `useMemo`를 적극 활용하여 정렬/필터링/페이지네이션 결과를 캐싱하세요.
- 정렬 상태: `{ columnId: string; direction: 'asc' | 'desc' } | null`
- 페이지네이션: 원본 데이터를 먼저 필터 → 정렬 → 슬라이스 순서로 처리하세요.

</details>

---

## 문제 3: Feature-Sliced Design 프로젝트 구조 (⭐⭐⭐⭐⭐)

### 설명

소셜 미디어 애플리케이션을 Feature-Sliced Design(FSD) 아키텍처로 구조화하세요. 다음 기능이 포함됩니다:

- 사용자 인증 (로그인, 회원가입, 프로필)
- 게시글 작성, 조회, 좋아요
- 알림 시스템
- 검색 기능
- 설정 (테마, 알림 설정)

### 요구 사항

1. FSD 6개 레이어에 맞는 디렉토리 구조를 설계하세요.
2. 각 슬라이스의 `index.ts` 공개 API를 정의하세요.
3. 다음을 구현하세요:
   - `entities/user/` - User 엔티티 (타입, 모델, UI 컴포넌트)
   - `features/auth/` - 인증 기능 (로그인 폼, 로직)
   - `features/create-post/` - 게시글 작성 기능
   - `widgets/post-feed/` - 게시글 피드 위젯
   - `pages/home/` - 홈 페이지 조합
4. 레이어 간 의존성 규칙이 올바르게 지켜지는지 확인하세요.

### 힌트

<details><summary>힌트 보기</summary>

- 프로젝트 구조 예시:
  ```
  src/
  ├── app/          # 앱 설정, 프로바이더, 라우터
  ├── pages/        # 페이지 조합
  │   ├── home/
  │   └── profile/
  ├── widgets/      # 독립적 UI 블록
  │   ├── header/
  │   └── post-feed/
  ├── features/     # 비즈니스 로직 + UI
  │   ├── auth/
  │   ├── create-post/
  │   └── search/
  ├── entities/     # 비즈니스 엔티티
  │   ├── user/
  │   ├── post/
  │   └── notification/
  └── shared/       # 공유 유틸리티
      ├── ui/
      ├── api/
      └── lib/
  ```
- 각 슬라이스 내부 세그먼트: `ui/`, `model/`, `api/`, `lib/`
- `index.ts`에서 외부 공개할 것만 export하세요 (내부 구현은 숨김).
- 같은 레이어의 슬라이스끼리는 직접 import하면 안 됩니다. `shared/` 레이어를 통해 공유하세요.

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 각 패턴의 핵심 아이디어와 사용 시나리오를 명확히 이해하세요.
