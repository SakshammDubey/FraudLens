import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# --------------------------------------------------
# 1. PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "raw" / "train_transaction.csv"
MODEL_DIR = ROOT / "ml" / "artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "fraud_model.joblib"
METRICS_PATH = MODEL_DIR / "baseline_metrics.json"


# --------------------------------------------------
# 2. SELECT BASELINE FEATURES
# --------------------------------------------------

numeric_features = [
    "TransactionAmt",
    "card1",
    "card2",
    "card3",
    "card5",
    "addr1",
    "dist1",
    "C1",
    "C2",
    "C3",
    "C5",
    "C6",
    "C9",
    "D1",
    "D2",
    "D3",
    "D4",
    "D10",
    "D15",
]

categorical_features = [
    "ProductCD",
    "card4",
    "card6",
    "P_emaildomain",
]

feature_columns = numeric_features + categorical_features
required_columns = [
    "TransactionID",
    "TransactionDT",
    "isFraud",
] + feature_columns


# --------------------------------------------------
# 3. LOAD SELECTED DATA
# --------------------------------------------------

print("Loading selected transaction features...")

df = pd.read_csv(
    DATA_PATH,
    usecols=required_columns,
    low_memory=False,
)

df = df.dropna(subset=["isFraud", "TransactionDT"])
df = df.sort_values("TransactionDT").reset_index(drop=True)

print(f"Rows loaded: {len(df):,}")
print(f"Features selected: {len(feature_columns)}")


# --------------------------------------------------
# 4. CHRONOLOGICAL TRAIN/VALIDATION SPLIT
# --------------------------------------------------

split_index = int(len(df) * 0.80)

train_df = df.iloc[:split_index]
valid_df = df.iloc[split_index:]

X_train = train_df[feature_columns]
y_train = train_df["isFraud"].astype(int)

X_valid = valid_df[feature_columns]
y_valid = valid_df["isFraud"].astype(int)

print(f"Training rows: {len(X_train):,}")
print(f"Validation rows: {len(X_valid):,}")
print(f"Training fraud rate: {y_train.mean():.2%}")
print(f"Validation fraud rate: {y_valid.mean():.2%}")


# --------------------------------------------------
# 5. PREPROCESSING
# --------------------------------------------------

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    (
        "encoder",
        OneHotEncoder(
            handle_unknown="ignore",
            min_frequency=100,
        ),
    ),
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features),
])


# --------------------------------------------------
# 6. MODEL
# --------------------------------------------------

model = Pipeline([
    ("preprocessor", preprocessor),
    (
        "classifier",
        LogisticRegression(
            class_weight="balanced",
            max_iter=500,
            solver="liblinear",
            random_state=42,
        ),
    ),
])


# --------------------------------------------------
# 7. TRAIN
# --------------------------------------------------

print("\nTraining baseline model...")
model.fit(X_train, y_train)

print("Training complete.")


# --------------------------------------------------
# 8. EVALUATE
# --------------------------------------------------

probabilities = model.predict_proba(X_valid)[:, 1]

# Initial operating threshold; tune using validation results.
threshold = 0.50
predictions = (probabilities >= threshold).astype(int)

metrics = {
    "model": "LogisticRegression",
    "split": "chronological_80_20",
    "threshold": threshold,
    "training_rows": int(len(X_train)),
    "validation_rows": int(len(X_valid)),
    "training_fraud_rate": round(float(y_train.mean()), 6),
    "validation_fraud_rate": round(float(y_valid.mean()), 6),
    "precision": float(precision_score(
        y_valid, predictions, zero_division=0
    )),
    "recall": float(recall_score(
        y_valid, predictions, zero_division=0
    )),
    "f1": float(f1_score(
        y_valid, predictions, zero_division=0
    )),
    "average_precision_pr_auc": float(
        average_precision_score(y_valid, probabilities)
    ),
    "roc_auc": float(roc_auc_score(y_valid, probabilities)),
    "confusion_matrix": confusion_matrix(
        y_valid, predictions
    ).tolist(),
    "classification_report": classification_report(
        y_valid,
        predictions,
        output_dict=True,
        zero_division=0,
    ),
    "features": feature_columns,
}

print("\n========== BASELINE RESULTS ==========")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall:    {metrics['recall']:.4f}")
print(f"F1 score:  {metrics['f1']:.4f}")
print(f"PR-AUC:    {metrics['average_precision_pr_auc']:.4f}")
print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
print("\nConfusion matrix:")
print(metrics["confusion_matrix"])


# --------------------------------------------------
# 9. SAVE MODEL AND METRICS
# --------------------------------------------------

joblib.dump(model, MODEL_PATH)

with open(METRICS_PATH, "w", encoding="utf-8") as file:
    json.dump(metrics, file, indent=4)

print("\nSaved model:", MODEL_PATH)
print("Saved metrics:", METRICS_PATH)
