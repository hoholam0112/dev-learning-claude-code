DO $$
DECLARE
  top_name text;
  top_total int;
BEGIN
  SELECT name, total_amount INTO top_name, top_total
  FROM (
    SELECT c.name, sum(o.amount) AS total_amount
    FROM customers c JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    ORDER BY total_amount DESC
    LIMIT 1
  ) t;

  IF top_name <> 'Kim' OR top_total <> 30000 THEN
    RAISE EXCEPTION '집계 결과가 예상과 다릅니다. name=%, total=%', top_name, top_total;
  END IF;
END $$;

SELECT 'sec01-joins-grouping-window test passed' AS result;
