/**
 * 챕터 07 - 연습 문제 모범 답안
 *
 * 이 파일은 exercise.md의 세 문제에 대한 모범 답안을 담고 있습니다.
 *
 * 실행 방법:
 *   1. Next.js 프로젝트에서 실행:
 *      npx create-next-app@latest solution-demo --typescript --app --tailwind
 *      cd solution-demo
 *
 *   2. 아래 코드를 해당 경로에 배치하고:
 *      npm run dev
 *
 * 참고: 실제 Next.js 프로젝트에서는 각 컴포넌트를 별도 파일로 분리합니다.
 *       이 파일은 학습 목적으로 하나에 합쳐져 있습니다.
 */

import React, {
  Suspense,
  useState,
  useOptimistic,
  useTransition,
  useRef,
  useCallback,
  useEffect,
  useActionState,
} from 'react';

// ============================================================
// 문제 1 답안: 서버/클라이언트 경계 설계 - 전자상거래 상품 페이지
// ============================================================

/**
 * 컴포넌트 분류 설계:
 *
 * [서버 컴포넌트] - JS 번들에 포함되지 않음
 *   - ProductPage: 페이지 레이아웃, 데이터 페칭
 *   - ProductInfo: 상품 이름, 가격, 설명 (정적 정보)
 *   - ProductImages: 이미지 갤러리 (정적)
 *   - StockStatus: 재고 현황 (서버에서 실시간 조회)
 *   - ReviewList: 리뷰 목록 (데이터 페칭)
 *   - RelatedProducts: 관련 상품 (느린 API - 별도 Suspense)
 *
 * [클라이언트 컴포넌트] - 상호작용 필요
 *   - VariantSelector: 색상/사이즈 선택 (useState)
 *   - QuantitySelector: 수량 선택 (useState)
 *   - AddToCartButton: 장바구니 추가 (이벤트 핸들러)
 *   - ReviewForm: 리뷰 작성 (폼 + Server Action)
 */

// --- 타입 정의 ---

interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
  images: string[];
  variants: {
    colors: { name: string; value: string; available: boolean }[];
    sizes: { name: string; available: boolean }[];
  };
  stock: number;
}

interface Review {
  id: number;
  author: string;
  rating: number;
  content: string;
  createdAt: string;
}

// --- 데이터 페칭 함수 (서버 전용) ---

async function fetchProduct(productId: string): Promise<Product> {
  const response = await fetch(
    `${process.env.API_URL}/api/products/${productId}`,
    {
      next: {
        tags: [`product-${productId}`],
        revalidate: 60, // 1분마다 재검증
      },
    }
  );
  if (!response.ok) throw new Error('상품을 찾을 수 없습니다.');
  return response.json();
}

async function fetchReviews(productId: string): Promise<Review[]> {
  const response = await fetch(
    `${process.env.API_URL}/api/products/${productId}/reviews`,
    {
      next: {
        tags: [`reviews-${productId}`],
        revalidate: 120, // 2분마다 재검증
      },
    }
  );
  if (!response.ok) return [];
  return response.json();
}

async function fetchRelatedProducts(productId: string): Promise<Product[]> {
  // 느린 API (3초+ 소요)
  const response = await fetch(
    `${process.env.API_URL}/api/products/${productId}/related`,
    {
      next: { revalidate: 300 }, // 5분마다 재검증
    }
  );
  if (!response.ok) return [];
  return response.json();
}

// --- 상품 페이지 (서버 컴포넌트) ---
// app/products/[id]/page.tsx

export async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await fetchProduct(id);

  return (
    <main>
      <div className="product-layout">
        {/* 서버 컴포넌트: 이미지 갤러리 */}
        <ProductImages images={product.images} name={product.name} />

        <div className="product-details">
          {/* 서버 컴포넌트: 상품 정보 */}
          <ProductInfo product={product} />

          {/* 서버 컴포넌트: 재고 현황 */}
          <StockStatus stock={product.stock} />

          {/* 클라이언트 컴포넌트: 옵션 선택 + 장바구니 */}
          <AddToCartForm product={product} />
        </div>
      </div>

      {/* 서버 컴포넌트: 리뷰 목록 (별도 Suspense) */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <ReviewSection productId={id} />
      </Suspense>

      {/* 서버 컴포넌트: 관련 상품 (느린 API, 별도 Suspense) */}
      <Suspense fallback={<RelatedProductsSkeleton />}>
        <RelatedProducts productId={id} />
      </Suspense>
    </main>
  );
}

