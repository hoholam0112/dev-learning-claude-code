DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
  id BIGSERIAL PRIMARY KEY,
  owner VARCHAR(100) NOT NULL,
  balance INTEGER NOT NULL CHECK (balance >= 0)
);

INSERT INTO accounts (owner, balance) VALUES ('Alice', 100000), ('Bob', 50000);

BEGIN;
UPDATE accounts SET balance = balance - 10000 WHERE id = 1;
UPDATE accounts SET balance = balance + 10000 WHERE id = 2;
COMMIT;
