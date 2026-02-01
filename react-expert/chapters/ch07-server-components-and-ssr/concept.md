# 챕터 07: Server Components와 SSR

> **난이도**: ⭐⭐⭐⭐⭐ (5/5)
> **예상 학습 시간**: 8시간
> **선수 지식**: React 기본, Next.js 개념, 비동기 프로그래밍, 캐싱 전략

---

## 학습 목표

이 챕터를 마치면 다음을 할 수 있습니다:

- React Server Components(RSC)의 아키텍처와 렌더링 파이프라인을 이해할 수 있습니다.
- 서버 컴포넌트와 클라이언트 컴포넌트의 경계를 올바르게 설계할 수 있습니다.
- 스트리밍 SSR과 Suspense를 활용한 점진적 페이지 로딩을 구현할 수 있습니다.
- Next.js App Router 기반으로 데이터 페칭, 캐싱, 재검증 전략을 적용할 수 있습니다.
- 서버 액션(Server Actions)을 활용한 폼 처리와 뮤테이션을 구현할 수 있습니다.

---

## 핵심 개념

### 1. React Server Components(RSC) 아키텍처

RSC는 서버에서만 실행되는 컴포넌트입니다. 클라이언트로 JavaScript 번들을 전송하지 않으며, 데이터베이스나 파일 시스템에 직접 접근할 수 있습니다.

```mermaid
graph TB
    subgraph "서버"
        SC1["서버 컴포넌트<br/>Layout.tsx"]
        SC2["서버 컴포넌트<br/>PostList.tsx"]
        SC3["서버 컴포넌트<br/>PostDetail.tsx"]
        DB[(데이터베이스)]
        FS[파일 시스템]

        SC2 --> DB
        SC3 --> DB
        SC1 --> FS
    end

    subgraph "클라이언트"
        CC1["클라이언트 컴포넌트<br/>LikeButton.tsx"]
        CC2["클라이언트 컴포넌트<br/>CommentForm.tsx"]
        CC3["클라이언트 컴포넌트<br/>SearchBar.tsx"]
    end

    SC1 -->|"children으로 전달"| CC3
    SC2 -->|"직렬화된 트리"| CC1
    SC3 -->|"직렬화된 트리"| CC2

    subgraph "RSC 페이로드"
        direction LR
        P1["직렬화된 React 트리"]
        P2["클라이언트 컴포넌트 참조"]
        P3["서버 데이터"]
    end

    style SC1 fill:#2196F3,stroke:#333,color:#fff
    style SC2 fill:#2196F3,stroke:#333,color:#fff
    style SC3 fill:#2196F3,stroke:#333,color:#fff
    style CC1 fill:#FF9800,stroke:#333,color:#fff
    style CC2 fill:#FF9800,stroke:#333,color:#fff
    style CC3 fill:#FF9800,stroke:#333,color:#fff
```

**RSC의 핵심 원칙:**

| 특성 | 서버 컴포넌트 | 클라이언트 컴포넌트 |
|------|--------------|-------------------|
| 실행 환경 | 서버만 | 서버 + 클라이언트 |
| JS 번들 | 포함 안 됨 | 포함됨 |
| `useState`/`useEffect` | 사용 불가 | 사용 가능 |
| 이벤트 핸들러 | 사용 불가 | 사용 가능 |
| DB/파일 직접 접근 | 가능 | 불가능 |
| `async/await` | 컴포넌트 레벨 가능 | 컴포넌트 레벨 불가 |
| 시리얼라이즈 | 가능해야 함 | 제약 없음 |

### 2. 스트리밍 SSR과 Suspense

전통적인 SSR은 전체 페이지를 한 번에 렌더링하여 응답합니다. 스트리밍 SSR은 **준비된 부분부터 점진적으로** 클라이언트에 전송합니다.

