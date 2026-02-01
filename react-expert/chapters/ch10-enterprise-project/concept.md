# 챕터 10: 엔터프라이즈 프로젝트 - 관리자 대시보드

> **난이도**: ⭐⭐⭐⭐⭐ (5/5)
> **예상 학습 시간**: 12시간
> **선수 지식**: 챕터 01~09의 모든 개념, REST API, WebSocket 기본

---

## 학습 목표

이 챕터를 마치면 다음을 할 수 있습니다:

- JWT 기반 인증/인가 시스템을 설계하고 구현할 수 있습니다.
- 역할 기반 접근 제어(RBAC)를 React 라우터와 통합할 수 있습니다.
- 대시보드 레이아웃에서 차트와 데이터 시각화를 구현할 수 있습니다.
- WebSocket을 활용한 실시간 데이터 업데이트를 구현할 수 있습니다.
- Feature-Sliced Design 기반으로 확장 가능한 대시보드 아키텍처를 설계할 수 있습니다.

---

## 핵심 개념

### 1. 인증/인가 시스템 아키텍처

JWT(JSON Web Token) 기반 인증은 엔터프라이즈 SPA에서 가장 널리 사용되는 패턴입니다. Access Token과 Refresh Token을 활용하여 보안과 사용자 경험을 모두 확보합니다.

```mermaid
sequenceDiagram
    participant User as 사용자
    participant App as React 앱
    participant API as API 서버
    participant Auth as 인증 서버

    User->>App: 로그인 폼 제출
    App->>Auth: POST /auth/login (email, password)
    Auth-->>App: { accessToken, refreshToken }
    Note over App: accessToken: 메모리 저장<br/>refreshToken: httpOnly 쿠키

    User->>App: 데이터 요청
    App->>API: GET /api/data (Authorization: Bearer {accessToken})
    API-->>App: 데이터 응답

    Note over App: accessToken 만료 (15분)
    User->>App: 데이터 요청
    App->>API: GET /api/data (만료된 토큰)
    API-->>App: 401 Unauthorized

    App->>Auth: POST /auth/refresh (refreshToken)
    Auth-->>App: { newAccessToken }
    App->>API: GET /api/data (새 accessToken)
    API-->>App: 데이터 응답
```

**보안 원칙:**

| 토큰 | 저장 위치 | 만료 시간 | 용도 |
|------|----------|----------|------|
| Access Token | 메모리 (변수) | 15분 | API 요청 인증 |
| Refresh Token | httpOnly 쿠키 | 7일 | Access Token 갱신 |
| CSRF Token | 커스텀 헤더 | 세션 | CSRF 공격 방지 |

### 2. 역할 기반 접근 제어 (RBAC)

```mermaid
graph TD
    subgraph "역할 계층"
        SUPER["슈퍼 관리자<br/>모든 권한"]
        ADMIN["관리자<br/>사용자/콘텐츠 관리"]
        EDITOR["편집자<br/>콘텐츠 CRUD"]
        VIEWER["뷰어<br/>읽기 전용"]
    end

    SUPER -->|"포함"| ADMIN
    ADMIN -->|"포함"| EDITOR
    EDITOR -->|"포함"| VIEWER

    subgraph "권한 매핑"
        P1["dashboard:read"]
        P2["users:read"]
        P3["users:write"]
        P4["users:delete"]
        P5["content:read"]
        P6["content:write"]
        P7["settings:manage"]
    end

    VIEWER --> P1
    VIEWER --> P5
    EDITOR --> P6
    ADMIN --> P2
    ADMIN --> P3
    SUPER --> P4
    SUPER --> P7

    subgraph "React 라우트 보호"
        R1["/dashboard<br/>VIEWER 이상"]
        R2["/users<br/>ADMIN 이상"]
        R3["/settings<br/>SUPER만"]
    end

    style SUPER fill:#f44336,color:#fff
    style ADMIN fill:#FF9800,color:#fff
    style EDITOR fill:#4CAF50,color:#fff
    style VIEWER fill:#2196F3,color:#fff
```

### 3. 대시보드 데이터 시각화

