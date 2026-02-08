# LLM-Powered Fraud & Risk Investigation Assistant

A production-oriented LLM system designed to assist fraud and risk analysts by combining transaction data, internal policies, and historical cases using retrieval-augmented generation (RAG). The system provides explainable, structured fraud risk assessments with confidence scores and policy references.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Evaluation](#evaluation)
- [Key Design Decisions](#key-design-decisions)
- [Limitations](#limitations)
- [Future Work](#future-work)

## Features

- **RAG-Powered Risk Assessment**: Retrieves relevant policies and historical cases for context
- **Structured Output**: JSON-formatted risk assessments with risk levels, factors, and recommendations
- **Explainability**: Policy references and confidence scores for every assessment
- **Deterministic Results**: LLM temperature set to 0 for consistent, reproducible decisions
- **Modular Architecture**: Easily extensible ingestion, retrieval, and assessment pipeline

## Architecture

```
┌─────────────────┐
│   Transaction   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Vector Store (Chroma + RAG)    │
│  - Policies (markdown)          │
│  - Historical Cases (CSV)       │
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   Context Retrieval              │
│   (Similarity Search)            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   LLM Agent (ChatOpenAI)         │
│   - System Prompt                │
│   - Transaction + Context        │
│   - Structured Output            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   Risk Assessment Result         │
│   - Risk Level                   │
│   - Risk Factors                 │
│   - Policy References            │
│   - Recommended Action           │
│   - Confidence Score             │
└──────────────────────────────────┘
```

### Key Components

- **Embeddings-based retrieval** over policies and past cases
- **Structured prompt-constrained reasoning** for consistent outputs
- **Deterministic LLM behavior** with temperature=0
- **Explainable decisions** with policy references and confidence scores

## Project Structure

```
llm-risk-assistant/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Project configuration
├── main.py                           # Alternative entry point
├── src/
│   ├── run_assessment.py            # Main pipeline orchestrator
│   ├── agent.py                     # LLM fraud risk agent
│   ├── retrieval.py                 # Context retrieval module
│   ├── ingest.py                    # Vector store ingestion
│   ├── evaluate.py                  # Evaluation metrics
│   ├── prompts.py                   # LLM prompt templates
│   └── schemas.py                   # Pydantic data models
├── data/
│   ├── transactions/
│   │   └── sample_transaction.json  # Sample transaction for testing
│   ├── policies/
│   │   └── card_fraud_policy.md     # Fraud detection policies
│   └── cases/
│       └── historical_cases.csv     # Historical fraud cases
├── notebooks/
│   └── evaluations.ipynb            # Evaluation analysis notebook
└── vectorstore/                     # Chroma vector database (generated)
```

## Installation

### Prerequisites

- Python 3.9+
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-risk-assistant
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Set the following environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-openai-api-key
```

## Usage

### Running the Assessment Pipeline

```bash
python -m src.run_assessment
```

This will:
1. Load the sample transaction from `data/transactions/sample_transaction.json`
2. Build or load the vector store with policies and cases
3. Retrieve relevant context documents
4. Run the LLM agent to assess fraud risk
5. Output the assessment to `evaluations_output.json`

### Output Format

```json
{
  "risk_level": "high",
  "key_risk_factors": [
    "Unusual transaction amount",
    "Geographic mismatch"
  ],
  "policy_references": [
    "Policy Section 3.2: Amount Thresholds",
    "Policy Section 4.1: Geographic Verification"
  ],
  "recommended_action": "block",
  "confidence": 0.92
}
```

### Programmatic Usage

```python
from src.agent import run_agent
import json

# Load your transaction
transaction = {
    "amount": 5000,
    "merchant": "Electronics Store",
    "location": "New York",
    "timestamp": "2024-02-08T10:30:00Z"
}

# Get risk assessment
assessment = run_agent(transaction=transaction)

# Access results
print(f"Risk Level: {assessment.risk_level}")
print(f"Confidence: {assessment.confidence}")
print(f"Recommended Action: {assessment.recommended_action}")
```
