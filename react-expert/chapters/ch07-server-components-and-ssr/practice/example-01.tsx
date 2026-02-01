/**
 * 챕터 07 - 예제 01: Next.js App Router 기반 블로그 - 서버 컴포넌트
 *
 * 이 예제는 Next.js App Router에서 서버 컴포넌트를 활용한
 * 블로그 애플리케이션의 핵심 구조를 보여줍니다.
 *
 * 실행 방법:
 *   1. Next.js 프로젝트 생성:
 *      npx create-next-app@latest blog-demo --typescript --app --tailwind
 *      cd blog-demo
 *
 *   2. 아래 파일들을 해당 경로에 배치:
 *      - app/layout.tsx
 *      - app/blog/page.tsx
 *      - app/blog/[slug]/page.tsx
 *      - app/blog/loading.tsx
 *      - app/blog/error.tsx
 *      - lib/api.ts
 *
 *   3. 개발 서버 실행:
 *      npm run dev
 *      http://localhost:3000/blog 에서 확인
 *
 * 참고: 이 파일은 여러 Next.js 파일의 코드를 하나로 합친 학습용 예제입니다.
 *       실제 프로젝트에서는 각 파일을 분리하여 사용합니다.
 */

import React, { Suspense } from 'react';

// ============================================================
// 1. 타입 정의 (lib/types.ts)
// ============================================================

/** 블로그 게시글 타입 */
interface Post {
  id: number;
  slug: string;
  title: string;
  content: string;
  excerpt: string;
  author: {
    name: string;
    avatar: string;
  };
  publishedAt: string;
  tags: string[];
  readingTime: number;
}

/** 게시글 목록 응답 */
interface PostListResponse {
  posts: Post[];
  total: number;
  page: number;
  hasMore: boolean;
}

/** 페이지 파라미터 */
interface PageParams {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ page?: string; tag?: string }>;
}

// ============================================================
// 2. 데이터 페칭 함수 (lib/api.ts)
// ============================================================

/**
 * 게시글 목록 조회
 * - 서버 컴포넌트에서 직접 호출합니다.
 * - fetch의 캐싱 옵션으로 ISR(Incremental Static Regeneration)을 구현합니다.
 */
async function fetchPosts(
  page: number = 1,
  tag?: string
): Promise<PostListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    limit: '10',
    ...(tag && { tag }),
  });

  const response = await fetch(
    `${process.env.API_URL}/api/posts?${params}`,
    {
      // 60초마다 재검증 (ISR)
      next: { revalidate: 60, tags: ['posts'] },
    }
  );

  if (!response.ok) {
    throw new Error('게시글 목록을 불러오지 못했습니다.');
  }

  return response.json();
}

/**
 * 개별 게시글 조회
 * - 동적 라우트에서 사용합니다.
 * - 태그 기반 재검증을 활용합니다.
 */
async function fetchPost(slug: string): Promise<Post> {
  const response = await fetch(
    `${process.env.API_URL}/api/posts/${slug}`,
    {
      next: { tags: [`post-${slug}`] },
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      // Next.js의 notFound() 함수를 호출하여 404 페이지 표시
      throw new Error('POST_NOT_FOUND');
    }
    throw new Error('게시글을 불러오지 못했습니다.');
  }

  return response.json();
}

/**
 * 관련 게시글 조회 (느린 API를 시뮬레이션)
 * - Suspense와 함께 사용하여 스트리밍 SSR을 보여줍니다.
 */
async function fetchRelatedPosts(slug: string): Promise<Post[]> {
  // 의도적으로 느린 요청 (스트리밍 데모용)
  const response = await fetch(
    `${process.env.API_URL}/api/posts/${slug}/related`,
    {
      next: { revalidate: 300 },
    }
  );

  if (!response.ok) return [];
  return response.json();
}

// ============================================================
// 3. 루트 레이아웃 (app/layout.tsx) - 서버 컴포넌트
// ============================================================

/**
 * 루트 레이아웃
 * - 서버 컴포넌트 (기본값)로 실행됩니다.
 * - 모든 페이지에 공통으로 적용됩니다.
 * - 메타데이터를 정적으로 정의합니다.
 */
// export const metadata = {
//   title: { template: '%s | 기술 블로그', default: '기술 블로그' },
//   description: 'React, TypeScript, Next.js 관련 기술 블로그',
// };