// --- 서버 컴포넌트들 ---

function ProductImages({
  images,
  name,
}: {
  images: string[];
  name: string;
}) {
  return (
    <div className="product-images">
      {images.map((src, i) => (
        <img
          key={src}
          src={src}
          alt={`${name} 이미지 ${i + 1}`}
          loading={i === 0 ? 'eager' : 'lazy'}
        />
      ))}
    </div>
  );
}

function ProductInfo({ product }: { product: Product }) {
  return (
    <div>
      <h1>{product.name}</h1>
      <p className="price">{product.price.toLocaleString()}원</p>
      <p className="description">{product.description}</p>
    </div>
  );
}

function StockStatus({ stock }: { stock: number }) {
  const statusText =
    stock > 10 ? '충분한 재고' : stock > 0 ? `${stock}개 남음` : '품절';
  const statusColor =
    stock > 10 ? 'green' : stock > 0 ? 'orange' : 'red';

  return (
    <div aria-label="재고 현황">
      <span style={{ color: statusColor }}>{statusText}</span>
    </div>
  );
}

async function ReviewSection({ productId }: { productId: string }) {
  const reviews = await fetchReviews(productId);

  return (
    <section aria-label="상품 리뷰">
      <h2>리뷰 ({reviews.length})</h2>
      <ul role="list">
        {reviews.map((review) => (
          <li key={review.id}>
            <div>
              <strong>{review.author}</strong>
              <span aria-label={`평점 ${review.rating}점`}>
                {'⭐'.repeat(review.rating)}
              </span>
            </div>
            <p>{review.content}</p>
            <time dateTime={review.createdAt}>
              {new Date(review.createdAt).toLocaleDateString('ko-KR')}
            </time>
          </li>
        ))}
      </ul>
      {/* 리뷰 작성 폼 (클라이언트 컴포넌트) */}
      {/* <ReviewForm productId={productId} /> */}
    </section>
  );
}

async function RelatedProducts({ productId }: { productId: string }) {
  const products = await fetchRelatedProducts(productId);

  if (products.length === 0) return null;

  return (
    <section aria-label="관련 상품">
      <h2>관련 상품</h2>
      <div className="product-grid">
        {products.map((product) => (
          <a key={product.id} href={`/products/${product.id}`}>
            <img src={product.images[0]} alt={product.name} />
            <h3>{product.name}</h3>
            <p>{product.price.toLocaleString()}원</p>
          </a>
        ))}
      </div>
    </section>
  );
}

// --- 클라이언트 컴포넌트: 장바구니 추가 폼 ---
// 'use client';

function AddToCartForm({ product }: { product: Product }) {
  const [selectedColor, setSelectedColor] = useState('');
  const [selectedSize, setSelectedSize] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [isPending, startTransition] = useTransition();

  const handleAddToCart = () => {
    startTransition(async () => {
      // Server Action 호출
      // await addToCart({
      //   productId: product.id,
      //   color: selectedColor,
      //   size: selectedSize,
      //   quantity,
      // });
      console.log('장바구니 추가:', {
        productId: product.id,
        color: selectedColor,
        size: selectedSize,
        quantity,
      });
    });
  };

  return (
    <div>
      {/* 색상 선택 */}
      <fieldset>
        <legend>색상 선택</legend>
        {product.variants.colors.map((color) => (
          <label key={color.value}>
            <input
              type="radio"
              name="color"
              value={color.value}
              checked={selectedColor === color.value}
              onChange={() => setSelectedColor(color.value)}
              disabled={!color.available}
            />
            {color.name}
            {!color.available && ' (품절)'}
          </label>
        ))}
      </fieldset>

      {/* 사이즈 선택 */}
      <fieldset>
        <legend>사이즈 선택</legend>
        {product.variants.sizes.map((size) => (
          <label key={size.name}>
            <input
              type="radio"
              name="size"
              value={size.name}
              checked={selectedSize === size.name}
              onChange={() => setSelectedSize(size.name)}
              disabled={!size.available}
            />
            {size.name}
            {!size.available && ' (품절)'}
          </label>
        ))}
      </fieldset>

      {/* 수량 선택 */}
      <div>
        <label htmlFor="quantity">수량</label>
        <button
          onClick={() => setQuantity((q) => Math.max(1, q - 1))}
          aria-label="수량 감소"
          disabled={quantity <= 1}
        >
          -
        </button>
        <input
          id="quantity"
          type="number"
          min={1}
          max={product.stock}
          value={quantity}
          onChange={(e) => setQuantity(Number(e.target.value))}
          aria-label="수량"
        />
        <button
          onClick={() => setQuantity((q) => Math.min(product.stock, q + 1))}
          aria-label="수량 증가"
          disabled={quantity >= product.stock}
        >
          +
        </button>
      </div>

      {/* 장바구니 추가 버튼 */}
      <button
        onClick={handleAddToCart}
        disabled={
          isPending || !selectedColor || !selectedSize || product.stock === 0
        }
      >
        {isPending
          ? '추가 중...'
          : product.stock === 0
            ? '품절'
            : '장바구니에 추가'}
      </button>
    </div>
  );
}

