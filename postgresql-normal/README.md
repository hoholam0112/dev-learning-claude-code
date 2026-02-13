# PostgreSQL 학습 커리큘럼 (Production Track)

> 대상: DB를 다시 기초부터 정리하고 프로덕션 운영까지 가고 싶은 개발자
> 기간: 10주 (주 2~3시간)
> 환경: macOS + Docker

## 로드맵

- Ch01. 시작하기: Docker 환경, psql 기본 CRUD
- Ch02. 스키마 설계: 데이터 타입/제약조건, 관계 모델링
- Ch03. 쿼리/성능: JOIN/집계/윈도우 함수, 인덱스/실행계획
- Ch04. 트랜잭션/동시성: ACID/MVCC, 락/격리수준/데드락
- Ch05. 운영 실무: 백업/복구/마이그레이션, 권한/보안/풀링
- Ch06. 캡스톤: 주문 시스템 스키마 설계, 운영 체크리스트

## 학습 방법

1. 각 섹션 `concept.md`를 읽고 핵심 개념을 이해한다.
2. `exercise.md` 요구사항을 보고 `exercise.sql`을 완성한다.
3. `test.sql`로 검증한다.
4. 필요 시 `solution.sql`과 비교한다.

## 실행 빠른 시작

```bash
cd postgresql-normal/resources
docker compose up -d
```

```bash
# 예시: 섹션 테스트 실행
cd ../ch01-getting-started/sec02-psql-crud-basics
docker exec -i pg-learning psql -U postgres -d postgres < solution.sql
docker exec -i pg-learning psql -U postgres -d postgres < test.sql
```
