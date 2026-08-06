"""
Project: Customer 360 Analytics Platform
Author: Mahinul Mannan
Role: Data Scientist / Machine Learning Engineer
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import os

# Page config
st.set_page_config(
    page_title="Churn Prediction Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Header with Dark Grey Background ---
st.markdown("""
    <div style='
        background-color: #2d2d2d; 
        padding: 1rem; 
        border-radius: 8px; 
        margin-bottom: 2rem;
        text-align: center;
    '>
        <h1 style='color: #ffffff; margin: 0;'>📊 Customer Churn Prediction Dashboard</h1>
        <p style='color: #e0e0e0; margin: 0; font-weight: 500;'>
            <strong>Author:</strong> Mahinul Mannan | 
            <strong>Role:</strong> Data Scientist / Machine Learning Engineer
        </p>
    </div>
""", unsafe_allow_html=True)

# Create two columns: Input and Results
col1, col2 = st.columns(2)

# --- Input Section (col1) ---
with col1:
    st.subheader("Customer Data Input")
    
    with st.form("prediction_form"):
        tenure = st.number_input("Tenure (months)", min_value=0, max_value=72, value=12)
        monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, max_value=200.0, value=70.0)
        total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=840.0)
        
        tenure_segment = st.selectbox("Tenure Segment", ["New", "Mid", "Long"])
        contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
        paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        payment_method = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
        
        total_transactions = st.number_input("Total Transactions", min_value=0, value=10)
        avg_transaction_amount = st.number_input("Avg Transaction Amount ($)", min_value=0.0, value=15.5)
        total_spent = st.number_input("Total Spent ($)", min_value=0.0, value=155.0)
        recency_days = st.number_input("Recency (days since last transaction)", min_value=0, value=5)
        avg_amount_last_3m = st.number_input("Avg Amount Last 3 Months ($)", min_value=0.0, value=16.2)
        frequency_last_3m = st.number_input("Frequency Last 3 Months", min_value=0, value=4)
        
        submitted = st.form_submit_button("🔮 Predict Churn")

# --- Results Section (col2) ---
with col2:
    st.subheader("Prediction Results")
    
    if submitted:
        input_data = {
            "tenure": tenure,
            "monthly_charges": monthly_charges,
            "total_charges": total_charges,
            "tenure_segment": tenure_segment,
            "contract": contract,
            "paperless_billing": paperless_billing,
            "payment_method": payment_method,
            "total_transactions": total_transactions,
            "avg_transaction_amount": avg_transaction_amount,
            "total_spent": total_spent,
            "recency_days": recency_days,
            "avg_amount_last_3m": avg_amount_last_3m,
            "frequency_last_3m": frequency_last_3m
        }
        
        try:
            response = requests.post("http://localhost:8000/predict", json=input_data)
            
            if response.status_code == 200:
                result = response.json()
                prob = result["churn_probability"]
                pred = result["churn_prediction"]
                
                st.metric("Churn Probability", f"{prob:.2%}")
                
                if pred == "Yes":
                    st.error("⚠️ Churn Predicted")
                else:
                    st.success("✅ No Churn Predicted")
                
                st.markdown("---")
                st.markdown("**Interpretation:**")
                if prob < 0.3:
                    st.info("🟢 Low risk customer. No action needed.")
                elif prob < 0.7:
                    st.warning("🟡 Medium risk. Monitor closely.")
                else:
                    st.error("🔴 High risk. Immediate retention action recommended!")
                
                fig = px.bar(x=["Churn Risk"], y=[prob], 
                             color=[prob], 
                             color_continuous_scale="RdYlGn_r",
                             range_color=[0, 1],
                             labels={"y": "Probability"},
                             height=150)
                fig.update_layout(showlegend=False, yaxis_range=[0, 1])
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error(f"API Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to API. Make sure FastAPI is running on port 8000.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("👈 Enter customer data and click 'Predict Churn'")

# --- Analytics Section ---
st.markdown("---")
st.subheader("📈 Model Performance Summary")

try:
    artifacts_path = "artifacts/"
    if os.path.exists(f"{artifacts_path}permutation_importance.csv"):
        perm_df = pd.read_csv(f"{artifacts_path}permutation_importance.csv")
        st.dataframe(perm_df.head(10), use_container_width=True)
        
        fig = px.bar(perm_df.head(10), x="feature", y="importance",
                     title="Top 10 Feature Importance (Permutation)",
                     labels={"importance": "Importance", "feature": "Feature"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run model training first to see feature importance.")
except Exception as e:
    st.info("Feature importance not available yet.")

# --- Footer with Dark Grey Background ---
st.markdown("---")
st.markdown("""
    <div style='
        background-color: #2d2d2d; 
        padding: 1rem; 
        border-radius: 8px; 
        margin-top: 1rem;
        text-align: center;
    '>
        <p style='color: #ffffff; margin: 0; font-weight: bold;'>
            © Mahinul Mannan | Data Scientist / Machine Learning Engineer
        </p>
        <p style='color: #e0e0e0; margin: 0.25rem 0 0 0; font-size: 0.8rem;'>
            Customer 360 Analytics Platform | End-to-End ML with XGBoost, FastAPI, Streamlit &amp; RAG
        </p>
    </div>
""", unsafe_allow_html=True)