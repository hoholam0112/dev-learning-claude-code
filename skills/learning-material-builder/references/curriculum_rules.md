# Curriculum Rules

## Planning Principles

- 커리큘럼 규모를 고정하지 않는다.
- 학습자 레벨과 시간 제약으로 분량을 조정한다.
- 선행지식이 부족하면 선행 챕터를 먼저 넣는다.
- 섹션은 실습 가능 단위로 작게 쪼갠다.

## Dynamic Sizing

- 주당 3시간 미만: 챕터 수를 줄이고 핵심 섹션 우선
- 주당 3~6시간: 표준 분량
- 주당 6시간 이상: 심화/프로젝트 섹션 추가

## Prerequisite Insertion

- React + JS 약함 -> JS 기초 챕터 추가
- FastAPI + Python 약함 -> Python 함수/타입힌트/비동기 챕터 추가
- Spring + Java 약함 -> Java OOP/예외/컬렉션 챕터 추가

## Section Requirements

각 섹션은 다음 파일을 가진다:

- `concept.md`
- `exercise.md`
- `exercise.*`
- `solution.*`
- `test.*`

## Content Minimums

- `concept.md`: 목표, 핵심개념, 예제, 주의사항
- `exercise.md`: 문제설명, 요구사항, 입출력 규칙, 실행법, 체크리스트
- `exercise.*`: TODO가 포함된 미완성 코드
- `solution.*`: 완성 코드 + 최소 주석
- `test.*`: 정상/경계/오류 시나리오를 포함한 실행 가능한 테스트

