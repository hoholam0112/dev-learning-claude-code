# Dev Learning with Claude Code

Claude Code를 활용하여 생성한 개발 학습 자료 레포지토리입니다.

## 학습 자료 목록

### FastAPI

| 과정 | 난이도 | 대상 | 설명 |
|------|--------|------|------|
| [fastapi-normal](./fastapi-normal/) | ⭐ ~ ⭐⭐⭐ | Python 중급자, 웹 API 입문자 | REST API 구축을 위한 핵심 개념과 실습 (8개 챕터) |

#### 챕터 구성 (8개 챕터, 챕터당 3개 섹션)

| 챕터 | 주제 | 섹션 |
|------|------|------|
| Ch01 | FastAPI 시작하기 | 설치, 첫 번째 앱, 개발 서버 |
| Ch02 | 경로/쿼리 매개변수 | 경로 매개변수, 쿼리 매개변수, 매개변수 검증 |
| Ch03 | 요청 본문 | Pydantic 모델, 중첩 모델, 폼/파일 처리 |
| Ch04 | 응답 처리 | 응답 모델, 상태 코드, 에러 처리 |
| Ch05 | 의존성 주입 | 기본 의존성, 클래스 의존성, 중첩 의존성 |
| Ch06 | 미들웨어와 CORS | 미들웨어 기본, CORS 설정, 커스텀 미들웨어 |
| Ch07 | 데이터베이스 연동 | SQLAlchemy 설정, CRUD 구현, 관계 매핑 |
| Ch08 | 인증과 보안 | OAuth2/JWT, 비밀번호 해싱, 보호된 라우트 |

## 레포지토리 구조

```
fastapi-normal/
├── ch01-getting-started/
│   ├── README.md                   # 챕터 개요
│   ├── sec01-installation/
│   │   ├── concept.md              # 개념 설명
│   │   ├── exercise.md             # 연습 문제
│   │   ├── exercise.py             # 풀이용 스켈레톤 코드
│   │   └── solution.py             # 정답 코드
│   ├── sec02-first-app/
│   └── sec03-dev-server/
├── ch02-path-query-params/
│   └── ...
├── resources/
│   ├── glossary.md                 # 용어 사전
│   └── references.md               # 참고 자료
└── README.md                       # 커리큘럼 가이드
```

## 학습 방법

각 섹션별로 아래 순서를 따릅니다.

1. `concept.md`를 읽고 핵심 개념을 이해한다
2. `exercise.md`의 연습 문제를 읽는다
3. `exercise.py`를 직접 완성해본다
4. 막히면 `solution.py`를 참고한다
5. `resources/glossary.md`에서 용어를 복습한다

## 생성 도구

이 학습 자료는 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)를 사용하여 생성되었습니다.
