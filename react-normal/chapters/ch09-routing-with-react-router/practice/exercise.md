# 챕터 09 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.jsx` 참조

---

## 문제 1: 상품 카탈로그 라우팅 (⭐⭐)

### 설명
상품 카탈로그 웹사이트의 라우팅을 구현하세요. 홈, 상품 목록, 상품 상세, 소개 페이지로 구성됩니다.

### 요구 사항
- 4개 이상의 더미 상품 데이터를 만들 것 (id, name, price, description, category)
- 라우트 구성:
  - `/` : 홈 페이지 (추천 상품 2~3개 표시)
  - `/products` : 전체 상품 목록
  - `/products/:id` : 상품 상세 페이지
  - `/about` : 소개 페이지
  - `*` : 404 페이지
- `NavLink`를 사용하여 현재 페이지에 해당하는 네비게이션 항목을 강조 표시
- 상품 상세 페이지에서 `useNavigate`로 "목록으로 돌아가기" 버튼 구현
- 존재하지 않는 상품 ID 접근 시 적절한 에러 메시지 표시

### 힌트
<details><summary>힌트 보기</summary>

- `useParams()`로 받은 id는 문자열이므로 `Number(id)`로 변환하여 상품을 찾습니다
- NavLink의 `style` 속성에 함수를 전달하면 `isActive` 값을 받을 수 있습니다
- `navigate(-1)`은 브라우저 히스토리에서 뒤로 가기와 동일합니다

</details>

---

## 문제 2: 쿼리 파라미터 기반 필터링 (⭐⭐⭐)

### 설명
상품 목록에 카테고리 필터와 정렬 기능을 URL 쿼리 파라미터로 구현하세요. 필터 상태가 URL에 반영되어 링크 공유가 가능해야 합니다.

### 요구 사항
- `useSearchParams`를 사용하여 URL 쿼리 파라미터 관리
- 카테고리 필터: `?category=전자기기` 형태로 URL에 반영
- 정렬 옵션: `?sort=price_asc` 또는 `?sort=price_desc` 또는 `?sort=name`
- 카테고리와 정렬을 동시에 적용 가능: `?category=도서&sort=price_asc`
- "필터 초기화" 버튼으로 모든 쿼리 파라미터 제거
- URL을 직접 입력해도 필터가 올바르게 적용되어야 함

### 힌트
<details><summary>힌트 보기</summary>

- `searchParams.get('category')`로 현재 카테고리 필터값을 가져옵니다
- 여러 파라미터를 동시에 설정하려면:
  ```jsx
  setSearchParams({ category: '도서', sort: 'price_asc' });
  ```
- 하나의 파라미터만 변경하고 나머지는 유지하려면:
  ```jsx
  const newParams = new URLSearchParams(searchParams);
  newParams.set('sort', 'price_asc');
  setSearchParams(newParams);
  ```
- 정렬은 `Array.sort()`를 사용하되 원본 배열을 변경하지 않도록 `[...arr].sort()`를 사용합니다

</details>

---

## 문제 3: 보호된 라우트 (Protected Route) (⭐⭐⭐)

### 설명
로그인 여부에 따라 접근 가능한 페이지를 제한하는 **보호된 라우트** 패턴을 구현하세요. 로그인하지 않은 사용자가 보호된 페이지에 접근하면 로그인 페이지로 리다이렉트됩니다.

### 요구 사항
- 간단한 로그인/로그아웃 기능 구현 (실제 API 호출 불필요, state로 관리)
- `ProtectedRoute` 래퍼 컴포넌트를 만들 것:
  - 로그인된 경우: 자식 컴포넌트(Outlet) 렌더링
  - 로그인되지 않은 경우: `/login`으로 리다이렉트 (`Navigate` 컴포넌트 사용)
- 라우트 구성:
  - `/` : 홈 (공개)
  - `/login` : 로그인 페이지 (공개)
  - `/dashboard` : 대시보드 (보호됨)
  - `/profile` : 프로필 (보호됨)
  - `/settings` : 설정 (보호됨)
- 로그인 후 원래 가려던 페이지로 리다이렉트 (예: `/settings` 접근 시도 → 로그인 → `/settings`으로 이동)
- 네비게이션 바에서 로그인 상태에 따라 다른 메뉴 표시

### 힌트
<details><summary>힌트 보기</summary>

- `Navigate` 컴포넌트로 리다이렉트:
  ```jsx
  import { Navigate, useLocation } from 'react-router-dom';

  function ProtectedRoute() {
    const { user } = useAuth();
    const location = useLocation();

    if (!user) {
      // state에 현재 위치를 저장하여 로그인 후 돌아올 수 있게 함
      return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <Outlet />;
  }
  ```
- 로그인 후 원래 페이지로 이동:
  ```jsx
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';
  navigate(from, { replace: true });
  ```

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요.
> 특히 "useParams", "useNavigate", "useSearchParams"의 사용법을 복습하면 도움이 됩니다.