// --- 스켈레톤 UI ---

function ReviewsSkeleton() {
  return (
    <div role="status" aria-label="리뷰 로딩 중">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="skeleton-review" />
      ))}
    </div>
  );
}

function RelatedProductsSkeleton() {
  return (
    <div role="status" aria-label="관련 상품 로딩 중">
      <h2>관련 상품</h2>
      <div className="product-grid">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skeleton-product-card" />
        ))}
      </div>
    </div>
  );
}

// ============================================================
// 문제 2 답안: Server Actions 기반 게시글 편집
// ============================================================

// --- Server Action ---
// app/blog/[slug]/edit/actions.ts
// 'use server';

interface EditPostState {
  title: string;
  content: string;
  success: boolean;
  error?: string;
  lastSaved?: string;
}

async function updatePost(
  prevState: EditPostState,
  formData: FormData
): Promise<EditPostState> {
  // 'use server';

  const title = formData.get('title') as string;
  const content = formData.get('content') as string;
  const slug = formData.get('slug') as string;

  // 유효성 검사
  if (!title || title.length < 2) {
    return { ...prevState, success: false, error: '제목은 2자 이상이어야 합니다.' };
  }
  if (!content || content.length < 10) {
    return { ...prevState, success: false, error: '내용은 10자 이상이어야 합니다.' };
  }

  try {
    // await db.post.update({
    //   where: { slug },
    //   data: { title, content, updatedAt: new Date() },
    // });
    // revalidateTag(`post-${slug}`);

    console.log('게시글 수정:', { slug, title, content });

    return {
      title,
      content,
      success: true,
      lastSaved: new Date().toISOString(),
    };
  } catch {
    return { ...prevState, success: false, error: '저장에 실패했습니다.' };
  }
}

async function autoSavePost(slug: string, content: string): Promise<void> {
  // 'use server';
  // await db.post.update({
  //   where: { slug },
  //   data: { content, updatedAt: new Date() },
  // });
  console.log('자동 저장:', { slug, content: content.substring(0, 50) + '...' });
}

// --- 편집 페이지 (서버 컴포넌트) ---
// app/blog/[slug]/edit/page.tsx

interface PostData {
  slug: string;
  title: string;
  content: string;
}

async function fetchPostForEdit(slug: string): Promise<PostData> {
  // const post = await db.post.findUnique({ where: { slug } });
  return {
    slug,
    title: '예시 게시글 제목',
    content: '예시 게시글 내용입니다. 이것은 편집 가능한 콘텐츠입니다.',
  };
}

export async function EditPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await fetchPostForEdit(slug);

  return (
    <main>
      <h1>게시글 편집</h1>
      {/* 클라이언트 컴포넌트에 서버 데이터를 props로 전달 */}
      <EditPostForm post={post} />
    </main>
  );
}

// --- 편집 폼 (클라이언트 컴포넌트) ---
// 'use client';

