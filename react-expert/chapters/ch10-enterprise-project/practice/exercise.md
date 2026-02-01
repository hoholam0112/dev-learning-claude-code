# 챕터 10 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: JWT 인증 시스템 완성 (⭐⭐⭐⭐)

### 설명

로그인 폼, 토큰 관리, 자동 갱신을 포함한 완전한 JWT 인증 시스템을 구현하세요.

### 요구 사항

1. **로그인 폼 구현**:
   - 이메일/비밀번호 필드와 유효성 검사
   - 에러 메시지 표시 (잘못된 인증 정보, 네트워크 오류 등)
   - 로딩 상태 표시
   - "로그인 상태 유지" 체크박스

2. **토큰 관리**:
   - Access Token을 메모리(변수)에 저장
   - API 요청 시 Authorization 헤더 자동 추가 (axios interceptor 또는 fetch 래퍼)
   - 401 응답 시 자동으로 토큰 갱신 후 요청 재시도

3. **자동 토큰 갱신**:
   - Access Token 만료 1분 전에 자동 갱신
   - Refresh Token도 만료되면 로그아웃 처리
   - 여러 동시 요청이 401을 받았을 때 토큰 갱신은 한 번만 실행

### 힌트

<details><summary>힌트 보기</summary>

- 동시 요청 시 토큰 갱신 중복 방지:
  ```tsx
  let refreshPromise: Promise<string> | null = null;

  async function getValidToken(): Promise<string> {
    if (isTokenExpired(accessToken)) {
      if (!refreshPromise) {
        refreshPromise = refreshTokenRequest().finally(() => {
          refreshPromise = null;
        });
      }
      return refreshPromise;
    }
    return accessToken;
  }
  ```
- axios interceptor를 사용하면 모든 요청에 자동으로 토큰을 추가할 수 있습니다.

</details>

---

## 문제 2: 역할 기반 접근 제어 (RBAC) 시스템 (⭐⭐⭐⭐)

### 설명

유연하고 확장 가능한 RBAC 시스템을 구현하세요. 정적 역할뿐 아니라 동적 권한 검사도 지원해야 합니다.

### 요구 사항

1. **역할 정의** (super_admin > admin > editor > viewer):
   - 각 역할의 권한을 매핑 테이블로 관리
   - 상위 역할은 하위 역할의 모든 권한을 포함

2. **React 통합**:
   - `<ProtectedRoute>` 컴포넌트 (라우트 보호)
   - `<Can>` 컴포넌트 (선언적 권한 렌더링)
   - `usePermission()` 훅 (명령적 권한 검사)

3. **동적 권한 검사**:
   - 특정 리소스에 대한 소유권 검사 (예: 자신의 게시글만 편집 가능)
   - 조건부 권한 (예: 관리자지만 특정 부서의 사용자만 관리 가능)

4. **네비게이션 연동**:
   - 권한에 따라 사이드바 메뉴 항목을 자동으로 필터링
   - 권한 없는 페이지 접근 시 적절한 에러 UI 표시

### 힌트

<details><summary>힌트 보기</summary>

- 동적 권한 검사:
  ```tsx
  interface PermissionCheck {
    permission: Permission;
    /** 리소스 소유권 검사 */
    ownerCheck?: (resource: any, user: User) => boolean;
  }

  function Can({ check, children }: { check: PermissionCheck; children: ReactNode }) {
    const { user } = useAuth();
    const hasStaticPermission = hasPermission(user.role, check.permission);
    const passesOwnerCheck = check.ownerCheck
      ? check.ownerCheck(resource, user)
      : true;
    // ...
  }
  ```
- URL 기반 리다이렉트: 미인증 사용자를 `/login?redirect=/original-path`로 보내고, 로그인 후 원래 경로로 돌아가게 하세요.

</details>

---

## 문제 3: 데이터 시각화 대시보드 (⭐⭐⭐⭐⭐)

### 설명

다양한 차트와 KPI를 포함한 대시보드 페이지를 구현하세요.

### 요구 사항

1. **KPI 카드 4개**: 매출, 사용자, 주문, 전환율
   - 이전 기간 대비 변화율 표시
   - 값 포맷팅 (통화, 퍼센트, 숫자)
   - 로딩 스켈레톤

2. **차트 3개** (Recharts 사용):
   - 라인 차트: 일별 매출 추이 (30일)
   - 바 차트: 카테고리별 판매량
   - 파이 차트: 사용자 역할 분포

