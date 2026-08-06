-- Create analytics schema
CREATE SCHEMA IF NOT EXISTS analytics;

-- Customers table (core dimension)
CREATE TABLE IF NOT EXISTS analytics.customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen INTEGER,
    partner VARCHAR(10),
    dependents VARCHAR(10),
    tenure INTEGER,
    phone_service VARCHAR(10),
    multiple_lines VARCHAR(20),
    internet_service VARCHAR(20),
    online_security VARCHAR(20),
    online_backup VARCHAR(20),
    device_protection VARCHAR(20),
    tech_support VARCHAR(20),
    streaming_tv VARCHAR(20),
    streaming_movies VARCHAR(20),
    contract VARCHAR(20),
    paperless_billing VARCHAR(10),
    payment_method VARCHAR(30),
    monthly_charges NUMERIC(10, 2),
    total_charges NUMERIC(10, 2),
    churn VARCHAR(10)
);

-- Synthetic transactions table (for rolling features)
CREATE TABLE IF NOT EXISTS analytics.transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES analytics.customers(customer_id),
    transaction_date DATE,
    amount NUMERIC(10, 2),
    transaction_type VARCHAR(20)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_customer_id ON analytics.customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_transaction_customer ON analytics.transactions(customer_id);