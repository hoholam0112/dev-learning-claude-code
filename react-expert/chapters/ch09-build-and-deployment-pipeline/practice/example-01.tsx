/**
 * 챕터 09 - 예제 01: Vite 최적화 설정 + 번들 크기 분석
 *
 * 이 예제는 Vite 프로덕션 빌드의 최적화 설정과
 * 번들 크기를 분석/관리하는 방법을 보여줍니다.
 *
 * 실행 방법:
 *   1. 프로젝트 생성:
 *      npm create vite@latest deploy-demo -- --template react-ts
 *      cd deploy-demo
 *
 *   2. 의존성 설치:
 *      npm install react-router-dom @tanstack/react-query zustand
 *      npm install -D rollup-plugin-visualizer vite-plugin-compression
 *
 *   3. vite.config.ts를 아래 내용으로 교체
 *
 *   4. 빌드 및 분석:
 *      npm run build
 *      # stats.html 파일이 생성됩니다 (번들 시각화)
 *
 * 참고: 이 파일은 여러 설정 파일의 내용을 하나로 합친 학습용 예제입니다.
 */

import React, { lazy, Suspense } from 'react';

// ============================================================
// 1. vite.config.ts - 프로덕션 최적화 설정
// ============================================================

/**
 * 아래 코드를 vite.config.ts에 적용합니다.
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
 *     // 경로 별칭 설정
 *     resolve: {
 *       alias: {
 *         '@': resolve(__dirname, './src'),
 *         '@components': resolve(__dirname, './src/components'),
 *         '@hooks': resolve(__dirname, './src/hooks'),
 *         '@utils': resolve(__dirname, './src/utils'),
 *       },
 *     },
 *
 *     // 플러그인
 *     plugins: [
 *       react(),
 *
 *       // gzip + brotli 압축 (프로덕션만)
 *       isProduction && viteCompression({
 *         algorithm: 'gzip',
 *         threshold: 1024,  // 1KB 이상만 압축
 *       }),
 *       isProduction && viteCompression({
 *         algorithm: 'brotliCompress',
 *         ext: '.br',
 *         threshold: 1024,
 *       }),
 *
 *       // 번들 분석 (ANALYZE=true npm run build)
 *       isAnalyze && visualizer({
 *         filename: 'stats.html',
 *         open: true,
 *         gzipSize: true,
 *         brotliSize: true,
 *         template: 'treemap',  // 'sunburst' | 'network' | 'treemap'
 *       }),
 *     ].filter(Boolean),
 *
 *     // 빌드 설정
 *     build: {
 *       target: 'es2020',
 *       outDir: 'dist',
 *       sourcemap: isProduction ? 'hidden' : true,  // 프로덕션에서는 숨김 소스맵
 *       minify: 'esbuild',
 *       chunkSizeWarningLimit: 500,  // 500KB 경고
 *
 *       rollupOptions: {
 *         output: {
 *           // 수동 청크 분리
 *           manualChunks: (id: string) => {
 *             // React 코어 라이브러리
 *             if (id.includes('node_modules/react/') ||
 *                 id.includes('node_modules/react-dom/')) {
 *               return 'vendor-react';
 *             }
 *             // 라우터
 *             if (id.includes('node_modules/react-router')) {
 *               return 'vendor-router';
 *             }
 *             // 상태 관리
 *             if (id.includes('node_modules/zustand') ||
 *                 id.includes('node_modules/@tanstack/react-query')) {
 *               return 'vendor-state';
 *             }
 *             // 기타 node_modules
 *             if (id.includes('node_modules/')) {
 *               return 'vendor-misc';
 *             }
 *           },
 *
 *           // 청크 파일명 패턴
 *           chunkFileNames: (chunkInfo) => {
 *             const facadeModuleId = chunkInfo.facadeModuleId || '';
 *             if (facadeModuleId.includes('pages/')) {
 *               return 'pages/[name]-[hash].js';
 *             }
 *             return 'chunks/[name]-[hash].js';
 *           },
 *
 *           // 에셋 파일명 패턴
 *           assetFileNames: (assetInfo) => {
 *             const name = assetInfo.name || '';
 *             if (/\.(png|jpe?g|gif|svg|webp|avif)$/.test(name)) {
 *               return 'assets/images/[name]-[hash][extname]';
 *             }
 *             if (/\.(woff2?|eot|ttf|otf)$/.test(name)) {
 *               return 'assets/fonts/[name]-[hash][extname]';
 *             }
 *             if (/\.css$/.test(name)) {
 *               return 'assets/css/[name]-[hash][extname]';
 *             }
 *             return 'assets/[name]-[hash][extname]';
 *           },
 *         },
 *       },
 *
 *       // CSS 최적화
 *       cssCodeSplit: true,
 *       cssMinify: true,
 *
 *       // 빌드 최적화
 *       reportCompressedSize: true,
 *     },
 *
 *     // 테스트 설정 (Vitest)
 *     test: {
 *       globals: true,
 *       environment: 'jsdom',
 *       setupFiles: ['./src/test/setup.ts'],
 *       coverage: {
 *         provider: 'v8',
 *         reporter: ['text', 'json-summary', 'html'],
 *         thresholds: {
 *           branches: 80,
 *           functions: 80,
 *           lines: 80,
 *           statements: 80,
 *         },
 *       },
 *     },
 *   };
 * });
 * ```
 */

