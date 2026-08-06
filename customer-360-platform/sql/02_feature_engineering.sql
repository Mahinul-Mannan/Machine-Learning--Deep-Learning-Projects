-- ============================================================
-- Feature Engineering: Customer 360 Analytics
-- Creates a feature table for churn prediction modeling
-- ============================================================

-- Drop the feature table if it already exists (for fresh runs)
DROP TABLE IF EXISTS analytics.customer_features;

-- Create the feature table with all derived features
CREATE TABLE analytics.customer_features AS
WITH 
-- 1. Transaction aggregates per customer
transaction_agg AS (
    SELECT 
        customer_id,
        COUNT(*) AS total_transactions,
        AVG(amount) AS avg_transaction_amount,
        SUM(amount) AS total_spent,
        MAX(transaction_date) AS last_transaction_date,
        MIN(transaction_date) AS first_transaction_date,
        -- ✅ Corrected: Direct date difference (returns integer days)
        (CURRENT_DATE - MAX(transaction_date)) AS recency_days
    FROM analytics.transactions
    GROUP BY customer_id
),

-- 2. Rolling averages (last 3 months)
rolling_avg AS (
    SELECT 
        customer_id,
        AVG(amount) AS avg_amount_last_3m
    FROM analytics.transactions
    WHERE transaction_date >= (CURRENT_DATE - INTERVAL '3 months')
    GROUP BY customer_id
),

-- 3. Frequency: transactions in last 3 months
frequency AS (
    SELECT 
        customer_id,
        COUNT(*) AS frequency_last_3m
    FROM analytics.transactions
    WHERE transaction_date >= (CURRENT_DATE - INTERVAL '3 months')
    GROUP BY customer_id
),

-- 4. Tenure-based segments
tenure_segments AS (
    SELECT 
        customer_id,
        tenure,
        CASE 
            WHEN tenure < 6 THEN 'New'
            WHEN tenure BETWEEN 6 AND 18 THEN 'Mid'
            WHEN tenure > 18 THEN 'Long'
        END AS tenure_segment
    FROM analytics.customers
)

-- 5. Final feature table: join all CTEs with customer base
SELECT 
    c.customer_id,
    c.tenure,
    ts.tenure_segment,
    c.monthly_charges,
    c.total_charges,
    c.contract,
    c.paperless_billing,
    c.payment_method,
    COALESCE(ta.total_transactions, 0) AS total_transactions,
    COALESCE(ta.avg_transaction_amount, 0) AS avg_transaction_amount,
    COALESCE(ta.total_spent, 0) AS total_spent,
    COALESCE(ta.recency_days, 999) AS recency_days,
    COALESCE(ra.avg_amount_last_3m, 0) AS avg_amount_last_3m,
    COALESCE(fr.frequency_last_3m, 0) AS frequency_last_3m,
    c.churn
FROM analytics.customers c
LEFT JOIN transaction_agg ta ON c.customer_id = ta.customer_id
LEFT JOIN rolling_avg ra ON c.customer_id = ra.customer_id
LEFT JOIN frequency fr ON c.customer_id = fr.customer_id
LEFT JOIN tenure_segments ts ON c.customer_id = ts.customer_id;

-- Add a primary key for convenience
ALTER TABLE analytics.customer_features ADD PRIMARY KEY (customer_id);

-- Create an index for faster queries
CREATE INDEX idx_customer_features_churn ON analytics.customer_features(churn);

-- Display the first 10 rows (for verification)
SELECT * FROM analytics.customer_features LIMIT 10;