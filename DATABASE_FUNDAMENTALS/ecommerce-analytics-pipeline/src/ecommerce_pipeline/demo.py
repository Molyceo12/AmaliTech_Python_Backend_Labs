"""``ecommerce demo``: one walk through every store (needs ``setup`` and ``seed``)."""

from typing import Any

import redis
from psycopg2.pool import ThreadedConnectionPool
from pymongo.database import Database

from ecommerce_pipeline.cache.top_products import CACHE_KEY, get_top_products
from ecommerce_pipeline.display import print_table
from ecommerce_pipeline.repositories.orders import create_order, get_customer_orders
from ecommerce_pipeline.repositories.products import find_by_metadata
from ecommerce_pipeline.sessions.carts import add_to_cart, create_session, get_cart

CUSTOMER_ID = 1
RED = {"colors": ["red"]}


def run_demo(
    pool: ThreadedConnectionPool,
    cache: redis.Redis,
    mongo: Database[dict[str, Any]],
) -> None:
    """Search JSONB, fill a Mongo cart, order it in PostgreSQL, cache best sellers."""
    red_products = find_by_metadata(pool, RED)
    print_table(
        "1. JSONB: products with metadata @> {'colors': ['red']}",
        ["id", "product", "price"],
        [[p.product_id, p.name, p.price] for p in red_products],
    )

    session_id = create_session(mongo, CUSTOMER_ID)
    for product in red_products[:2]:
        add_to_cart(mongo, session_id, product.product_id, 1)
    cart = get_cart(mongo, session_id)
    print_table(
        f"\n2. MongoDB: cart of customer {CUSTOMER_ID} (session {session_id})",
        ["product id", "quantity"],
        list(cart.items()),
    )

    order_id = create_order(pool, CUSTOMER_ID, cart)
    print_table(
        f"\n3. PostgreSQL: cart ordered in one transaction (order {order_id})",
        ["order", "created", "items", "total"],
        [
            [o.order_id, f"{o.created_at:%Y-%m-%d %H:%M}", o.item_count, o.total]
            for o in get_customer_orders(pool, CUSTOMER_ID)
        ],
    )

    cache.delete(CACHE_KEY)
    calls = []
    for call in (1, 2):
        source = "cache" if cache.exists(CACHE_KEY) else "database"
        top = get_top_products(pool, cache)
        calls.append([call, source, ", ".join(p.name for p in top[:3]) + ", ..."])
    print_table(
        "\n4. Redis: top 10 best-selling products, asked twice",
        ["call", "from", "top products"],
        calls,
    )
