/**
 * 챕터 07 - 예제 02: 클라이언트 컴포넌트와 Server Actions
 *
 * 이 예제는 다음을 다룹니다:
 *   1. 'use client' 경계 설정과 클라이언트 컴포넌트
 *   2. Server Actions를 활용한 폼 처리와 데이터 뮤테이션
 *   3. Optimistic UI 패턴
 *   4. 서버/클라이언트 컴포넌트 Composition 패턴
 *
 * 실행 방법:
 *   1. Next.js 프로젝트에서 실행 (example-01의 blog-demo 사용):
 *      cd blog-demo
 *
 *   2. 아래 파일들을 해당 경로에 배치:
 *      - app/blog/[slug]/actions.ts (Server Actions)
 *      - app/blog/[slug]/InteractionBar.tsx
 *      - app/blog/[slug]/CommentSection.tsx
 *      - app/blog/new/page.tsx
 *
 *   3. 개발 서버 실행:
 *      npm run dev
 *
 * 참고: 이 파일은 여러 Next.js 파일의 코드를 하나로 합친 학습용 예제입니다.
 */

import React, {
  useState,
  useOptimistic,
  useTransition,
  useRef,
  useActionState,
} from 'react';

// ============================================================
// 1. Server Actions 정의 (app/blog/[slug]/actions.ts)
// ============================================================

/**
 * 실제 파일에서는 최상단에 'use server' 지시어를 추가합니다.
 *
 * Server Actions 핵심 원칙:
 * - 항상 서버에서만 실행됩니다.
 * - FormData 또는 일반 인자를 받을 수 있습니다.
 * - revalidatePath/revalidateTag로 캐시를 무효화합니다.
 * - redirect()로 페이지를 전환합니다.
 */

// 'use server';

// import { revalidatePath, revalidateTag } from 'next/cache';
// import { redirect } from 'next/navigation';

interface Comment {
  id: number;
  postId: number;
  author: string;
  content: string;
  createdAt: string;
}

interface ActionResult {
  success: boolean;
  error?: string;
}

/** 게시글 작성 Server Action */
async function createPost(
  _prevState: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  // 'use server';

  // 유효성 검사
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;
  const tags = formData.get('tags') as string;

  if (!title || title.length < 2) {
    return { success: false, error: '제목은 2자 이상이어야 합니다.' };
  }

  if (!content || content.length < 10) {
    return { success: false, error: '내용은 10자 이상이어야 합니다.' };
  }

  try {
    // DB에 게시글 저장
    // await db.post.create({
    //   data: {
    //     title,
    //     content,
    //     tags: tags.split(',').map(t => t.trim()),
    //     slug: generateSlug(title),
    //     authorId: getCurrentUser().id,
    //   },
    // });

    // 캐시 무효화
    // revalidateTag('posts');

    console.log('게시글 생성:', { title, content, tags });
    return { success: true };
  } catch {
    return { success: false, error: '게시글 작성에 실패했습니다.' };
  }

  // 성공 시 리다이렉트
  // redirect('/blog');
}

/** 좋아요 토글 Server Action */
async function toggleLike(postId: number): Promise<{ liked: boolean; count: number }> {
  // 'use server';

  // const user = await getCurrentUser();
  // const existing = await db.like.findUnique({
  //   where: { postId_userId: { postId, userId: user.id } },
  // });
  //
  // if (existing) {
  //   await db.like.delete({ where: { id: existing.id } });
  // } else {
  //   await db.like.create({ data: { postId, userId: user.id } });
  // }
  //
  // const count = await db.like.count({ where: { postId } });
  // revalidateTag(`post-${postId}`);

  console.log('좋아요 토글:', postId);
  return { liked: true, count: 42 };
}

/** 댓글 작성 Server Action */
async function createComment(
  postId: number,
  formData: FormData
): Promise<Comment> {
  // 'use server';

  const content = formData.get('content') as string;

  if (!content?.trim()) {
    throw new Error('댓글 내용을 입력해주세요.');
  }

  // const user = await getCurrentUser();
  // const comment = await db.comment.create({
  //   data: { postId, content, authorId: user.id },
  //   include: { author: true },
  // });
  //
  // revalidateTag(`post-${postId}-comments`);

  const comment: Comment = {
    id: Date.now(),
    postId,
    author: '현재 사용자',
    content,
    createdAt: new Date().toISOString(),
  };

  return comment;
}

// ============================================================
// 2. 게시글 작성 폼 (app/blog/new/page.tsx) - useActionState
// ============================================================

/**
 * 게시글 작성 폼
 *
 * 핵심 포인트:
 * - useActionState(React 19)를 사용하여 Server Action의 상태를 관리합니다.
 * - 폼 제출 시 자동으로 pending 상태가 처리됩니다.
 * - 서버에서 반환된 에러 메시지를 표시합니다.
 */

