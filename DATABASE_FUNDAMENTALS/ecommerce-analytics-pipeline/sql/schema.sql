-- E-commerce schema in third normal form (3NF).
-- IF NOT EXISTS lets `ecommerce setup` run more than once.

CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name       VARCHAR(100)  NOT NULL,
    price      NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock      INTEGER        NOT NULL CHECK (stock >= 0),
    metadata   JSONB          NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER     NOT NULL REFERENCES customers (customer_id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id   INTEGER        NOT NULL REFERENCES orders (order_id) ON DELETE CASCADE,
    product_id INTEGER        NOT NULL REFERENCES products (product_id),
    quantity   INTEGER        NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id)
);
