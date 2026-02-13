DO $$
DECLARE
  total_count int;
  keyboard_price int;
  mouse_count int;
BEGIN
  SELECT count(*) INTO total_count FROM products;
  IF total_count <> 2 THEN
    RAISE EXCEPTION 'products 건수는 2여야 합니다. 현재=%', total_count;
  END IF;

  SELECT price INTO keyboard_price FROM products WHERE name = 'Keyboard';
  IF keyboard_price <> 69000 THEN
    RAISE EXCEPTION 'Keyboard 가격이 69000이 아닙니다. 현재=%', keyboard_price;
  END IF;

  SELECT count(*) INTO mouse_count FROM products WHERE name = 'Mouse';
  IF mouse_count <> 0 THEN
    RAISE EXCEPTION 'Mouse 데이터가 삭제되지 않았습니다.';
  END IF;
END $$;

SELECT 'sec02-psql-crud-basics test passed' AS result;