// 'use client';

export function CreatePostForm() {
  // useActionState: Server Action의 반환값과 pending 상태를 관리
  const [state, formAction, isPending] = useActionState(createPost, null);

  return (
    <form action={formAction} aria-label="게시글 작성">
      <h2>새 게시글 작성</h2>

      {/* 서버 사이드 에러 메시지 */}
      {state?.error && (
        <div role="alert" aria-live="assertive">
          {state.error}
        </div>
      )}

      {/* 성공 메시지 */}
      {state?.success && (
        <div role="status" aria-live="polite">
          게시글이 성공적으로 작성되었습니다!
        </div>
      )}

      <div>
        <label htmlFor="post-title">제목</label>
        <input
          id="post-title"
          name="title"
          type="text"
          required
          minLength={2}
          aria-required="true"
          disabled={isPending}
        />
      </div>

      <div>
        <label htmlFor="post-content">내용</label>
        <textarea
          id="post-content"
          name="content"
          required
          minLength={10}
          rows={10}
          aria-required="true"
          disabled={isPending}
        />
      </div>

      <div>
        <label htmlFor="post-tags">태그 (쉼표로 구분)</label>
        <input
          id="post-tags"
          name="tags"
          type="text"
          placeholder="React, TypeScript, Next.js"
          disabled={isPending}
        />
      </div>

      <button type="submit" disabled={isPending}>
        {isPending ? '저장 중...' : '게시글 작성'}
      </button>
    </form>
  );
}

// ============================================================
// 3. 좋아요 버튼 - Optimistic UI (app/blog/[slug]/InteractionBar.tsx)
// ============================================================

/**
 * 상호작용 바 (좋아요, 공유)
 *
 * 핵심 포인트:
 * - useOptimistic(React 19)을 사용하여 낙관적 UI 업데이트를 구현합니다.
 * - 서버 응답 전에 UI를 먼저 업데이트하여 즉각적인 피드백을 제공합니다.
 * - 서버 요청이 실패하면 자동으로 이전 상태로 롤백됩니다.
 */

// 'use client';

interface InteractionBarProps {
  postId: number;
  initialLiked: boolean;
  initialLikeCount: number;
}

export function InteractionBar({
  postId,
  initialLiked,
  initialLikeCount,
}: InteractionBarProps) {
  // 실제 서버 상태
  const [liked, setLiked] = useState(initialLiked);
  const [likeCount, setLikeCount] = useState(initialLikeCount);

  // 낙관적 상태 (즉시 반영)
  const [optimisticLiked, setOptimisticLiked] = useOptimistic(liked);
  const [optimisticCount, setOptimisticCount] = useOptimistic(likeCount);

  const [isPending, startTransition] = useTransition();

  const handleLike = () => {
    // 낙관적 업데이트 (즉시)
    startTransition(async () => {
      setOptimisticLiked(!liked);
      setOptimisticCount(liked ? likeCount - 1 : likeCount + 1);

      try {
        // 서버에 요청
        const result = await toggleLike(postId);
        // 서버 응답으로 실제 상태 업데이트
        setLiked(result.liked);
        setLikeCount(result.count);
      } catch {
        // 에러 시 자동으로 optimistic 상태가 롤백됨
        console.error('좋아요 처리 실패');
      }
    });
  };

  const handleShare = async () => {
    try {
      await navigator.share({
        title: '게시글 공유',
        url: window.location.href,
      });
    } catch {
      // 공유 취소 또는 미지원
      await navigator.clipboard.writeText(window.location.href);
      alert('링크가 복사되었습니다.');
    }
  };

  return (
    <div role="group" aria-label="게시글 상호작용">
      <button
        onClick={handleLike}
        disabled={isPending}
        aria-pressed={optimisticLiked}
        aria-label={`좋아요 ${optimisticCount}개`}
      >
        {optimisticLiked ? '❤️' : '🤍'} {optimisticCount}
      </button>

      <button onClick={handleShare} aria-label="공유하기">
        📤 공유
      </button>
    </div>
  );
}

// ============================================================
// 4. 댓글 섹션 - Optimistic Updates (app/blog/[slug]/CommentSection.tsx)
// ============================================================

/**
 * 댓글 섹션
 *
 * 핵심 포인트:
 * - useOptimistic으로 새 댓글을 즉시 표시합니다.
 * - 서버 확인 전에 "전송 중..." 스타일로 임시 표시합니다.
 * - useRef로 폼 초기화를 처리합니다.
 */

// 'use client';

interface CommentSectionProps {
  postId: number;
  initialComments: Comment[];
}

