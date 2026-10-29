# E-Commerce Analytics Data Pipeline

Data pipeline for a fictional e-commerce store: PostgreSQL for customers, products and orders, Redis for caching popular products, and MongoDB for user sessions and carts.

## Setup

```bash
cp .env.example .env
docker compose up -d
python -m poetry install
python -m poetry run ecommerce setup      # create the tables
```

## ER diagram

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : "appears in"

    CUSTOMERS {
        serial customer_id PK
        varchar name
        varchar email UK
        timestamptz created_at
    }
    PRODUCTS {
        serial product_id PK
        varchar name
        numeric price
        integer stock
        jsonb metadata
    }
    ORDERS {
        serial order_id PK
        integer customer_id FK
        timestamptz created_at
    }
    ORDER_ITEMS {
        integer order_id PK, FK
        integer product_id PK, FK
        integer quantity
        numeric unit_price
    }
```

## Schema

DDL: [sql/schema.sql](sql/schema.sql)

| Table | Why it exists | Constraints |
|---|---|---|
| `customers` | One row per customer | `email` is `UNIQUE` and `NOT NULL` |
| `products` | One row per product; sizes, colors etc. go in `metadata` (JSONB) | `price >= 0`, `stock >= 0` |
| `orders` | One row per order, linked to its customer | FK to `customers` |
| `order_items` | One row per product in an order (resolves the many-to-many between orders and products) | PK `(order_id, product_id)`, `quantity > 0`, FKs to `orders` and `products` |

## Normalization decisions

- **1NF:** every column holds one value. The products in an order are rows in `order_items`, not a list in `orders`.
- **2NF:** in `order_items`, `quantity` and `unit_price` depend on the whole key `(order_id, product_id)`, not on just one part.
- **3NF:** no column depends on another non-key column. Customer details live only in `customers`, and order totals are not stored: they are computed from `order_items`.
- **`order_items.unit_price`** is not a copy of `products.price`. It is the price at the time of purchase, so old orders keep their real total when a price changes.
- **`products.metadata`** is JSONB on purpose: attributes differ per product (a shirt has a size, a mug doesn't), so they don't fit fixed columns.