```mermaid
sequenceDiagram
    participant Client as 브라우저
    participant Server as Next.js 서버
    participant DB as 데이터베이스

    Client->>Server: GET /blog/1

    Note over Server: 1단계: 즉시 응답 시작
    Server-->>Client: <html><head>...</head><body>
    Server-->>Client: <nav>네비게이션</nav>
    Server-->>Client: <Suspense fallback="로딩...">

    Note over Server: 2단계: 비동기 데이터 대기
    Server->>DB: SELECT * FROM posts WHERE id = 1
    DB-->>Server: 게시글 데이터

    Note over Server: 3단계: 스트리밍 전송
    Server-->>Client: <article>게시글 내용</article>
    Server-->>Client: </Suspense>

    Note over Server: 4단계: 댓글 데이터 (느림)
    Server->>DB: SELECT * FROM comments
    DB-->>Server: 댓글 목록

    Server-->>Client: <section>댓글 목록</section>
    Server-->>Client: </body></html>

    Note over Client: 점진적 하이드레이션 수행
```

### 3. 서버/클라이언트 경계 설계

`'use client'` 지시어는 서버-클라이언트 경계를 정의합니다. 이 경계를 올바르게 설계하는 것이 RSC 아키텍처의 핵심입니다.

```mermaid
graph TD
    subgraph "서버 컴포넌트 트리"
        A["RootLayout (서버)"]
        B["BlogPage (서버)"]
        C["PostContent (서버)<br/>async - DB에서 데이터 페칭"]
        D["Sidebar (서버)<br/>최근 게시글 표시"]
    end

    subgraph "경계 (use client)"
        E["'use client' 경계"]
    end

    subgraph "클라이언트 컴포넌트 트리"
        F["InteractivePost (클라이언트)<br/>좋아요, 공유 버튼"]
        G["CommentSection (클라이언트)<br/>댓글 입력, 실시간 업데이트"]
        H["ThemeToggle (클라이언트)<br/>다크/라이트 모드 전환"]
    end

    A --> B
    B --> C
    B --> D
    C --> E
    E --> F
    E --> G
    A --> H

    style A fill:#2196F3,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#2196F3,color:#fff
    style D fill:#2196F3,color:#fff
    style E fill:#f44336,color:#fff,stroke-width:3px
    style F fill:#FF9800,color:#fff
    style G fill:#FF9800,color:#fff
    style H fill:#FF9800,color:#fff
```

**경계 설계 원칙:**

1. **경계를 가능한 아래로 내려라**: 클라이언트 컴포넌트 영역을 최소화합니다.
2. **서버 컴포넌트를 클라이언트 컴포넌트의 children으로 전달하라**: Composition 패턴을 활용합니다.
3. **직렬화 가능한 props만 경계를 넘을 수 있다**: 함수, 클래스 인스턴스는 전달 불가합니다.

### 4. 데이터 페칭과 캐싱 전략

Next.js App Router에서의 데이터 페칭은 서버 컴포넌트 내에서 `async/await`로 직접 수행합니다.

```mermaid
graph LR
    subgraph "캐싱 레이어"
        RC["Request Memoization<br/>같은 요청 중복 제거"]
        DC["Data Cache<br/>서버 측 응답 캐시"]
        FPC["Full Route Cache<br/>빌드 시 정적 생성"]
        RRC["Router Cache<br/>클라이언트 측 캐시"]
    end

    RC -->|"per request"| DC
    DC -->|"persistent"| FPC
    FPC -->|"in memory"| RRC

    subgraph "재검증 전략"
        TB["시간 기반<br/>revalidate: 60"]
        OD["온디맨드<br/>revalidateTag()"]
    end

    DC -.->|"무효화"| TB
    DC -.->|"무효화"| OD
```

### 5. Server Actions

Server Actions는 서버에서 실행되는 비동기 함수로, 폼 제출이나 데이터 뮤테이션에 사용됩니다.

