
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from rag.retrieve import retrieve_context

from api.auth import get_current_user, router as auth_router

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "raw" / "train_transaction.csv"
MODEL_PATH = ROOT / "ml" / "artifacts" / "fraud_model.joblib"

THRESHOLD = 0.50

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

PROFILE_FIELDS = {
    "card1": ("Card identifier 1", "Card attributes"),
    "card2": ("Card identifier 2", "Card attributes"),
    "card3": ("Card identifier 3", "Card attributes"),
    "card4": ("Card brand", "Card attributes"),
    "card5": ("Card identifier 5", "Card attributes"),
    "card6": ("Card type", "Card attributes"),
    "addr1": ("Address identifier", "Address and distance"),
    "dist1": ("Distance feature", "Address and distance"),
    "P_emaildomain": ("Purchaser email domain", "Email attributes"),
    "C1": ("Count feature C1", "Behavioral features"),
    "C2": ("Count feature C2", "Behavioral features"),
    "C3": ("Count feature C3", "Behavioral features"),
    "C5": ("Count feature C5", "Behavioral features"),
    "C6": ("Count feature C6", "Behavioral features"),
    "C9": ("Count feature C9", "Behavioral features"),
    "D1": ("Time-delta feature D1", "Temporal features"),
    "D2": ("Time-delta feature D2", "Temporal features"),
    "D3": ("Time-delta feature D3", "Temporal features"),
    "D4": ("Time-delta feature D4", "Temporal features"),
    "D10": ("Time-delta feature D10", "Temporal features"),
    "D15": ("Time-delta feature D15", "Temporal features"),
}

FEATURE_LABELS = {
    "TransactionAmt": "Transaction amount",
    "ProductCD": "Product category",
    "card1": "Card identifier 1",
    "card2": "Card identifier 2",
    "card3": "Card identifier 3",
    "card4": "Card brand",
    "card5": "Card identifier 5",
    "card6": "Card type",
    "addr1": "Address identifier",
    "dist1": "Distance feature",
    "P_emaildomain": "Purchaser email domain",
    "C1": "Count feature C1",
    "C2": "Count feature C2",
    "C3": "Count feature C3",
    "C5": "Count feature C5",
    "C6": "Count feature C6",
    "C9": "Count feature C9",
    "D1": "Time-delta feature D1",
    "D2": "Time-delta feature D2",
    "D3": "Time-delta feature D3",
    "D4": "Time-delta feature D4",
    "D10": "Time-delta feature D10",
    "D15": "Time-delta feature D15",
}


# MAIN

app = FastAPI(
    title="FraudLens API",
    description=(
        "Baseline fraud scoring and transaction "
        "investigation prototype"
    ),
    version="0.4.0",
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


# LOAD MODEL AND TRANSACTION DATA

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

    # Verify the expected model pipeline structure.
    if not hasattr(model, "named_steps"):
        raise RuntimeError(
            "The saved model is not the expected "
            "scikit-learn Pipeline."
        )

    if (
        "preprocessor" not in model.named_steps
        or "classifier" not in model.named_steps
    ):
        raise RuntimeError(
            "The model pipeline must contain "
            "'preprocessor' and 'classifier' steps."
        )

    classifier = model.named_steps["classifier"]

    if not hasattr(classifier, "coef_") or not hasattr(
        classifier, "intercept_"
    ):
        raise RuntimeError(
            "The model classifier does not expose "
            "the coefficients required for explanations."
        )

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


# model logging check 

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


# 5. BASIC TRANSACTION SCORING

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
                    if score >= THRESHOLD
                    else "legitimate"
                ),
            }
        )

    return records


# JSON-SAFE DISPLAY VALUES

