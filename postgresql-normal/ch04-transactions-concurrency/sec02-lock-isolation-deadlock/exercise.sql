DROP TABLE IF EXISTS lock_lab;

-- TODO: lock_lab(id, value) 생성 후 2행 삽입
-- TODO: 아래 주석의 세션 시나리오를 완성
-- Session A: BEGIN; UPDATE lock_lab SET ... WHERE id=1; (대기) UPDATE ... WHERE id=2;
-- Session B: BEGIN; UPDATE lock_lab SET ... WHERE id=2; (대기) UPDATE ... WHERE id=1;
-- TODO: 데드락 회피 규칙을 SQL 주석으로 작성
