# 챕터 09: 빌드와 배포 파이프라인

> **난이도**: ⭐⭐⭐⭐ (4/5)
> **예상 학습 시간**: 6시간
> **선수 지식**: React 프로젝트 구조, 기본 CLI 명령어, Git 기본, YAML 문법

---

## 학습 목표

이 챕터를 마치면 다음을 할 수 있습니다:

- Vite의 빌드 시스템을 깊이 이해하고 최적화 설정을 적용할 수 있습니다.
- 번들 크기를 분석하고 코드 스플리팅, 트리 쉐이킹 전략을 적용할 수 있습니다.
- GitHub Actions로 CI/CD 파이프라인을 구축할 수 있습니다.
- 환경 변수 관리, 스테이징/프로덕션 배포 전략을 설계할 수 있습니다.
- Sentry 등을 활용한 에러 모니터링 시스템을 구축할 수 있습니다.

---

## 핵심 개념

### 1. Vite 빌드 시스템 이해

Vite는 개발 시 **ESM 기반 HMR**(Hot Module Replacement)로 즉각적인 피드백을 제공하고, 프로덕션 빌드 시 **Rollup**을 사용하여 최적화된 번들을 생성합니다.

```mermaid
graph LR
    subgraph "개발 환경 (dev)"
        A["소스 코드<br/>.tsx, .ts, .css"]
        B["Vite Dev Server<br/>ESBuild 트랜스파일"]
        C["브라우저<br/>Native ESM"]

        A -->|"요청 시 변환"| B
        B -->|"ESM 모듈"| C
    end

    subgraph "프로덕션 빌드 (build)"
        D["소스 코드"]
        E["Rollup 번들링"]
        F["최적화"]
        G["번들 결과물"]

        D -->|"엔트리 분석"| E
        E -->|"트리 쉐이킹"| F
        F -->|"코드 스플리팅<br/>압축, 해싱"| G
    end

    subgraph "최적화 결과"
        H["index.html"]
        I["vendor.[hash].js"]
        J["app.[hash].js"]
        K["lazy-page.[hash].js"]
        L["style.[hash].css"]
    end

    G --> H
    G --> I
    G --> J
    G --> K
    G --> L

    style B fill:#646CFF,color:#fff
    style E fill:#646CFF,color:#fff
```

**Vite 핵심 설정:**

| 설정 | 용도 | 기본값 |
|------|------|--------|
| `build.target` | 빌드 타겟 브라우저 | `modules` |
| `build.outDir` | 출력 디렉토리 | `dist` |
| `build.rollupOptions` | Rollup 고급 설정 | - |
| `build.chunkSizeWarningLimit` | 청크 크기 경고 한도 | 500kB |
| `build.sourcemap` | 소스맵 생성 | `false` |
| `build.minify` | 압축 도구 | `esbuild` |

### 2. 번들 크기 최적화 전략

```mermaid
graph TD
    A["번들 크기 최적화"] --> B["코드 스플리팅"]
    A --> C["트리 쉐이킹"]
    A --> D["의존성 최적화"]
    A --> E["에셋 최적화"]

    B --> B1["React.lazy() 동적 import"]
    B --> B2["라우트 기반 스플리팅"]
    B --> B3["vendor 청크 분리"]

    C --> C1["ESM 모듈 사용"]
    C --> C2["사이드 이펙트 제거"]
    C --> C3["barrel exports 주의"]

    D --> D1["경량 대안 라이브러리"]
    D --> D2["lodash-es 사용"]
    D --> D3["date-fns vs moment"]

    E --> E1["이미지 압축"]
    E --> E2["폰트 서브셋"]
    E --> E3["CSS 모듈"]

    style A fill:#FF9800,color:#fff
```

### 3. GitHub Actions CI/CD 파이프라인

```mermaid
graph LR
    subgraph "CI 파이프라인"
        T1["린트 검사<br/>ESLint"]
        T2["타입 검사<br/>tsc --noEmit"]
        T3["단위 테스트<br/>Vitest"]
        T4["빌드 검증<br/>vite build"]
        T5["번들 크기 검사"]
    end

    subgraph "CD 파이프라인"
        D1["스테이징 배포<br/>Preview URL"]
        D2["E2E 테스트<br/>Playwright"]
        D3["프로덕션 배포<br/>Vercel/AWS"]
        D4["에러 모니터링<br/>Sentry Release"]
    end

    T1 --> T2 --> T3 --> T4 --> T5
    T5 -->|"main 브랜치"| D1
    D1 --> D2
    D2 -->|"성공"| D3
    D3 --> D4

    style T1 fill:#4CAF50,color:#fff
    style D3 fill:#2196F3,color:#fff
```

### 4. 환경 변수와 멀티 스테이지 배포

