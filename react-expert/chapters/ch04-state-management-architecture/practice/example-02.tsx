/**
 * 챕터 04 - 예제 2: 상태 정규화와 셀렉터 패턴
 *
 * 중첩된 API 응답 데이터를 정규화하고,
 * 셀렉터(selector)로 파생 데이터를 효율적으로 계산하는 방법을 보여줍니다.
 *
 * 실행 방법:
 *   npx tsx practice/example-02.tsx
 */

// ============================================================
// 1. 타입 정의
// ============================================================

/** API에서 받는 중첩된 응답 */
interface ApiPost {
  id: string;
  title: string;
  body: string;
  createdAt: string;
  author: {
    id: string;
    name: string;
    avatar: string;
  };
  comments: Array<{
    id: string;
    text: string;
    author: {
      id: string;
      name: string;
      avatar: string;
    };
    createdAt: string;
  }>;
  tags: string[];
}

/** 정규화된 엔티티 타입 */
interface NormalizedUser {
  id: string;
  name: string;
  avatar: string;
}

interface NormalizedComment {
  id: string;
  text: string;
  authorId: string;
  postId: string;
  createdAt: string;
}

interface NormalizedPost {
  id: string;
  title: string;
  body: string;
  authorId: string;
  commentIds: string[];
  tags: string[];
  createdAt: string;
}

/** 정규화된 상태 구조 */
interface NormalizedState {
  entities: {
    users: Record<string, NormalizedUser>;
    posts: Record<string, NormalizedPost>;
    comments: Record<string, NormalizedComment>;
  };
  ids: {
    posts: string[];
  };
}

// ============================================================
// 2. 정규화 함수
// ============================================================

/**
 * API 응답을 정규화하는 함수
 *
 * 중첩된 데이터를 평탄한 구조로 변환합니다.
 * 각 엔티티는 ID로 인덱싱된 객체에 저장됩니다.
 */
function normalizeApiResponse(posts: ApiPost[]): NormalizedState {
  const state: NormalizedState = {
    entities: {
      users: {},
      posts: {},
      comments: {},
    },
    ids: {
      posts: [],
    },
  };

  for (const post of posts) {
    // 사용자 정규화 (중복 자동 제거)
    state.entities.users[post.author.id] = {
      id: post.author.id,
      name: post.author.name,
      avatar: post.author.avatar,
    };

    // 댓글 정규화
    const commentIds: string[] = [];
    for (const comment of post.comments) {
      // 댓글 작성자
      state.entities.users[comment.author.id] = {
        id: comment.author.id,
        name: comment.author.name,
        avatar: comment.author.avatar,
      };

      // 댓글
      state.entities.comments[comment.id] = {
        id: comment.id,
        text: comment.text,
        authorId: comment.author.id,
        postId: post.id,
        createdAt: comment.createdAt,
      };

      commentIds.push(comment.id);
    }

    // 게시글 정규화
    state.entities.posts[post.id] = {
      id: post.id,
      title: post.title,
      body: post.body,
      authorId: post.author.id,
      commentIds,
      tags: post.tags,
      createdAt: post.createdAt,
    };

    state.ids.posts.push(post.id);
  }

  return state;
}

// ============================================================
// 3. 셀렉터(Selector) 패턴
// ============================================================

/**
 * 셀렉터: 정규화된 상태에서 파생 데이터를 계산하는 함수들
 *
 * 셀렉터의 장점:
 * 1. 데이터 접근 로직이 한 곳에 집중
 * 2. 컴포넌트에서 상태 구조에 대한 지식 불필요
 * 3. Memoization 적용 가능 (reselect, useMemo)
 */

// 기본 셀렉터
const selectAllPosts = (state: NormalizedState): NormalizedPost[] =>
  state.ids.posts.map((id) => state.entities.posts[id]);

const selectPostById = (state: NormalizedState, postId: string): NormalizedPost | undefined =>
  state.entities.posts[postId];

const selectUserById = (state: NormalizedState, userId: string): NormalizedUser | undefined =>
  state.entities.users[userId];

