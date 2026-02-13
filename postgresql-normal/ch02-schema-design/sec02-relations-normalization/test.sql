DO $$
DECLARE
  fk_error boolean := false;
BEGIN
  BEGIN
    INSERT INTO posts (user_id, title, body) VALUES (999, 'bad', 'fk fail');
  EXCEPTION WHEN foreign_key_violation THEN
    fk_error := true;
  END;

  IF NOT fk_error THEN
    RAISE EXCEPTION 'FK 제약조건이 동작하지 않습니다.';
  END IF;
END $$;

SELECT 'sec02-relations-normalization test passed' AS result;
