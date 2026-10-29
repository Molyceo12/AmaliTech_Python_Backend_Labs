-- Rank products by units sold. RANK() gives ties the same rank and skips the
-- next one (1, 2, 2, 4). Products never sold get 0 units and rank last.
WITH sales AS (
    SELECT p.product_id,
           p.name,
           COALESCE(SUM(oi.quantity), 0)::int                 AS units_sold,
           COALESCE(SUM(oi.quantity * oi.unit_price), 0)      AS revenue
    FROM products p
    LEFT JOIN order_items oi ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.name
)
SELECT RANK() OVER (ORDER BY units_sold DESC)::int AS sales_rank,
       product_id,
       name,
       units_sold,
       revenue
FROM sales
ORDER BY sales_rank, product_id;
