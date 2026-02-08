# Synthetic Data for Fraud Risk Assessment System

This directory contains comprehensive synthetic datasets designed for testing and evaluating the fraud risk assessment system.

## Dataset Overview

### 📊 **Transactions Data**

#### `sample_transaction.json`
- **Purpose:** Quick single transaction test
- **Records:** 1
- **Use Case:** Testing main pipeline
- **Fields:** amount, country, device_new, velocity

#### `test_transactions.json` ⭐ **PRIMARY DATASET**
- **Purpose:** Comprehensive evaluation and testing
- **Records:** 20 diverse transactions
- **Coverage:**
  - Low-risk transactions (normal behavior)
  - High-risk transactions (fraud indicators)
  - Medium-risk transactions (ambiguous cases)
  - Edge cases and boundary conditions
- **Fields:**
  - Basic: amount, country, device_new, velocity
  - Extended: merchant, location, timestamp, card_present
  - Metadata: merchant_category, customer_age, account_age_days
  - Labels: ground_truth (low/medium/high), description

#### `edge_cases.json` 🔍 **BOUNDARY TESTING**
- **Purpose:** Test system on corner cases and boundaries
- **Records:** 10 edge case scenarios
- **Examples:**
  - Just above/below €5,000 threshold
  - Extreme amounts (€1 and €50,000+)
  - Maximum velocity (9 transactions/10 min)
  - Conflicting risk signals (high-risk country, established customer)

### 📜 **Historical Cases (Context)**

#### `historical_cases.csv` 📚 **RAG CONTEXT DATA**
- **Purpose:** Provide grounding context for RAG system
- **Records:** 40 historical fraud and legitimate transaction cases
- **Use:** Vector store ingestion for similarity search
- **Risk Coverage:**
  - 15 High-risk cases (actual fraud)
  - 15 Low-risk cases (legitimate transactions)
  - 10 Medium-risk cases (borderline)
- **Columns:**
  - `case_id`: Unique identifier
  - `amount`: Transaction amount
  - `country`: Country code
  - `device_new`: New device flag
  - `velocity`: Transaction frequency
  - `merchant_category`: Type of merchant
  - `account_age_days`: Customer account age
  - `label`: Risk classification (High/Medium/Low)
  - `notes`: Case description
  - `risk_score`: Calibrated risk score (0-1)

### 📋 **Policy Documentation**

#### `card_fraud_policy.md` 📜 **COMPREHENSIVE POLICY**
- **Purpose:** Define fraud detection rules and thresholds
- **Sections:**
  1. Transaction Amount Rules (micro vs high-value)
  2. Geographic Risk Assessment (country tiers)
  3. Device and Account Risk Factors
  4. Transaction Velocity Rules
  5. Merchant Category Rules
  6. Decision Rules (block/approve/review)
  7. Risk Scoring Model
  8. Special Cases (travel, subscriptions)
  9. Compliance and Escalation
  10. Performance Targets

## Data Characteristics

### Risk Distribution
```
Low Risk:    45% (routine transactions, established customers)
Medium Risk: 20% (ambiguous, needs review)
High Risk:   35% (fraud indicators, should be blocked/escalated)
```

### Geographic Diversity
- **High-Risk Countries:** NG, GH, VN, RU, CN (30%)
- **Moderate-Risk Countries:** SG, JP, AE, PK (20%)
- **Low-Risk Countries:** US, DE, etc. (50%)

### Transaction Types
- **Small Retail:** €45-300 (28%)
- **Medium Purchases:** €1,200-3,500 (35%)
- **High-Value:** €5,000+ (25%)
- **Extreme/Edge Cases:** €1, €999,999 (12%)

### Account Profiles
- **New Accounts:** < 30 days (25%)
- **Growing Accounts:** 30-90 days (20%)
- **Established Accounts:** > 90 days (55%)

## Usage Examples

### Loading Data

```python
from src.data_loader import load_transactions, load_historical_cases, get_statistics

# Load test transactions
test_txns = load_transactions('data/transactions/test_transactions.json')
print(f"Loaded {len(test_txns)} transactions")

# Load historical cases for RAG
historical = load_historical_cases('data/cases/historical_cases.csv')
print(f"Loaded {len(historical)} historical cases")

# Get statistics
stats = get_statistics(test_txns)
print(f"Risk distribution: {stats['by_label']}")
```

### Filtering by Risk Level

```python
# Get low-risk transactions
low_risk = test_txns[test_txns['ground_truth'] == 'low']

# Get high-risk transactions
high_risk = test_txns[test_txns['ground_truth'] == 'high']

# Sample from edge cases
edge_cases = load_transactions('data/transactions/edge_cases.json')
boundary_cases = edge_cases.sample(n=3)
```

### Running Evaluations

```python
# Use in evaluation notebook
from notebooks.evaluations import *

# Load and use test dataset
test_data = load_transactions()
for _, txn in test_data.iterrows():
    assessment = run_agent(transaction=txn.to_dict())
    # Compare with ground_truth
```

## Data Quality Notes

### ✓ Synthetic Characteristics
- **Realistic:** Based on actual fraud patterns
- **Balanced:** Mix of high/low/medium risk
- **Diverse:** Multiple countries, merchants, patterns
- **Labeled:** Ground truth for all transactions
- **Documented:** Descriptions for each transaction

### ⚠️ Limitations
- **Synthetic Data:** Not real transactions (privacy)
- **Simplified Features:** Limited to key risk factors
- **Balanced Distribution:** Real fraud is < 1% (this dataset is ~35%)
- **No Temporal Patterns:** Limited time-series modeling

## Extending the Datasets

To add more data:

```python
# Add to test_transactions.json
new_transaction = {
    "transaction_id": "txn_021",
    "amount": 2500,
    "merchant": "New Merchant",
    "country": "US",
    "device_new": False,
    "velocity": 1,
    "ground_truth": "low",
    "description": "New test transaction"
}

# Add to historical_cases.csv
# Use the existing CSV format with case_id, amount, country, etc.
```

## For Evaluation

Run the evaluation notebook to:
1. Load all datasets
2. Compute RAG quality metrics
3. Test risk detection accuracy
4. Benchmark latency
5. Analyze hallucinations
6. Generate performance reports

```bash
# Make sure OPENAI_API_KEY is set
export OPENAI_API_KEY=your-key

# Run evaluation
jupyter notebook notebooks/evaluations.ipynb
```

## Data Statistics

**Total Transactions Available:** 30 (20 test + 10 edge cases)
**Historical Cases:** 40 (for RAG context)
**Risk Levels:** 3 (Low, Medium, High)
**Countries:** 15 unique
**Merchants:** 20+ categories
**Account Ages:** 1 day to 3000 days

---

**Last Updated:** February 2024
**Version:** 1.0
**Status:** ✓ Ready for evaluation and testing
