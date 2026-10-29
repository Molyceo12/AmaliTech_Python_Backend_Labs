-- Indexes for the slow lookups (see "Optimization report" in README.md).

-- B-tree: find one customer's orders without reading every order.
-- PostgreSQL indexes primary keys on its own, but not foreign keys.
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id);

-- GIN: index every key and value inside the JSONB, so @> searches
-- (e.g. metadata @> '{"brand": "X"}') don't read every product.
CREATE INDEX IF NOT EXISTS idx_products_metadata ON products USING GIN (metadata);
