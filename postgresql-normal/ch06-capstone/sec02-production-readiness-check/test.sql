DO $$
DECLARE
  active_connections int;
BEGIN
  SELECT count(*) INTO active_connections
  FROM pg_stat_activity
  WHERE state = 'active';

  IF active_connections < 1 THEN
    RAISE EXCEPTION '활성 연결 수 점검 결과가 비정상입니다.';
  END IF;
END $$;

SELECT 'sec02-production-readiness-check test passed' AS result;
