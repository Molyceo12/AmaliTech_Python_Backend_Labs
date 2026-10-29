-- Sample data for the e-commerce store.
-- TRUNCATE first, so `ecommerce seed` can run more than once with the same ids.

TRUNCATE order_items, orders, products, customers RESTART IDENTITY CASCADE;

INSERT INTO customers (name, email, created_at) VALUES
    ('Ama Mensah',     'ama.mensah@example.com',     '2026-01-05'),
    ('Kofi Boateng',   'kofi.boateng@example.com',   '2026-01-09'),
    ('Esi Owusu',      'esi.owusu@example.com',      '2026-01-14'),
    ('Kwame Asante',   'kwame.asante@example.com',   '2026-01-20'),
    ('Abena Darko',    'abena.darko@example.com',    '2026-02-02'),
    ('Yaw Ofori',      'yaw.ofori@example.com',      '2026-02-11'),
    ('Akosua Addo',    'akosua.addo@example.com',    '2026-02-18'),
    ('Kojo Antwi',     'kojo.antwi@example.com',     '2026-03-01'),
    ('Adwoa Amoah',    'adwoa.amoah@example.com',    '2026-03-07'),
    ('Kwesi Appiah',   'kwesi.appiah@example.com',   '2026-03-15');

-- metadata is JSONB: each category has its own keys (sizes, colors, ...).
INSERT INTO products (name, price, stock, metadata) VALUES
    ('Cotton T-Shirt',     15.00, 120, '{"category": "clothing", "colors": ["red", "blue", "white"], "sizes": ["S", "M", "L"]}'),
    ('Denim Jeans',        45.00,  60, '{"category": "clothing", "colors": ["blue", "black"], "sizes": ["M", "L", "XL"]}'),
    ('Hoodie',             35.00,  40, '{"category": "clothing", "colors": ["grey", "black"], "sizes": ["S", "M", "L", "XL"]}'),
    ('Kente Scarf',        25.00,  30, '{"category": "clothing", "colors": ["gold", "green"], "material": "silk"}'),
    ('Running Shoes',      80.00,  25, '{"category": "shoes", "colors": ["white", "red"], "sizes": ["40", "41", "42", "43"]}'),
    ('Leather Sandals',    30.00,  35, '{"category": "shoes", "colors": ["brown"], "sizes": ["39", "40", "41"]}'),
    ('Wireless Earbuds',   60.00,  50, '{"category": "electronics", "brand": "SoundMax", "battery_hours": 8}'),
    ('Phone Charger',      12.50, 200, '{"category": "electronics", "brand": "VoltUp", "watts": 20}'),
    ('Bluetooth Speaker',  55.00,  20, '{"category": "electronics", "brand": "SoundMax", "colors": ["black", "red"]}'),
    ('Smart Watch',       120.00,  15, '{"category": "electronics", "brand": "TimeOn", "colors": ["black", "silver"]}'),
    ('Ceramic Mug',         8.00,  90, '{"category": "home", "colors": ["white", "blue"], "capacity_ml": 350}'),
    ('Throw Pillow',       18.00,  45, '{"category": "home", "colors": ["red", "gold"], "sizes": ["M"]}'),
    ('Table Lamp',         40.00,  18, '{"category": "home", "colors": ["white"], "bulb": "LED"}'),
    ('Notebook',            4.50, 300, '{"category": "stationery", "pages": 120}'),
    ('Backpack',           38.00,  28, '{"category": "bags", "colors": ["black", "green"], "capacity_l": 25}');

INSERT INTO orders (customer_id, created_at) VALUES
    (1, '2026-03-02'), (2, '2026-03-03'), (3, '2026-03-05'), (1, '2026-03-08'),
    (4, '2026-03-10'), (5, '2026-03-12'), (6, '2026-03-15'), (2, '2026-03-18'),
    (7, '2026-03-20'), (8, '2026-03-22'), (9, '2026-03-25'), (3, '2026-03-28'),
    (10, '2026-04-01'), (1, '2026-04-03'), (5, '2026-04-06'), (6, '2026-04-09'),
    (4, '2026-04-12'), (7, '2026-04-15'), (2, '2026-04-18'), (9, '2026-04-21');

-- unit_price is copied from the product: the price at the time of the order.
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT v.order_id, v.product_id, v.quantity, p.price
FROM (VALUES
    (1, 1, 2), (1, 11, 1),
    (2, 5, 1), (2, 8, 2),
    (3, 2, 1), (3, 1, 3),
    (4, 7, 1),
    (5, 10, 1), (5, 8, 1),
    (6, 3, 2), (6, 14, 5),
    (7, 9, 1),
    (8, 1, 1), (8, 12, 2),
    (9, 4, 2), (9, 15, 1),
    (10, 7, 2),
    (11, 6, 1), (11, 11, 4),
    (12, 13, 1),
    (13, 1, 4), (13, 2, 1),
    (14, 5, 1), (14, 14, 3),
    (15, 7, 1), (15, 8, 1),
    (16, 15, 1),
    (17, 3, 1), (17, 12, 1),
    (18, 1, 2), (18, 9, 1),
    (19, 10, 1),
    (20, 11, 2), (20, 4, 1)
) AS v (order_id, product_id, quantity)
JOIN products p ON p.product_id = v.product_id;