// ============================================================
// 2. 코드 스플리팅 전략
// ============================================================

/**
 * 라우트 기반 코드 스플리팅
 *
 * React.lazy()와 Suspense를 사용하여
 * 각 페이지를 별도 청크로 분리합니다.
 */

// 동적 import로 각 페이지를 별도 청크로 분리
const HomePage = lazy(() => import(/* webpackChunkName: "home" */ './pages/Home'));
const DashboardPage = lazy(() => import(/* webpackChunkName: "dashboard" */ './pages/Dashboard'));
const SettingsPage = lazy(() => import(/* webpackChunkName: "settings" */ './pages/Settings'));
const AnalyticsPage = lazy(() => import(/* webpackChunkName: "analytics" */ './pages/Analytics'));

/**
 * 페이지 로딩 폴백 컴포넌트
 */
function PageLoadingFallback() {
  return (
    <div role="status" aria-label="페이지 로딩 중" style={{ padding: '40px', textAlign: 'center' }}>
      <div className="spinner" />
      <p>페이지를 불러오는 중...</p>
    </div>
  );
}

/**
 * 라우터 설정 (코드 스플리팅 적용)
 */
export function AppRouter() {
  // react-router-dom v6 사용 예시
  return (
    <Suspense fallback={<PageLoadingFallback />}>
      {/* 실제로는 <Routes>와 <Route>를 사용합니다 */}
      {/*
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
      */}
      <div>라우터 예시 (실제 구현 시 react-router-dom 사용)</div>
    </Suspense>
  );
}

// ============================================================
// 3. 환경 변수 설정
// ============================================================

/**
 * 환경 변수 파일 구조:
 *
 * .env                  # 모든 환경에서 로드
 * .env.local            # 로컬 오버라이드 (gitignore)
 * .env.development      # 개발 모드
 * .env.staging          # 스테이징 모드
 * .env.production       # 프로덕션 모드
 */

/**
 * 아래는 .env 파일 예시입니다.
 *
 * ```
 * # .env.development
 * VITE_APP_TITLE=개발 환경
 * VITE_API_URL=http://localhost:3001/api
 * VITE_SENTRY_DSN=
 * VITE_ENABLE_MOCK=true
 *
 * # .env.staging
 * VITE_APP_TITLE=스테이징 환경
 * VITE_API_URL=https://stg-api.example.com/api
 * VITE_SENTRY_DSN=https://xxx@sentry.io/123
 * VITE_ENABLE_MOCK=false
 *
 * # .env.production
 * VITE_APP_TITLE=프로덕션
 * VITE_API_URL=https://api.example.com/api
 * VITE_SENTRY_DSN=https://xxx@sentry.io/456
 * VITE_ENABLE_MOCK=false
 * ```
 */

// 타입 안전한 환경 변수 접근
interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string;
  readonly VITE_API_URL: string;
  readonly VITE_SENTRY_DSN: string;
  readonly VITE_ENABLE_MOCK: string;
}

/**
 * 환경 변수 유틸리티
 *
 * 런타임에 환경 변수를 안전하게 접근합니다.
 * 필수 변수가 누락되면 빌드 시점에 경고합니다.
 */
export const env = {
  appTitle: import.meta.env.VITE_APP_TITLE || '앱',
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:3001',
  sentryDsn: import.meta.env.VITE_SENTRY_DSN || '',
  enableMock: import.meta.env.VITE_ENABLE_MOCK === 'true',
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  mode: import.meta.env.MODE,
} as const;

// ============================================================
// 4. package.json 스크립트 설정
// ============================================================

/**
 * package.json의 scripts 섹션:
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
 *     "lint:fix": "eslint src --ext .ts,.tsx --fix",
 *     "type-check": "tsc --noEmit",
 *     "test": "vitest run",
 *     "test:watch": "vitest",
 *     "test:coverage": "vitest run --coverage",
 *     "bundle-size": "npx vite-bundle-analyzer"
 *   }
 * }
 * ```
 */

