DO $$
DECLARE
  idx_count int;
BEGIN
  SELECT count(*) INTO idx_count
  FROM pg_indexes
  WHERE tablename = 'events' AND indexname = 'idx_events_user_id';

  IF idx_count <> 1 THEN
    RAISE EXCEPTION 'idx_events_user_id 인덱스가 없습니다.';
  END IF;
END $$;

SELECT 'sec02-index-and-explain test passed' AS result;
