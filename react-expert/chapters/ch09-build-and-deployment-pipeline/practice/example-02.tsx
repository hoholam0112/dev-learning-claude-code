/**
 * 챕터 09 - 예제 02: GitHub Actions CI/CD 워크플로우
 *
 * 이 예제는 GitHub Actions를 활용한 완전한 CI/CD 파이프라인을 보여줍니다.
 *
 * 실행 방법:
 *   1. 프로젝트 루트에 .github/workflows/ 디렉토리 생성:
 *      mkdir -p .github/workflows
 *
 *   2. 아래 YAML 코드를 .github/workflows/ci.yml로 저장
 *
 *   3. GitHub 저장소에 push하면 자동으로 실행:
 *      git add .github/workflows/ci.yml
 *      git commit -m "ci: add CI/CD pipeline"
 *      git push origin main
 *
 *   4. GitHub Actions 탭에서 실행 결과 확인
 *
 * 참고: 이 파일은 .tsx 확장자이지만, 실제 내용은 YAML 워크플로우 설정과
 *       관련 설정 파일들을 문서화한 학습용 파일입니다.
 */

import React from 'react';

// ============================================================
// 1. CI/CD 메인 워크플로우 (.github/workflows/ci.yml)
// ============================================================

/**
 * ```yaml
 * name: CI/CD Pipeline
 *
 * # 트리거 조건
 * on:
 *   push:
 *     branches: [main, develop]
 *   pull_request:
 *     branches: [main]
 *
 * # 동시 실행 제어 (같은 브랜치의 이전 실행 취소)
 * concurrency:
 *   group: ${{ github.workflow }}-${{ github.ref }}
 *   cancel-in-progress: true
 *
 * # 환경 변수
 * env:
 *   NODE_VERSION: '20'
 *   PNPM_VERSION: '9'
 *
 * jobs:
 *   # ========================================
 *   # Job 1: 린트 + 타입 검사
 *   # ========================================
 *   lint-and-typecheck:
 *     name: 린트 & 타입 검사
 *     runs-on: ubuntu-latest
 *     timeout-minutes: 10
 *
 *     steps:
 *       - name: 코드 체크아웃
 *         uses: actions/checkout@v4
 *
 *       - name: pnpm 설치
 *         uses: pnpm/action-setup@v4
 *         with:
 *           version: ${{ env.PNPM_VERSION }}
 *
 *       - name: Node.js 설정
 *         uses: actions/setup-node@v4
 *         with:
 *           node-version: ${{ env.NODE_VERSION }}
 *           cache: 'pnpm'
 *
 *       - name: 의존성 설치
 *         run: pnpm install --frozen-lockfile
 *
 *       - name: ESLint 실행
 *         run: pnpm lint
 *
 *       - name: TypeScript 타입 검사
 *         run: pnpm type-check
 *
 *   # ========================================
 *   # Job 2: 단위 + 통합 테스트
 *   # ========================================
 *   test:
 *     name: 테스트
 *     runs-on: ubuntu-latest
 *     timeout-minutes: 15
 *     needs: [lint-and-typecheck]
 *
 *     steps:
 *       - name: 코드 체크아웃
 *         uses: actions/checkout@v4
 *
 *       - name: pnpm 설치
 *         uses: pnpm/action-setup@v4
 *         with:
 *           version: ${{ env.PNPM_VERSION }}
 *
 *       - name: Node.js 설정
 *         uses: actions/setup-node@v4
 *         with:
 *           node-version: ${{ env.NODE_VERSION }}
 *           cache: 'pnpm'
 *
 *       - name: 의존성 설치
 *         run: pnpm install --frozen-lockfile
 *
 *       - name: 테스트 실행 (커버리지 포함)
 *         run: pnpm test:coverage
 *
 *       - name: 커버리지 리포트 업로드
 *         uses: actions/upload-artifact@v4
 *         if: always()
 *         with:
 *           name: coverage-report
 *           path: coverage/
 *           retention-days: 7
 *
 *       - name: 커버리지 코멘트 (PR)
 *         if: github.event_name == 'pull_request'
 *         uses: davelosert/vitest-coverage-report-action@v2
 *
 *   # ========================================
 *   # Job 3: 빌드 + 번들 크기 검사
 *   # ========================================
 *   build:
 *     name: 빌드 & 번들 검사
 *     runs-on: ubuntu-latest
 *     timeout-minutes: 10
 *     needs: [lint-and-typecheck]
 *
 *     steps:
 *       - name: 코드 체크아웃
 *         uses: actions/checkout@v4
 *
 *       - name: pnpm 설치
 *         uses: pnpm/action-setup@v4
 *         with:
 *           version: ${{ env.PNPM_VERSION }}
 *
 *       - name: Node.js 설정
 *         uses: actions/setup-node@v4
 *         with:
 *           node-version: ${{ env.NODE_VERSION }}
 *           cache: 'pnpm'
 *
 *       - name: 의존성 설치
 *         run: pnpm install --frozen-lockfile
 *
 *       - name: 프로덕션 빌드
 *         run: pnpm build
 *         env:
 *           VITE_APP_VERSION: ${{ github.sha }}
 *
 *       - name: 번들 크기 검사
 *         run: |
 *           echo "=== 번들 크기 리포트 ==="
 *           du -sh dist/
 *           echo ""
 *           echo "=== JS 파일 크기 ==="
 *           find dist -name "*.js" -exec du -sh {} \;
 *           echo ""
 *           echo "=== CSS 파일 크기 ==="
 *           find dist -name "*.css" -exec du -sh {} \;
 *
 *       - name: 번들 크기 예산 검사
 *         run: |
 *           TOTAL_SIZE=$(du -sb dist/assets/ | cut -f1)
 *           MAX_SIZE=$((500 * 1024))  # 500KB
 *           echo "총 에셋 크기: $((TOTAL_SIZE / 1024))KB"
 *           echo "예산: $((MAX_SIZE / 1024))KB"
 *           if [ "$TOTAL_SIZE" -gt "$MAX_SIZE" ]; then
 *             echo "::error::번들 크기 예산 초과!"
 *             exit 1
 *           fi
 *           echo "번들 크기 검사 통과!"
 *
 *       - name: 빌드 결과물 업로드
 *         uses: actions/upload-artifact@v4
 *         with:
 *           name: build-output
 *           path: dist/
 *           retention-days: 3
 *
 *   # ========================================
 *   # Job 4: 스테이징 배포 (PR)
 *   # ========================================
 *   deploy-staging:
 *     name: 스테이징 배포
 *     runs-on: ubuntu-latest
 *     needs: [test, build]
 *     if: github.event_name == 'pull_request'
 *     environment:
 *       name: staging
 *       url: ${{ steps.deploy.outputs.preview-url }}
 *
 *     steps:
 *       - name: 빌드 결과물 다운로드
 *         uses: actions/download-artifact@v4
 *         with:
 *           name: build-output
 *           path: dist/
 *
 *       - name: Vercel 프리뷰 배포
 *         id: deploy
 *         uses: amondnet/vercel-action@v25
 *         with:
 *           vercel-token: ${{ secrets.VERCEL_TOKEN }}
 *           vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
 *           vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
 *           working-directory: ./dist
 *
 *       - name: PR에 프리뷰 URL 코멘트
 *         uses: actions/github-script@v7
 *         with:
 *           script: |
 *             github.rest.issues.createComment({
 *               issue_number: context.issue.number,
 *               owner: context.repo.owner,
 *               repo: context.repo.repo,
 *               body: `## 스테이징 배포 완료\n\n프리뷰: ${{ steps.deploy.outputs.preview-url }}`
 *             })
 *
 *   # ========================================
 *   # Job 5: 프로덕션 배포 (main 브랜치)
 *   # ========================================
 *   deploy-production:
 *     name: 프로덕션 배포
 *     runs-on: ubuntu-latest
 *     needs: [test, build]
 *     if: github.ref == 'refs/heads/main' && github.event_name == 'push'
 *     environment:
 *       name: production
 *       url: https://app.example.com
 *
 *     steps:
 *       - name: 코드 체크아웃
 *         uses: actions/checkout@v4
 *
 *       - name: 빌드 결과물 다운로드
 *         uses: actions/download-artifact@v4
 *         with:
 *           name: build-output
 *           path: dist/
 *
 *       - name: Vercel 프로덕션 배포
 *         uses: amondnet/vercel-action@v25
 *         with:
 *           vercel-token: ${{ secrets.VERCEL_TOKEN }}
 *           vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
 *           vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
 *           vercel-args: '--prod'
 *           working-directory: ./dist
 *
 *       - name: Sentry 릴리스 생성
 *         uses: getsentry/action-release@v1
 *         env:
 *           SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
 *           SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
 *           SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
 *         with:
 *           environment: production
 *           version: ${{ github.sha }}
 *           sourcemaps: './dist/assets'
 *
 *       - name: Slack 알림
 *         if: always()
 *         uses: 8398a7/action-slack@v3
 *         with:
 *           status: ${{ job.status }}
 *           fields: repo,message,commit,author,action,workflow
 *         env:
 *           SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
 * ```
 */

