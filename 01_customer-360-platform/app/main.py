"""
Project: Customer 360 Analytics Platform
Author: Mahinul Mannan
Role: Data Scientist / Machine Learning Engineer
Description: End-to-End ML pipeline for churn prediction with RAG advisory layer.
"""

"""
FastAPI Backend for Churn Prediction Model
Endpoints: /health, /predict
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from typing import List

app = FastAPI(title="Churn Prediction API", version="1.0.0")

# Global variables
model = None
label_encoders = None
feature_names = None

# Define input schema
class CustomerInput(BaseModel):
    tenure: int
    monthly_charges: float
    total_charges: float
    tenure_segment: str
    contract: str
    paperless_billing: str
    payment_method: str
    total_transactions: int
    avg_transaction_amount: float
    total_spent: float
    recency_days: int
    avg_amount_last_3m: float
    frequency_last_3m: int

@app.on_event("startup")
def load_artifacts():
    global model, label_encoders, feature_names
    artifacts_path = "artifacts"
    if not os.path.exists(artifacts_path):
        raise Exception("Artifacts folder not found! Run training first.")
    try:
        model = joblib.load(f"{artifacts_path}/xgboost_model.pkl")
        label_encoders = joblib.load(f"{artifacts_path}/label_encoders.pkl")
        feature_names = [
    'tenure', 'tenure_segment', 'monthly_charges', 'total_charges',
    'contract', 'paperless_billing', 'payment_method', 'total_transactions',
    'avg_transaction_amount', 'total_spent', 'recency_days',
    'avg_amount_last_3m', 'frequency_last_3m'
]
        print("✅ Model and artifacts loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading artifacts: {e}")
        raise e

@app.get("/health")
def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict")
def predict(customer: CustomerInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        input_dict = customer.dict()
        for col in ['tenure_segment', 'contract', 'paperless_billing', 'payment_method']:
            if col in input_dict:
                le = label_encoders[col]
                try:
                    input_dict[col] = le.transform([input_dict[col]])[0]
                except ValueError:
                    input_dict[col] = le.transform([le.classes_[0]])[0]
        input_df = pd.DataFrame([input_dict])[feature_names]
        prob = float(model.predict_proba(input_df)[0, 1])
        pred_class = int(prob >= 0.5)
        return {
            "churn_probability": round(prob, 4),
            "churn_prediction": "Yes" if pred_class == 1 else "No"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")