3. **날짜 필터**: 기간 선택 시 모든 데이터가 업데이트
4. **React Query**: 서버 데이터 캐싱 + 자동 리패치
5. **반응형 레이아웃**: 모바일/태블릿/데스크톱 대응

### 힌트

<details><summary>힌트 보기</summary>

- React Query로 데이터 페칭:
  ```tsx
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard', 'metrics', dateRange],
    queryFn: () => fetchDashboardMetrics(dateRange),
    refetchInterval: 60000, // 1분마다 자동 리패치
  });
  ```
- Recharts ResponsiveContainer로 반응형 차트:
  ```tsx
  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={data}>
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Line dataKey="value" stroke="#8884d8" />
    </LineChart>
  </ResponsiveContainer>
  ```

</details>

---

## 문제 4: 실시간 알림 시스템 (⭐⭐⭐⭐⭐)

### 설명

WebSocket 기반 실시간 알림 시스템을 구현하세요.

### 요구 사항

1. **useWebSocket 훅**:
   - 자동 재연결 (지수 백오프)
   - 하트비트 (ping/pong)
   - 구독/구독 해제 패턴
   - 연결 상태 표시

2. **알림 센터 UI**:
   - 헤더에 알림 벨 아이콘 (안 읽은 수 표시)
   - 클릭 시 알림 목록 드롭다운
   - 알림 유형별 아이콘/색상 구분
   - 읽음/안 읽음 토글
   - "모두 읽음" 기능

3. **실시간 업데이트**:
   - 새 알림 도착 시 토스트 표시
   - KPI 카드 실시간 업데이트
   - 활동 로그 실시간 추가

### 힌트

<details><summary>힌트 보기</summary>

- WebSocket과 React Query 통합:
  ```tsx
  const queryClient = useQueryClient();

  useWebSocket('ws://api/events', {
    onMessage: (event) => {
      switch (event.type) {
        case 'metrics_update':
          queryClient.setQueryData(['metrics'], event.data);
          break;
        case 'new_notification':
          queryClient.invalidateQueries({ queryKey: ['notifications'] });
          showToast(event.data.message);
          break;
      }
    },
  });
  ```
- 알림 드롭다운은 Compound Components 패턴으로 구현하세요 (챕터 08 참조).

</details>

---

## 문제 5: 통합 프로젝트 - 관리자 대시보드 MVP (⭐⭐⭐⭐⭐)

### 설명

지금까지 배운 모든 개념을 통합하여 관리자 대시보드 MVP를 완성하세요.

### 요구 사항

1. **프로젝트 구조**: Feature-Sliced Design (챕터 08)
2. **인증**: JWT + RBAC (문제 1, 2)
3. **대시보드**: KPI + 차트 (문제 3)
4. **실시간**: WebSocket 알림 (문제 4)
5. **테스팅**: 핵심 기능 통합 테스트 (챕터 06)
6. **빌드/배포**: Vite 최적화 + CI/CD 설정 (챕터 09)
7. **접근성**: 모든 컴포넌트 WCAG 2.1 AA 준수
8. **타입 안전성**: 엄격한 TypeScript 활용 (챕터 05)

### 구현 범위 (최소)

- 로그인 페이지
- 대시보드 페이지 (KPI + 차트 + 활동 로그)
- 사용자 관리 페이지 (목록 + 상세)
- 설정 페이지
- 사이드바 + 헤더 레이아웃
- 알림 드롭다운

### 힌트

<details><summary>힌트 보기</summary>

- 프로젝트 구조:
  ```
  src/
  ├── app/          (프로바이더, 라우터)
  ├── pages/        (login, dashboard, users, settings)
  ├── widgets/      (sidebar, header, kpi-grid, chart-panel)
  ├── features/     (auth, realtime, notification, date-filter)
  ├── entities/     (user, metric, notification)
  └── shared/       (ui, api, lib, hooks)
  ```
- 순서: shared → entities → features → widgets → pages → app
- 각 슬라이스의 index.ts로 공개 API를 관리하세요.

</details>

---

## 채점 기준

| 항목 | 배점 |
|------|------|
| 정확한 동작 | 30% |
| 코드 가독성 | 15% |
| 엣지 케이스 처리 | 15% |
| 아키텍처 설계 | 20% |
| 타입 안전성 | 10% |
| 접근성 | 10% |

> 💡 **팁**: 이 챕터는 Expert 시리즈의 최종 프로젝트입니다. 이전 챕터(01~09)에서 배운 모든 개념을 종합적으로 활용하세요. 먼저 전체 아키텍처를 설계한 후, 기능 단위로 점진적으로 구현하는 것을 권장합니다.