```mermaid
graph TB
    subgraph "환경별 설정"
        ENV_DEV[".env.development<br/>VITE_API_URL=http://localhost:3000"]
        ENV_STG[".env.staging<br/>VITE_API_URL=https://stg-api.example.com"]
        ENV_PROD[".env.production<br/>VITE_API_URL=https://api.example.com"]
    end

    subgraph "빌드 모드"
        BUILD_DEV["npm run dev<br/>mode: development"]
        BUILD_STG["npm run build:staging<br/>mode: staging"]
        BUILD_PROD["npm run build<br/>mode: production"]
    end

    ENV_DEV --> BUILD_DEV
    ENV_STG --> BUILD_STG
    ENV_PROD --> BUILD_PROD

    subgraph "배포 대상"
        DEPLOY_DEV["로컬 개발 서버"]
        DEPLOY_STG["스테이징 서버"]
        DEPLOY_PROD["프로덕션 서버"]
    end

    BUILD_DEV --> DEPLOY_DEV
    BUILD_STG --> DEPLOY_STG
    BUILD_PROD --> DEPLOY_PROD
```

### 5. 에러 모니터링과 소스맵

```mermaid
sequenceDiagram
    participant User as 사용자
    participant App as React 앱
    participant Sentry as Sentry
    participant Dev as 개발자

    User->>App: 기능 사용
    App->>App: 런타임 에러 발생
    App->>Sentry: 에러 보고 (에러 객체 + 컨텍스트)
    Note over Sentry: 소스맵으로 원본 코드 매핑
    Sentry->>Dev: 알림 (Slack/이메일)
    Note over Dev: 원본 소스 위치에서<br/>에러 원인 파악
    Dev->>App: 핫픽스 배포
```

---

## 코드로 이해하기

### 예제 1: Vite 최적화 설정 + 번들 분석
> 📁 `practice/example-01.tsx` 파일을 참고하세요.

```tsx
// vite.config.ts - 프로덕션 최적화 설정
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@radix-ui/react-dialog'],
        },
      },
    },
  },
});
```

**실행 방법**:
```bash
npm create vite@latest deploy-demo -- --template react-ts
cd deploy-demo
npm install
npm install -D rollup-plugin-visualizer
npm run build
```

### 예제 2: GitHub Actions CI/CD 워크플로우
> 📁 `practice/example-02.tsx` 파일을 참고하세요.

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

**실행 방법**:
```bash
# GitHub 저장소에 push하면 자동으로 실행됩니다
git add .github/workflows/ci.yml
git commit -m "ci: add CI/CD pipeline"
git push origin main
```

---

## 주의 사항

- ⚠️ **소스맵을 프로덕션에 노출하지 마세요**: Sentry 등 모니터링 서비스에만 업로드하세요.
- ⚠️ **환경 변수에 비밀 키를 넣지 마세요**: `VITE_` 접두사가 붙은 변수는 클라이언트 번들에 포함됩니다.
- ⚠️ **번들 크기를 정기적으로 모니터링하세요**: CI에서 자동으로 검사하는 것이 가장 좋습니다.
- 💡 **`npm run build -- --mode staging`**: Vite에서 커스텀 모드를 사용하여 스테이징 빌드를 할 수 있습니다.
- 💡 **`rollup-plugin-visualizer`**: 번들 구성을 시각적으로 분석할 수 있습니다.
- 💡 **`vite-plugin-compression`**: gzip/brotli 압축 파일을 미리 생성할 수 있습니다.

---

## 정리

| 개념 | 설명 | 도구 |
|------|------|------|
| Vite 빌드 | ESBuild + Rollup 기반 빌드 | `vite build` |
| 코드 스플리팅 | 청크 단위 분리 로딩 | `React.lazy()`, `manualChunks` |
| 번들 분석 | 번들 구성 시각화 | `rollup-plugin-visualizer` |
| CI/CD | 자동화된 빌드/배포 | GitHub Actions |
| 환경 변수 | 환경별 설정 분리 | `.env.*` 파일, Vite 모드 |
| 에러 모니터링 | 프로덕션 에러 추적 | Sentry |

---

## 다음 단계

- ✅ `practice/exercise.md`의 연습 문제를 풀어보세요.
- 📖 다음 챕터: **챕터 10 - 엔터프라이즈 프로젝트: 관리자 대시보드**
- 🔗 참고 자료:
  - [Vite 공식 문서](https://vitejs.dev/)
  - [Rollup 공식 문서](https://rollupjs.org/)
  - [GitHub Actions 문서](https://docs.github.com/en/actions)
  - [Sentry React 문서](https://docs.sentry.io/platforms/javascript/guides/react/)
  - [번들 포비아](https://bundlephobia.com/)
