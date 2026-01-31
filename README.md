# Dev Learning with Claude Code

Claude Code를 활용하여 생성한 개발 학습 자료 레포지토리입니다.

## 학습 자료 목록

### FastAPI

Python 기반 웹 프레임워크 FastAPI를 체계적으로 학습할 수 있는 커리큘럼입니다.
Normal(초중급)과 Expert(고급) 두 단계로 구성되어 있습니다.

| 과정 | 난이도 | 대상 | 설명 |
|------|--------|------|------|
| [fastapi-normal](./fastapi-normal/) | ⭐ ~ ⭐⭐⭐ | FastAPI 입문자 ~ 초중급 | REST API 구축을 위한 핵심 개념과 실습 |
| [fastapi-expert](./fastapi-expert/) | ⭐⭐⭐ ~ ⭐⭐⭐⭐⭐ | 중급 이상 | 프로덕션 수준의 아키텍처, 최적화, 운영 |

#### 챕터 구성

**Normal (10개 챕터)**

| 챕터 | 주제 |
|------|------|
| Ch01 | FastAPI 소개 및 환경 설정 |
| Ch02 | 경로 매개변수와 쿼리 매개변수 |
| Ch03 | 요청 본문과 Pydantic 모델 |
| Ch04 | 응답 모델과 상태 코드 |
| Ch05 | 의존성 주입 |
| Ch06 | 인증과 보안 기초 |
| Ch07 | 데이터베이스 연동 (SQLAlchemy) |
| Ch08 | 에러 핸들링과 미들웨어 |
| Ch09 | 파일 업로드와 폼 데이터 |
| Ch10 | 백그라운드 작업과 테스팅 |

**Expert (10개 챕터)**

| 챕터 | 주제 |
|------|------|
| Ch01 | ASGI 아키텍처와 내부 구조 |
| Ch02 | 고급 Pydantic 패턴 |
| Ch03 | 고급 의존성 주입과 라이프사이클 |
| Ch04 | 비동기 프로그래밍 심화 |
| Ch05 | 고급 보안 패턴 |
| Ch06 | 데이터베이스 최적화 (Async SQLAlchemy) |
| Ch07 | 성능 최적화와 캐싱 |
| Ch08 | WebSocket과 실시간 통신 |
| Ch09 | 마이크로서비스와 확장 가능한 아키텍처 |
| Ch10 | 프로덕션 배포와 운영 |

## 레포지토리 구조

```
dev-learning-claude-code/
├── fastapi-normal/
│   ├── chapters/
│   │   └── ch01 ~ ch10/
│   │       ├── concept.md          # 개념 설명
│   │       └── practice/
│   │           ├── example-01.py   # 예제 코드 1
│   │           ├── example-02.py   # 예제 코드 2
│   │           ├── exercise.md     # 연습 문제
│   │           └── solution.py     # 풀이 코드
│   └── resources/
│       ├── glossary.md             # 용어 사전
│       └── references.md           # 참고 자료
├── fastapi-expert/
│   ├── chapters/
│   │   └── (동일 구조)
│   └── resources/
│       ├── glossary.md
│       └── references.md
└── README.md
```

## 학습 방법

각 챕터별로 아래 순서를 따릅니다.

1. `concept.md`를 읽고 핵심 개념을 이해한다
2. `example-*.py` 예제 코드를 실행하며 동작을 확인한다
3. `exercise.md`의 연습 문제를 직접 풀어본다
4. 막히면 `solution.py`를 참고한다
5. `resources/glossary.md`에서 용어를 복습한다

## 생성 도구

이 학습 자료는 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)를 사용하여 생성되었습니다.
