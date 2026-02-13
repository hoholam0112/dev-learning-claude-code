DROP TABLE IF EXISTS products;

CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  price INTEGER NOT NULL CHECK (price >= 0)
);

INSERT INTO products (name, price) VALUES
('Keyboard', 59000),
('Mouse', 35000),
('Monitor', 250000);

SELECT *
FROM products
WHERE price >= 50000
ORDER BY price DESC;

UPDATE products
SET price = 69000
WHERE name = 'Keyboard';

DELETE FROM products
WHERE name = 'Mouse';
