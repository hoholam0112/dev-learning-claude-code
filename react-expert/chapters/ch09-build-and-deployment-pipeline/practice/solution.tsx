/**
 * 챕터 09 - 연습 문제 모범 답안
 *
 * 이 파일은 exercise.md의 세 문제에 대한 모범 답안을 담고 있습니다.
 *
 * 실행 방법:
 *   1. 프로젝트 설정:
 *      npm create vite@latest deploy-solution -- --template react-ts
 *      cd deploy-solution
 *      npm install
 *
 *   2. 아래 설정 파일들을 해당 경로에 배치
 *
 *   3. 빌드 및 확인:
 *      npm run build
 *      npm run build:analyze
 */

import React from 'react';

// ============================================================
// 문제 1 답안: Vite 프로덕션 빌드 최적화
// ============================================================

/**
 * vite.config.ts - 최적화된 빌드 설정
 *
 * ```ts
 * /// <reference types="vitest" />
 * import { defineConfig, type UserConfig } from 'vite';
 * import react from '@vitejs/plugin-react';
 * import { visualizer } from 'rollup-plugin-visualizer';
 * import viteCompression from 'vite-plugin-compression';
 * import { resolve } from 'path';
 *
 * export default defineConfig(({ mode }): UserConfig => {
 *   const isProduction = mode === 'production';
 *   const isAnalyze = process.env.ANALYZE === 'true';
 *
 *   return {
 *     resolve: {
 *       alias: {
 *         '@': resolve(__dirname, './src'),
 *       },
 *     },
 *
 *     plugins: [
 *       react(),
 *
 *       // gzip 압축 (프로덕션만)
 *       isProduction && viteCompression({
 *         algorithm: 'gzip',
 *         threshold: 1024,
 *         deleteOriginFile: false,
 *       }),
 *
 *       // brotli 압축 (프로덕션만)
 *       isProduction && viteCompression({
 *         algorithm: 'brotliCompress',
 *         ext: '.br',
 *         threshold: 1024,
 *       }),
 *
 *       // 번들 분석
 *       isAnalyze && visualizer({
 *         filename: 'stats.html',
 *         open: true,
 *         gzipSize: true,
 *         brotliSize: true,
 *         template: 'treemap',
 *       }),
 *     ].filter(Boolean),
 *
 *     build: {
 *       target: 'es2020',
 *       sourcemap: isProduction ? 'hidden' : true,
 *       minify: 'esbuild',
 *       chunkSizeWarningLimit: 250,
 *
 *       rollupOptions: {
 *         output: {
 *           // 핵심: 수동 청크 분리로 효율적인 캐싱
 *           manualChunks: (id: string) => {
 *             // React 코어 (변경 빈도 매우 낮음)
 *             if (id.includes('node_modules/react/') ||
 *                 id.includes('node_modules/react-dom/') ||
 *                 id.includes('node_modules/scheduler/')) {
 *               return 'vendor-react';
 *             }
 *
 *             // 라우터 (변경 빈도 낮음)
 *             if (id.includes('node_modules/react-router')) {
 *               return 'vendor-router';
 *             }
 *
 *             // 상태 관리 (변경 빈도 낮음)
 *             if (id.includes('node_modules/zustand') ||
 *                 id.includes('node_modules/@tanstack/react-query')) {
 *               return 'vendor-state';
 *             }
 *
 *             // UI 라이브러리 (크기가 크므로 별도 분리)
 *             if (id.includes('node_modules/@mui/') ||
 *                 id.includes('node_modules/@emotion/')) {
 *               return 'vendor-ui';
 *             }
 *
 *             // 차트 라이브러리 (크기가 크고 특정 페이지에서만 사용)
 *             if (id.includes('node_modules/chart.js') ||
 *                 id.includes('node_modules/react-chartjs-2')) {
 *               return 'vendor-chart';
 *             }
 *
 *             // 유틸리티 (lodash-es, date-fns)
 *             if (id.includes('node_modules/lodash-es') ||
 *                 id.includes('node_modules/date-fns')) {
 *               return 'vendor-utils';
 *             }
 *           },
 *
 *           chunkFileNames: 'assets/js/[name]-[hash].js',
 *           entryFileNames: 'assets/js/[name]-[hash].js',
 *           assetFileNames: (assetInfo) => {
 *             const name = assetInfo.name || '';
 *             if (/\.(png|jpe?g|gif|svg|webp)$/.test(name)) {
 *               return 'assets/images/[name]-[hash][extname]';
 *             }
 *             if (/\.(woff2?|eot|ttf)$/.test(name)) {
 *               return 'assets/fonts/[name]-[hash][extname]';
 *             }
 *             return 'assets/[name]-[hash][extname]';
 *           },
 *         },
 *       },
 *
 *       cssCodeSplit: true,
 *       reportCompressedSize: true,
 *     },
 *
 *     // 개발 서버 최적화
 *     optimizeDeps: {
 *       include: [
 *         'react',
 *         'react-dom',
 *         'react-router-dom',
 *         'zustand',
 *       ],
 *     },
 *   };
 * });
 * ```
 */