export function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        {/* 네비게이션 - 서버에서 렌더링 (JS 번들 없음) */}
        <header>
          <nav aria-label="주요 메뉴">
            <a href="/">홈</a>
            <a href="/blog">블로그</a>
            <a href="/about">소개</a>
          </nav>
          {/*
            ThemeToggle은 상호작용이 필요하므로 클라이언트 컴포넌트
            서버 컴포넌트인 레이아웃의 children으로 포함 가능
          */}
          {/* <ThemeToggle /> */}
        </header>

        <main>{children}</main>

        <footer>
          <p>&copy; 2024 기술 블로그</p>
        </footer>
      </body>
    </html>
  );
}

// ============================================================
// 4. 블로그 목록 페이지 (app/blog/page.tsx) - 서버 컴포넌트
// ============================================================

/**
 * 블로그 목록 페이지
 *
 * 핵심 포인트:
 * - async 컴포넌트로 서버에서 직접 데이터를 페칭합니다.
 * - searchParams로 페이지네이션과 필터를 처리합니다.
 * - Suspense로 로딩 상태를 세분화합니다.
 */
export async function BlogPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; tag?: string }>;
}) {
  const resolvedParams = await searchParams;
  const currentPage = Number(resolvedParams.page) || 1;
  const tag = resolvedParams.tag;

  // 서버에서 데이터 페칭 (클라이언트에 JS 전송 없음)
  const { posts, total, hasMore } = await fetchPosts(currentPage, tag);

  return (
    <section>
      <h1>블로그</h1>
      <p>총 {total}개의 게시글</p>

      {/* 태그 필터 - 서버에서 렌더링 */}
      <TagFilter activeTag={tag} />

      {/* 게시글 목록 */}
      <div role="list" aria-label="게시글 목록">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {/* 페이지네이션 */}
      <Pagination
        currentPage={currentPage}
        hasMore={hasMore}
        tag={tag}
      />
    </section>
  );
}

// ============================================================
// 5. 게시글 상세 페이지 (app/blog/[slug]/page.tsx)
// ============================================================

/**
 * 게시글 상세 페이지
 *
 * 핵심 포인트:
 * - generateMetadata로 동적 메타데이터를 생성합니다.
 * - 중첩 Suspense로 콘텐츠를 점진적으로 로딩합니다.
 * - 관련 게시글은 별도 Suspense boundary에서 스트리밍됩니다.
 */

// 동적 메타데이터 생성
export async function generateMetadata({ params }: PageParams) {
  const { slug } = await params;
  const post = await fetchPost(slug);
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.publishedAt,
      authors: [post.author.name],
      tags: post.tags,
    },
  };
}

