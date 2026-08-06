"""
XGBoost Churn Prediction Pipeline
- Loads data from PostgreSQL
- Trains and tunes XGBoost with Optuna
- Evaluates with multiple metrics
- Generates SHAP and Permutation Importance
- Logs everything to MLflow
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)
from sklearn.calibration import calibration_curve  # ✅ Fixed import
from sklearn.inspection import permutation_importance
import xgboost as xgb
import optuna
import shap
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Database connection parameters
DB_USER = "admin"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "customer_360"

# --- 1. Load feature table from PostgreSQL ---
def load_data():
    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_str)
    query = "SELECT * FROM analytics.customer_features"
    df = pd.read_sql(query, engine)
    return df

df = load_data()
print(f"Dataset shape: {df.shape}")
print(f"Churn distribution:\n{df['churn'].value_counts()}")

# --- 2. Preprocess data ---
# Drop customer_id as it is not a feature
df = df.drop(columns=['customer_id'])

# Encode categorical columns
categorical_cols = ['tenure_segment', 'contract', 'paperless_billing', 'payment_method']
le_dict = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    le_dict[col] = le

# Separate features and target
X = df.drop(columns=['churn'])
y = df['churn'].map({'Yes': 1, 'No': 0}).astype(int)

# Stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set size: {X_train.shape}")
print(f"Test set size: {X_test.shape}")
print(f"Train churn rate: {y_train.mean():.4f}")
print(f"Test churn rate: {y_test.mean():.4f}")

# --- 3. XGBoost Objective for Optuna ---
def objective(trial):
    param = {
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0.0, 5.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 2.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 3.0),
        'scale_pos_weight': trial.suggest_float('scale_pos_weight', 1, 5),
        'random_state': 42,
        'eval_metric': 'logloss'
    }
    model = xgb.XGBClassifier(**param)
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    return roc_auc_score(y_test, y_pred_prob)

# --- 4. Run Optuna tuning ---
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=30, timeout=600)

best_params = study.best_params
print("Best parameters found by Optuna:")
print(best_params)

# --- 5. Train final model with best params ---
final_model = xgb.XGBClassifier(**best_params, random_state=42, eval_metric='logloss')
final_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

# --- 6. Evaluation ---
y_pred_prob = final_model.predict_proba(X_test)[:, 1]
y_pred = (y_pred_prob >= 0.5).astype(int)

metrics = {
    'roc_auc': roc_auc_score(y_test, y_pred_prob),
    'pr_auc': average_precision_score(y_test, y_pred_prob),
    'f1': f1_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred),
    'recall': recall_score(y_test, y_pred),
    'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
}

print("Model Performance Metrics:")
for k, v in metrics.items():
    if k != 'confusion_matrix':
        print(f"{k}: {v:.4f}")
print(f"Confusion Matrix: {metrics['confusion_matrix']}")

# --- 7. SHAP Analysis ---
explainer = shap.TreeExplainer(final_model)
shap_values = explainer.shap_values(X_test)

# Plot SHAP summary
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test, show=False)
plt.savefig('artifacts/shap_summary.png', bbox_inches='tight')
plt.close()

# --- 8. Permutation Importance ---
perm_importance = permutation_importance(final_model, X_test, y_test, n_repeats=10, random_state=42)
perm_importance_df = pd.DataFrame({
    'feature': X_test.columns,
    'importance': perm_importance.importances_mean
}).sort_values('importance', ascending=False)

# --- 9. Calibration Curve ---
prob_true, prob_pred = calibration_curve(y_test, y_pred_prob, n_bins=10)
plt.figure(figsize=(8, 6))
plt.plot(prob_pred, prob_true, marker='o', label='XGBoost')
plt.plot([0, 1], [0, 1], linestyle='--', label='Perfect Calibration')
plt.xlabel('Mean predicted probability')
plt.ylabel('Fraction of positives')
plt.title('Calibration Curve')
plt.legend()
plt.savefig('artifacts/calibration_curve.png', bbox_inches='tight')
plt.close()

# --- 10. Save artifacts ---
os.makedirs('artifacts', exist_ok=True)
joblib.dump(final_model, 'artifacts/xgboost_model.pkl')
joblib.dump(le_dict, 'artifacts/label_encoders.pkl')
joblib.dump(best_params, 'artifacts/best_params.pkl')
perm_importance_df.to_csv('artifacts/permutation_importance.csv', index=False)

print("Artifacts saved to /artifacts folder.")

# --- 11. MLflow Tracking ---
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Customer_Churn_XGBoost")

with mlflow.start_run():
    mlflow.log_params(best_params)
    for k, v in metrics.items():
        if k != 'confusion_matrix':
            mlflow.log_metric(k, v)
    mlflow.log_metric('train_auc', roc_auc_score(y_train, final_model.predict_proba(X_train)[:, 1]))
    mlflow.log_artifact('artifacts/shap_summary.png')
    mlflow.log_artifact('artifacts/calibration_curve.png')
    mlflow.log_artifact('artifacts/permutation_importance.csv')
    mlflow.sklearn.log_model(final_model, "xgboost_churn_model")
    print("MLflow run logged successfully.")