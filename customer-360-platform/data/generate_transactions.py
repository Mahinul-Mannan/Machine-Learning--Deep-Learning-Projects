"""
Generate synthetic transaction data for all customers
Patterns:
- Higher tenure = more transactions
- Churned customers have fewer transactions in the last 2 months
- Transaction amount varies around monthly_charges/4
"""
import psycopg2
import random
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm  # optional, for progress bar

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port="5433",
    database="customer_360",
    user="admin",
    password="admin123"
)
cursor = conn.cursor()

# Step 1: Fetch all customers
print("📥 Fetching customers...")
df = pd.read_sql("SELECT customer_id, tenure, monthly_charges, churn FROM analytics.customers", conn)

# Step 2: Prepare transaction data
transactions = []
print("🔄 Generating transactions...")

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Customers"):
    customer_id = row['customer_id']
    tenure = int(row['tenure'])
    monthly = float(row['monthly_charges'])
    churn = row['churn']
    
    # Number of transactions: base + tenure effect
    # Customers with 0 tenure (new) get 0-2 transactions
    if tenure == 0:
        num_tx = random.randint(1, 3)
    else:
        # Higher tenure = more transactions (up to ~60)
        num_tx = random.randint(max(2, tenure // 3), max(5, tenure // 2 + 5))
    
    # Ensure at least 1 transaction
    num_tx = max(1, num_tx)
    
    # Generate random dates within the tenure period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=tenure * 30)  # approximate days
    
    for _ in range(num_tx):
        # Random date within the tenure period
        random_days = random.randint(0, max(1, tenure * 30))
        tx_date = start_date + timedelta(days=random_days)
        
        # Amount: fluctuate around monthly/4 (0.5x to 1.5x)
        base_amt = monthly / 4
        amount = round(random.uniform(base_amt * 0.5, base_amt * 1.8), 2)
        
        # If churn = Yes, drastically reduce transactions in the last 60 days
        if churn == 'Yes':
            last_60_days = datetime.now() - timedelta(days=60)
            if tx_date > last_60_days:
                # 70% chance to skip transaction if churned and date is recent
                if random.random() < 0.7:
                    continue
        
        transactions.append({
            'customer_id': customer_id,
            'transaction_date': tx_date.strftime('%Y-%m-%d'),
            'amount': amount,
            'transaction_type': random.choice(['Purchase', 'Refund', 'Upgrade'])
        })

print(f"✅ Generated {len(transactions)} transactions.")

# Step 3: Insert into PostgreSQL in batches
print("📤 Inserting into database...")
insert_query = """
INSERT INTO analytics.transactions (customer_id, transaction_date, amount, transaction_type)
VALUES (%s, %s, %s, %s)
"""

batch_size = 1000
for i in range(0, len(transactions), batch_size):
    batch = transactions[i:i+batch_size]
    # Convert to list of tuples
    values = [(t['customer_id'], t['transaction_date'], t['amount'], t['transaction_type']) for t in batch]
    cursor.executemany(insert_query, values)
    conn.commit()
    print(f"✅ Inserted {i+len(batch)} records...")

cursor.close()
conn.close()
print("🎉 Done! Synthetic transactions loaded successfully.")