/**
 * lodash -> lodash-es 마이그레이션 예시
 *
 * ```ts
 * // ❌ Before: 전체 lodash 번들 포함 (~70KB gzip)
 * import _ from 'lodash';
 * const result = _.debounce(fn, 300);
 * const filtered = _.filter(items, predicate);
 * const grouped = _.groupBy(items, 'category');
 *
 * // ✅ After: 사용하는 함수만 트리 쉐이킹 (~5KB gzip)
 * import { debounce, filter, groupBy } from 'lodash-es';
 * const result = debounce(fn, 300);
 * const filtered = filter(items, predicate);
 * const grouped = groupBy(items, 'category');
 * ```
 */

/**
 * date-fns 최적화 예시
 *
 * ```ts
 * // ❌ Before: 사용하지 않는 로케일/함수 포함 가능
 * import { format, parseISO, differenceInDays } from 'date-fns';
 * import { ko } from 'date-fns/locale';
 *
 * // ✅ After: 필요한 함수만 개별 import (이미 트리쉐이킹 지원)
 * import { format } from 'date-fns/format';
 * import { parseISO } from 'date-fns/parseISO';
 * import { differenceInDays } from 'date-fns/differenceInDays';
 * import { ko } from 'date-fns/locale/ko';
 * ```
 */

/**
 * MUI 아이콘 최적화 예시
 *
 * ```ts
 * // ❌ Before: 전체 아이콘 번들 포함 (~200KB gzip)
 * import { Delete, Edit, Add, Search } from '@mui/icons-material';
 *
 * // ✅ After: 개별 파일에서 import (~2KB per icon)
 * import Delete from '@mui/icons-material/Delete';
 * import Edit from '@mui/icons-material/Edit';
 * import Add from '@mui/icons-material/Add';
 * import Search from '@mui/icons-material/Search';
 * ```
 */

// ============================================================
// 문제 2 답안: GitHub Actions CI/CD 파이프라인
// ============================================================

