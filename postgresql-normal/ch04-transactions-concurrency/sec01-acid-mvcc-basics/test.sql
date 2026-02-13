DO $$
DECLARE
  total_balance int;
  a int;
  b int;
BEGIN
  SELECT sum(balance) INTO total_balance FROM accounts;
  SELECT balance INTO a FROM accounts WHERE id = 1;
  SELECT balance INTO b FROM accounts WHERE id = 2;

  IF total_balance <> 150000 THEN
    RAISE EXCEPTION '총 잔액 불일치: %', total_balance;
  END IF;
  IF a <> 90000 OR b <> 60000 THEN
    RAISE EXCEPTION '계좌 잔액이 예상과 다릅니다. a=%, b=%', a, b;
  END IF;
END $$;

SELECT 'sec01-acid-mvcc-basics test passed' AS result;
