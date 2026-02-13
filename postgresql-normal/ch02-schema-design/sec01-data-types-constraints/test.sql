DO $$
DECLARE
  dup_error boolean := false;
BEGIN
  INSERT INTO users (email, nickname, status) VALUES ('a@test.com', 'a', 'active');
  BEGIN
    INSERT INTO users (email, nickname, status) VALUES ('a@test.com', 'b', 'active');
  EXCEPTION WHEN unique_violation THEN
    dup_error := true;
  END;

  IF NOT dup_error THEN
    RAISE EXCEPTION 'UNIQUE 제약조건이 동작하지 않습니다.';
  END IF;
END $$;

SELECT 'sec01-data-types-constraints test passed' AS result;