function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function EditPostForm({ post }: { post: PostData }) {
  // Server Action 상태 관리
  const [state, formAction, isPending] = useActionState(updatePost, {
    title: post.title,
    content: post.content,
    success: false,
  });

  // 낙관적 제목 (미리보기용)
  const [optimisticTitle, setOptimisticTitle] = useOptimistic(state.title);

  // 자동 저장 상태
  const [autoSaveStatus, setAutoSaveStatus] = useState<string>('');
  const [, startAutoSaveTransition] = useTransition();

  // 자동 저장 (디바운스 3초)
  const debouncedAutoSave = useCallback(
    debounce((content: string) => {
      startAutoSaveTransition(async () => {
        setAutoSaveStatus('자동 저장 중...');
        await autoSavePost(post.slug, content);
        setAutoSaveStatus(
          `자동 저장됨: ${new Date().toLocaleTimeString('ko-KR')}`
        );
      });
    }, 3000),
    [post.slug]
  );

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    debouncedAutoSave(e.target.value);
  };

  return (
    <div className="edit-layout">
      {/* 편집 폼 */}
      <form action={formAction} aria-label="게시글 편집">
        <input type="hidden" name="slug" value={post.slug} />

        {state.error && (
          <div role="alert">{state.error}</div>
        )}

        {state.success && (
          <div role="status">
            저장 완료! ({new Date(state.lastSaved!).toLocaleTimeString('ko-KR')})
          </div>
        )}

        <div>
          <label htmlFor="edit-title">제목</label>
          <input
            id="edit-title"
            name="title"
            type="text"
            defaultValue={post.title}
            required
            minLength={2}
            disabled={isPending}
            onChange={(e) => setOptimisticTitle(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="edit-content">내용</label>
          <textarea
            id="edit-content"
            name="content"
            defaultValue={post.content}
            required
            minLength={10}
            rows={20}
            disabled={isPending}
            onChange={handleContentChange}
          />
          {autoSaveStatus && (
            <span className="auto-save-status" aria-live="polite">
              {autoSaveStatus}
            </span>
          )}
        </div>

        <button type="submit" disabled={isPending}>
          {isPending ? '저장 중...' : '저장'}
        </button>
      </form>

      {/* 미리보기 (낙관적 제목 반영) */}
      <aside aria-label="미리보기">
        <h2>미리보기</h2>
        <article>
          <h3>{optimisticTitle}</h3>
          <div>{/* 마크다운 렌더링 영역 */}</div>
        </article>
      </aside>
    </div>
  );
}

// ============================================================
// 문제 3 답안: 스트리밍 SSR 대시보드
// ============================================================

// --- 데이터 페칭 함수들 (서버 전용) ---

interface UserProfile {
  name: string;
  avatar: string;
  role: string;
}

interface Notification {
  id: number;
  message: string;
  read: boolean;
  createdAt: string;
}

interface Activity {
  id: number;
  type: string;
  description: string;
  timestamp: string;
}

interface Recommendation {
  id: number;
  title: string;
  category: string;
  score: number;
}

async function fetchUserProfile(): Promise<UserProfile> {
  // ~100ms
  const res = await fetch(`${process.env.API_URL}/api/me`, {
    next: { revalidate: 300, tags: ['user-profile'] }, // 5분
  });
  if (!res.ok) throw new Error('프로필을 불러올 수 없습니다.');
  return res.json();
}

async function fetchNotifications(): Promise<Notification[]> {
  // ~500ms
  const res = await fetch(`${process.env.API_URL}/api/notifications`, {
    next: { revalidate: 30, tags: ['notifications'] }, // 30초
  });
  if (!res.ok) throw new Error('알림을 불러올 수 없습니다.');
  return res.json();
}

async function fetchActivityFeed(): Promise<Activity[]> {
  // ~1500ms
  const res = await fetch(`${process.env.API_URL}/api/activity`, {
    next: { revalidate: 60, tags: ['activity'] }, // 1분
  });
  if (!res.ok) throw new Error('활동 피드를 불러올 수 없습니다.');
  return res.json();
}

async function fetchRecommendations(): Promise<Recommendation[]> {
  // ~3000ms
  const res = await fetch(`${process.env.API_URL}/api/recommendations`, {
    next: { revalidate: 600, tags: ['recommendations'] }, // 10분
  });
  if (!res.ok) throw new Error('추천을 불러올 수 없습니다.');
  return res.json();
}

// --- 대시보드 페이지 (서버 컴포넌트) ---
// app/dashboard/page.tsx

export async function DashboardPage() {
  // 프로필은 빠르므로 await으로 즉시 가져옴
  const profile = await fetchUserProfile();

  return (
    <main>
      <h1>대시보드</h1>

      {/* 1. 프로필: 즉시 표시 (~100ms) */}
      <UserProfileSection profile={profile} />

      {/* 2. 알림: 별도 Suspense (~500ms) */}
      <ErrorBoundaryWrapper fallbackMessage="알림을 불러올 수 없습니다.">
        <Suspense fallback={<NotificationsSkeleton />}>
          <NotificationsSection />
        </Suspense>
      </ErrorBoundaryWrapper>

      {/* 3. 활동 피드: 별도 Suspense (~1500ms) */}
      <ErrorBoundaryWrapper fallbackMessage="활동 피드를 불러올 수 없습니다.">
        <Suspense fallback={<ActivityFeedSkeleton />}>
          <ActivityFeedSection />
        </Suspense>
      </ErrorBoundaryWrapper>

      {/* 4. 추천: 별도 Suspense (~3000ms) */}
      <ErrorBoundaryWrapper fallbackMessage="추천을 불러올 수 없습니다.">
        <Suspense fallback={<RecommendationsSkeleton />}>
          <RecommendationsSection />
        </Suspense>
      </ErrorBoundaryWrapper>
    </main>
  );
}

// --- 비동기 서버 컴포넌트 (각 섹션) ---

function UserProfileSection({ profile }: { profile: UserProfile }) {
  return (
    <section aria-label="사용자 프로필">
      <img src={profile.avatar} alt={profile.name} />
      <h2>{profile.name}</h2>
      <span>{profile.role}</span>
    </section>
  );
}

async function NotificationsSection() {
  const notifications = await fetchNotifications();
  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <section aria-label="알림">
      <h2>알림 ({unreadCount}개 안 읽음)</h2>
      <ul role="list">
        {notifications.map((notification) => (
          <li
            key={notification.id}
            aria-label={notification.read ? '읽음' : '안 읽음'}
          >
            <p>{notification.message}</p>
            <time dateTime={notification.createdAt}>
              {new Date(notification.createdAt).toLocaleDateString('ko-KR')}
            </time>
          </li>
        ))}
      </ul>
    </section>
  );
}

