# 실습: 백업/복구 리허설

## 요구사항
- 실습 DB에 샘플 테이블 생성
- `pg_dump`로 백업 생성
- 새 DB에 복구 후 row 수 검증

## 명령 예시
```bash
docker exec pg-learning pg_dump -U postgres -d postgres -t products > products.sql
```
