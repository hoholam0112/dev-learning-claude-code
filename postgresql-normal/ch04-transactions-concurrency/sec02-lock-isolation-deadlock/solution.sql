DROP TABLE IF EXISTS lock_lab;

CREATE TABLE lock_lab (
  id INTEGER PRIMARY KEY,
  value INTEGER NOT NULL
);

INSERT INTO lock_lab (id, value) VALUES (1, 10), (2, 20);

-- Deadlock-prone scenario (manual multi-session test)
-- Session A
-- BEGIN;
-- UPDATE lock_lab SET value = value + 1 WHERE id = 1;
-- UPDATE lock_lab SET value = value + 1 WHERE id = 2;
-- COMMIT;

-- Session B
-- BEGIN;
-- UPDATE lock_lab SET value = value + 1 WHERE id = 2;
-- UPDATE lock_lab SET value = value + 1 WHERE id = 1;
-- COMMIT;

-- Deadlock avoidance rule:
-- 모든 트랜잭션에서 같은 순서(id 오름차순)로 row를 잠근다.