const selectCommentById = (state: NormalizedState, commentId: string): NormalizedComment | undefined =>
  state.entities.comments[commentId];

// 파생 셀렉터 (여러 엔티티를 조합)
interface PostWithAuthor extends NormalizedPost {
  author: NormalizedUser;
}

const selectPostWithAuthor = (
  state: NormalizedState,
  postId: string
): PostWithAuthor | undefined => {
  const post = selectPostById(state, postId);
  if (!post) return undefined;
  const author = selectUserById(state, post.authorId);
  if (!author) return undefined;
  return { ...post, author };
};

interface CommentWithAuthor extends NormalizedComment {
  author: NormalizedUser;
}

const selectCommentsForPost = (
  state: NormalizedState,
  postId: string
): CommentWithAuthor[] => {
  const post = selectPostById(state, postId);
  if (!post) return [];

  return post.commentIds
    .map((commentId) => {
      const comment = selectCommentById(state, commentId);
      if (!comment) return null;
      const author = selectUserById(state, comment.authorId);
      if (!author) return null;
      return { ...comment, author };
    })
    .filter((c): c is CommentWithAuthor => c !== null);
};

const selectPostsByTag = (
  state: NormalizedState,
  tag: string
): NormalizedPost[] =>
  selectAllPosts(state).filter((post) => post.tags.includes(tag));

const selectPostsByAuthor = (
  state: NormalizedState,
  authorId: string
): NormalizedPost[] =>
  selectAllPosts(state).filter((post) => post.authorId === authorId);

// 집계 셀렉터
const selectTotalCommentCount = (state: NormalizedState): number =>
  Object.keys(state.entities.comments).length;

const selectUniqueUserCount = (state: NormalizedState): number =>
  Object.keys(state.entities.users).length;

// ============================================================
// 4. 상태 업데이트 함수 (Reducer 패턴)
// ============================================================

type StateAction =
  | { type: "ADD_COMMENT"; postId: string; comment: { id: string; text: string; authorId: string; createdAt: string } }
  | { type: "UPDATE_POST"; postId: string; changes: Partial<NormalizedPost> }
  | { type: "DELETE_POST"; postId: string }
  | { type: "UPDATE_USER"; userId: string; changes: Partial<NormalizedUser> };

/**
 * 정규화된 상태의 업데이트는 한 곳만 변경하면 됩니다.
 * 이것이 정규화의 가장 큰 이점입니다.
 */
function stateReducer(
  state: NormalizedState,
  action: StateAction
): NormalizedState {
  switch (action.type) {
    case "ADD_COMMENT": {
      const { postId, comment } = action;
      return {
        ...state,
        entities: {
          ...state.entities,
          comments: {
            ...state.entities.comments,
            [comment.id]: { ...comment, postId },
          },
          posts: {
            ...state.entities.posts,
            [postId]: {
              ...state.entities.posts[postId],
              commentIds: [
                ...state.entities.posts[postId].commentIds,
                comment.id,
              ],
            },
          },
        },
      };
    }

    case "UPDATE_POST": {
      const { postId, changes } = action;
      return {
        ...state,
        entities: {
          ...state.entities,
          posts: {
            ...state.entities.posts,
            [postId]: { ...state.entities.posts[postId], ...changes },
          },
        },
      };
    }

    case "DELETE_POST": {
      const { postId } = action;
      const post = state.entities.posts[postId];
      const { [postId]: _, ...remainingPosts } = state.entities.posts;

      // 관련 댓글도 삭제
      const remainingComments = { ...state.entities.comments };
      post.commentIds.forEach((commentId) => {
        delete remainingComments[commentId];
      });

      return {
        entities: {
          ...state.entities,
          posts: remainingPosts,
          comments: remainingComments,
        },
        ids: {
          posts: state.ids.posts.filter((id) => id !== postId),
        },
      };
    }

    case "UPDATE_USER": {
      const { userId, changes } = action;
      return {
        ...state,
        entities: {
          ...state.entities,
          users: {
            ...state.entities.users,
            [userId]: { ...state.entities.users[userId], ...changes },
          },
        },
      };
    }
  }
}

