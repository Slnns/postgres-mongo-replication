-- Создание таблиц
CREATE TABLE IF NOT EXISTS customers (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id           SERIAL PRIMARY KEY,
    customer_id  INT REFERENCES customers(id) ON DELETE CASCADE,
    product      VARCHAR(200) NOT NULL,
    amount       NUMERIC(10, 2) NOT NULL,
    status       VARCHAR(50) DEFAULT 'pending',
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_orders_updated ON orders(updated_at);
CREATE INDEX IF NOT EXISTS idx_customers_created ON customers(created_at);