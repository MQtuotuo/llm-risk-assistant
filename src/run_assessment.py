"""
Main entry point for the LLM Risk Assessment system.

This module orchestrates the complete fraud risk assessment pipeline:
1. Loads a sample transaction from JSON
2. Builds or loads the vector store with policy and case data
3. Retrieves relevant context documents
4. Runs the AI agent to perform risk assessment
5. Outputs the assessment results to a JSON file
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

from src.ingest import build_vector_store
from src.retrieval import retrieve_context
from src.agent import run_agent

SAMPLE_TX_PATH = Path("data/transactions/sample_transaction.json")
VECTORSTORE_DIR = Path("vectorstore")
OUTPUT_PATH = Path("evaluations_output.json")


def main() -> None:
    """
    Execute the complete risk assessment pipeline.

    Workflow:
    - Validates OPENAI_API_KEY environment variable
    - Loads sample transaction from JSON file
    - Initializes or loads the vector store with policy and historical case data
    - Executes the AI agent to assess fraud risk
    - Outputs the assessment result to a JSON file

    Returns:
        None

    Raises:
        SystemExit: If OPENAI_API_KEY environment variable is not set
    """
    if "OPENAI_API_KEY" not in os.environ:
        raise SystemExit("Set OPENAI_API_KEY in your environment (e.g. export OPENAI_API_KEY=...)")

    tx = json.loads(SAMPLE_TX_PATH.read_text())

    # build or load vectorstore (idempotent)
    build_vector_store()

    # run the agent (returns python dict or pydantic model)
    result = run_agent(transaction=tx)

    # normalize to dict and write
    if hasattr(result, "dict"):
        out = result.dict()
    else:
        out = result

    print(json.dumps(out, indent=2))
    OUTPUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"Wrote output to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()