// 정적 경로 생성 (빌드 타임에 미리 생성)
export async function generateStaticParams() {
  const { posts } = await fetchPosts(1);
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export async function PostDetailPage({ params }: PageParams) {
  const { slug } = await params;
  const post = await fetchPost(slug);

  return (
    <article>
      {/* 헤더 - 즉시 렌더링 */}
      <header>
        <h1>{post.title}</h1>
        <div>
          <img src={post.author.avatar} alt={post.author.name} />
          <span>{post.author.name}</span>
          <time dateTime={post.publishedAt}>
            {new Date(post.publishedAt).toLocaleDateString('ko-KR')}
          </time>
          <span>{post.readingTime}분 소요</span>
        </div>
        <div>
          {post.tags.map((tag) => (
            <a key={tag} href={`/blog?tag=${tag}`}>
              #{tag}
            </a>
          ))}
        </div>
      </header>

      {/* 본문 - 서버에서 렌더링 */}
      <div dangerouslySetInnerHTML={{ __html: post.content }} />

      {/* 좋아요/공유 버튼 - 클라이언트 컴포넌트 (경계) */}
      {/* <InteractionBar postId={post.id} /> */}

      {/* 관련 게시글 - 별도 Suspense로 스트리밍 */}
      <Suspense fallback={<RelatedPostsSkeleton />}>
        <RelatedPosts slug={slug} />
      </Suspense>

      {/* 댓글 섹션 - 클라이언트 컴포넌트 (경계) */}
      {/* <CommentSection postId={post.id} /> */}
    </article>
  );
}

// ============================================================
// 6. 스트리밍 SSR을 위한 비동기 컴포넌트
// ============================================================

/**
 * 관련 게시글 (비동기 서버 컴포넌트)
 * - 느린 API를 호출하므로 별도 Suspense boundary에 배치합니다.
 * - 메인 콘텐츠가 먼저 표시되고, 이 컴포넌트는 나중에 스트리밍됩니다.
 */
async function RelatedPosts({ slug }: { slug: string }) {
  const relatedPosts = await fetchRelatedPosts(slug);

  if (relatedPosts.length === 0) {
    return null;
  }

  return (
    <section aria-label="관련 게시글">
      <h2>관련 게시글</h2>
      <div>
        {relatedPosts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </section>
  );
}

// ============================================================
// 7. 서버 컴포넌트로 구현한 하위 컴포넌트
// ============================================================

/** 게시글 카드 - 서버 컴포넌트 (상호작용 없음) */
function PostCard({ post }: { post: Post }) {
  return (
    <div role="listitem">
      <a href={`/blog/${post.slug}`}>
        <h3>{post.title}</h3>
        <p>{post.excerpt}</p>
        <div>
          <span>{post.author.name}</span>
          <time dateTime={post.publishedAt}>
            {new Date(post.publishedAt).toLocaleDateString('ko-KR')}
          </time>
          <span>{post.readingTime}분 소요</span>
        </div>
        <div>
          {post.tags.map((tag) => (
            <span key={tag}>#{tag}</span>
          ))}
        </div>
      </a>
    </div>
  );
}

/** 태그 필터 - 서버 컴포넌트 */
function TagFilter({ activeTag }: { activeTag?: string }) {
  const tags = ['React', 'TypeScript', 'Next.js', 'Node.js', 'CSS'];

  return (
    <nav aria-label="태그 필터">
      <a
        href="/blog"
        aria-current={!activeTag ? 'page' : undefined}
      >
        전체
      </a>
      {tags.map((tag) => (
        <a
          key={tag}
          href={`/blog?tag=${tag}`}
          aria-current={activeTag === tag ? 'page' : undefined}
        >
          {tag}
        </a>
      ))}
    </nav>
  );
}

/** 페이지네이션 - 서버 컴포넌트 */
function Pagination({
  currentPage,
  hasMore,
  tag,
}: {
  currentPage: number;
  hasMore: boolean;
  tag?: string;
}) {
  const baseUrl = tag ? `/blog?tag=${tag}&` : '/blog?';

  return (
    <nav aria-label="페이지 이동">
      {currentPage > 1 && (
        <a href={`${baseUrl}page=${currentPage - 1}`}>이전</a>
      )}
      <span aria-current="page">{currentPage} 페이지</span>
      {hasMore && (
        <a href={`${baseUrl}page=${currentPage + 1}`}>다음</a>
      )}
    </nav>
  );
}

// ============================================================
// 8. 스켈레톤 UI (로딩 폴백)
// ============================================================

/** 게시글 목록 스켈레톤 */
function PostListSkeleton() {
  return (
    <div role="status" aria-label="게시글 목록 로딩 중">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="skeleton-card">
          <div className="skeleton-title" />
          <div className="skeleton-text" />
          <div className="skeleton-text" />
          <div className="skeleton-meta" />
        </div>
      ))}
    </div>
  );
}

/** 관련 게시글 스켈레톤 */
function RelatedPostsSkeleton() {
  return (
    <div role="status" aria-label="관련 게시글 로딩 중">
      <h2>관련 게시글</h2>
      <div>
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="skeleton-card-small" />
        ))}
      </div>
    </div>
  );
}

// ============================================================
// 9. 로딩/에러 파일 (app/blog/loading.tsx, app/blog/error.tsx)
// ============================================================

/**
 * loading.tsx - 자동 Suspense boundary
 * Next.js가 이 파일을 감지하여 자동으로 Suspense를 설정합니다.
 */
export function Loading() {
  return <PostListSkeleton />;
}

/**
 * error.tsx - 자동 Error Boundary
 * 반드시 'use client'로 선언해야 합니다.
 * (실제 파일에서는 상단에 'use client' 지시어를 추가합니다)
 */
export function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div role="alert">
      <h2>오류가 발생했습니다</h2>
      <p>{error.message}</p>
      <button onClick={reset}>다시 시도</button>
    </div>
  );
}

// 기본 내보내기 (학습용)
export default BlogPage;
