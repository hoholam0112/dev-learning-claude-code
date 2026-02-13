DO $$
DECLARE
  ro_has_select boolean;
  rw_has_insert boolean;
BEGIN
  SELECT has_table_privilege('app_readonly', 'sample_data', 'SELECT') INTO ro_has_select;
  SELECT has_table_privilege('app_readwrite', 'sample_data', 'INSERT') INTO rw_has_insert;

  IF NOT ro_has_select THEN
    RAISE EXCEPTION 'app_readonly에 SELECT 권한이 없습니다.';
  END IF;
  IF NOT rw_has_insert THEN
    RAISE EXCEPTION 'app_readwrite에 INSERT 권한이 없습니다.';
  END IF;
END $$;

SELECT 'sec02-role-security-pooling test passed' AS result;