/**
 * .github/workflows/ci.yml
 *
 * ```yaml
 * name: CI/CD Pipeline
 *
 * on:
 *   push:
 *     branches: [main, develop]
 *   pull_request:
 *     branches: [main]
 *
 * concurrency:
 *   group: ${{ github.workflow }}-${{ github.ref }}
 *   cancel-in-progress: true
 *
 * env:
 *   NODE_VERSION: '20'
 *   PNPM_VERSION: '9'
 *
 * jobs:
 *   # === 품질 검사 ===
 *   quality:
 *     name: 코드 품질 검사
 *     runs-on: ubuntu-latest
 *     timeout-minutes: 10
 *     steps:
 *       - uses: actions/checkout@v4
 *
 *       - uses: pnpm/action-setup@v4
 *         with:
 *           version: ${{ env.PNPM_VERSION }}
 *
 *       - uses: actions/setup-node@v4
 *         with:
 *           node-version: ${{ env.NODE_VERSION }}
 *           cache: 'pnpm'
 *
 *       - name: 의존성 설치
 *         run: pnpm install --frozen-lockfile
 *
 *       - name: ESLint
 *         run: pnpm lint
 *
 *       - name: TypeScript 검사
 *         run: pnpm type-check
 *
 *   # === 테스트 ===
 *   test:
 *     name: 테스트
 *     runs-on: ubuntu-latest
 *     timeout-minutes: 15
 *     needs: [quality]
 *     steps:
 *       - uses: actions/checkout@v4
 *
 *       - uses: pnpm/action-setup@v4
 *         with:
 *           version: ${{ env.PNPM_VERSION }}
 *
 *       - uses: actions/setup-node@v4
 *         with:
 *           node-version: ${{ env.NODE_VERSION }}
 *           cache: 'pnpm'
 *
 *       - name: 의존성 설치
 *         run: pnpm install --frozen-lockfile
 *
 *       - name: 테스트 (커버리지)
 *         run: pnpm test:coverage
 *
 *       - name: 커버리지 리포트 저장
 *         uses: actions/upload-artifact@v4
 *         if: always()
 *         with:
 *           name: coverage
 *           path: coverage/
 *
 *       - name: PR 커버리지 코멘트
 *         if: github.event_name == 'pull_request'
 *         uses: davelosert/vitest-coverage-report-action@v2
 *         with:
 *           json-summary-path: coverage/coverage-summary.json
 *
 *   # === 빌드 ===
 *   build:
 *     name: 빌드 & 번들 검사
 *     runs-on: ubuntu-latest
 *     timeout-minutes: 10
 *     needs: [quality]
 *     steps:
 *       - uses: actions/checkout@v4
 *
 *       - uses: pnpm/action-setup@v4
 *         with:
 *           version: ${{ env.PNPM_VERSION }}
 *
 *       - uses: actions/setup-node@v4
 *         with:
 *           node-version: ${{ env.NODE_VERSION }}
 *           cache: 'pnpm'
 *
 *       - name: 의존성 설치
 *         run: pnpm install --frozen-lockfile
 *
 *       - name: 빌드
 *         run: pnpm build
 *         env:
 *           VITE_APP_VERSION: ${{ github.sha }}
 *
 *       - name: 번들 크기 검사
 *         run: |
 *           echo "## 번들 크기 리포트" >> $GITHUB_STEP_SUMMARY
 *           echo "" >> $GITHUB_STEP_SUMMARY
 *
 *           TOTAL=$(du -sb dist/assets/ | cut -f1)
 *           TOTAL_KB=$((TOTAL / 1024))
 *           MAX_KB=500
 *
 *           echo "| 파일 | 크기 |" >> $GITHUB_STEP_SUMMARY
 *           echo "|------|------|" >> $GITHUB_STEP_SUMMARY
 *
 *           for f in dist/assets/js/*.js; do
 *             SIZE=$(du -sb "$f" | cut -f1)
 *             SIZE_KB=$((SIZE / 1024))
 *             NAME=$(basename "$f")
 *             echo "| $NAME | ${SIZE_KB}KB |" >> $GITHUB_STEP_SUMMARY
 *           done
 *
 *           echo "" >> $GITHUB_STEP_SUMMARY
 *           echo "**총 크기: ${TOTAL_KB}KB / ${MAX_KB}KB**" >> $GITHUB_STEP_SUMMARY
 *
 *           if [ "$TOTAL" -gt "$((MAX_KB * 1024))" ]; then
 *             echo "::error::번들 크기 예산 초과! (${TOTAL_KB}KB > ${MAX_KB}KB)"
 *             exit 1
 *           fi
 *
 *       - name: 빌드 결과물 저장
 *         uses: actions/upload-artifact@v4
 *         with:
 *           name: dist
 *           path: dist/
 *           retention-days: 3
 *
 *   # === 프로덕션 배포 ===
 *   deploy:
 *     name: 프로덕션 배포
 *     runs-on: ubuntu-latest
 *     needs: [test, build]
 *     if: github.ref == 'refs/heads/main' && github.event_name == 'push'
 *     environment:
 *       name: production
 *       url: https://app.example.com
 *     steps:
 *       - uses: actions/checkout@v4
 *
 *       - name: 빌드 결과물 다운로드
 *         uses: actions/download-artifact@v4
 *         with:
 *           name: dist
 *           path: dist/
 *
 *       - name: Vercel 배포
 *         uses: amondnet/vercel-action@v25
 *         with:
 *           vercel-token: ${{ secrets.VERCEL_TOKEN }}
 *           vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
 *           vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
 *           vercel-args: '--prod'
 *           working-directory: ./dist
 *
 *       - name: Sentry 릴리스
 *         uses: getsentry/action-release@v1
 *         env:
 *           SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
 *           SENTRY_ORG: my-org
 *           SENTRY_PROJECT: my-app
 *         with:
 *           environment: production
 *           version: ${{ github.sha }}
 *           sourcemaps: './dist/assets/js'
 *
 *       - name: 배포 완료 알림
 *         if: success()
 *         uses: 8398a7/action-slack@v3
 *         with:
 *           status: ${{ job.status }}
 *           text: '프로덕션 배포 완료! :rocket:'
 *         env:
 *           SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
 * ```
 */

// ============================================================
// 문제 3 답안: 에러 모니터링 + 환경 관리 시스템
// ============================================================

/**
 * 환경 변수 파일들:
 *
 * ```
 * # .env (공통)
 * VITE_APP_NAME=MyApp
 *
 * # .env.development
 * VITE_API_URL=http://localhost:3001/api
 * VITE_SENTRY_DSN=
 * VITE_ENABLE_MOCK=true
 * VITE_LOG_LEVEL=debug
 *
 * # .env.staging
 * VITE_API_URL=https://stg-api.example.com/api
 * VITE_SENTRY_DSN=https://abc@o123.ingest.sentry.io/456
 * VITE_ENABLE_MOCK=false
 * VITE_LOG_LEVEL=info
 *
 * # .env.production
 * VITE_API_URL=https://api.example.com/api
 * VITE_SENTRY_DSN=https://def@o123.ingest.sentry.io/789
 * VITE_ENABLE_MOCK=false
 * VITE_LOG_LEVEL=error
 * ```
 */