```mermaid
graph TB
    subgraph "데이터 흐름"
        API["API 서버"]
        WS["WebSocket 서버"]
        RQ["React Query<br/>캐시 + 자동 갱신"]
        WSH["WebSocket 훅<br/>실시간 업데이트"]
    end

    subgraph "시각화 컴포넌트"
        KPI["KPI 카드<br/>핵심 지표"]
        LINE["라인 차트<br/>트렌드 분석"]
        BAR["바 차트<br/>비교 분석"]
        PIE["파이 차트<br/>분포 분석"]
        TABLE["데이터 테이블<br/>상세 데이터"]
    end

    API --> RQ
    WS --> WSH
    RQ --> KPI
    RQ --> LINE
    RQ --> BAR
    RQ --> PIE
    RQ --> TABLE
    WSH -->|"실시간 업데이트"| KPI
    WSH -->|"실시간 업데이트"| TABLE
```

### 4. 실시간 업데이트 (WebSocket)

```mermaid
sequenceDiagram
    participant App as React 앱
    participant WS as WebSocket 서버
    participant Queue as 메시지 큐

    App->>WS: ws.connect() + JWT 토큰
    WS-->>App: connection_established

    App->>WS: subscribe('dashboard:metrics')
    WS-->>App: subscription_confirmed

    loop 실시간 데이터
        Queue->>WS: 새로운 메트릭 데이터
        WS-->>App: { type: 'metrics_update', data: {...} }
        Note over App: React Query 캐시 업데이트<br/>또는 직접 상태 업데이트
    end

    App->>WS: unsubscribe('dashboard:metrics')
    App->>WS: ws.disconnect()
```

### 5. 확장 가능한 대시보드 아키텍처

```mermaid
graph TD
    subgraph "app/"
        APP["App.tsx<br/>프로바이더, 라우터"]
        AUTH_P["AuthProvider"]
        THEME_P["ThemeProvider"]
        QUERY_P["QueryProvider"]
    end

    subgraph "pages/"
        DASH["DashboardPage"]
        USERS["UsersPage"]
        ANALYTICS["AnalyticsPage"]
        SETTINGS["SettingsPage"]
    end

    subgraph "widgets/"
        SIDEBAR["Sidebar"]
        HEADER["DashboardHeader"]
        KPI_W["KPIWidget"]
        CHART_W["ChartWidget"]
        TABLE_W["DataTableWidget"]
        NOTIFY_W["NotificationWidget"]
    end

    subgraph "features/"
        AUTH_F["auth/<br/>로그인, 토큰 관리"]
        REALTIME_F["realtime/<br/>WebSocket 관리"]
        EXPORT_F["data-export/<br/>CSV/PDF 내보내기"]
        FILTER_F["filter/<br/>날짜/카테고리 필터"]
    end

    subgraph "entities/"
        USER_E["user/"]
        METRIC_E["metric/"]
        ACTIVITY_E["activity/"]
    end

    subgraph "shared/"
        UI_S["ui/ (Button, Input, Modal)"]
        API_S["api/ (HTTP 클라이언트)"]
        LIB_S["lib/ (유틸리티)"]
        HOOKS_S["hooks/ (공용 훅)"]
    end

    APP --> DASH
    DASH --> KPI_W
    DASH --> CHART_W
    DASH --> TABLE_W
    KPI_W --> REALTIME_F
    KPI_W --> METRIC_E
    CHART_W --> FILTER_F
    TABLE_W --> EXPORT_F
    AUTH_F --> USER_E
    USER_E --> API_S

    style APP fill:#f44336,color:#fff
    style DASH fill:#FF9800,color:#fff
    style KPI_W fill:#FFC107,color:#333
    style AUTH_F fill:#4CAF50,color:#fff
    style USER_E fill:#2196F3,color:#fff
    style UI_S fill:#9C27B0,color:#fff
```

---

## 코드로 이해하기

### 예제 1: 인증 시스템 + RBAC + 대시보드 레이아웃
> 📁 `practice/example-01.tsx` 파일을 참고하세요.

```tsx
// 핵심: 인증 상태 관리
const { user, login, logout, isAuthenticated } = useAuth();

// 핵심: 역할 기반 라우트 보호
<ProtectedRoute requiredPermission="dashboard:read">
  <DashboardPage />
</ProtectedRoute>
```

**실행 방법**:
```bash
npm create vite@latest admin-dashboard -- --template react-ts
cd admin-dashboard
npm install react-router-dom @tanstack/react-query zustand
npm install recharts date-fns
npm run dev
```

