DO $$
DECLARE
  total_amount int;
BEGIN
  SELECT SUM(quantity * unit_price)
  INTO total_amount
  FROM order_items
  WHERE order_id = 1;

  IF total_amount <> 30000 THEN
    RAISE EXCEPTION '주문 총액이 예상과 다릅니다. total=%', total_amount;
  END IF;
END $$;

SELECT 'sec01-order-system-schema test passed' AS result;