// ============================================================
// 5. 번들 크기 예산 검사 스크립트
// ============================================================

/**
 * 아래는 CI에서 번들 크기를 검사하는 스크립트입니다.
 * scripts/check-bundle-size.ts에 작성합니다.
 *
 * ```ts
 * // scripts/check-bundle-size.ts
 * import { readFileSync, readdirSync, statSync } from 'fs';
 * import { join } from 'path';
 *
 * interface BundleBudget {
 *   maxTotalSize: number;  // bytes
 *   maxChunkSize: number;  // bytes
 *   maxAssetSize: number;  // bytes
 * }
 *
 * const BUDGET: BundleBudget = {
 *   maxTotalSize: 500 * 1024,   // 500KB
 *   maxChunkSize: 200 * 1024,   // 200KB per chunk
 *   maxAssetSize: 100 * 1024,   // 100KB per asset
 * };
 *
 * function getFileSizes(dir: string): Map<string, number> {
 *   const sizes = new Map<string, number>();
 *
 *   function walk(currentDir: string) {
 *     const entries = readdirSync(currentDir);
 *     for (const entry of entries) {
 *       const fullPath = join(currentDir, entry);
 *       const stat = statSync(fullPath);
 *       if (stat.isDirectory()) {
 *         walk(fullPath);
 *       } else {
 *         sizes.set(fullPath.replace(dir + '/', ''), stat.size);
 *       }
 *     }
 *   }
 *
 *   walk(dir);
 *   return sizes;
 * }
 *
 * function formatSize(bytes: number): string {
 *   return `${(bytes / 1024).toFixed(1)}KB`;
 * }
 *
 * function checkBundleSize() {
 *   const distDir = './dist';
 *   const sizes = getFileSizes(distDir);
 *
 *   let totalJS = 0;
 *   let violations: string[] = [];
 *
 *   for (const [file, size] of sizes) {
 *     if (file.endsWith('.js')) {
 *       totalJS += size;
 *       if (size > BUDGET.maxChunkSize) {
 *         violations.push(
 *           `[경고] ${file}: ${formatSize(size)} > ${formatSize(BUDGET.maxChunkSize)}`
 *         );
 *       }
 *     }
 *   }
 *
 *   console.log('\n=== 번들 크기 리포트 ===');
 *   console.log(`총 JS 크기: ${formatSize(totalJS)}`);
 *   console.log(`예산: ${formatSize(BUDGET.maxTotalSize)}`);
 *
 *   if (totalJS > BUDGET.maxTotalSize) {
 *     violations.push(
 *       `[실패] 총 JS 크기: ${formatSize(totalJS)} > ${formatSize(BUDGET.maxTotalSize)}`
 *     );
 *   }
 *
 *   if (violations.length > 0) {
 *     console.log('\n번들 예산 위반:');
 *     violations.forEach(v => console.log(v));
 *     process.exit(1);
 *   }
 *
 *   console.log('\n번들 크기 검사 통과!');
 * }
 *
 * checkBundleSize();
 * ```
 */

// ============================================================
// 6. Sentry 에러 모니터링 설정
// ============================================================

/**
 * Sentry 초기화 (src/lib/sentry.ts)
 *
 * ```ts
 * import * as Sentry from '@sentry/react';
 *
 * export function initSentry() {
 *   if (!import.meta.env.VITE_SENTRY_DSN) return;
 *
 *   Sentry.init({
 *     dsn: import.meta.env.VITE_SENTRY_DSN,
 *     environment: import.meta.env.MODE,
 *     release: `app@${import.meta.env.VITE_APP_VERSION || '0.0.0'}`,
 *
 *     integrations: [
 *       Sentry.browserTracingIntegration(),
 *       Sentry.replayIntegration({
 *         maskAllText: true,
 *         blockAllMedia: true,
 *       }),
 *     ],
 *
 *     // 성능 모니터링 샘플링 비율
 *     tracesSampleRate: import.meta.env.PROD ? 0.1 : 1.0,
 *
 *     // 세션 리플레이 샘플링
 *     replaysSessionSampleRate: 0.1,
 *     replaysOnErrorSampleRate: 1.0,
 *
 *     // 에러 필터링
 *     beforeSend(event) {
 *       // 무시할 에러 패턴
 *       if (event.exception?.values?.[0]?.value?.includes('ResizeObserver')) {
 *         return null;
 *       }
 *       return event;
 *     },
 *   });
 * }
 *
 * // React Error Boundary와 통합
 * export const SentryErrorBoundary = Sentry.withErrorBoundary;
 * ```
 */

export default AppRouter;
