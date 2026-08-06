"""
Load Telco Customer Churn dataset (Excel format) into PostgreSQL
Fixed column mapping: 'Monthly Charges' -> 'monthly_charges'
"""
import pandas as pd
from sqlalchemy import create_engine

# Database connection parameters
DB_USER = "admin"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "customer_360"

# Local Excel file path
file_path = "data/Telco_customer_churn.xlsx"

# --- Step 1: Read the Excel file ---
try:
    df = pd.read_excel(file_path, sheet_name="Telco_Churn")
    print(f"✅ Dataset loaded from Excel. Shape: {df.shape}")
except Exception as e:
    print(f"❌ Error reading Excel file: {e}")
    exit(1)

# --- Step 2: Clean column names (strip spaces) ---
df.columns = df.columns.str.strip()

# --- Step 3: Rename columns using correct mapping ---
column_mapping = {
    'CustomerID': 'customer_id',
    'Gender': 'gender',
    'Senior Citizen': 'senior_citizen',
    'Partner': 'partner',
    'Dependents': 'dependents',
    'Tenure Months': 'tenure',
    'Phone Service': 'phone_service',
    'Multiple Lines': 'multiple_lines',
    'Internet Service': 'internet_service',
    'Online Security': 'online_security',
    'Online Backup': 'online_backup',
    'Device Protection': 'device_protection',
    'Tech Support': 'tech_support',
    'Streaming TV': 'streaming_tv',
    'Streaming Movies': 'streaming_movies',
    'Contract': 'contract',
    'Paperless Billing': 'paperless_billing',
    'Payment Method': 'payment_method',
    'Monthly Charges': 'monthly_charges',   # ✅ FIXED: correct column name
    'Total Charges': 'total_charges',
    'Churn Label': 'churn'
}

# Apply renaming
df.rename(columns=column_mapping, inplace=True)

# --- Step 4: Verify required columns exist ---
required_cols = ['monthly_charges', 'tenure', 'total_charges']
missing = [col for col in required_cols if col not in df.columns]
if missing:
    print(f"❌ Still missing: {missing}")
    print("Available columns:", df.columns.tolist())
    exit(1)

# --- Step 5: Clean data ---
df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce')
df['total_charges'] = df['total_charges'].fillna(df['monthly_charges'] * df['tenure'])

# --- Step 6: Select only needed columns ---
columns_needed = [
    'customer_id', 'gender', 'senior_citizen', 'partner', 'dependents',
    'tenure', 'phone_service', 'multiple_lines', 'internet_service',
    'online_security', 'online_backup', 'device_protection', 'tech_support',
    'streaming_tv', 'streaming_movies', 'contract', 'paperless_billing',
    'payment_method', 'monthly_charges', 'total_charges', 'churn'
]

# Ensure all columns exist (add missing ones with None if needed)
for col in columns_needed:
    if col not in df.columns:
        df[col] = None

df = df[columns_needed]

print(f"✅ Data cleaned. Rows ready to insert: {len(df)}")

# --- Step 7: Load into PostgreSQL ---
try:
    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_str)
    
    df.to_sql('customers', engine, schema='analytics', if_exists='replace', index=False, method='multi', chunksize=1000)
    print(f"✅ Successfully loaded {len(df)} records into analytics.customers")
    
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)