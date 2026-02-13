DO $$
DECLARE
  c int;
BEGIN
  SELECT count(*) INTO c FROM backup_lab;
  IF c <> 3 THEN
    RAISE EXCEPTION 'backup_lab row 수가 3이 아닙니다. 현재=%', c;
  END IF;
END $$;

SELECT 'sec01-backup-restore-migration test passed' AS result;
