DO $$
DECLARE
  cnt int;
BEGIN
  SELECT count(*) INTO cnt FROM lock_lab;
  IF cnt <> 2 THEN
    RAISE EXCEPTION 'lock_lab 초기 데이터가 2건이 아닙니다.';
  END IF;
END $$;

SELECT 'sec02-lock-isolation-deadlock test passed' AS result;