def _display_value(value):
    """Convert a dataset value to JSON-safe display data."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, (float, np.floating)):
        return round(float(value), 4)

    if isinstance(value, (int, np.integer)):
        return int(value)

    if isinstance(value, (bool, np.bool_)):
        return bool(value)

    if isinstance(value, str):
        return value

    return str(value)


# TRANSACTION PROFILE

def _build_transaction_profile(row) -> list[dict]:
    """Build a categorized profile from stored transaction fields."""
    profile = []

    for column, (label, category) in PROFILE_FIELDS.items():
        value = _display_value(row[column])

        profile.append(
            {
                "key": column,
                "label": label,
                "category": category,
                "value": value,
                "available": value is not None,
            }
        )

    return profile


# DATA QUALITY

def _build_data_quality(profile: list[dict]) -> dict:
    """Summarize completeness of the displayed profile."""
    total_fields = len(profile)

    available_fields = sum(
        1 for field in profile if field["available"]
    )

    missing_labels = [
        field["label"]
        for field in profile
        if not field["available"]
    ]

    completeness = (
        round(available_fields / total_fields * 100, 1)
        if total_fields
        else 0.0
    )

    return {
        "total_fields": total_fields,
        "available_fields": available_fields,
        "missing_fields": len(missing_labels),
        "completeness_percent": completeness,
        "missing_field_labels": missing_labels,
    }


# MISSING-DATA OBSERVATIONS

def _build_observations(row) -> list[str]:
    """Report missing values without interpreting them as fraud."""
    checks = [
        ("card4", "Card brand information is missing"),
        ("card6", "Card type information is missing"),
        (
            "P_emaildomain",
            "Purchaser email domain is unavailable",
        ),
        ("dist1", "Distance feature is unavailable"),
        ("addr1", "Address identifier is unavailable"),
    ]

    observations = []

    for column, message in checks:
        if pd.isna(row[column]):
            observations.append(message)

    return observations


# MODEL FEATURE CONTRIBUTIONS

def _original_feature_name(transformed_name: str) -> str:
    """
    Convert transformed ColumnTransformer names back to their
    original input feature names.

    Examples:
      numeric__TransactionAmt -> TransactionAmt
      categorical__card4_visa -> card4
      categorical__P_emaildomain_gmail.com -> P_emaildomain
    """
    if "__" in transformed_name:
        _, feature_name = transformed_name.split("__", 1)
    else:
        feature_name = transformed_name

    for feature in CATEGORICAL_FEATURES:
        if (
            feature_name == feature
            or feature_name.startswith(feature + "_")
        ):
            return feature

    if feature_name in NUMERIC_FEATURES:
        return feature_name

    return feature_name


def _build_feature_contributions(
    features: pd.DataFrame,
    probability: float,
) -> dict:
    """
    Explain one Logistic Regression prediction using coefficient
    contributions in log-odds space.

    For this binary Logistic Regression model:

        logit = intercept + sum(transformed_feature * coefficient)

    Each transformed contribution is then aggregated back to its
    original input field. These are model contributions, not causal
    explanations or proof of fraud.
    """
    if model is None:
        raise RuntimeError("Model is not loaded.")

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    transformed = preprocessor.transform(features)

    if hasattr(transformed, "toarray"):
        transformed_row = transformed.toarray()[0]
    else:
        transformed_row = np.asarray(transformed)[0]

    coefficients = np.asarray(classifier.coef_[0])
    intercept = float(classifier.intercept_[0])

    transformed_names = preprocessor.get_feature_names_out()

    if not (
        len(transformed_row)
        == len(coefficients)
        == len(transformed_names)
    ):
        raise RuntimeError(
            "The transformed features and model coefficients "
            "have inconsistent lengths."
        )

    # Each value is that transformed feature's contribution
    # to the classifier's linear log-odds score.
    raw_contributions = transformed_row * coefficients

    grouped = {}

    for name, contribution in zip(
        transformed_names,
        raw_contributions,
    ):
        original_name = _original_feature_name(str(name))

        grouped[original_name] = (
            grouped.get(original_name, 0.0)
            + float(contribution)
        )

    # Numerical consistency check:
    # intercept + sum(contributions) should equal the model logit.
    calculated_logit = intercept + float(
        np.sum(raw_contributions)
    )

    clipped_probability = float(
        np.clip(probability, 1e-12, 1 - 1e-12)
    )

    probability_logit = float(
        np.log(
            clipped_probability
            / (1 - clipped_probability)
        )
    )

    contribution_sum = float(sum(grouped.values()))

    # Round only for presentation, not during calculation.
    def _make_item(feature_name: str, value: float) -> dict:
        feature_value = features.iloc[0][feature_name]

        return {
            "key": feature_name,
            "label": FEATURE_LABELS.get(
                feature_name,
                feature_name,
            ),
            "value": _display_value(feature_value),
            "contribution": round(float(value), 6),
            "direction": (
                "increases_risk"
                if value > 0
                else "decreases_risk"
                if value < 0
                else "neutral"
            ),
        }

    contributions = [
        _make_item(name, value)
        for name, value in grouped.items()
        if abs(value) > 1e-10
    ]

    contributions.sort(
        key=lambda item: abs(item["contribution"]),
        reverse=True,
    )

    increasing = [
        item
        for item in contributions
        if item["contribution"] > 0
    ]

    decreasing = [
        item
        for item in contributions
        if item["contribution"] < 0
    ]

    # A positive log-odds contribution pushes the score toward
    # the fraud class; a negative contribution pushes it away.
    # This does not mean a field independently proves fraud.
    return {
        "method": "logistic_regression_coefficient_contributions",
        "unit": "log_odds",
        "intercept": round(intercept, 6),
        "calculated_logit": round(calculated_logit, 6),
        "probability_logit": round(probability_logit, 6),
        "contribution_sum": round(contribution_sum, 6),
        "consistency_check": bool(
            np.isclose(
                calculated_logit,
                probability_logit,
                atol=1e-5,
                rtol=1e-5,
            )
        ),
        "increases_risk": increasing[:5],
        "decreases_risk": decreasing[:5],
        "all_contributions": contributions,
        "interpretation": (
            "Positive contributions push this model's score "
            "toward the fraud class; negative contributions "
            "push it away. Contributions are measured in "
            "log-odds units. They describe this model's "
            "calculation, not causal effects or proof of fraud."
        ),
    }


# --------------------------------------------------
# 11. INVESTIGATION RECOMMENDATION
# --------------------------------------------------

def _build_recommendation(probability: float) -> str:
    if probability >= THRESHOLD:
        return (
            "Manual review recommended. Verify the transaction "
            "against trusted account and payment records before "
            "taking action. The model score alone is not sufficient "
            "to confirm fraud."
        )

    return (
        "The baseline model did not flag this transaction at the "
        "configured threshold. This does not guarantee that the "
        "transaction is legitimate. Apply normal verification "
        "procedures where appropriate."
    )


# --------------------------------------------------
# 12. PUBLIC HISTORICAL FEED
# --------------------------------------------------

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


# --------------------------------------------------
# 13. LIST TRANSACTIONS
# --------------------------------------------------

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


# --------------------------------------------------
# 14. TRANSACTION INVESTIGATION
# --------------------------------------------------

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

    risk_score = round(probability * 100, 2)

    prediction = (
        "fraud"
        if probability >= THRESHOLD
        else "legitimate"
    )

    observations = _build_observations(row)
    profile = _build_transaction_profile(row)
    data_quality = _build_data_quality(profile)

    feature_contributions = _build_feature_contributions(
        features,
        probability,
    )

    status = (
        "review_required"
        if probability >= THRESHOLD
        else "not_flagged_by_baseline"
    )

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
        "risk_score": risk_score,
        "prediction": prediction,
        "threshold": THRESHOLD,
        "investigation": {
            "status": status,
            "observations": observations,
            "explanation": (
                "The risk score is generated by the baseline "
                "Logistic Regression model. Risk evidence shows "
                "how transformed transaction features contribute "
                "to this individual model score. These contributions "
                "do not establish causation and are not proof of fraud."
            ),
            "feature_contributions": feature_contributions,
            "recommendation": _build_recommendation(probability),
            "transaction_profile": profile,
            "data_quality": data_quality,
            "limitations": [
                "The model score is an estimate, not proof of fraud.",
                (
                    "Feature contributions describe the model's "
                    "calculation, not causal explanations."
                ),
                "This report uses a historical dataset record.",
                (
                    "The transaction time is a dataset-relative "
                    "offset, not a verified calendar timestamp."
                ),
                (
                    "The classifier uses class_weight='balanced'; "
                    "its scores should not automatically be treated "
                    "as calibrated real-world fraud probabilities."
                ),
                (
                    "Human verification is required before taking "
                    "action against a transaction."
                ),
            ],
        },
    }

# FRAUDLENS INTELLIGENCE ASSISTANT — RAG

class InvestigationQuestion(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
        description="Question about a transaction investigation",
    )


@app.post(
    "/investigate/{transaction_id}/ask",
    dependencies=[Depends(get_current_user)],
)
def ask_investigation_question(
    transaction_id: int,
    body: InvestigationQuestion,
):
    if model is None or transactions is None:
        raise HTTPException(
            status_code=503,
            detail="FraudLens is not ready",
        )

    if transaction_id not in transactions.index:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    question = body.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty",
        )

    try:
        evidence = retrieve_context(question, top_k=4)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="The local fraud knowledge base is unavailable",
        ) from exc

    row = transactions.loc[transaction_id]

    features = pd.DataFrame(
        [row[FEATURES].to_dict()],
        columns=FEATURES,
    )

    probability = float(
        model.predict_proba(features)[0, 1]
    )

    sources = [
        {
            "source": item["source"],
            "chunk": item["chunk"],
            "text": item["text"],
            "distance": round(float(item["distance"]), 4),
        }
        for item in evidence
    ]

    return {
        "assistant": "FraudLens Intelligence Assistant",
        "transaction_id": int(transaction_id),
        "question": question,
        "transaction": {
            "amount": round(
                float(row["TransactionAmt"]), 2
            ),
            "product": (
                str(row["ProductCD"])
                if pd.notna(row["ProductCD"])
                else "Unknown"
            ),
            "risk_score": round(probability * 100, 2),
            "prediction": (
                "fraud"
                if probability >= THRESHOLD
                else "legitimate"
            ),
            "threshold": THRESHOLD,
        },
        "answer": (
            "Retrieved reference evidence is provided below. "
            "No generated answer is available yet; use these "
            "passages with the transaction details to support "
            "a grounded investigation."
        ),
        "evidence": sources,
        "evidence_count": len(sources),
        "disclaimer": (
            "A model risk score is not proof of fraud. "
            "Retrieved reference material is guidance, not "
            "independent evidence that this transaction is fraudulent."
        ),
    }

