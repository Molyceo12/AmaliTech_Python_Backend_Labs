-- Remove the indexes from indexes.sql (the benchmark's "before" run).
DROP INDEX IF EXISTS idx_orders_customer_id;
DROP INDEX IF EXISTS idx_products_metadata;
