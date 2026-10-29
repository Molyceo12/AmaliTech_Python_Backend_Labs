"""``ecommerce demo``: one walk through every store (needs ``setup`` and ``seed``)."""

from typing import Any

import redis
from psycopg2.pool import ThreadedConnectionPool
from pymongo.database import Database

from ecommerce_pipeline.cache.top_products import CACHE_KEY, get_top_products
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
    print("1. JSONB: products with metadata @> {'colors': ['red']}")
    red_products = find_by_metadata(pool, RED)
    for product in red_products:
        print(f"   {product.product_id:>3}  {product.name:<20} {product.price:>8}")

    print(f"\n2. MongoDB: cart for customer {CUSTOMER_ID}")
    session_id = create_session(mongo, CUSTOMER_ID)
    for product in red_products[:2]:
        add_to_cart(mongo, session_id, product.product_id, 1)
    cart = get_cart(mongo, session_id)
    print(f"   session {session_id}: {cart}")

    print("\n3. PostgreSQL: order the cart in one transaction")
    order_id = create_order(pool, CUSTOMER_ID, cart)
    print(f"   created order {order_id}")
    for order in get_customer_orders(pool, CUSTOMER_ID):
        print(f"   order {order.order_id}: {order.item_count} items, {order.total}")

    print("\n4. Redis: top 10 best sellers, asked twice")
    cache.delete(CACHE_KEY)
    for _ in range(2):
        source = "cache" if cache.exists(CACHE_KEY) else "database"
        top = get_top_products(pool, cache)
        names = ", ".join(product.name for product in top[:3])
        print(f"   from {source}: {names}, ...")
