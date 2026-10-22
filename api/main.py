
from pathlib import Path

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.auth import get_current_user, router as auth_router

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "raw" / "train_transaction.csv"
MODEL_PATH = ROOT / "ml" / "artifacts" / "fraud_model.joblib"

NUMERIC_FEATURES = [
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

CATEGORICAL_FEATURES = [
    "ProductCD",
    "card4",
    "card6",
    "P_emaildomain",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

COLUMNS = [
    "TransactionID",
    "TransactionDT",
    "TransactionAmt",
    "ProductCD",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "addr1",
    "dist1",
    "P_emaildomain",
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

app = FastAPI(
    title="FraudLens API",
    description=(
        "Baseline fraud scoring and transaction "
        "investigation prototype"
    ),
    version="0.2.0",
)

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
transactions = None


@app.on_event("startup")
def load_resources():
    global model, transactions

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model not found: {MODEL_PATH}. "
            "Train the model first."
        )

    if not DATA_PATH.exists():
        raise RuntimeError(
            f"Transaction dataset not found: {DATA_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    transactions = pd.read_csv(
        DATA_PATH,
        usecols=COLUMNS,
        low_memory=False,
    )

    transactions = transactions.set_index(
        "TransactionID",
        drop=False,
    )

    print(
        f"FraudLens loaded "
        f"{len(transactions):,} historical transactions."
    )


@app.get("/health")
def health():
    return {
        "status": (
            "ok"
            if model is not None and transactions is not None
            else "loading"
        ),
        "model_loaded": model is not None,
        "transactions_loaded": transactions is not None,
    }


def _score_rows(subset: pd.DataFrame) -> list[dict]:
    if subset.empty:
        return []

    probabilities = model.predict_proba(
        subset[FEATURES]
    )[:, 1]

    records = []

    for (_, row), probability in zip(
        subset.iterrows(),
        probabilities,
    ):
        score = float(probability)

        records.append(
            {
                "transaction_id": int(row["TransactionID"]),
                "amount": round(
                    float(row["TransactionAmt"]),
                    2,
                ),
                "product": (
                    str(row["ProductCD"])
                    if pd.notna(row["ProductCD"])
                    else "Unknown"
                ),
                "transaction_dt": int(row["TransactionDT"]),
                "fraud_probability": round(score, 6),
                "risk_score": round(score * 100, 2),
                "prediction": (
                    "fraud"
                    if score >= 0.50
                    else "legitimate"
                ),
            }
        )

    return records


@app.get("/public/feed")
def public_feed(
    limit: int = Query(default=8, ge=1, le=12),
):
    if transactions is None or model is None:
        raise HTTPException(
            status_code=503,
            detail="Feed is unavailable",
        )

    subset = transactions.iloc[::-1].iloc[:limit]

    return {
        "mode": "historical_replay",
        "label": "Historical dataset replay",
        "events": _score_rows(subset),
    }


@app.get(
    "/transactions",
    dependencies=[Depends(get_current_user)],
)
def list_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    if transactions is None or model is None:
        raise HTTPException(
            status_code=503,
            detail="Service is not ready",
        )

    subset = transactions.iloc[::-1].iloc[
        offset:offset + limit
    ]

    return {
        "total": len(transactions),
        "count": len(subset),
        "offset": offset,
        "transactions": _score_rows(subset),
    }


@app.get(
    "/investigate/{transaction_id}",
    dependencies=[Depends(get_current_user)],
)
def investigate(transaction_id: int):
    if model is None or transactions is None:
        raise HTTPException(
            status_code=503,
            detail="Service is not ready",
        )

    if transaction_id not in transactions.index:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    row = transactions.loc[transaction_id]

    features = pd.DataFrame(
        [row[FEATURES].to_dict()],
        columns=FEATURES,
    )

    probability = float(
        model.predict_proba(features)[0, 1]
    )

    prediction = (
        "fraud"
        if probability >= 0.50
        else "legitimate"
    )

    observations = []

    for column, label in [
        ("card4", "Card brand information is missing"),
        ("card6", "Card type information is missing"),
        (
            "P_emaildomain",
            "Purchaser email domain is unavailable",
        ),
    ]:
        if pd.isna(row[column]):
            observations.append(label)

    return {
        "transaction_id": int(transaction_id),
        "amount": round(float(row["TransactionAmt"]), 2),
        "product": (
            str(row["ProductCD"])
            if pd.notna(row["ProductCD"])
            else "Unknown"
        ),
        "transaction_dt": int(row["TransactionDT"]),
        "fraud_probability": round(probability, 6),
        "risk_score": round(probability * 100, 2),
        "prediction": prediction,
        "threshold": 0.50,
        "investigation": {
            "status": (
                "review_required"
                if prediction == "fraud"
                else "not_flagged_by_baseline"
            ),
            "observations": observations,
            "explanation": (
                "The score is produced by the baseline ML model. "
                "Observations describe data availability and are "
                "not claimed to cause the prediction."
            ),
        },
    }