// ============================================================
// 5. 데모 실행
// ============================================================

console.log("╔══════════════════════════════════════════════════════════╗");
console.log("║ 상태 정규화와 셀렉터 패턴                                ║");
console.log("╚══════════════════════════════════════════════════════════╝\n");

// API 응답 시뮬레이션
const apiResponse: ApiPost[] = [
  {
    id: "p1",
    title: "React 19의 새로운 기능",
    body: "React 19에서는...",
    createdAt: "2025-01-15",
    author: { id: "u1", name: "김개발", avatar: "/avatars/kim.jpg" },
    comments: [
      {
        id: "c1",
        text: "좋은 글이네요!",
        author: { id: "u2", name: "이프론트", avatar: "/avatars/lee.jpg" },
        createdAt: "2025-01-16",
      },
      {
        id: "c2",
        text: "React Compiler가 기대됩니다",
        author: { id: "u3", name: "박풀스택", avatar: "/avatars/park.jpg" },
        createdAt: "2025-01-16",
      },
    ],
    tags: ["react", "frontend"],
  },
  {
    id: "p2",
    title: "TypeScript 5.x 가이드",
    body: "TypeScript 5에서는...",
    createdAt: "2025-01-20",
    author: { id: "u2", name: "이프론트", avatar: "/avatars/lee.jpg" }, // 같은 사용자!
    comments: [
      {
        id: "c3",
        text: "const 타입 파라미터가 유용하네요",
        author: { id: "u1", name: "김개발", avatar: "/avatars/kim.jpg" }, // 같은 사용자!
        createdAt: "2025-01-21",
      },
    ],
    tags: ["typescript", "frontend"],
  },
  {
    id: "p3",
    title: "Zustand vs Redux 비교",
    body: "상태 관리 라이브러리 선택...",
    createdAt: "2025-02-01",
    author: { id: "u1", name: "김개발", avatar: "/avatars/kim.jpg" },
    comments: [],
    tags: ["react", "state-management"],
  },
];

// --- 정규화 ---
console.log("=== 1. API 응답 정규화 ===\n");

const normalizedState = normalizeApiResponse(apiResponse);

console.log("정규화 전 (중첩 구조):");
console.log(`  게시글 ${apiResponse.length}개에 작성자 정보가 ${apiResponse.length + apiResponse.reduce((s, p) => s + p.comments.length, 0)}회 중복 포함\n`);

console.log("정규화 후 (평탄 구조):");
console.log(`  users: ${Object.keys(normalizedState.entities.users).length}명 (중복 제거됨)`);
console.log(`  posts: ${Object.keys(normalizedState.entities.posts).length}개`);
console.log(`  comments: ${Object.keys(normalizedState.entities.comments).length}개\n`);

console.log("entities.users:");
Object.values(normalizedState.entities.users).forEach((user) =>
  console.log(`  ${user.id}: ${user.name}`)
);

console.log("\nentities.posts:");
Object.values(normalizedState.entities.posts).forEach((post) =>
  console.log(`  ${post.id}: "${post.title}" (by ${post.authorId}, comments: [${post.commentIds}])`)
);

// --- 셀렉터 테스트 ---
console.log("\n\n=== 2. 셀렉터 패턴 ===\n");

console.log("selectPostWithAuthor('p1'):");
const postWithAuthor = selectPostWithAuthor(normalizedState, "p1");
if (postWithAuthor) {
  console.log(`  제목: ${postWithAuthor.title}`);
  console.log(`  작성자: ${postWithAuthor.author.name}`);
  console.log(`  태그: [${postWithAuthor.tags.join(", ")}]`);
}

console.log("\nselectCommentsForPost('p1'):");
const comments = selectCommentsForPost(normalizedState, "p1");
comments.forEach((c) =>
  console.log(`  ${c.author.name}: "${c.text}"`)
);

