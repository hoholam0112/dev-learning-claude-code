# 챕터 07 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: 서버/클라이언트 경계 설계 (⭐⭐⭐⭐)

### 설명

전자상거래 상품 페이지를 서버 컴포넌트와 클라이언트 컴포넌트로 분리 설계하세요. 다음 요소들이 포함됩니다:

- 상품 정보 (이름, 가격, 설명, 이미지)
- 재고 현황 표시
- 색상/사이즈 선택기
- 수량 선택 및 장바구니 추가 버튼
- 상품 리뷰 목록
- 리뷰 작성 폼
- 관련 상품 추천 (느린 API)

### 요구 사항

1. 각 요소를 서버 컴포넌트 또는 클라이언트 컴포넌트로 분류하고 이유를 설명하세요.
2. `'use client'` 경계를 최소화하는 컴포넌트 트리를 설계하세요.
3. Suspense 경계를 적절히 배치하여 스트리밍 SSR을 구현하세요.
4. 상품 데이터 페칭 함수에 캐싱과 재검증 전략을 적용하세요.

### 힌트

<details><summary>힌트 보기</summary>

- 상품 정보, 재고 현황, 리뷰 목록은 서버에서 직접 가져올 수 있습니다.
- 색상/사이즈 선택기, 수량 선택, 장바구니 버튼은 상호작용이 필요합니다.
- 관련 상품 추천은 느린 API이므로 별도 Suspense boundary에 배치합니다.
- `<ProductInfo>` (서버)가 `<AddToCartForm>` (클라이언트)를 children으로 포함하는 구조를 고려하세요.

</details>

---

## 문제 2: Server Actions 기반 폼 처리 (⭐⭐⭐⭐⭐)

### 설명

블로그 게시글 편집 기능을 Server Actions로 구현하세요. 다음 요구 사항을 충족해야 합니다:

- 기존 게시글 데이터를 서버 컴포넌트에서 불러와 표시
- Server Action으로 게시글 수정 처리
- `useActionState`로 폼 상태와 에러 관리
- `useOptimistic`으로 미리보기에 낙관적 업데이트 적용
- 자동 저장(Auto-save) 기능 구현

### 요구 사항

1. 편집 페이지의 서버 컴포넌트(`app/blog/[slug]/edit/page.tsx`)를 작성하세요.
2. `updatePost` Server Action을 구현하세요 (유효성 검사 포함).
3. 클라이언트 컴포넌트에서 `useActionState`로 제출 상태를 관리하세요.
4. 제목 변경 시 미리보기에 `useOptimistic`으로 즉시 반영하세요.
5. 내용 변경 후 3초 동안 추가 변경이 없으면 자동 저장하세요.

### 힌트

<details><summary>힌트 보기</summary>

- `useActionState(updatePost, initialState)`에서 `initialState`에 기존 게시글 데이터를 넣으세요.
- 자동 저장은 디바운스와 Server Action을 결합합니다:
  ```tsx
  const debouncedSave = useCallback(
    debounce((content: string) => {
      startTransition(async () => {
        await autoSavePost(postId, content);
      });
    }, 3000),
    [postId]
  );
  ```
- `revalidateTag('post-${slug}')`로 캐시를 무효화하세요.

</details>

---

## 문제 3: 스트리밍 SSR 대시보드 (⭐⭐⭐⭐⭐)

### 설명

여러 데이터 소스에서 정보를 가져와 표시하는 대시보드를 스트리밍 SSR로 구현하세요. 각 데이터 소스의 응답 속도가 다릅니다:

| 데이터 | 소요 시간 | 설명 |
|--------|----------|------|
| 사용자 프로필 | ~100ms | 빠름 |
| 알림 목록 | ~500ms | 보통 |
| 활동 피드 | ~1500ms | 느림 |
| 추천 콘텐츠 | ~3000ms | 매우 느림 |

### 요구 사항

1. 각 섹션을 개별 Suspense boundary로 감싸서 점진적 로딩을 구현하세요.
2. 각 섹션에 적절한 스켈레톤 UI 폴백을 제공하세요.
3. 에러가 발생한 섹션만 ErrorBoundary로 격리하세요 (다른 섹션은 영향 없음).
4. `loading.tsx`와 `error.tsx`를 활용한 파일 기반 로딩/에러 처리를 구현하세요.
5. 각 데이터 소스에 적절한 캐싱 전략(revalidate 간격)을 적용하세요.

### 힌트

<details><summary>힌트 보기</summary>

- 각 섹션을 비동기 서버 컴포넌트로 구현하면 자연스럽게 스트리밍됩니다:
  ```tsx
  <main>
    <UserProfile />  {/* 즉시 표시 */}
    <Suspense fallback={<NotificationsSkeleton />}>
      <Notifications />  {/* 500ms 후 스트리밍 */}
    </Suspense>
    <Suspense fallback={<ActivityFeedSkeleton />}>
      <ActivityFeed />  {/* 1500ms 후 스트리밍 */}
    </Suspense>
    <Suspense fallback={<RecommendationsSkeleton />}>
      <Recommendations />  {/* 3000ms 후 스트리밍 */}
    </Suspense>
  </main>
  ```
- 에러 격리를 위해 각 Suspense 내부에 ErrorBoundary를 배치하거나, Next.js의 `error.tsx`를 활용하세요.
- 사용자 프로필은 `revalidate: 300`, 알림은 `revalidate: 30`, 피드는 `revalidate: 60`으로 설정하세요.

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 40% |
| 코드 가독성 | 20% |
| 엣지 케이스 처리 | 20% |
| 효율성 | 20% |

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 서버/클라이언트 경계 설계 원칙과 Suspense 배치 전략을 복습하세요.
