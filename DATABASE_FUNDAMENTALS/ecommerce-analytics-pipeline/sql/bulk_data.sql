-- Bulk rows for the EXPLAIN ANALYZE benchmark, added after sample_data.sql.
-- Indexes only pay off on big tables, so generate_series makes thousands of rows.

INSERT INTO customers (name, email)
SELECT 'Customer ' || i, 'customer' || i || '@bulk.example.com'
FROM generate_series(1, 20000) AS i;

-- 1,000 brands over 50,000 products: one brand matches about 50 products.
INSERT INTO products (name, price, stock, metadata)
SELECT 'Product ' || i,
       (i % 200) + 0.99,
       1000,
       jsonb_build_object(
           'category', (ARRAY['clothing', 'shoes', 'electronics', 'home', 'bags'])[i % 5 + 1],
           'brand',    'Brand-' || (i % 1000),
           'colors',   jsonb_build_array((ARRAY['red', 'blue', 'black', 'white', 'green', 'grey'])[i % 6 + 1])
       )
FROM generate_series(1, 50000) AS i;

-- 200,000 orders over 20,010 customers: about 10 orders per customer.
INSERT INTO orders (customer_id, created_at)
SELECT i % 20010 + 1, now() - (i % 365) * INTERVAL '1 day'
FROM generate_series(1, 200000) AS i;

-- One item per bulk order (the 20 sample orders already have items).
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT o.order_id, p.product_id, o.order_id % 3 + 1, p.price
FROM orders o
JOIN products p ON p.product_id = (o.order_id * 7919) % 50015 + 1
WHERE o.order_id > 20;

-- Refresh the planner's statistics so it knows the tables are big now.
ANALYZE;