export function CommentSection({
  postId,
  initialComments,
}: CommentSectionProps) {
  const [comments, setComments] = useState(initialComments);
  const formRef = useRef<HTMLFormElement>(null);

  // 낙관적 댓글 목록
  const [optimisticComments, addOptimisticComment] = useOptimistic(
    comments,
    (currentComments: Comment[], newComment: Comment) => [
      ...currentComments,
      newComment,
    ]
  );

  const handleSubmit = async (formData: FormData) => {
    const content = formData.get('content') as string;

    // 낙관적으로 즉시 추가
    const tempComment: Comment = {
      id: -Date.now(), // 임시 ID
      postId,
      author: '나',
      content,
      createdAt: new Date().toISOString(),
    };

    addOptimisticComment(tempComment);
    formRef.current?.reset();

    try {
      // 서버에 댓글 생성 요청
      const savedComment = await createComment(postId, formData);
      // 서버에서 확인된 댓글로 상태 업데이트
      setComments((prev) => [...prev, savedComment]);
    } catch (error) {
      // 에러 시 optimistic 상태가 롤백됨
      console.error('댓글 작성 실패:', error);
    }
  };

  return (
    <section aria-label="댓글">
      <h2>댓글 ({optimisticComments.length})</h2>

      {/* 댓글 목록 */}
      <ul role="list" aria-label="댓글 목록">
        {optimisticComments.map((comment) => (
          <li
            key={comment.id}
            style={{
              opacity: comment.id < 0 ? 0.6 : 1, // 임시 댓글은 반투명
            }}
          >
            <div>
              <strong>{comment.author}</strong>
              <time dateTime={comment.createdAt}>
                {new Date(comment.createdAt).toLocaleDateString('ko-KR')}
              </time>
              {comment.id < 0 && (
                <span aria-label="전송 중">전송 중...</span>
              )}
            </div>
            <p>{comment.content}</p>
          </li>
        ))}
      </ul>

      {/* 댓글 입력 폼 */}
      <form ref={formRef} action={handleSubmit} aria-label="댓글 작성">
        <label htmlFor="comment-content">댓글 입력</label>
        <textarea
          id="comment-content"
          name="content"
          required
          rows={3}
          placeholder="댓글을 입력하세요"
          aria-required="true"
        />
        <button type="submit">댓글 작성</button>
      </form>
    </section>
  );
}

// ============================================================
// 5. Composition 패턴: 서버 컴포넌트를 클라이언트의 children으로
// ============================================================

/**
 * Composition 패턴 예시
 *
 * 핵심: 클라이언트 컴포넌트가 서버 컴포넌트를 children으로 받으면,
 * 서버 컴포넌트는 서버에서 렌더링된 결과(HTML)만 전달됩니다.
 * 이렇게 하면 서버 컴포넌트의 데이터 페칭 이점을 유지할 수 있습니다.
 */

// --- 클라이언트 컴포넌트 (탭 UI) ---
// 'use client';

interface TabsProps {
  tabs: { label: string; content: React.ReactNode }[];
}

export function Tabs({ tabs }: TabsProps) {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <div>
      <div role="tablist">
        {tabs.map((tab, index) => (
          <button
            key={tab.label}
            role="tab"
            aria-selected={index === activeTab}
            onClick={() => setActiveTab(index)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div role="tabpanel">{tabs[activeTab].content}</div>
    </div>
  );
}

// --- 서버 컴포넌트에서 사용 ---
/**
 * 아래와 같이 서버 컴포넌트에서 Tabs(클라이언트)를 사용하되,
 * 각 탭의 content에 서버 컴포넌트를 넣을 수 있습니다.
 *
 * ```tsx
 * // app/dashboard/page.tsx (서버 컴포넌트)
 * import { Tabs } from './Tabs';
 * import { RecentPosts } from './RecentPosts';   // 서버 컴포넌트
 * import { PopularPosts } from './PopularPosts'; // 서버 컴포넌트
 *
 * export default function DashboardPage() {
 *   return (
 *     <Tabs
 *       tabs={[
 *         {
 *           label: '최신 게시글',
 *           content: <RecentPosts />,  // 서버에서 렌더링됨
 *         },
 *         {
 *           label: '인기 게시글',
 *           content: <PopularPosts />, // 서버에서 렌더링됨
 *         },
 *       ]}
 *     />
 *   );
 * }
 * ```
 *
 * RecentPosts와 PopularPosts는 서버에서 렌더링되어
 * 직렬화된 React 트리로 Tabs에 전달됩니다.
 * Tabs는 클라이언트에서 탭 전환만 처리합니다.
 */

// 기본 내보내기 (학습용)
export default CreatePostForm;