async function ActivityFeedSection() {
  const activities = await fetchActivityFeed();

  return (
    <section aria-label="활동 피드">
      <h2>최근 활동</h2>
      <ul role="list">
        {activities.map((activity) => (
          <li key={activity.id}>
            <span className={`badge-${activity.type}`}>{activity.type}</span>
            <p>{activity.description}</p>
            <time dateTime={activity.timestamp}>
              {new Date(activity.timestamp).toLocaleString('ko-KR')}
            </time>
          </li>
        ))}
      </ul>
    </section>
  );
}

async function RecommendationsSection() {
  const recommendations = await fetchRecommendations();

  return (
    <section aria-label="추천 콘텐츠">
      <h2>추천 콘텐츠</h2>
      <div className="recommendation-grid">
        {recommendations.map((item) => (
          <article key={item.id}>
            <span>{item.category}</span>
            <h3>{item.title}</h3>
            <div
              role="meter"
              aria-label="관련도"
              aria-valuenow={item.score}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              {item.score}%
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

// --- ErrorBoundary 래퍼 (클라이언트 컴포넌트) ---
// 'use client';

/**
 * 실제 Next.js에서는 error.tsx를 사용하거나
 * react-error-boundary 라이브러리를 사용합니다.
 * 여기서는 개념을 보여주기 위한 의사 코드입니다.
 */
function ErrorBoundaryWrapper({
  children,
  fallbackMessage,
}: {
  children: React.ReactNode;
  fallbackMessage: string;
}) {
  // 실제 구현에서는 React Error Boundary 클래스 컴포넌트 또는
  // react-error-boundary의 ErrorBoundary를 사용합니다.
  // Next.js App Router에서는 error.tsx 파일을 사용할 수 있습니다.
  return <>{children}</>;

  // 에러 발생 시 표시되는 UI:
  // <div role="alert">
  //   <p>{fallbackMessage}</p>
  //   <button onClick={reset}>다시 시도</button>
  // </div>
}

// --- 스켈레톤 UI ---

function NotificationsSkeleton() {
  return (
    <section role="status" aria-label="알림 로딩 중">
      <h2>알림</h2>
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="skeleton-notification">
          <div className="skeleton-line" style={{ width: '80%' }} />
          <div className="skeleton-line" style={{ width: '40%' }} />
        </div>
      ))}
    </section>
  );
}

function ActivityFeedSkeleton() {
  return (
    <section role="status" aria-label="활동 피드 로딩 중">
      <h2>최근 활동</h2>
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="skeleton-activity">
          <div className="skeleton-badge" />
          <div className="skeleton-line" style={{ width: '60%' }} />
        </div>
      ))}
    </section>
  );
}

function RecommendationsSkeleton() {
  return (
    <section role="status" aria-label="추천 콘텐츠 로딩 중">
      <h2>추천 콘텐츠</h2>
      <div className="recommendation-grid">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skeleton-card" />
        ))}
      </div>
    </section>
  );
}

// 기본 내보내기 (학습용)
export default DashboardPage;
