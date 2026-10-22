# FraudLens
### Agentic Real-Time Financial Fraud Investigation & Risk Intelligence Platform

FraudLens is a financial fraud risk intelligence platform designed to identify potentially fraudulent transactions and support evidence-based investigation. It combines machine learning, a FastAPI backend, secure user authentication, and a React dashboard to make fraud-risk information accessible and actionable.

The project currently includes a trained baseline fraud-detection model, a historical transaction dataset pipeline, authenticated API endpoints, and a web-based dashboard. Advanced investigation workflows, retrieval-augmented generation (RAG), and real-time streaming are planned extensions.

> **Project status:** Baseline ML, backend API, authentication, and frontend dashboard implemented. Advanced agentic investigation and live streaming remain under development. The backend has also encountered a Windows Application Control policy error while importing a compiled SciPy module; a successful build does not establish that runtime issue is resolved.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Key Features](#4-key-features)
5. [System Architecture](#5-system-architecture)
6. [Technology Stack](#6-technology-stack)
7. [Dataset](#7-dataset)
8. [Machine Learning Model](#8-machine-learning-model)
9. [Backend API](#9-backend-api)
10. [Authentication and Security](#10-authentication-and-security)
11. [Frontend Dashboard](#11-frontend-dashboard)
12. [Project Structure](#12-project-structure)
13. [Installation and Setup](#13-installation-and-setup)
14. [Running the Application](#14-running-the-application)
15. [API Endpoints](#15-api-endpoints)
16. [Model Evaluation](#16-model-evaluation)
17. [Current Limitations](#17-current-limitations)
18. [Development Roadmap](#18-development-roadmap)
19. [Contributing](#19-contributing)
20. [Disclaimer](#20-disclaimer)

---

## 1. Project Overview

Traditional fraud-detection systems often focus on assigning a risk score or classifying a transaction as fraudulent or legitimate. However, a risk score alone does not explain what investigators should examine next.

FraudLens is intended to extend basic classification into an investigation-oriented workflow.

The platform aims to connect:

- **Risk scoring:** Estimate the likelihood that a transaction belongs to the fraudulent class.
- **Transaction exploration:** Browse historical transactions and their associated risk scores.
- **Investigation:** Present transaction details and observable data-quality or attribute findings.
- **Evidence-based explanations:** Separate observed facts, model predictions, and investigative hypotheses.
- **Agentic investigation:** Introduce controlled workflows that gather evidence, analyze related activity, and produce structured investigation reports.

The current implementation establishes the foundation for these capabilities. The full agentic workflow is not yet implemented.

## 2. Problem Statement

Financial institutions process large volumes of transactions, making manual review inefficient. Fraud is also relatively rare compared with legitimate activity, creating class imbalance and making simple accuracy an unreliable evaluation metric.

A useful fraud-risk platform should help answer:

1. Which transactions deserve further review?
2. What risk score did the model assign?
3. What transaction attributes are available or missing?
4. Are there related transactions that merit examination?
5. Which findings are supported by evidence?
6. What additional investigation steps should be taken?

FraudLens addresses the initial classification and transaction-review requirements while providing an architecture for evidence-backed investigation.

## 3. Objectives

- Build a baseline machine learning pipeline for transaction fraud detection.
- Evaluate performance using precision, recall, F1-score, ROC-AUC, and average precision.
- Expose predictions and transaction data through a REST API.
- Implement registration, login, password hashing, and bearer-token authentication.
- Develop a responsive dashboard for exploring transactions and reviewing investigations.
- Establish a modular structure for future streaming, investigation, and RAG components.
- Progress toward explainable, evidence-backed fraud investigation rather than relying exclusively on a classification label.

## 4. Key Features

### Implemented

- Historical IEEE-CIS transaction dataset inspection and auditing.
- Baseline classification model and saved model artifact.
- Evaluation metrics stored as a JSON artifact.
- FastAPI application with health and transaction endpoints.
- Transaction risk scores and predicted classifications.
- Protected transaction and investigation routes.
- User registration and login.
- PBKDF2-HMAC-SHA256 password hashing with individual salts.
- Signed bearer tokens with a 12-hour lifetime.
- SQLite-based user storage.
- React, TypeScript, and Vite frontend.
- Landing page, authentication screens, dashboard navigation, transaction explorer, pagination, and investigation modal.
- Frontend production build successfully verified.

### Planned

- Related-transaction and behavioral-pattern analysis.
- More comprehensive investigation evidence.
- Model-feature attribution and calibrated risk estimates.
- LangGraph-based agent orchestration.
- RAG over relevant fraud patterns and investigation guidance.
- Simulated transaction streaming using Pub/Sub and Dataflow.
- Human review and investigation feedback.
- Expanded monitoring, testing, and deployment automation.
- Email or OTP verification and account recovery.

---

## 5. System Architecture

The current application follows a modular frontend–backend–ML architecture.

```text
                 ┌──────────────────────────┐
                 │     React Dashboard      │
                 │    TypeScript + Vite     │
                 └────────────┬─────────────┘
                              │ HTTP / JSON
                              ▼
                 ┌──────────────────────────┐
                 │       FastAPI API        │
                 │                          │
                 │ Health / Transactions    │
                 │ Authentication           │
                 │ Investigation endpoint   │
                 └──────┬─────────┬─────────┘
                        │         │
               ┌────────▼───┐ ┌───▼────────────┐
               │ Saved ML   │ │ SQLite User DB │
               │ Pipeline   │ │ Accounts       │
               └──────┬─────┘ └────────────────┘
                      │
               ┌──────▼──────────┐
               │ Historical      │
               │ Transaction CSV │
               └─────────────────┘
```

### Planned extension

```text
Transaction Generator
        │
        ▼
   Pub/Sub / Queue
        │
        ▼
  Dataflow Processing
        │
        ▼
  Risk Scoring Service
        │
        ▼
 Investigation Workflow
        │
        ├── Related activity analysis
        ├── Evidence collection
        ├── Fraud-pattern retrieval
        ├── Structured explanation
        └── Human review
```

The streaming and agentic architecture represents the intended direction, not a claim that the complete pipeline is currently operational.

---

## 6. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Data processing | pandas, NumPy |
| Machine learning | scikit-learn |
| Model serialization | joblib |
| Backend framework | FastAPI |
| API server | Uvicorn |
| Authentication | PBKDF2, HMAC, bearer tokens |
| Database | SQLite |
| Configuration | python-dotenv |
| Request validation | Pydantic |
| Frontend | React, TypeScript |
| Build tool | Vite |
| Icons | Lucide React |
| Dataset | IEEE-CIS Fraud Detection |
| Development environment | VS Code, Git Bash, Python virtual environment |

### Intended future technologies

- LangGraph for controlled agent orchestration.
- Retrieval-augmented generation for fraud-pattern evidence.
- Google Cloud Pub/Sub and Dataflow for streaming.
- BigQuery for analytical storage.
- Vertex AI for selected model or AI workflows.

These are planned integrations and should not be considered active dependencies of the current working implementation.

---

## 7. Dataset

FraudLens uses the IEEE-CIS Fraud Detection dataset, originally released for a Kaggle fraud-detection competition.

The dataset contains transaction records, transaction attributes, and a separate identity table.

### Dataset audit

| Metric | Value |
|---|---:|
| Transaction rows | 590,540 |
| Transaction columns | 394 |
| Fraudulent transactions | 20,663 |
| Legitimate transactions | 569,877 |
| Fraud prevalence | Approximately 3.50% |
| Duplicate TransactionIDs | 0 |
| Identity rows | 144,233 |
| Unique identity IDs | 144,233 |
| Identity coverage | Approximately 24.42% |

The transaction dataset is highly imbalanced: approximately 96.5% of records are legitimate and 3.5% are fraudulent.

### Data preparation considerations

- `TransactionID` is used to identify transaction records.
- `TransactionDT` represents relative elapsed time rather than a calendar timestamp.
- Many transaction attributes contain missing values.
- Identity information is not available for every transaction.
- Missing values must be handled without accidentally leaking validation information into model training.
- Chronological validation is preferred to random splitting when evaluating future-facing fraud detection.

Dataset audit outputs are stored under `data/audit/`.

**Data source:** [IEEE-CIS Fraud Detection — Kaggle](https://www.kaggle.com/competitions/ieee-fraud-detection)

The dataset is historical and is not a live banking feed.

---

## 8. Machine Learning Model

### Baseline approach

The initial model is a scikit-learn classification pipeline trained on selected transaction attributes.

The current pipeline uses:

- Logistic regression.
- Class weighting to account for class imbalance.
- Median imputation for numerical features.
- Numerical feature scaling.
- One-hot encoding for categorical features, with infrequent categories grouped using `min_frequency=100`.
- A maximum of 500 iterations and the `liblinear` solver.
- A chronological training–validation split.

The model uses 23 selected features.

### Selected numerical features

`TransactionAmt`, `card1`, `card2`, `card3`, `card5`, `addr1`, `dist1`, `C1`, `C2`, `C3`, `C5`, `C6`, `C9`, `D1`, `D2`, `D3`, `D4`, `D10`, and `D15`.

### Selected categorical features

`ProductCD`, `card4`, `card6`, and `P_emaildomain`.

### Training and validation split

| Partition | Records |
|---|---:|
| Training | 472,432 |
| Validation | 118,108 |

The validation set has a fraud prevalence of approximately 3.44%.

### Saved artifacts

- `ml/artifacts/fraud_model.joblib` — trained scikit-learn pipeline.
- `ml/artifacts/baseline_metrics.json` — baseline evaluation metrics.

The pipeline includes preprocessing and classification, so the API can apply the same transformations used during training.

### Important distinction

The API exposes `predict_proba` output as a fraud probability and derives a risk score. These are model estimates, not automatically calibrated real-world probabilities. Calibration and threshold selection require additional evaluation.

---

## 9. Backend API

The backend is implemented in `api/main.py` using FastAPI.

### Responsibilities

- Load the saved model artifact.
- Load historical transaction records.
- Provide a health-check endpoint.
- Return transaction records with model predictions.
- Protect selected endpoints using bearer-token authentication.
- Provide an investigation endpoint for an individual transaction.
- Integrate the authentication router from `api/auth.py`.

### Risk scoring

For each requested transaction, the API returns fields including:

- Transaction ID.
- Transaction amount.
- Product category.
- Relative transaction time.
- Fraud probability.
- Risk score.
- Predicted class.

The current classification threshold is `0.50`. This is a baseline threshold, not a final operational decision threshold.

### Investigation endpoint

The current investigation endpoint returns a transaction's score, predicted class, investigation status, observations, and an explanation.

At present, its explicitly implemented observations include checks for missing values in selected attributes such as `card4`, `card6`, and `P_emaildomain`.

Missing attributes are data observations, not proof of fraud. The current endpoint should not be interpreted as a complete autonomous fraud investigation.

---

## 10. Authentication and Security

Authentication is implemented in `api/auth.py`.

### Implemented mechanisms

- Account registration using an email address and password.
- Email format validation through Pydantic.
- Password length validation.
- Password hashing with PBKDF2-HMAC-SHA256.
- A unique random salt for each password.
- Constant-time password-hash comparison.
- Signed bearer tokens using HMAC-SHA256.
- Token expiration after 12 hours.
- Protected API endpoints using FastAPI dependencies.
- SQLite storage for account records.

Passwords are not stored as plaintext.

### Environment configuration

The application reads `FRAUDLENS_SECRET_KEY` from the root `.env` file using `python-dotenv`.

Example:

```dotenv
FRAUDLENS_SECRET_KEY=replace_with_your_generated_secret
```

Generate a secret locally:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into `.env`. Do not commit the actual `.env` file or disclose its secret.

The root `.gitignore` should exclude:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
node_modules/
dist/
```

Additional ignore rules should protect local databases, private data, logs, and generated artifacts as appropriate. Preserve any existing project-specific rules.

### Current security limitations

The current authentication implementation does not yet include:

- Email verification or OTP.
- Password reset.
- Login rate limiting.
- Refresh tokens or server-side session revocation.
- Production-grade account abuse controls.
- A managed identity provider.

This implementation is suitable as a project prototype, not as a production banking authentication system.

---

## 11. Frontend Dashboard

The frontend is located in `dashboard/` and uses React, TypeScript, Vite, and Lucide React icons.

### Landing page

The public landing page introduces FraudLens, displays high-level baseline model metrics, and describes the platform's capabilities and methodology.

### Authentication screens

- Registration.
- Login.
- Session checking.
- Logout.

### Authenticated dashboard

- Overview screen.
- Transaction explorer.
- Paginated transaction table.
- Risk indicators.
- Investigation view and modal.
- Navigation between dashboard sections.

The frontend communicates with the backend through `dashboard/src/api.ts`.

The visual design uses a dark charcoal interface with lime and orange accents, typography optimized for dashboard use, and responsive styling.

### Build verification

The production build has previously completed successfully with:

```bash
npm run build
```

The build runs TypeScript project checks followed by Vite production bundling.

A successful frontend build confirms compilation and bundling; it does not by itself prove that the backend is running or that every integration works at runtime.

---

## 12. Project Structure

```text
FraudLens/
│
├── api/
│   ├── auth.py
│   └── main.py
│
├── dashboard/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── api.ts
│   ├── vite.config.ts
│   └── package.json
│
├── data/
│   ├── raw/
│   │   ├── train_transaction.csv
│   │   └── train_identity.csv
│   ├── audit/
│   │   ├── dataset_summary.json
│   │   └── transaction_missingness.csv
│   ├── features/
│   ├── processed/
│   ├── schemas/
│   └── scripts/
│       └── inspect_data.py
│
├── ml/
│   ├── artifacts/
│   │   ├── fraud_model.joblib
│   │   └── baseline_metrics.json
│   └── train_model.py
│
├── investigation/
├── rag/
├── streaming/
├── monitoring/
├── infrastructure/
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Some directories are scaffolding for future development and may not yet contain completed implementations.

The local `.env` file, `.venv/`, and SQLite database should be handled according to the project's ignore and data-management policies.

---

## 13. Installation and Setup

### Prerequisites

- Python compatible with the project's pinned dependencies.
- Node.js and npm.
- Git.
- The IEEE-CIS dataset files, where required by the local implementation.

Commands below use Git Bash on Windows. Adjust the paths if your repository is located elsewhere.

### Step 1: Clone or open the repository

If the repository is already on your computer, open its root directory:

```bash
cd ~/Desktop/FraudLens
```

### Step 2: Create and activate the virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate
```

If activation succeeds, install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 3: Configure environment variables

Create `.env` from the template:

```bash
cp .env.example .env
```

Edit `.env` and set a secure value for `FRAUDLENS_SECRET_KEY`. Preserve other required configuration entries.

The authentication module loads the file from the project root.

### Step 4: Prepare the dataset

Place the required dataset files in `data/raw/` using the filenames expected by the application:

```text
data/raw/train_transaction.csv
data/raw/train_identity.csv
```

Do not commit the raw dataset unless you have explicitly reviewed the dataset's redistribution terms and your repository's data policy.

### Step 5: Install frontend dependencies

```bash
cd dashboard
npm install
cd ..
```

---

## 14. Running the Application

Open two terminal sessions from the project root.

### Terminal A: Start the backend

Activate the virtual environment if it is not already active:

```bash
source .venv/Scripts/activate
```

Run:

```bash
python -m uvicorn api.main:app --reload
```

The default local address is:

`http://127.0.0.1:8000`

Open the interactive API documentation at:

`http://127.0.0.1:8000/docs`

### Terminal B: Start the frontend

```bash
cd dashboard
npm run dev
```

Vite normally serves the frontend at:

`http://localhost:5173`

Use the actual local address printed by Vite if it differs.

### Verify backend health

```bash
curl http://127.0.0.1:8000/health
```

A previously verified healthy response was:

```json
{
  "status": "ok",
  "model_loaded": true,
  "transactions_loaded": true
}
```

If the backend fails to start while loading `fraud_model.joblib`, resolve the Python environment or dependency issue before testing frontend-to-backend functionality.

### Windows Application Control issue

A previous startup attempt failed while importing a compiled SciPy module, with an error stating that an Application Control policy blocked the file.

This is an operating-system or environment restriction, not an authentication configuration error. If it recurs:

1. Confirm that the virtual environment is active.
2. Test the SciPy import independently.
3. Check Python and package compatibility.
4. Use an approved Python environment or consult the device administrator if application policy is blocking a legitimate package.

Do not disable security controls or attempt to bypass organizational application policies.

---

## 15. API Endpoints

The following routes are implemented in the current backend.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/health` | Public | Check application and resource status |
| POST | `/auth/register` | Public | Create an account |
| POST | `/auth/login` | Public | Authenticate and obtain a token |
| GET | `/auth/me` | Bearer token | Retrieve the current user's identity |
| GET | `/public/feed` | Public | Read the historical public transaction feed |
| GET | `/transactions` | Bearer token | Retrieve paginated transaction data and scores |
| GET | `/investigate/{transaction_id}` | Bearer token | Retrieve the current investigation result |

### Register

`POST /auth/register`

Example request:

```json
{
  "email": "analyst@example.com",
  "password": "replace-with-a-strong-password"
}
```

A successful response includes an access token, token type, and user information.

### Login

`POST /auth/login`

Example request:

```json
{
  "email": "analyst@example.com",
  "password": "replace-with-a-strong-password"
}
```

Use the returned bearer token when accessing protected endpoints.

### Current user

`GET /auth/me`

Header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Retrieve transactions

`GET /transactions?limit=20&offset=0`

This endpoint requires authentication. It returns paginated historical transactions with model scores.

### Investigate a transaction

`GET /investigate/{transaction_id}`

Replace `{transaction_id}` with a transaction identifier from the dataset.

The endpoint requires authentication and returns the currently implemented investigation summary.

Exact response schemas should be checked in `/docs`, because they reflect the running implementation.

---

## 16. Model Evaluation

The current baseline metrics are:

| Metric | Score |
|---|---:|
| Precision | 0.0942 |
| Recall | 0.6373 |
| F1-score | 0.1641 |
| Average precision / PR-AUC | 0.1314 |
| ROC-AUC | 0.7772 |

At the current classification threshold of 0.50, the validation confusion matrix is:

| Actual / Predicted | Legitimate | Fraud |
|---|---:|---:|
| Legitimate | 89,127 | 24,917 |
| Fraud | 1,474 | 2,590 |

### Interpretation

- **Recall of 0.6373:** The baseline identifies approximately 63.7% of fraudulent transactions in the validation set at the selected threshold.
- **Precision of 0.0942:** Approximately 9.4% of transactions predicted as fraud are actually fraudulent in this validation set.
- **ROC-AUC of 0.7772:** The model demonstrates discriminatory ability, but this metric does not establish operational readiness.
- **Average precision of 0.1314:** Precision–recall performance must be considered in the context of the low fraud prevalence.

The baseline has a substantial false-positive burden. It should be treated as an initial benchmark rather than a production fraud-control system.

Potential improvements include threshold tuning, calibration, stronger models, time-aware validation, feature engineering, and investigator feedback. Any improvement should be verified on an appropriate held-out dataset.

---

## 17. Current Limitations

1. **Historical data:** The current dataset is not a live transaction stream.
2. **Baseline model:** Logistic regression is an initial benchmark, not a final model-selection decision.
3. **False positives:** The current threshold flags many legitimate transactions for potential review.
4. **Probability calibration:** Model outputs have not been established as calibrated real-world probabilities.
5. **Limited investigation evidence:** The current investigation endpoint performs basic checks and does not yet provide comprehensive behavioral analysis.
6. **No completed agent workflow:** LangGraph orchestration and autonomous multi-step investigation remain planned.
7. **No completed RAG pipeline:** Fraud-pattern retrieval and grounded knowledge-base evidence remain planned.
8. **No completed streaming pipeline:** Pub/Sub and Dataflow integration remain planned.
9. **Prototype authentication:** Email verification, OTP, password reset, rate limiting, and production session management are not implemented.
10. **Runtime dependency issue:** A Windows Application Control restriction previously blocked a SciPy compiled module during model loading. Runtime health must be reverified after remediation.
11. **Limited test coverage:** Existing manual checks and build verification do not replace a comprehensive automated test suite.
12. **No production deployment claim:** Monitoring, deployment hardening, privacy review, and operational controls require additional work.

---

## 18. Development Roadmap

### Phase 1 — Foundation

- [x] Inspect and audit the dataset.
- [x] Train a baseline fraud classifier.
- [x] Save the model and baseline metrics.
- [x] Implement core FastAPI endpoints.
- [x] Implement registration and login.
- [x] Implement protected transaction and investigation routes.
- [x] Build the React dashboard.
- [x] Verify the frontend production build.
- [ ] Resolve and verify the backend's Windows SciPy import issue.

### Phase 2 — Evidence-backed investigation

- [ ] Build a structured risk assessment schema.
- [ ] Analyze related transactions and suspicious activity.
- [ ] Separate observed facts, model predictions, and hypotheses.
- [ ] Add grounded feature-level explanations.
- [ ] Produce structured investigation reports.
- [ ] Add tests for investigation outputs.

### Phase 3 — Agentic workflows and RAG

- [ ] Design a controlled LangGraph investigation workflow.
- [ ] Retrieve relevant fraud-pattern evidence.
- [ ] Add source-grounded summaries and recommended next steps.
- [ ] Add safeguards against unsupported claims.
- [ ] Introduce human review and feedback.

### Phase 4 — Streaming and analytics

- [ ] Implement a simulated transaction generator.
- [ ] Integrate a message queue or Pub/Sub.
- [ ] Process incoming events through a streaming pipeline.
- [ ] Persist analytical outputs in an appropriate store.
- [ ] Expose new events and investigation results in the dashboard.

### Phase 5 — Reliability and deployment

- [ ] Expand unit, integration, and end-to-end tests.
- [ ] Improve model evaluation and threshold selection.
- [ ] Add drift and performance monitoring.
- [ ] Improve account security and operational configuration.
- [ ] Document deployment, observability, and recovery procedures.

---

## 19. Contributing

For local development:

1. Create a feature branch before making substantial changes.
2. Keep raw data, secrets, and local environment files out of version control.
3. Use the same preprocessing pipeline for training and inference.
4. Add tests for new API or investigation behavior.
5. Run frontend build checks after frontend changes.
6. Record new model metrics and evaluation conditions when changing the model.
7. Update this README when implementation status or configuration changes.

Before committing, review the staged files:

```bash
git status
git diff --cached
```

Never commit `.env`, credentials, access tokens, or sensitive data.

---

## 20. Disclaimer

FraudLens is an academic and research prototype. Its risk scores and investigation outputs are intended for demonstration and evaluation, not as the sole basis for financial, legal, or account-access decisions.

Model predictions can be incorrect, and a high risk score is not proof of fraud. Any real-world deployment would require appropriate validation, security review, privacy safeguards, human oversight, and compliance with applicable requirements.

---

**FraudLens — From transaction risk scoring to evidence-backed fraud investigation.**
