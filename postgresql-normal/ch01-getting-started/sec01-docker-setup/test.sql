DO $$
DECLARE
  v text;
  db_name text;
BEGIN
  SELECT version() INTO v;
  IF v NOT ILIKE '%PostgreSQL%' THEN
    RAISE EXCEPTION 'version() 결과가 비정상입니다.';
  END IF;

  SELECT current_database() INTO db_name;
  IF db_name IS NULL OR db_name = '' THEN
    RAISE EXCEPTION 'current_database() 결과가 비어 있습니다.';
  END IF;
END $$;

SELECT 'sec01-docker-setup test passed' AS result;
