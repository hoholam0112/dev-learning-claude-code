# 챕터 09 연습 문제

> **관련 개념**: `concept.md` 참조
> **모범 답안**: `solution.tsx` 참조

---

## 문제 1: Vite 프로덕션 빌드 최적화 (⭐⭐⭐⭐)

### 설명

기존 React 프로젝트의 번들 크기가 1.2MB로 과도하게 큽니다. Vite 설정을 최적화하여 번들 크기를 500KB 이하로 줄이세요.

현재 프로젝트의 의존성:
- react, react-dom
- react-router-dom
- @tanstack/react-query
- zustand
- date-fns
- lodash
- chart.js + react-chartjs-2
- @mui/material + @emotion/react + @emotion/styled

### 요구 사항

1. `vite.config.ts`에 `manualChunks` 설정을 추가하여 다음과 같이 청크를 분리하세요:
   - `vendor-react`: React 코어
   - `vendor-router`: React Router
   - `vendor-state`: 상태 관리 (React Query, Zustand)
   - `vendor-ui`: MUI + Emotion
   - `vendor-chart`: Chart.js
2. `lodash`를 `lodash-es`로 교체하여 트리 쉐이킹을 활성화하세요.
3. `date-fns`에서 사용하는 함수만 named import하도록 코드를 수정하세요.
4. MUI의 아이콘을 선별적으로 import하세요 (`@mui/icons-material/Delete` 방식).
5. `rollup-plugin-visualizer`로 최적화 전후 번들 구성을 비교하세요.
6. gzip 기준 300KB 이하가 되도록 `vite-plugin-compression`을 설정하세요.

### 힌트

<details><summary>힌트 보기</summary>

- `lodash`에서 `lodash-es`로 마이그레이션:
  ```tsx
  // Before
  import _ from 'lodash';
  _.debounce(fn, 300);

  // After
  import { debounce } from 'lodash-es';
  debounce(fn, 300);
  ```
- MUI 아이콘 최적화:
  ```tsx
  // Before (전체 번들 포함)
  import { Delete, Edit } from '@mui/icons-material';

  // After (개별 파일에서 import)
  import Delete from '@mui/icons-material/Delete';
  import Edit from '@mui/icons-material/Edit';
  ```
- `npx vite-bundle-visualizer` 명령으로 번들을 분석할 수 있습니다.

</details>

---

## 문제 2: GitHub Actions CI/CD 파이프라인 구축 (⭐⭐⭐⭐)

### 설명

프로젝트에 완전한 CI/CD 파이프라인을 구축하세요. PR이 올라오면 자동으로 린트, 테스트, 빌드를 수행하고, `main` 브랜치에 머지되면 자동으로 배포합니다.

### 요구 사항

1. `.github/workflows/ci.yml` 파일을 작성하세요:
   - **트리거**: `push` (main, develop), `pull_request` (main)
   - **Job 1 - 품질 검사**: ESLint + TypeScript 타입 검사
   - **Job 2 - 테스트**: Vitest 실행 + 커버리지 리포트
   - **Job 3 - 빌드**: Vite 빌드 + 번들 크기 검사
   - **Job 4 - 배포**: main 브랜치만 프로덕션 배포

2. 다음 최적화를 적용하세요:
   - `pnpm` 캐싱으로 의존성 설치 시간 단축
   - `concurrency` 설정으로 같은 브랜치의 이전 실행 취소
   - Job 간 의존성 설정 (`needs`)
   - 환경별 secrets 관리

3. PR에 자동으로 커버리지 리포트를 코멘트하세요.

### 힌트

<details><summary>힌트 보기</summary>

- pnpm 캐싱:
  ```yaml
  - uses: pnpm/action-setup@v4
    with:
      version: 9
  - uses: actions/setup-node@v4
    with:
      node-version: 20
      cache: 'pnpm'
  ```
- 번들 크기 검사 스크립트는 `du -sb` 명령을 사용합니다.
- `actions/upload-artifact`로 빌드 결과물을 저장하고, 다른 Job에서 `actions/download-artifact`로 가져옵니다.
- `if: github.ref == 'refs/heads/main'`으로 main 브랜치만 배포합니다.

</details>

---

## 문제 3: 에러 모니터링 + 환경 관리 시스템 (⭐⭐⭐⭐)

### 설명

Sentry를 활용한 에러 모니터링 시스템과 멀티 환경(development/staging/production) 관리 시스템을 구축하세요.

### 요구 사항

1. **환경 변수 시스템 구축**:
   - `.env`, `.env.development`, `.env.staging`, `.env.production` 파일 작성
   - TypeScript 타입 안전한 환경 변수 접근 유틸리티 작성
   - `package.json`에 환경별 빌드 스크립트 추가

2. **Sentry 에러 모니터링 설정**:
   - `@sentry/react` 초기화 코드 작성
   - Error Boundary와 Sentry 통합
   - 커스텀 에러 컨텍스트 (사용자 정보, 페이지 경로 등) 추가
   - 성능 모니터링 (트레이싱) 설정

3. **릴리스 관리**:
   - GitHub Actions에서 Sentry 릴리스 자동 생성
   - 소스맵 업로드 (프로덕션 배포 시)
   - 배포 완료 알림 (Slack/이메일)

### 힌트

<details><summary>힌트 보기</summary>

- Vite에서 환경 변수 타입 정의:
  ```ts
  // src/vite-env.d.ts
  interface ImportMetaEnv {
    readonly VITE_API_URL: string;
    readonly VITE_SENTRY_DSN: string;
    // ...
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
  ```
- Sentry Error Boundary:
  ```tsx
  import * as Sentry from '@sentry/react';

  function FallbackComponent({ error, resetError }) {
    return (
      <div role="alert">
        <p>오류: {error.message}</p>
        <button onClick={resetError}>다시 시도</button>
      </div>
    );
  }

  <Sentry.ErrorBoundary fallback={FallbackComponent}>
    <App />
  </Sentry.ErrorBoundary>
  ```
- 빌드 시 소스맵 생성 후 Sentry에 업로드:
  ```yaml
  - uses: getsentry/action-release@v1
    with:
      sourcemaps: './dist/assets'
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

> 💡 **팁**: 문제를 풀기 전에 `concept.md`를 다시 읽어보세요. 특히 Vite 빌드 최적화 옵션과 GitHub Actions 워크플로우 문법을 복습하세요.
