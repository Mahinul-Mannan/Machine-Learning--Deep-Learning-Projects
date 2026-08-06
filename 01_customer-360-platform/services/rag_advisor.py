"""
Project: Customer 360 Analytics Platform
Author: Mahinul Mannan
Role: Data Scientist / Machine Learning Engineer
Description: RAG-based Retention Advisor using SHAP outputs and company policies.
"""
import json
import requests
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import joblib
import shap
import psycopg2
import warnings
warnings.filterwarnings('ignore')

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "retention_policies"
EMBEDDING_MODEL = "BAAI/bge-m3"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"

class RetentionAdvisor:
    def __init__(self):
        """Initialize embedding model."""
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self.model = None
        self.label_encoders = None
        self.feature_names = None
        
    def load_model_artifacts(self):
        """Load the trained model and encoders."""
        self.model = joblib.load("artifacts/xgboost_model.pkl")
        self.label_encoders = joblib.load("artifacts/label_encoders.pkl")
        self.feature_names = self.model.get_booster().feature_names
        print("✅ Model and artifacts loaded.")
        
    def get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Fetch customer data from PostgreSQL."""
        conn = psycopg2.connect(
            host="localhost", port="5433",
            database="customer_360",
            user="admin", password="admin123"
        )
        cursor = conn.cursor()
        query = "SELECT * FROM analytics.customer_features WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise ValueError(f"Customer {customer_id} not found.")
        
        columns = ['customer_id', 'tenure', 'tenure_segment', 'monthly_charges', 'total_charges',
                   'contract', 'paperless_billing', 'payment_method', 'total_transactions',
                   'avg_transaction_amount', 'total_spent', 'recency_days',
                   'avg_amount_last_3m', 'frequency_last_3m', 'churn']
        return dict(zip(columns, row))
    
    def get_shap_explanation(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SHAP values for a customer."""
        input_df = pd.DataFrame([customer_data])[self.feature_names]

        numeric_cols = ['avg_transaction_amount', 'total_spent', 'avg_amount_last_3m']
        for col in numeric_cols:
            if col in input_df.columns:
                input_df[col] = pd.to_numeric(input_df[col], errors='coerce')

        for col in ['tenure_segment', 'contract', 'paperless_billing', 'payment_method']:
            if col in input_df.columns:
                le = self.label_encoders[col]
                input_df[col] = le.transform(input_df[col].astype(str))

        for col in input_df.columns:
            if input_df[col].dtype == 'object':
                input_df[col] = pd.to_numeric(input_df[col], errors='coerce')

        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(input_df)

        feature_importance = dict(zip(self.feature_names, shap_values[0]))
        sorted_features = sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)

        return {
            "top_3_features": sorted_features[:3],
            "full_shap": feature_importance
        }
    
    def retrieve_policies(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve relevant policy chunks from Qdrant using direct HTTP API."""
        # Generate embedding for the query
        query_vector = self.encoder.encode(query).tolist()
        
        # Prepare REST API request
        url = f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}/points/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "vector": query_vector,
            "limit": top_k,
            "with_payload": True
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()
            
            # Extract text from results
            results = data.get("result", [])
            policies = [hit["payload"]["text"] for hit in results if "payload" in hit and "text" in hit["payload"]]
            return policies
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Qdrant. Make sure it's running on port 6333.")
            return []
        except Exception as e:
            print(f"⚠️ Qdrant API error: {e}")
            return []
    
    def generate_advice(self, customer_data: Dict[str, Any], shap_explanation: Dict, policies: List[str]) -> str:
        """Generate retention advice using Ollama LLM."""
        top_features = shap_explanation["top_3_features"]
        feature_text = "\n".join([f"- {feat}: {float(val):.4f}" for feat, val in top_features])
        
        # If no policies retrieved, use a default fallback
        if not policies:
            policies = ["General Retention Policy: Focus on reducing monthly charges and improving contract terms for high-risk customers."]
        
        context = f"""
Customer Profile:
- Tenure: {customer_data['tenure']} months
- Contract: {customer_data['contract']}
- Monthly Charges: ${customer_data['monthly_charges']:.2f}
- Total Transactions: {customer_data['total_transactions']}
- Recency: {customer_data['recency_days']} days since last transaction

Key Drivers for Churn (SHAP analysis):
{feature_text}

Company Retention Policies:
{chr(10).join(policies)}

Based on the above, generate a personalized retention strategy for this customer. Be specific and actionable.
Keep the response concise (max 150 words).
"""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": context,
            "stream": False,
            "temperature": 0.7
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("response", "No response from model.")
            else:
                return f"Error generating advice: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    advisor = RetentionAdvisor()
    advisor.load_model_artifacts()
    
    customer_id = "3668-QPYBK"
    print(f"\n🔍 Analyzing customer: {customer_id}")
    
    try:
        customer_data = advisor.get_customer_data(customer_id)
        print(f"✅ Customer data loaded.")
        
        shap_explanation = advisor.get_shap_explanation(customer_data)
        print(f"✅ SHAP analysis complete.")
        print(f"   Top drivers: {[(feat, float(val)) for feat, val in shap_explanation['top_3_features']]}")
        
        top_driver = shap_explanation['top_3_features'][0][0]
        policies = advisor.retrieve_policies(top_driver, top_k=3)
        print(f"✅ Retrieved {len(policies)} policy chunks.")
        
        print("\n🤖 Generating AI Retention Advice...")
        advice = advisor.generate_advice(customer_data, shap_explanation, policies)
        
        print("\n" + "="*60)
        print("💡 RETENTION ADVISORY:")
        print("="*60)
        print(advice)
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()