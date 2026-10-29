-- Revenue per customer, built in two CTE steps:
--   order_totals:     one total per order
--   customer_revenue: orders and revenue per customer
WITH order_totals AS (
    SELECT o.order_id,
           o.customer_id,
           SUM(oi.quantity * oi.unit_price) AS order_total
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id, o.customer_id
),
customer_revenue AS (
    SELECT customer_id,
           COUNT(*)::int    AS order_count,
           SUM(order_total) AS revenue
    FROM order_totals
    GROUP BY customer_id
)
SELECT c.customer_id,
       c.name,
       cr.order_count,
       cr.revenue
FROM customer_revenue cr
JOIN customers c ON c.customer_id = cr.customer_id
ORDER BY cr.revenue DESC, c.customer_id;
