/**
 * 챕터 03 - 예제 2: 코드 스플리팅과 지연 로딩 패턴
 *
 * React.lazy, Suspense, dynamic import를 활용한
 * 다양한 코드 스플리팅 패턴을 보여줍니다.
 *
 * 실행 방법:
 *   npx tsx practice/example-02.tsx
 *
 * 브라우저에서 실제 코드 스플리팅을 테스트하려면:
 *   Vite 또는 Webpack 번들러 환경에서 실행하세요.
 */

import React, { Suspense, ComponentType, useState, useEffect, useCallback } from "react";

// ============================================================
// 1. 기본 코드 스플리팅 패턴
// ============================================================

/**
 * 패턴 1: 라우트 기반 코드 스플리팅
 *
 * 각 페이지를 별도 청크로 분리하여 초기 로딩 시간을 줄입니다.
 * 사용자가 해당 페이지에 접근할 때만 해당 청크를 다운로드합니다.
 */

// 예시 (실제 프로젝트에서의 사용법):
// const Home = React.lazy(() => import('./pages/Home'));
// const Dashboard = React.lazy(() => import('./pages/Dashboard'));
// const Settings = React.lazy(() => import('./pages/Settings'));

// ============================================================
// 2. 프리로딩(Preloading) 패턴
// ============================================================

/**
 * 패턴 2: 프리로딩 가능한 lazy 컴포넌트
 *
 * 사용자가 링크 위에 마우스를 올렸을 때(hover) 미리 로딩을 시작하여
 * 실제 네비게이션 시 즉시 표시할 수 있습니다.
 */
interface LazyWithPreload<T extends ComponentType<any>> {
  Component: React.LazyExoticComponent<T>;
  preload: () => Promise<{ default: T }>;
}

function lazyWithPreload<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>
): LazyWithPreload<T> {
  let modulePromise: Promise<{ default: T }> | null = null;

  const lazyComponent = React.lazy(() => {
    // 이미 프리로딩이 시작되었으면 해당 Promise 재사용
    if (modulePromise) return modulePromise;
    modulePromise = factory();
    return modulePromise;
  });

  return {
    Component: lazyComponent,
    preload: () => {
      if (!modulePromise) {
        modulePromise = factory();
      }
      return modulePromise;
    },
  };
}

// ============================================================
// 3. 재시도(Retry) 패턴
// ============================================================

/**
 * 패턴 3: 로딩 실패 시 자동 재시도
 *
 * 네트워크 오류로 청크 로딩이 실패할 수 있습니다.
 * 자동 재시도와 수동 재시도를 모두 지원합니다.
 */
