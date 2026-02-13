# 실습: 기본 CRUD

## 요구사항
1. `products` 테이블 생성
2. 샘플 데이터 3건 삽입
3. 가격 50000 이상 상품 조회
4. 특정 상품 가격 수정
5. 특정 상품 삭제

## 실행
```bash
docker exec -i pg-learning psql -U postgres -d postgres < solution.sql
docker exec -i pg-learning psql -U postgres -d postgres < test.sql
```