console.log("\nselectPostsByTag('react'):");
const reactPosts = selectPostsByTag(normalizedState, "react");
reactPosts.forEach((p) => console.log(`  ${p.title}`));

console.log("\nselectPostsByAuthor('u1'):");
const kimPosts = selectPostsByAuthor(normalizedState, "u1");
kimPosts.forEach((p) => console.log(`  ${p.title}`));

console.log(`\n총 댓글 수: ${selectTotalCommentCount(normalizedState)}`);
console.log(`고유 사용자 수: ${selectUniqueUserCount(normalizedState)}`);

// --- 상태 업데이트 ---
console.log("\n\n=== 3. 정규화된 상태 업데이트 ===\n");

// 사용자 이름 변경 - 한 곳만 변경하면 모든 곳에 반영!
console.log("시나리오: 김개발 → 김시니어 이름 변경\n");

const updatedState = stateReducer(normalizedState, {
  type: "UPDATE_USER",
  userId: "u1",
  changes: { name: "김시니어" },
});

console.log("변경 후 사용자 정보:");
console.log(`  ${JSON.stringify(updatedState.entities.users["u1"])}`);

console.log("\n이 변경이 반영되는 곳들:");
const post1Author = selectPostWithAuthor(updatedState, "p1");
console.log(`  게시글 "p1"의 작성자: ${post1Author?.author.name}`);
const post3Author = selectPostWithAuthor(updatedState, "p3");
console.log(`  게시글 "p3"의 작성자: ${post3Author?.author.name}`);
const p2Comments = selectCommentsForPost(updatedState, "p2");
p2Comments.forEach((c) =>
  console.log(`  게시글 "p2"의 댓글 작성자: ${c.author.name}`)
);

console.log("\n정규화의 이점: 1번의 업데이트로 모든 참조가 자동 반영!");

// 댓글 추가
console.log("\n\n시나리오: 게시글 'p3'에 댓글 추가\n");

const stateWithNewComment = stateReducer(updatedState, {
  type: "ADD_COMMENT",
  postId: "p3",
  comment: {
    id: "c4",
    text: "Zustand이 더 간단해 보이네요",
    authorId: "u3",
    createdAt: "2025-02-02",
  },
});

const p3Comments = selectCommentsForPost(stateWithNewComment, "p3");
console.log("p3의 댓글:");
p3Comments.forEach((c) =>
  console.log(`  ${c.author.name}: "${c.text}"`)
);

// --- 정규화 vs 비정규화 비교 ---
console.log("\n\n=== 4. 정규화 vs 비정규화 비교 ===\n");
console.log(`
┌──────────────────┬──────────────────────┬──────────────────────┐
│ 관점             │ 비정규화 (중첩)      │ 정규화 (평탄)        │
├──────────────────┼──────────────────────┼──────────────────────┤
│ 데이터 중복      │ 많음                 │ 없음                 │
│ 업데이트 일관성  │ 위험 (여러 곳 수정)  │ 안전 (한 곳만 수정)  │
│ ID 기반 조회     │ O(n) 탐색 필요       │ O(1) 직접 접근       │
│ 읽기 복잡도      │ 간단 (이미 결합됨)   │ 셀렉터 필요          │
│ 쓰기 복잡도      │ 복잡 (깊은 업데이트) │ 간단 (얕은 업데이트) │
│ 메모이제이션     │ 어려움               │ 쉬움 (엔티티 단위)   │
│ 적합한 규모      │ 소규모               │ 중/대규모            │
└──────────────────┴──────────────────────┴──────────────────────┘
`);

console.log("✅ 상태 정규화 데모 완료!");

export {
  normalizeApiResponse,
  stateReducer,
  selectAllPosts,
  selectPostById,
  selectPostWithAuthor,
  selectCommentsForPost,
  selectPostsByTag,
  selectPostsByAuthor,
  NormalizedState,
  NormalizedPost,
  NormalizedUser,
  NormalizedComment,
};