// ============================================================
// 2. PR 자동 라벨링 (.github/workflows/labeler.yml)
// ============================================================

/**
 * ```yaml
 * name: PR Labeler
 * on:
 *   pull_request:
 *     types: [opened, synchronize]
 *
 * jobs:
 *   label:
 *     runs-on: ubuntu-latest
 *     steps:
 *       - uses: actions/labeler@v5
 *         with:
 *           repo-token: ${{ secrets.GITHUB_TOKEN }}
 * ```
 *
 * .github/labeler.yml:
 * ```yaml
 * # 파일 경로 기반 자동 라벨링
 * frontend:
 *   - 'src/**'
 * testing:
 *   - '**/*.test.ts'
 *   - '**/*.test.tsx'
 * ci/cd:
 *   - '.github/**'
 * documentation:
 *   - '**/*.md'
 * dependencies:
 *   - 'package.json'
 *   - 'pnpm-lock.yaml'
 * ```
 */

// ============================================================
// 3. 의존성 자동 업데이트 (Dependabot)
// ============================================================

/**
 * .github/dependabot.yml:
 *
 * ```yaml
 * version: 2
 * updates:
 *   # npm 패키지 업데이트
 *   - package-ecosystem: "npm"
 *     directory: "/"
 *     schedule:
 *       interval: "weekly"
 *       day: "monday"
 *     open-pull-requests-limit: 10
 *     groups:
 *       # React 관련 패키지를 하나의 PR로
 *       react:
 *         patterns:
 *           - "react*"
 *           - "@types/react*"
 *       # 테스트 도구를 하나의 PR로
 *       testing:
 *         patterns:
 *           - "vitest*"
 *           - "@testing-library/*"
 *       # 린트/포맷 도구를 하나의 PR로
 *       linting:
 *         patterns:
 *           - "eslint*"
 *           - "prettier*"
 *     labels:
 *       - "dependencies"
 *       - "automated"
 *
 *   # GitHub Actions 업데이트
 *   - package-ecosystem: "github-actions"
 *     directory: "/"
 *     schedule:
 *       interval: "weekly"
 *     labels:
 *       - "ci/cd"
 *       - "automated"
 * ```
 */

// ============================================================
// 4. Docker 멀티 스테이지 빌드 (선택사항)
// ============================================================

/**
 * Dockerfile:
 *
 * ```dockerfile
 * # 1단계: 빌드
 * FROM node:20-alpine AS builder
 *
 * WORKDIR /app
 *
 * # 의존성 캐시 활용
 * COPY package.json pnpm-lock.yaml ./
 * RUN corepack enable && pnpm install --frozen-lockfile
 *
 * # 소스 코드 복사 및 빌드
 * COPY . .
 * ARG VITE_API_URL
 * ARG VITE_APP_VERSION
 * RUN pnpm build
 *
 * # 2단계: 서빙
 * FROM nginx:alpine AS production
 *
 * # nginx 설정
 * COPY nginx.conf /etc/nginx/conf.d/default.conf
 *
 * # 빌드 결과물만 복사
 * COPY --from=builder /app/dist /usr/share/nginx/html
 *
 * # 헬스 체크
 * HEALTHCHECK --interval=30s --timeout=3s \
 *   CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1
 *
 * EXPOSE 80
 * CMD ["nginx", "-g", "daemon off;"]
 * ```
 *
 * nginx.conf:
 * ```nginx
 * server {
 *     listen 80;
 *     server_name _;
 *     root /usr/share/nginx/html;
 *     index index.html;
 *
 *     # SPA 라우팅 지원
 *     location / {
 *         try_files $uri $uri/ /index.html;
 *     }
 *
 *     # 정적 에셋 캐싱 (해시 파일명)
 *     location /assets/ {
 *         expires 1y;
 *         add_header Cache-Control "public, immutable";
 *     }
 *
 *     # gzip 압축
 *     gzip on;
 *     gzip_types text/plain application/json application/javascript text/css;
 *     gzip_min_length 1024;
 *
 *     # 보안 헤더
 *     add_header X-Frame-Options "SAMEORIGIN" always;
 *     add_header X-Content-Type-Options "nosniff" always;
 *     add_header X-XSS-Protection "1; mode=block" always;
 * }
 * ```
 */

// ============================================================
// 5. 시각화: CI/CD 파이프라인 요약 컴포넌트
// ============================================================

/**
 * CI/CD 파이프라인 개요를 보여주는 컴포넌트 (학습용)
 */
export function CIPipelineOverview() {
  const stages = [
    {
      name: '린트 & 타입 검사',
      duration: '~2분',
      tools: ['ESLint', 'TypeScript'],
      status: 'success' as const,
    },
    {
      name: '테스트',
      duration: '~5분',
      tools: ['Vitest', 'React Testing Library'],
      status: 'success' as const,
    },
    {
      name: '빌드 & 번들 검사',
      duration: '~3분',
      tools: ['Vite', 'Rollup'],
      status: 'success' as const,
    },
    {
      name: '스테이징 배포',
      duration: '~2분',
      tools: ['Vercel'],
      status: 'pending' as const,
    },
    {
      name: '프로덕션 배포',
      duration: '~2분',
      tools: ['Vercel', 'Sentry'],
      status: 'waiting' as const,
    },
  ];

  const statusStyles = {
    success: { background: '#4CAF50', color: 'white' },
    pending: { background: '#FF9800', color: 'white' },
    waiting: { background: '#9E9E9E', color: 'white' },
    failed: { background: '#f44336', color: 'white' },
  };

  const statusLabels = {
    success: '완료',
    pending: '진행 중',
    waiting: '대기',
    failed: '실패',
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '24px' }}>
      <h2>CI/CD 파이프라인</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {stages.map((stage, index) => (
          <div
            key={stage.name}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              padding: '12px 16px',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
            }}
          >
            <span
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                fontWeight: 'bold',
                ...statusStyles[stage.status],
              }}
            >
              {index + 1}
            </span>
            <div style={{ flex: 1 }}>
              <strong>{stage.name}</strong>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {stage.tools.join(', ')} | {stage.duration}
              </div>
            </div>
            <span
              style={{
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '12px',
                ...statusStyles[stage.status],
              }}
            >
              {statusLabels[stage.status]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CIPipelineOverview;