function lazyWithRetry<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>,
  maxRetries: number = 3,
  retryDelay: number = 1000
): React.LazyExoticComponent<T> {
  return React.lazy(async () => {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await factory();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        console.warn(
          `[LazyRetry] 로딩 실패 (시도 ${attempt + 1}/${maxRetries + 1}): ${lastError.message}`
        );

        if (attempt < maxRetries) {
          // 지수 백오프로 대기
          const delay = retryDelay * Math.pow(2, attempt);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError;
  });
}

// ============================================================
// 4. 조건부 로딩 패턴
// ============================================================

/**
 * 패턴 4: 기능 플래그 기반 조건부 로딩
 *
 * 특정 조건(기능 플래그, 사용자 권한 등)에 따라
 * 다른 컴포넌트를 동적으로 로딩합니다.
 */
interface ConditionalImportOptions<T extends ComponentType<any>> {
  condition: boolean;
  importTrue: () => Promise<{ default: T }>;
  importFalse: () => Promise<{ default: T }>;
}

function useLazyConditional<T extends ComponentType<any>>(
  options: ConditionalImportOptions<T>
): React.LazyExoticComponent<T> {
  const { condition, importTrue, importFalse } = options;
  // 조건에 따라 다른 모듈을 동적으로 import
  return React.lazy(() => (condition ? importTrue() : importFalse()));
}

// ============================================================
// 5. 번들 분석 유틸리티
// ============================================================

/**
 * 청크 크기 시뮬레이션 및 분석
 * 실제 프로젝트에서는 webpack-bundle-analyzer나 vite의 visualizer를 사용합니다.
 */
interface ChunkInfo {
  name: string;
  size: number; // KB
  isLazy: boolean;
  route?: string;
}

interface BundleAnalysis {
  totalSize: number;
  initialSize: number;
  lazySize: number;
  chunks: ChunkInfo[];
}

function analyzeBundles(chunks: ChunkInfo[]): BundleAnalysis {
  const totalSize = chunks.reduce((sum, c) => sum + c.size, 0);
  const initialSize = chunks
    .filter((c) => !c.isLazy)
    .reduce((sum, c) => sum + c.size, 0);
  const lazySize = chunks
    .filter((c) => c.isLazy)
    .reduce((sum, c) => sum + c.size, 0);

  return { totalSize, initialSize, lazySize, chunks };
}

/**
 * 로딩 시간 시뮬레이터
 * 번들 크기와 네트워크 속도에 따른 로딩 시간을 추정합니다.
 */
interface NetworkProfile {
  name: string;
  downloadSpeed: number; // KB/s
  latency: number; // ms
}

const networkProfiles: NetworkProfile[] = [
  { name: "Fast 3G", downloadSpeed: 187, latency: 562 },
  { name: "Slow 4G", downloadSpeed: 500, latency: 200 },
  { name: "4G", downloadSpeed: 4000, latency: 100 },
  { name: "WiFi", downloadSpeed: 30000, latency: 10 },
];

function estimateLoadTime(
  sizeKB: number,
  network: NetworkProfile
): number {
  return network.latency + (sizeKB / network.downloadSpeed) * 1000;
}

// ============================================================
// 6. 데모 실행
// ============================================================

console.log("╔══════════════════════════════════════════════════════════╗");
console.log("║ 코드 스플리팅과 지연 로딩 패턴                           ║");
console.log("╚══════════════════════════════════════════════════════════╝\n");

// --- 번들 분석 시뮬레이션 ---
console.log("=== 번들 분석 시뮬레이션 ===\n");

const chunks: ChunkInfo[] = [
  { name: "main.js", size: 150, isLazy: false },
  { name: "vendor.js", size: 200, isLazy: false },
  { name: "react.js", size: 45, isLazy: false },
  { name: "dashboard.chunk.js", size: 120, isLazy: true, route: "/dashboard" },
  { name: "settings.chunk.js", size: 80, isLazy: true, route: "/settings" },
  { name: "reports.chunk.js", size: 250, isLazy: true, route: "/reports" },
  { name: "admin.chunk.js", size: 180, isLazy: true, route: "/admin" },
  { name: "charts.chunk.js", size: 300, isLazy: true, route: "/reports" },
];

const analysis = analyzeBundles(chunks);

console.log("코드 스플리팅 전:");
console.log(`  전체 번들: ${analysis.totalSize}KB (단일 파일)\n`);

console.log("코드 스플리팅 후:");
console.log(`  초기 로딩: ${analysis.initialSize}KB`);
console.log(`  지연 로딩: ${analysis.lazySize}KB`);
console.log(`  초기 번들 크기 절감: ${((1 - analysis.initialSize / analysis.totalSize) * 100).toFixed(1)}%\n`);

console.log("청크 상세:");
chunks.forEach((chunk) => {
  const type = chunk.isLazy ? "🔵 Lazy" : "🟢 Initial";
  const route = chunk.route ? ` (${chunk.route})` : "";
  console.log(`  ${type} ${chunk.name}: ${chunk.size}KB${route}`);
});

// --- 네트워크별 로딩 시간 비교 ---
console.log("\n\n=== 네트워크별 초기 로딩 시간 비교 ===\n");

console.log("┌───────────┬──────────────────┬──────────────────┬──────────┐");
console.log("│ 네트워크  │ 전체 번들 (ms)   │ 코드 스플리팅 (ms)│ 절감    │");
console.log("├───────────┼──────────────────┼──────────────────┼──────────┤");

networkProfiles.forEach((profile) => {
  const fullTime = estimateLoadTime(analysis.totalSize, profile);
  const splitTime = estimateLoadTime(analysis.initialSize, profile);
  const saving = ((1 - splitTime / fullTime) * 100).toFixed(0);
  console.log(
    `│ ${profile.name.padEnd(9)} │ ${String(Math.round(fullTime)).padStart(14)}ms │ ${String(Math.round(splitTime)).padStart(14)}ms │ ${String(saving).padStart(5)}%  │`
  );
});

console.log("└───────────┴──────────────────┴──────────────────┴──────────┘");

// --- 프리로딩 효과 ---
console.log("\n\n=== 프리로딩 효과 시뮬레이션 ===\n");

const dashboardChunk = chunks.find((c) => c.name === "dashboard.chunk.js")!;

console.log("시나리오: 사용자가 Dashboard 링크 클릭\n");

networkProfiles.forEach((profile) => {
  const loadTime = estimateLoadTime(dashboardChunk.size, profile);
  console.log(`[${profile.name}]`);
  console.log(`  프리로딩 없음: 클릭 → ${Math.round(loadTime)}ms 대기 → 페이지 표시`);
  console.log(`  프리로딩 적용: 클릭 → 즉시 표시 (hover 시 미리 로드 완료)`);
  console.log();
});

// --- 패턴 요약 ---
console.log("\n=== 코드 스플리팅 패턴 요약 ===\n");
console.log(`
┌────────────────────────┬────────────────────────────────────────────┐
│ 패턴                   │ 사용 시점                                  │
├────────────────────────┼────────────────────────────────────────────┤
│ 라우트 기반            │ 모든 SPA의 기본 전략                       │
│ 프리로딩               │ 네비게이션 UX 개선 (hover/focus 시)        │
│ 재시도                 │ 불안정한 네트워크 환경                      │
│ 조건부 로딩            │ A/B 테스트, 기능 플래그, 권한 기반          │
│ 컴포넌트 레벨          │ 무거운 모달, 차트, 에디터                   │
└────────────────────────┴────────────────────────────────────────────┘
`);

console.log("=== React 사용 예시 ===\n");
console.log(`
// 1. 프리로딩 가능한 lazy 컴포넌트
const Dashboard = lazyWithPreload(() => import('./Dashboard'));

function NavLink() {
  return (
    <Link
      to="/dashboard"
      onMouseEnter={() => Dashboard.preload()}  // hover 시 프리로드
      onFocus={() => Dashboard.preload()}       // 포커스 시 프리로드
    >
      Dashboard
    </Link>
  );
}

// 2. 재시도 가능한 lazy 컴포넌트
const HeavyChart = lazyWithRetry(
  () => import('./HeavyChart'),
  3,      // 최대 3회 재시도
  1000    // 1초 간격 (지수 백오프)
);

// 3. Suspense + Error Boundary 조합
function App() {
  return (
    <ErrorBoundary fallback={<ErrorPage />}>
      <Suspense fallback={<PageSkeleton />}>
        <Dashboard.Component />
      </Suspense>
    </ErrorBoundary>
  );
}
`);

console.log("✅ 코드 스플리팅 패턴 데모 완료!");

export {
  lazyWithPreload,
  lazyWithRetry,
  analyzeBundles,
  estimateLoadTime,
  ChunkInfo,
  BundleAnalysis,
  NetworkProfile,
};
