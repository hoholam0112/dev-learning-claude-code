# 실습: Docker PostgreSQL 준비

## 요구사항
- `resources/docker-compose.yml`로 PostgreSQL 컨테이너 실행
- `psql` 접속 후 버전과 현재 DB 확인
- 아래 `exercise.sql`을 실행해 결과 확인

## 실행
```bash
cd postgresql-normal/resources
docker compose up -d
docker exec -i pg-learning psql -U postgres -d postgres < ../ch01-getting-started/sec01-docker-setup/exercise.sql
```
