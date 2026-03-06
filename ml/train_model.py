"""
XGBoost credit risk model training script.
Loads synthetic data, engineers features, trains with stratified split,
and saves model + SHAP explainer + feature importance chart.
"""

import os
import sys
import pickle
import logging

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)

try:
    from ml.features import engineer_features, get_feature_names
except ModuleNotFoundError:
    # Support direct execution: python ml/train_model.py
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from ml.features import engineer_features, get_feature_names

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train():
    """Train the XGBoost credit risk model and save artifacts."""
    # Load data
    data_path = os.path.join(os.path.dirname(__file__), "data", "synthetic_credit_data.csv")
    if not os.path.exists(data_path):
        logger.info("Generating synthetic data first...")
        try:
            from ml.synthetic_data import main as generate_data
        except ModuleNotFoundError:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from ml.synthetic_data import main as generate_data
        generate_data()

    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} samples")

    # Engineer features
    X = engineer_features(df)
    y = df["stress_label"]

    # Stratified 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Train XGBoost
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
        use_label_encoder=False,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc_roc = roc_auc_score(y_test, y_prob)

    print("\n" + "=" * 50)
    print("  INTELLI-CREDIT XGBoost Model Performance")
    print("=" * 50)
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  AUC-ROC:   {auc_roc:.4f}")
    print("=" * 50)
    print("\n" + classification_report(y_test, y_pred, target_names=["Healthy", "Stress"]))

    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "xgb_credit_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ Model saved to: {model_path}")

    # Save SHAP explainer
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        explainer_path = os.path.join(model_dir, "shap_explainer.pkl")
        with open(explainer_path, "wb") as f:
            pickle.dump(explainer, f)
        print(f"✅ SHAP explainer saved to: {explainer_path}")
    except Exception as e:
        logger.warning(f"SHAP explainer save failed: {e}")

    # Save feature importance chart
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        feature_names = get_feature_names()
        importances = model.feature_importances_
        sorted_idx = np.argsort(importances)

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(
            [feature_names[i] for i in sorted_idx],
            importances[sorted_idx],
            color="#1e40af",
        )
        ax.set_xlabel("Feature Importance (Gain)")
        ax.set_title("Intelli-Credit — XGBoost Feature Importance")
        plt.tight_layout()

        chart_path = os.path.join(model_dir, "feature_importance.png")
        plt.savefig(chart_path, dpi=150)
        plt.close()
        print(f"✅ Feature importance chart saved to: {chart_path}")
    except Exception as e:
        logger.warning(f"Chart generation failed: {e}")


if __name__ == "__main__":
    train()