/**
 * 타입 안전한 환경 변수 유틸리티 (src/lib/env.ts)
 *
 * ```ts
 * // src/vite-env.d.ts
 * interface ImportMetaEnv {
 *   readonly VITE_APP_NAME: string;
 *   readonly VITE_API_URL: string;
 *   readonly VITE_SENTRY_DSN: string;
 *   readonly VITE_ENABLE_MOCK: string;
 *   readonly VITE_LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error';
 *   readonly VITE_APP_VERSION?: string;
 * }
 *
 * interface ImportMeta {
 *   readonly env: ImportMetaEnv;
 * }
 *
 * // src/lib/env.ts
 * function getEnvVar(key: keyof ImportMetaEnv, required = true): string {
 *   const value = import.meta.env[key];
 *   if (required && !value) {
 *     throw new Error(`환경 변수 ${key}가 설정되지 않았습니다.`);
 *   }
 *   return value ?? '';
 * }
 *
 * export const env = {
 *   appName: getEnvVar('VITE_APP_NAME'),
 *   apiUrl: getEnvVar('VITE_API_URL'),
 *   sentryDsn: getEnvVar('VITE_SENTRY_DSN', false),
 *   enableMock: getEnvVar('VITE_ENABLE_MOCK', false) === 'true',
 *   logLevel: getEnvVar('VITE_LOG_LEVEL', false) || 'info',
 *   appVersion: getEnvVar('VITE_APP_VERSION', false) || 'dev',
 *   isDev: import.meta.env.DEV,
 *   isProd: import.meta.env.PROD,
 *   mode: import.meta.env.MODE,
 * } as const;
 *
 * // 개발 환경에서 환경 변수 확인용
 * if (import.meta.env.DEV) {
 *   console.log('[ENV]', env);
 * }
 * ```
 */

/**
 * Sentry 초기화 (src/lib/sentry.ts)
 *
 * ```ts
 * import * as Sentry from '@sentry/react';
 * import { env } from './env';
 *
 * export function initSentry() {
 *   if (!env.sentryDsn) {
 *     console.log('[Sentry] DSN이 설정되지 않아 초기화를 건너뜁니다.');
 *     return;
 *   }
 *
 *   Sentry.init({
 *     dsn: env.sentryDsn,
 *     environment: env.mode,
 *     release: `${env.appName}@${env.appVersion}`,
 *     enabled: env.isProd || env.mode === 'staging',
 *
 *     integrations: [
 *       // 성능 모니터링
 *       Sentry.browserTracingIntegration({
 *         tracePropagationTargets: [
 *           'localhost',
 *           /^https:\/\/api\.example\.com/,
 *         ],
 *       }),
 *
 *       // 세션 리플레이
 *       Sentry.replayIntegration({
 *         maskAllText: true,
 *         blockAllMedia: true,
 *       }),
 *     ],
 *
 *     // 샘플링 설정
 *     tracesSampleRate: env.isProd ? 0.1 : 1.0,
 *     replaysSessionSampleRate: 0.1,
 *     replaysOnErrorSampleRate: 1.0,
 *
 *     // 에러 필터링
 *     beforeSend(event, hint) {
 *       const error = hint?.originalException;
 *
 *       // 무시할 에러 패턴
 *       const ignoredErrors = [
 *         'ResizeObserver loop',
 *         'Network request failed',
 *         'Load failed',
 *       ];
 *
 *       if (error instanceof Error) {
 *         if (ignoredErrors.some(msg => error.message.includes(msg))) {
 *           return null;
 *         }
 *       }
 *
 *       return event;
 *     },
 *
 *     // 브레드크럼 필터링
 *     beforeBreadcrumb(breadcrumb) {
 *       // 콘솔 로그 중 debug 레벨은 제외
 *       if (breadcrumb.category === 'console' && breadcrumb.level === 'debug') {
 *         return null;
 *       }
 *       return breadcrumb;
 *     },
 *   });
 * }
 *
 * // 사용자 정보 설정
 * export function setSentryUser(user: { id: string; email: string; role: string }) {
 *   Sentry.setUser({
 *     id: user.id,
 *     email: user.email,
 *     role: user.role,
 *   });
 * }
 *
 * // 사용자 정보 제거 (로그아웃 시)
 * export function clearSentryUser() {
 *   Sentry.setUser(null);
 * }
 *
 * // 커스텀 컨텍스트 추가
 * export function setSentryContext(name: string, data: Record<string, unknown>) {
 *   Sentry.setContext(name, data);
 * }
 *
 * // 수동 에러 보고
 * export function captureError(error: Error, context?: Record<string, unknown>) {
 *   Sentry.captureException(error, {
 *     extra: context,
 *   });
 * }
 * ```
 */

