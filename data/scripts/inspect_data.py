
import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PATHS AND CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRANSACTION_PATH = (
    PROJECT_ROOT / "data" / "raw" / "train_transaction.csv"
)
IDENTITY_PATH = (
    PROJECT_ROOT / "data" / "raw" / "train_identity.csv"
)

AUDIT_DIR = PROJECT_ROOT / "data" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 50_000


# --------------------------------------------------
# 2. VALIDATE INPUT FILES
# --------------------------------------------------

for path in [TRANSACTION_PATH, IDENTITY_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")


# --------------------------------------------------
# 3. LOAD IDENTITY IDS ONLY
# --------------------------------------------------

print("Loading identity TransactionIDs...")

identity_df = pd.read_csv(
    IDENTITY_PATH,
    usecols=["TransactionID"],
)

identity_ids = set(
    identity_df["TransactionID"].dropna().tolist()
)

identity_rows = len(identity_df)
identity_duplicate_count = int(
    identity_df["TransactionID"].duplicated().sum()
)

print(f"Identity rows: {identity_rows:,}")
print(f"Unique identity IDs: {len(identity_ids):,}")


# --------------------------------------------------
# 4. INITIALIZE TRANSACTION AUDIT
# --------------------------------------------------

total_rows = 0
fraud_count = 0
legitimate_count = 0
missing_target_count = 0

duplicate_transaction_count = 0
seen_transaction_ids = set()

matched_transaction_rows = 0

min_transaction_dt = None
max_transaction_dt = None
previous_last_dt = None
globally_ordered = True

missing_counts = None
column_count = None


# --------------------------------------------------
# 5. SCAN TRANSACTIONS IN CHUNKS
# --------------------------------------------------

print("\nScanning transaction dataset...")

for chunk_number, chunk in enumerate(
    pd.read_csv(
        TRANSACTION_PATH,
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ),
    start=1,
):
    total_rows += len(chunk)

    # Fraud label counts
    fraud_count += int((chunk["isFraud"] == 1).sum())
    legitimate_count += int((chunk["isFraud"] == 0).sum())
    missing_target_count += int(chunk["isFraud"].isna().sum())

    # Missing values for every column
    chunk_missing = chunk.isna().sum()

    if missing_counts is None:
        missing_counts = chunk_missing
        column_count = len(chunk.columns)
    else:
        missing_counts = missing_counts.add(
            chunk_missing,
            fill_value=0,
        )

    # Detect duplicate transaction IDs across and within chunks
    for transaction_id in chunk["TransactionID"].dropna():
        if transaction_id in seen_transaction_ids:
            duplicate_transaction_count += 1
        else:
            seen_transaction_ids.add(transaction_id)

    # Exact transaction-row coverage by identity data
    matched_transaction_rows += int(
        chunk["TransactionID"].isin(identity_ids).sum()
    )

    # TransactionDT range and chronological ordering
    times = chunk["TransactionDT"].dropna()

    if not times.empty:
        chunk_min = times.min()
        chunk_max = times.max()

        if (
            min_transaction_dt is None
            or chunk_min < min_transaction_dt
        ):
            min_transaction_dt = chunk_min

        if (
            max_transaction_dt is None
            or chunk_max > max_transaction_dt
        ):
            max_transaction_dt = chunk_max

        if not times.is_monotonic_increasing:
            globally_ordered = False

        if (
            previous_last_dt is not None
            and times.iloc[0] < previous_last_dt
        ):
            globally_ordered = False

        previous_last_dt = times.iloc[-1]

    print(
        f"Processed chunk {chunk_number} | "
        f"Transactions scanned: {total_rows:,}"
    )


# --------------------------------------------------
# 6. CALCULATE DATASET METRICS
# --------------------------------------------------

fraud_percentage = (
    fraud_count / total_rows * 100 if total_rows else 0
)

legitimate_percentage = (
    legitimate_count / total_rows * 100 if total_rows else 0
)

identity_coverage = (
    matched_transaction_rows / total_rows * 100
    if total_rows else 0
)

missingness = pd.DataFrame({
    "column": missing_counts.index,
    "missing_count": missing_counts.values.astype(int),
})

missingness["missing_percent"] = (
    missingness["missing_count"] / total_rows * 100
).round(2)

missingness = missingness.sort_values(
    "missing_percent",
    ascending=False,
)


# --------------------------------------------------
# 7. SAVE AUDIT RESULTS
# --------------------------------------------------

summary = {
    "dataset": "IEEE-CIS Fraud Detection",
    "transaction_file": TRANSACTION_PATH.name,
    "identity_file": IDENTITY_PATH.name,
    "transaction_rows": int(total_rows),
    "transaction_columns": int(column_count or 0),
    "identity_rows": int(identity_rows),
    "unique_transaction_ids": int(len(seen_transaction_ids)),
    "duplicate_transaction_ids": int(
        duplicate_transaction_count
    ),
    "identity_duplicate_ids": int(identity_duplicate_count),
    "fraud_count": int(fraud_count),
    "legitimate_count": int(legitimate_count),
    "missing_target_count": int(missing_target_count),
    "fraud_percentage": round(fraud_percentage, 4),
    "legitimate_percentage": round(legitimate_percentage, 4),
    "matched_transaction_rows": int(matched_transaction_rows),
    "identity_coverage_percentage": round(identity_coverage, 2),
    "transaction_dt_min": (
        int(min_transaction_dt)
        if min_transaction_dt is not None else None
    ),
    "transaction_dt_max": (
        int(max_transaction_dt)
        if max_transaction_dt is not None else None
    ),
    "transaction_dt_globally_ordered": bool(globally_ordered),
    "chunk_size": CHUNK_SIZE,
}

summary_path = AUDIT_DIR / "dataset_summary.json"
missingness_path = AUDIT_DIR / "transaction_missingness.csv"

with open(summary_path, "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=4)

missingness.to_csv(missingness_path, index=False)


# --------------------------------------------------
# 8. PRINT FINAL SUMMARY
# --------------------------------------------------

print("\n========== FULL DATASET AUDIT ==========")
print(f"Transaction rows: {total_rows:,}")
print(f"Transaction columns: {column_count}")
print(f"Fraudulent transactions: {fraud_count:,} "
      f"({fraud_percentage:.2f}%)")
print(f"Legitimate transactions: {legitimate_count:,} "
      f"({legitimate_percentage:.2f}%)")
print(f"Duplicate TransactionIDs: {duplicate_transaction_count:,}")
print(f"Identity coverage: {identity_coverage:.2f}%")
print(f"TransactionDT range: {min_transaction_dt} to "
      f"{max_transaction_dt}")
print(f"Globally ordered by TransactionDT: {globally_ordered}")

print("\nTop 15 columns by missing percentage:")
print(missingness.head(15).to_string(index=False))

print("\nAudit files saved:")
print(summary_path)
print(missingness_path)
