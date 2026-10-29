# Changelog

All notable changes to the E-Commerce Analytics Data Pipeline.

## [1.0.0] - 2026-10-29

### Added

- Project setup: Poetry, pre-commit hooks (Black, ruff, pylint, mypy strict),
  settings loaded from `.env`, exception hierarchy based on `EcommerceError`
  and a log file (`output/ecommerce.log`)
- `docker-compose.yml` with PostgreSQL 16, Redis 7 and MongoDB 7
- 3NF schema (`sql/schema.sql`) for customers, products, orders and
  order_items, with primary keys, foreign keys and check constraints; ER
  diagram in the README
- psycopg2 connection pool and the `ecommerce setup` command
- Repositories: `add_customer()`, `add_product()`, `create_order()` and
  `get_customer_orders()`, all with parameterized queries
- `create_order()` in one ACID transaction: rows locked with `FOR UPDATE`,
  stock checked and reduced, rollback on any error
- Sample data (`sql/sample_data.sql`) and the `ecommerce seed` command
- Redis cache-aside for the top 10 best sellers (5-minute TTL)
- MongoDB sessions and carts with pymongo
- JSONB product metadata searched with `@>`, and the `ecommerce demo` command
- `RANK()` product ranking and CTE revenue per customer (`ecommerce report`)
- B-tree index on `orders(customer_id)` and GIN index on `products(metadata)`
- `EXPLAIN ANALYZE` benchmark on 200,000 orders (`ecommerce benchmark`) and
  the optimization report in the README
- 73 unit and integration tests with 100 % coverage (`reports/coverage.txt`),
  `requirements.txt`
