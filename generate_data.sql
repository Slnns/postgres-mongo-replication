-- Очистка существующих данных
TRUNCATE orders CASCADE;
TRUNCATE customers CASCADE;

INSERT INTO customers (name, email)
SELECT
    'Customer_' || generate_series,
    'customer_' || generate_series || '@example.com'
FROM generate_series(1, 1000);

-- Генерация 500000 заказов
INSERT INTO orders (customer_id, product, amount, status, created_at, updated_at)
SELECT
    floor(random() * 1000 + 1)::int,
    'Product_' || floor(random() * 100 + 1)::int,
    (random() * 1000)::numeric(10,2),
    CASE floor(random() * 4)
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'completed'
        WHEN 2 THEN 'shipped'
        ELSE 'cancelled'
    END,
    NOW() - (random() * interval '30 days'),
    NOW() - (random() * interval '7 days')
FROM generate_series(1, 500000);