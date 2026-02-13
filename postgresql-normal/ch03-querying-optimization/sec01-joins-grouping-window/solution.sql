DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL
);

CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(id),
  amount INTEGER NOT NULL CHECK (amount > 0)
);

INSERT INTO customers (name) VALUES ('Kim'), ('Lee'), ('Park');
INSERT INTO orders (customer_id, amount) VALUES
(1, 10000), (1, 20000),
(2, 30000),
(3, 5000), (3, 7000), (3, 8000);

SELECT
  c.name,
  count(o.id) AS order_count,
  sum(o.amount) AS total_amount,
  dense_rank() OVER (ORDER BY sum(o.amount) DESC) AS amount_rank
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY total_amount DESC;