/**
 * Sentry Error Boundary (src/components/ErrorBoundary.tsx)
 *
 * ```tsx
 * import * as Sentry from '@sentry/react';
 * import { useNavigate } from 'react-router-dom';
 *
 * function ErrorFallback({
 *   error,
 *   resetError,
 * }: {
 *   error: Error;
 *   resetError: () => void;
 * }) {
 *   const navigate = useNavigate();
 *
 *   return (
 *     <div role="alert" style={{ padding: '40px', textAlign: 'center' }}>
 *       <h1>예기치 않은 오류가 발생했습니다</h1>
 *       <p style={{ color: '#666' }}>
 *         문제가 자동으로 보고되었습니다. 잠시 후 다시 시도해주세요.
 *       </p>
 *       {import.meta.env.DEV && (
 *         <pre style={{ textAlign: 'left', background: '#f5f5f5', padding: '16px' }}>
 *           {error.message}
 *           {'\n'}
 *           {error.stack}
 *         </pre>
 *       )}
 *       <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
 *         <button onClick={resetError}>다시 시도</button>
 *         <button onClick={() => navigate('/')}>홈으로 이동</button>
 *       </div>
 *     </div>
 *   );
 * }
 *
 * export function AppErrorBoundary({ children }: { children: React.ReactNode }) {
 *   return (
 *     <Sentry.ErrorBoundary
 *       fallback={({ error, resetError }) => (
 *         <ErrorFallback error={error} resetError={resetError} />
 *       )}
 *       beforeCapture={(scope) => {
 *         scope.setTag('boundary', 'app-root');
 *         scope.setLevel('fatal');
 *       }}
 *     >
 *       {children}
 *     </Sentry.ErrorBoundary>
 *   );
 * }
 * ```
 */

/**
 * 앱 진입점 (src/main.tsx)
 *
 * ```tsx
 * import React from 'react';
 * import ReactDOM from 'react-dom/client';
 * import { initSentry } from './lib/sentry';
 * import { AppErrorBoundary } from './components/ErrorBoundary';
 * import { App } from './App';
 *
 * // 1. Sentry 초기화 (가장 먼저)
 * initSentry();
 *
 * // 2. 앱 렌더링
 * ReactDOM.createRoot(document.getElementById('root')!).render(
 *   <React.StrictMode>
 *     <AppErrorBoundary>
 *       <App />
 *     </AppErrorBoundary>
 *   </React.StrictMode>
 * );
 * ```
 */

/**
 * package.json 스크립트:
 *
 * ```json
 * {
 *   "scripts": {
 *     "dev": "vite",
 *     "build": "tsc --noEmit && vite build",
 *     "build:staging": "tsc --noEmit && vite build --mode staging",
 *     "build:analyze": "ANALYZE=true vite build",
 *     "preview": "vite preview",
 *     "lint": "eslint src --ext .ts,.tsx --max-warnings 0",
 *     "type-check": "tsc --noEmit",
 *     "test": "vitest run",
 *     "test:watch": "vitest",
 *     "test:coverage": "vitest run --coverage"
 *   }
 * }
 * ```
 */

// 시각적 요약 컴포넌트 (학습용)
export function BuildPipelineSummary() {
  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <h1>빌드 & 배포 파이프라인 구성 완료</h1>

      <section>
        <h2>최적화 결과</h2>
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>항목</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>최적화 전</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>최적화 후</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>총 번들 크기</td>
              <td style={{ border: '1px solid #ddd', padding: '8px', color: 'red' }}>1,200KB</td>
              <td style={{ border: '1px solid #ddd', padding: '8px', color: 'green' }}>~420KB</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>gzip 크기</td>
              <td style={{ border: '1px solid #ddd', padding: '8px', color: 'red' }}>~380KB</td>
              <td style={{ border: '1px solid #ddd', padding: '8px', color: 'green' }}>~140KB</td>
            </tr>
            <tr>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>청크 수</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>1 (단일 번들)</td>
              <td style={{ border: '1px solid #ddd', padding: '8px' }}>6+ (최적 분할)</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default BuildPipelineSummary;
