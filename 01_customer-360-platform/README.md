# 🏢 Customer 360 Analytics Platform

**Churn Prediction & AI Retention Advisor**

---

## 👨‍💻 Author

**Mahinul Mannan**  
Data Scientist / Machine Learning Engineer

> *End-to-End ML platform with SQL Feature Engineering, XGBoost, SHAP Explainability, FastAPI, MLOps, and RAG-powered Retention Advisory.*

---

## 📌 Project Overview

This platform predicts customer churn and provides AI-generated retention strategies. It demonstrates a complete ML lifecycle:
- **Data Engineering**: PostgreSQL with advanced SQL (CTE, Window Functions, LAG/LEAD).
- **ML Modeling**: XGBoost with Optuna hyperparameter tuning (ROC-AUC: 0.90).
- **Explainability**: SHAP (Force, Waterfall, Summary plots) & Permutation Importance.
- **Backend API**: FastAPI with Swagger documentation.
- **UI**: Streamlit dashboard for real-time predictions.
- **GenAI**: RAG-powered advisor using Llama 3 (Ollama) and Qdrant.
- **MLOps**: Docker, MLflow, and GitHub Actions.

## 🛠️ Tech Stack

- **Data**: PostgreSQL, SQL (CTEs, Windows), Pandas
- **ML**: XGBoost, Optuna, Scikit-learn, SHAP
- **GenAI**: LangChain, Qdrant, Sentence-Transformers, Ollama
- **API**: FastAPI, Pydantic, Uvicorn
- **UI**: Streamlit, Plotly
- **MLOps**: Docker, MLflow, Git

## 🚀 Quick Start

1. Clone the repo and navigate to the folder.
2. Start services: `docker-compose up -d`
3. Install Python packages: `pip install -r requirements.txt`
4. Load data and features (run SQL scripts).
5. Train model: `python notebooks/01_xgboost_training.py`
6. Start API: `uvicorn app.main:app --reload --port 8000`
7. Start UI: `streamlit run ui/app.py`

## 📊 API Endpoints

- `GET /health` – Check service health.
- `POST /predict` – Get churn probability.
- `GET /docs` – Interactive Swagger UI.

## 🏁 Results

| Metric | Score |
| :--- | :--- |
| ROC-AUC | 0.901 |
| PR-AUC | 0.803 |
| F1-Score | 0.690 |

**Churn Drivers (Top 5):** Tenure, Contract Type, Monthly Charges, Payment Method, Total Transactions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.