### 예제 2: 실시간 대시보드 + 데이터 시각화
> 📁 `practice/example-02.tsx` 파일을 참고하세요.

```tsx
// 핵심: WebSocket 훅
const { data, isConnected } = useWebSocket('ws://api/metrics', {
  onMessage: (data) => queryClient.setQueryData(['metrics'], data),
});

// 핵심: KPI 카드 + 실시간 업데이트
<KPICard title="활성 사용자" value={metrics.activeUsers} trend={+12.5} />
```

**실행 방법**:
```bash
cd admin-dashboard
npm run dev
# http://localhost:5173 에서 확인
```

---

## 주의 사항

- ⚠️ **Access Token을 localStorage에 저장하지 마세요**: XSS 공격에 취약합니다. 메모리(변수)에 저장하세요.
- ⚠️ **Refresh Token은 httpOnly 쿠키에 저장하세요**: JavaScript로 접근 불가능한 쿠키를 사용합니다.
- ⚠️ **권한 검사를 프론트엔드에만 의존하지 마세요**: 클라이언트 측 검사는 UX 목적이며, 실제 보안은 서버에서 수행해야 합니다.
- ⚠️ **WebSocket 재연결 로직을 반드시 구현하세요**: 네트워크 불안정 환경을 고려해야 합니다.
- 💡 **React Query와 WebSocket 결합**: WebSocket 메시지로 React Query 캐시를 직접 업데이트하면 일관된 데이터 흐름을 유지할 수 있습니다.
- 💡 **차트 라이브러리 lazy loading**: 차트 컴포넌트는 크기가 크므로 `React.lazy()`로 동적 로딩하세요.
- 💡 **대시보드 상태 URL 동기화**: 필터, 날짜 범위 등의 상태를 URL 파라미터로 관리하면 공유 가능한 대시보드를 만들 수 있습니다.

---

## 정리

| 개념 | 설명 | 구현 |
|------|------|------|
| JWT 인증 | Access/Refresh Token 기반 | `useAuth()` 훅 |
| RBAC | 역할 기반 접근 제어 | `ProtectedRoute`, `usePermission()` |
| 데이터 시각화 | 차트, KPI, 테이블 | Recharts, 커스텀 KPI 카드 |
| 실시간 업데이트 | WebSocket 기반 | `useWebSocket()` 훅 |
| 확장 아키텍처 | FSD 기반 구조화 | 레이어별 관심사 분리 |

---

## 다음 단계

- ✅ `practice/exercise.md`의 연습 문제를 풀어보세요.
- 📖 이 챕터는 **Expert 시리즈의 최종 챕터**입니다.
- 🔗 참고 자료:
  - [Recharts 공식 문서](https://recharts.org/)
  - [React Query 공식 문서](https://tanstack.com/query/)
  - [JWT 보안 모범 사례](https://auth0.com/docs/secure/tokens/json-web-tokens)
  - [OWASP 인증 가이드](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
  - [WebSocket API](https://developer.mozilla.org/ko/docs/Web/API/WebSocket)

---

## 축하합니다!

Expert 레벨 10개 챕터를 모두 마쳤습니다. 이 과정을 통해 다음 역량을 갖추게 되었습니다:

1. **React 내부 동작** 이해 (가상 DOM, 재조정 알고리즘)
2. **고급 훅 패턴** 활용 (커스텀 훅, 최적화 훅)
3. **성능 최적화** 전략 (메모이제이션, 가상화, 코드 스플리팅)
4. **상태 관리 아키텍처** 설계 (Zustand, React Query, 전역/서버 상태)
5. **TypeScript 고급 활용** (제네릭, 조건부 타입, 유틸리티 타입)
6. **테스팅 전략** 수립 (RTL, MSW, 접근성 테스트)
7. **Server Components와 SSR** 구현 (RSC, 스트리밍, Server Actions)
8. **설계 패턴과 아키텍처** 적용 (Compound, Headless, FSD)
9. **빌드와 배포 파이프라인** 구축 (Vite, GitHub Actions, 모니터링)
10. **엔터프라이즈 프로젝트** 완성 (인증, 시각화, 실시간, 확장 아키텍처)