```mermaid
sequenceDiagram
    participant UI as 클라이언트 UI
    participant SA as Server Action
    participant DB as 데이터베이스
    participant Cache as 캐시

    UI->>SA: formAction(formData)
    Note over SA: 'use server' 환경에서 실행
    SA->>DB: INSERT INTO posts...
    DB-->>SA: 성공
    SA->>Cache: revalidatePath('/blog')
    Cache-->>SA: 캐시 무효화 완료
    SA-->>UI: redirect('/blog/new-post')
    Note over UI: 자동 UI 업데이트
```

---

## 코드로 이해하기

### 예제 1: Next.js App Router 기반 블로그 - 서버 컴포넌트
> 📁 `practice/example-01.tsx` 파일을 참고하세요.

```tsx
// app/blog/page.tsx - 서버 컴포넌트 (기본값)
export default async function BlogPage() {
  // 서버에서 직접 데이터 페칭 (DB, API 등)
  const posts = await fetchPosts();

  return (
    <main>
      <h1>블로그</h1>
      <Suspense fallback={<PostListSkeleton />}>
        <PostList posts={posts} />
      </Suspense>
    </main>
  );
}
```

**실행 방법**:
```bash
npx create-next-app@latest blog-demo --typescript --app --tailwind
cd blog-demo
npm run dev
```

### 예제 2: 클라이언트 컴포넌트와 Server Actions
> 📁 `practice/example-02.tsx` 파일을 참고하세요.

```tsx
// 서버 액션 정의
'use server';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  await db.post.create({ data: { title } });
  revalidatePath('/blog');
  redirect('/blog');
}
```

**실행 방법**:
```bash
cd blog-demo
npm run dev
# http://localhost:3000/blog 에서 확인
```

---

## 주의 사항

- ⚠️ **서버 컴포넌트에서 hooks 사용 금지**: `useState`, `useEffect`, `useContext` 등은 클라이언트 컴포넌트에서만 사용 가능합니다.
- ⚠️ **'use client'는 전파된다**: 클라이언트 컴포넌트가 import하는 모든 모듈도 클라이언트 번들에 포함됩니다.
- ⚠️ **서버 컴포넌트에서 함수를 props로 전달 불가**: 직렬화할 수 없는 값은 서버→클라이언트 경계를 넘을 수 없습니다.
- 💡 **Composition 패턴 활용**: 서버 컴포넌트를 클라이언트 컴포넌트의 `children`으로 전달하면 서버에서 렌더링된 결과가 전달됩니다.
- 💡 **`loading.tsx` 활용**: 파일 기반 라우팅에서 자동으로 Suspense boundary를 생성합니다.
- 💡 **`error.tsx` 활용**: Error Boundary를 파일 레벨에서 자동 설정합니다. 반드시 `'use client'`로 선언해야 합니다.

---

## 정리

| 개념 | 설명 | 예제 |
|------|------|------|
| RSC | 서버에서만 실행되는 컴포넌트 | `async function Page()` |
| 'use client' | 서버-클라이언트 경계 선언 | 상호작용이 필요한 컴포넌트 |
| 스트리밍 SSR | 점진적 HTML 전송 | `<Suspense fallback>` |
| Server Actions | 서버 측 뮤테이션 함수 | `'use server'` + `formAction` |
| 데이터 캐싱 | 다층 캐시 전략 | `fetch(url, { next: { revalidate: 60 } })` |
| 재검증 | 캐시 무효화 | `revalidatePath()`, `revalidateTag()` |

---

## 다음 단계

- ✅ `practice/exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 챕터: **챕터 08 - 설계 패턴과 아키텍처**
- 🔗 참고 자료:
  - [Next.js App Router 공식 문서](https://nextjs.org/docs/app)
  - [React Server Components RFC](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md)
  - [Server Actions 문서](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
  - [데이터 캐싱 전략](https://nextjs.org/docs/app/building-your-application/caching)
