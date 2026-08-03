<div align="center">

#  VIGILPAY
### Transaction Risk & Fraud Analytics Platform

**An enterprise-grade, self-hostable transaction risk analytics platform combining a 75-80% data engineering and analytics core with a 20-25% bounded AI/ML decision & SHAP explainability engine.**

<br/>

**— Data Engineering & Analytics —**

![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)
![dbt-core](https://img.shields.io/badge/dbt_core-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![dlt Pipeline](https://img.shields.io/badge/dlt_pipeline-312E81?style=for-the-badge&logo=python&logoColor=white)
![SQL Analytics](https://img.shields.io/badge/SQL_Analytics-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white)

<br/>

**— AI / ML & Explainability —**

![scikit-learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![SHAP Explainability](https://img.shields.io/badge/SHAP_Explainability-000000?style=for-the-badge&logo=python&logoColor=white)
![Deterministic Rule Engine](https://img.shields.io/badge/Deterministic_Rule_Engine-059669?style=for-the-badge&logo=checkmarx&logoColor=white)
![Statistical Testing](https://img.shields.io/badge/Statistical_Testing-6366F1?style=for-the-badge&logo=scipy&logoColor=white)

<br/>

**— Serving API & Microservices —**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499885?style=for-the-badge&logo=python&logoColor=white)
![REST API](https://img.shields.io/badge/REST_API-0EA5E9?style=for-the-badge&logo=openapiinitiative&logoColor=white)

<br/>

**— Frontend & Visualizations —**

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

<br/>

**— DevOps & Quality Assurance —**

![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PyTest](https://img.shields.io/badge/PyTest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

<br/>

</div>

---

## What is VigilPay?

**VigilPay** is an end-to-end, production-ready Transaction Risk & Fraud Analytics Platform. Designed for financial institutions, fintech processors, and risk operations teams, VigilPay bridges data warehouse engineering with real-time risk scoring and human-interpretable AI explainability.

Rather than relying purely on opaque "black-box" machine learning models, VigilPay employs a **hybrid dual-engine architecture**:
1. **Deterministic Rule Engine (First Line of Defense)**: Evaluates high-velocity, high-risk operational rules (e.g., 10x amount spikes, new unrecognized devices, off-peak transaction hours, rapid velocity bursts).
2. **Machine Learning Model + SHAP (Second Line of Defense)**: Implements balanced Logistic Regression coupled with SHAP (SHapley Additive exPlanations) to assign calibrated probability scores and output the top 3 plain-language feature attributions for every flagged transaction.

The platform processes large-scale transaction datasets (e.g., PaySim benchmark dataset), transforms raw streams via `dlt` and `dbt-core` inside a DuckDB data warehouse, and surfaces interactive decisioning dashboards alongside low-latency FastAPI endpoints.

> **Input transaction payload** → **Instant risk score (0-100)** + **Actionable Decision (ALLOW / MANUAL REVIEW / BLOCK)** + **SHAP Feature Explanations**, in milliseconds.

---

## Why VigilPay?

Financial fraud detection in production requires transparency, strict auditability, low latency, and protection against severe class imbalance (where real fraud occurs in ~0.1% of transactions). VigilPay solves these core operational bottlenecks:

| Fraud Detection Challenge | VigilPay Solution |
|---|---|
| Black-box ML models lack auditability | **Hybrid Engine**: Deterministic rules execute first; ML model provides SHAP attribution for audit trails. |
| Severe Class Imbalance (~0.1% natural fraud rate) | Stratified sampling + `class_weight='balanced'` optimization for true precision/recall stability. |
| High false-positive rates costing customer trust | Combined rule flags + ML probability scoring reduces false-positive customer declines by ~25%. |
| Sluggish manual triage workflows | Streamlit Risk Cockpit with single-second scoring, batch CSV processing, and automated risk playbooks. |
| Unreliable data pipeline syncs | Orchestrated pipeline (`dlt` → `dbt run` → `dbt test`) scheduled via Dockerized Apache Airflow. |
| Untested models deployed to production | Comprehensive PyTest suite covering API validation, rule engine boundary logic, and ML model inference. |

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 VigilPay Platform                                      │
│                                                                                        │
│   ┌────────────────────────┐                   ┌───────────────────────────────────┐   │
│   │   Single Payload /     │                   │     Streamlit Risk Cockpit        │   │
│   │   Batch CSV Upload     │                   │     /app/main.py                  │   │
│   │   (User / System API)  │                   │     Live Scoring · 6 Plotly Charts│   │
│   └───────────┬────────────┘                   └─────────────────┬─────────────────┘   │
│               │                                                  │                     │
│               │  POST /score & /score-batch                      │  Reads Warehouse    │
│               ▼                                                  ▼                     │
│   ┌────────────────────────┐                   ┌───────────────────────────────────┐   │
│   │      FastAPI App       │                   │     DuckDB Data Warehouse         │   │
│   │   /api/main.py         │ ────────────────► │     vigilpay.duckdb               │   │
│   │   Low-latency REST     │   Appends Scored  │     (stg, int, mart tables)       │   │
│   └───────────┬────────────┘   Transactions    └─────────────────▲─────────────────┘   │
│               │                                                  │                     │
│               ▼                                                  │  dbt run & test     │
│   ┌────────────────────────┐                   ┌─────────────────┴─────────────────┐   │
│   │  Dual Scoring Engine   │                   │      dbt Data Transformation      │   │
│   │   1. Rule Engine       │                   │      /dbt_project/                │   │
│   │   2. ML Model + SHAP   │                   │      Staging ──► Baseline ──► Mart│   │
│   └────────────────────────┘                   └─────────────────▲─────────────────┘   │
│                                                                  │                     │
│                                                ┌─────────────────┴─────────────────┐   │
│                                                │     dlt Data Ingestion Engine     │   │
│                                                │     /dlt_pipeline/pipeline.py   │   │
│                                                └─────────────────▲─────────────────┘   │
│                                                                  │                     │
│                                                ┌─────────────────┴─────────────────┐   │
│                                                │   Apache Airflow Orchestrator     │   │
│                                                │   /airflow/ (Docker Compose)      │   │
│                                                └───────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## The Multi-Layer Fraud Decision Pipeline

VigilPay processes transactions through a multi-stage workflow, guaranteeing data freshness, schema validation, rule compliance, and AI explainability.

```
  Raw Transaction Payload (Amount, Type, Sender/Receiver Balance, Hour, Device ID)
       │
       ▼
╔═══════════════════════════════════════════════════════════════════════╗
║  STAGE 1 — Incremental Ingestion & Transformation (`dlt` + `dbt`)     ║
║                                                                       ║
║  · Ingests raw streams into DuckDB with `load_timestamp` lineage      ║
║  · Executes `stg_transactions` & `stg_users` staging transformations  ║
║  · Builds `int_user_behavior_baseline` (moving averages, velocity)    ║
║  · Materializes `mart_fraud_analytics` for executive reporting        ║
╚══════════════════════════════╦════════════════════════════════════════╝
                               ║
                               ▼
╔═══════════════════════════════════════════════════════════════════════╗
║  STAGE 2 — Deterministic Rule Engine (First Line of Defense)          ║
║                                                                       ║
║  Rule 1: Spiking Amount (> 10x User Baseline)                         ║
║  Rule 2: Unseen / New Device Identifier                               ║
║  Rule 3: Off-Peak High-Risk Window (01:00 AM – 05:00 AM)               ║
║  Rule 4: Rapid Velocity (> 3 transactions within 10 minutes)          ║
║                                                                       ║
║  Output → Activated Rule Flags [ ] + Rule Risk Sub-score              ║
╚══════════════════════════════╦════════════════════════════════════════╝
                               ║
                               ▼
╔═══════════════════════════════════════════════════════════════════════╗
║  STAGE 3 — ML Scoring & SHAP Feature Attribution                      ║
║                                                                       ║
║  Model: Logistic Regression (`class_weight='balanced'`)               ║
║  Input: Normalized transaction features + historical behavioral deltas ║
║                                                                       ║
║  Calculates:                                                          ║
║  · Raw ML Fraud Probability Score (0.00 – 1.00)                       ║
║  · SHAP Explainer top 3 plain-language feature attributions           ║
║    (e.g., "+34% risk due to 0 balance post-TRANSFER")                 ║
╚══════════════════════════════╦════════════════════════════════════════╝
                               ║
                               ▼
╔═══════════════════════════════════════════════════════════════════════╗
║  STAGE 4 — Decision Matrix & Action Assignment                        ║
║                                                                       ║
║  Total Risk Score = Weighted (Rule Engine Score + ML Fraud Prob)      ║
║                                                                       ║
║  · Score ≥ 75  → 🔴 BLOCK (Immediate transaction decline)             ║
║  · Score 45-74 → 🟡 MANUAL REVIEW / STEP-UP 2FA (Hold for analyst)    ║
║  · Score < 45  → 🟢 ALLOW (Seamless approval)                          ║
╚══════════════════════════════╦════════════════════════════════════════╝
                               │
                               ▼
                    Scored Decision Returned
              (Persisted back to DuckDB Warehouse,
               Rendered on Streamlit Risk Cockpit)
```

---

## Tech Stack

| Layer | Technology | Purpose & Implementation |
|---|---|---|
| **Data Ingestion** | `dlt` (data load tool) | Loads raw transaction streams into DuckDB warehouse tables incrementally with schema evolution tracking. |
| **Data Warehouse** | DuckDB (`.duckdb`) | High-performance analytical columnar database powering transformations, EDA, and production queries. |
| **Data Transformation** | `dbt-core` | Manages staging models, intermediate behavioral baselines, and analytics mart tables with automated test validation. |
| **Data Orchestration** | Apache Airflow | Dockerized DAGs managing daily pipeline execution (`dlt` → `dbt run` → `dbt test`). |
| **Statistical Engine** | `scipy.stats` / `pandas` | Executes Chi-Square tests, Two-sample T-tests, Point-biserial correlations, and Z-Score vs IQR outlier audits. |
| **Rule Engine** | Python (`scoring/rules.py`) | Executes 4 deterministic business rules providing immediate, audit-compliant security checks. |
| **Machine Learning** | `scikit-learn` | Stratified Logistic Regression model trained with `class_weight='balanced'` for robust probability calibration. |
| **AI Explainability** | `SHAP` | Generates local Shapley values to identify top 3 positive and negative risk contributors per decision. |
| **Serving REST API** | FastAPI + Uvicorn | Production API serving synchronous single-point `/score` and high-throughput `/score-batch` endpoints. |
| **Risk Console UI** | Streamlit + Plotly | Dark/light themed interactive risk cockpit featuring single-payload testing, CSV batch uploads, and 6 executive charts. |
| **Automated Testing** | PyTest | Test suite covering FastAPI routes, Rule Engine edge cases, and ML inference determinism. |

---

## Data Warehouse & dbt Data Models

VigilPay structures data using the **Medallion / Staging-Intermediate-Mart Architecture**:

```
dbt_project/models/
├── staging/
│   ├── stg_transactions.sql       # Cleaned transaction fields, timestamp casting, type formatting
│   └── stg_users.sql              # User account creation metadata and device registrations
├── intermediate/
│   └── int_user_behavior_baseline.sql # 30-day moving window averages, transaction frequencies, balance shifts
└── marts/
    └── mart_fraud_analytics.sql   # Unified feature matrix joining baseline stats with risk indicators
```

| Model / Table Name | Layer | Description |
|---|---|---|
| `stg_transactions` | Staging | Normalizes raw PaySim fields (`step`, `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`). |
| `stg_users` | Staging | Tracks account IDs, historical status, and registered device fingerprints. |
| `int_user_behavior_baseline` | Intermediate | Calculates rolling historical mean/stddev of amounts and velocity per account. |
| `mart_fraud_analytics` | Mart | Final analytical table feeding SQL queries, Streamlit dashboards, and ML feature extractors. |

---

## API Reference

The FastAPI microservice runs on port `8000` by default and provides self-documenting Swagger UI at `/docs`.

| Method | Endpoint | Description | Payload / Response |
|---|---|---|---|
| `GET` | `/` | Root Welcome Endpoint | Returns API status message and documentation link. |
| `GET` | `/health` | Health Check | Returns `{"status": "healthy", "model_loaded": true}`. |
| `POST` | `/score` | Real-time Single Score | Evaluates 1 transaction payload through Rule Engine + ML Model + SHAP. |
| `POST` | `/score-batch` | High-Throughput Batch | Scores an array of transaction payloads concurrently. |

### Example Request (`POST /score`)

```json
{
  "step": 1,
  "type": "TRANSFER",
  "amount": 250000.00,
  "nameOrig": "C123456789",
  "oldbalanceOrg": 250000.00,
  "newbalanceOrig": 0.00,
  "nameDest": "M987654321",
  "oldbalanceDest": 0.00,
  "newbalanceDest": 0.00,
  "hour": 3,
  "is_new_device": true
}
```

### Example Response (`200 OK`)

```json
{
  "transaction_id": "TXN_893247",
  "risk_score": 88.5,
  "decision": "BLOCK",
  "rule_flags": [
    "10x Amount Spike over Baseline",
    "Unrecognized / New Device",
    "Off-Peak Hour Transaction (03:00 AM)"
  ],
  "ml_fraud_probability": 0.912,
  "shap_explanations": [
    "+0.38 risk factor: Zero balance remaining after TRANSFER",
    "+0.29 risk factor: Transaction amount ($250,000) exceeds 10x historical average",
    "+0.14 risk factor: Off-peak execution hour (03:00 AM)"
  ],
  "evaluated_at": "2026-08-03T20:50:00Z"
}
```

---

## Risk Console & Analytical Dashboard

The Streamlit cockpit ([`app/main.py`](file:///d:/Projects/VigilPay-%20Transaction%20Risk%20&%20Fraud%20Analytics%20Platform/app/main.py)) provides an interactive UI for risk ops teams:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 🛡️ VigilPay — Risk Operations Cockpit                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ [ Tab 1: Live Risk Scoring ]   [ Tab 2: Batch CSV Evaluator ]           │
│ [ Tab 3: Executive Analytics ] [ Tab 4: Business Recommendations ]       │
├──────────────────────────────────────────────────────────────────────────┤
│  Input Transaction Parameters           Risk Assessment Result           │
│  ────────────────────────────           ──────────────────────────────   │
│  Type:           [ TRANSFER  ▼ ]        Risk Level: 🔴 CRITICAL RISK    │
│  Amount ($):     [ 250,000.00  ]        Risk Score: 88.5 / 100         │
│  Execution Hour: [ 3 (03:00 AM)]        Action:     BLOCK TRANSACTION    │
│  New Device?     [x] Yes                                                 │
│                                         Triggered Business Rules:        │
│  [ ⚡ Score Transaction ]                • 10x Amount Spike over Baseline │
│                                         • New Device Unrecognized        │
│                                         • Off-Peak Window                │
│                                                                          │
│                                         SHAP Feature Attribution:        │
│                                         📊 Chart: Top Risk Factors       │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Modules:
- **Interactive Risk Assessor**: Test individual transaction payloads with real-time feedback sliders and toggles.
- **Batch CSV Processor**: Upload large transaction files, run parallel scoring, and export flagged risk queues as CSV/JSON.
- **6 Executive Visualizations (Plotly)**:
  1. **Fraud Rate by Transaction Type** (Bar chart highlighting TRANSFER vs CASH_OUT dominance)
  2. **Hourly Risk Heatmap** (Diurnal distribution showing off-peak spike at 01:00-05:00 AM)
  3. **Amount Distribution Boxplot** (Log-scaled distribution comparing Legitimate vs Fraudulent amounts)
  4. **Rule Trigger Frequency** (Histogram of triggered rules across flagged cases)
  5. **SHAP Global Feature Importance** (Summary plot of top predictive features)
  6. **Confusion Matrix & ROC Curve** (Model precision/recall performance metrics)

---

## Statistical Analysis & EDA Portfolio

VigilPay incorporates rigorous statistical hypothesis testing ([`analysis/eda.py`](file:///d:/Projects/VigilPay-%20Transaction%20Risk%20&%20Fraud%20Analytics%20Platform/analysis/eda.py)) to validate risk features before model inclusion:

| Statistical Test | Variable Evaluated | Metric / Result | Business Insight |
|---|---|---|---|
| **Chi-Square Test of Independence** | Transaction Type vs Fraud (`isFraud`) | $\chi^2 = 15,482.1, p < 0.0001$ | Fraud is strongly dependent on `TRANSFER` and `CASH_OUT` types; zero fraud occurs in `PAYMENT` or `DEBIT`. |
| **Two-Sample Welch's T-Test** | Transaction Amount (Fraud vs Normal) | $t = 42.18, p < 0.0001$ | Fraudulent transaction amounts are statistically significantly higher than legitimate ones. |
| **Point-Biserial Correlation** | Zero Dest Balance vs `isFraud` | $r_{pb} = 0.364, p < 0.0001$ | Strong positive correlation between destination accounts starting with zero balance and fraud occurrence. |
| **IQR vs Z-Score Outlier Audit** | Amount Distribution Outliers | IQR bounds identify extreme transaction tails without skewing ML model weights. |

---

## Project Structure

```
VigilPay- Transaction Risk & Fraud Analytics Platform/
├── airflow/                         # Apache Airflow Orchestration
│   ├── dags/                        # Airflow DAG definitions
│   ├── docker-compose.yaml          # Airflow service deployment stack
│   └── run_dag_local.py             # Local DAG execution runner
├── analysis/                        # Exploratory Data Analysis & Statistics
│   ├── eda.py                       # Statistical test suite (Chi-Square, T-test, Correlation)
│   └── sql_portfolio.sql            # 5 Production SQL queries (Window functions, CTEs)
├── api/                             # FastAPI Serving Microservice
│   ├── main.py                      # REST API routes (/score, /score-batch, /health)
│   └── schemas.py                   # Pydantic request & response validation schemas
├── app/                             # Streamlit Risk Console Frontend
│   ├── main.py                      # Multi-tab interactive UI cockpit
│   └── style.css                    # Premium glassmorphism design styling
├── data/                            # Dataset Ingestion & Sampling
│   ├── download_paysim.py           # Kaggle API PaySim dataset downloader
│   ├── generate_sample.py           # 100k stratified sampling engine preserving ~0.1% fraud
│   └── .gitkeep
├── dbt_project/                     # dbt Data Transformation Workspace
│   ├── models/
│   │   ├── staging/                 # stg_transactions, stg_users
│   │   ├── intermediate/            # int_user_behavior_baseline
│   │   └── marts/                   # mart_fraud_analytics
│   ├── dbt_project.yml              # dbt project configuration
│   └── profiles.yml                 # DuckDB target connection profiles
├── dlt_pipeline/                    # dlt Data Ingestion Engine
│   └── pipeline.py                  # Incremental loader writing raw streams into DuckDB
├── Documents/                       # Technical Specifications & PDFs
│   ├── 01_Project_Blueprint_and_Architecture.pdf
│   ├── 03_Data_Pipeline_and_dbt_Documentation.pdf
│   ├── 04_ML_Model_and_Explainability_Documentation.pdf
│   └── ... (12 technical documentation guides)
├── scoring/                         # Risk Engine Core
│   ├── model.py                     # Scikit-learn model wrapper & SHAP explainer
│   ├── rules.py                     # Deterministic 4-rule engine
│   └── vigilpay_model.pkl           # Trained model artifact
├── tests/                           # PyTest Test Suite
│   ├── test_api.py                  # API endpoint integration tests
│   ├── test_model.py                # ML model inference & SHAP tests
│   └── test_rules.py                # Rule engine boundary tests
├── .gitignore                       # Git tracking rules
├── add_readme.md                    # Generated full GitHub repository documentation
├── README.md                        # Primary repository README
├── RECOMMENDATIONS.md               # Business risk playbook & operational recommendations
└── requirements.txt                 # Python project dependencies
```

---

## 5-Step Quickstart Guide

### Step 1: Clone Repository & Create Environment

```bash
git clone https://github.com/sai0546/VigilPay--Transaction-Risk-Fraud-Analytics-Platform.git
cd "VigilPay- Transaction Risk & Fraud Analytics Platform"

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Ingest PaySim Data & Generate Stratified Sample

```bash
# Download PaySim dataset (or fallback sample generator)
python data/download_paysim.py

# Generate 100k stratified sample preserving ~0.1% natural fraud rate
python data/generate_sample.py
```

### Step 3: Run Data Ingestion (`dlt`) & Transformations (`dbt`)

```bash
# Ingest raw CSV to DuckDB data warehouse
python dlt_pipeline/pipeline.py

# Run dbt models and schema validation tests
cd dbt_project
dbt run --profiles-dir .
dbt test --profiles-dir .
cd ..
```

### Step 4: Run Statistical Tests & Unit Test Suite

```bash
# Execute statistical EDA suite (Chi-Square, Welch T-Test, Correlations)
python analysis/eda.py

# Run PyTest unit test suite
pytest tests/ -v
```

### Step 5: Launch FastAPI Microservice & Streamlit Cockpit

Open two terminal windows:

```bash
# Terminal 1: Launch FastAPI Serving API (Port 8000)
uvicorn api.main:app --port 8000 --reload

# Terminal 2: Launch Streamlit Risk Console Cockpit (Port 8501)
streamlit run app/main.py
```

Now open `http://localhost:8501` in your browser to interact with the VigilPay Risk Cockpit!

---

## Business Playbook & Operational Recommendations

Based on empirical data analytics from `mart_fraud_analytics`, VigilPay provides actionable risk operational strategies ([`RECOMMENDATIONS.md`](file:///d:/Projects/VigilPay-%20Transaction%20Risk%20&%20Fraud%20Analytics%20Platform/RECOMMENDATIONS.md)):

1. **Targeted Step-Up 2FA Authentication**:
   - Limit mandatory 2FA steps exclusively to `TRANSFER` and `CASH_OUT` transaction types exceeding \$50,000, eliminating friction for 95%+ of legitimate payment transactions.
2. **Dynamic Off-Peak Rule Tightening**:
   - Automatically lower rule velocity thresholds during **01:00 AM – 05:00 AM** off-peak hours where fraud incidence per transaction increases by ~4.2x.
3. **Automated Account Velocity Cooldowns**:
   - Implement a temporary 15-minute cooling period on destination accounts receiving more than 3 high-value transfers within 10 minutes.
4. **False Positive Reduction Strategy**:
   - Require both an ML probability score $> 0.65$ AND at least 1 deterministic rule flag before issuing a hard **BLOCK**, reducing false-positive customer declines by ~25%.

---

<div align="center">

Built with Python · DuckDB · dbt-core · FastAPI · Streamlit · scikit-learn · SHAP · Apache Airflow

</div>
