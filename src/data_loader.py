"""
Data loading utilities for evaluation and testing.

This module provides functions to load synthetic datasets for testing
the fraud risk assessment system.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple


def load_transactions(filepath: str = "data/transactions/test_transactions.json") -> pd.DataFrame:
    """
    Load transaction test dataset from JSON file.

    Args:
        filepath (str): Path to the transactions JSON file

    Returns:
        pd.DataFrame: DataFrame with columns:
                     - transaction_id: Unique transaction identifier
                     - amount: Transaction amount in euros
                     - country: Country code
                     - device_new: Whether device is new
                     - velocity: Transaction velocity (count in 10 min window)
                     - merchant_category: Category of merchant
                     - account_age_days: Age of account in days
                     - ground_truth: True risk label (low/medium/high)
                     - description: Human-readable description
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def load_historical_cases(filepath: str = "data/cases/historical_cases.csv") -> pd.DataFrame:
    """
    Load historical fraud cases for context/grounding.

    Args:
        filepath (str): Path to the historical cases CSV file

    Returns:
        pd.DataFrame: DataFrame with columns:
                     - case_id: Case identifier
                     - amount: Transaction amount
                     - country: Country code
                     - device_new: Device status
                     - velocity: Transaction velocity
                     - merchant_category: Merchant type
                     - account_age_days: Account age
                     - label: Risk label (Low/Medium/High)
                     - notes: Case description
                     - risk_score: Calculated risk score (0-1)
    """
    return pd.read_csv(filepath)


def load_edge_cases(filepath: str = "data/transactions/edge_cases.json") -> pd.DataFrame:
    """
    Load edge case transactions for boundary testing.

    Args:
        filepath (str): Path to the edge cases JSON file

    Returns:
        pd.DataFrame: DataFrame with edge case transactions
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def get_sample_by_label(df: pd.DataFrame, label: str, n: int = 3) -> pd.DataFrame:
    """
    Get sample transactions filtered by risk label.

    Args:
        df (pd.DataFrame): Transaction dataframe
        label (str): Risk label to filter by ('low', 'medium', 'high')
        n (int): Number of samples to return

    Returns:
        pd.DataFrame: Filtered dataframe with up to n transactions
    """
    filtered = df[df['ground_truth'].str.lower() == label.lower()]
    return filtered.head(n)


def get_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get statistics about the transaction dataset.

    Args:
        df (pd.DataFrame): Transaction dataframe

    Returns:
        Dict containing statistics:
               - count: Total transactions
               - by_label: Distribution by risk label
               - amount_stats: Amount statistics
               - country_diversity: Number of unique countries
               - device_new_pct: Percentage with new devices
               - avg_velocity: Average velocity score
    """
    stats = {
        'count': len(df),
        'by_label': df['ground_truth'].value_counts().to_dict(),
        'amount_stats': {
            'mean': float(df['amount'].mean()),
            'median': float(df['amount'].median()),
            'min': float(df['amount'].min()),
            'max': float(df['amount'].max()),
            'std': float(df['amount'].std())
        },
        'country_diversity': df['country'].nunique(),
        'countries': df['country'].unique().tolist(),
        'device_new_pct': float((df['device_new'].sum() / len(df)) * 100),
        'avg_velocity': float(df['velocity'].mean()),
        'avg_account_age': float(df['account_age_days'].mean()),
        'merchant_categories': df['merchant_category'].nunique()
    }
    return stats


def export_for_evaluation(output_dir: str = "data/evaluation") -> None:
    """
    Export all datasets in a structured format for evaluation.

    Creates subdirectories with curated datasets for different evaluation scenarios:
    - all_transactions.json: All test transactions
    - by_risk_level/: Transactions grouped by risk level
    - statistics.json: Dataset statistics

    Args:
        output_dir (str): Directory to export evaluation data to
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load all data
    test_txns = load_transactions()
    edge_cases = load_edge_cases()
    historical = load_historical_cases()

    # Save combined dataset
    combined = pd.concat([test_txns, edge_cases], ignore_index=True)
    combined.to_json(output_path / 'all_transactions.json', orient='records', indent=2)

    # Save by risk level
    by_risk = output_path / 'by_risk_level'
    by_risk.mkdir(exist_ok=True)

    for label in ['low', 'medium', 'high']:
        subset = get_sample_by_label(combined, label, n=100)
        subset.to_json(by_risk / f'{label}_risk.json', orient='records', indent=2)

    # Save statistics
    stats = get_statistics(combined)
    with open(output_path / 'statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)

    # Save historical cases
    historical.to_csv(output_path / 'historical_cases.csv', index=False)

    print(f"✓ Exported evaluation data to {output_dir}")
    print(f"  - Combined transactions: {len(combined)}")
    print(f"  - Historical cases: {len(historical)}")
    print(f"  - Statistics: {len(stats)} metrics")


def print_dataset_summary() -> None:
    """Print summary of all available datasets."""
    print("="*60)
    print("SYNTHETIC DATA SUMMARY")
    print("="*60)

    # Load test transactions
    test_txns = load_transactions()
    print(f"\n📊 Test Transactions (test_transactions.json):")
    print(f"   Total: {len(test_txns)}")
    stats = get_statistics(test_txns)
    print(f"   By Label: {stats['by_label']}")
    print(f"   Countries: {stats['country_diversity']} unique")
    print(f"   Amount Range: €{stats['amount_stats']['min']:.2f} - €{stats['amount_stats']['max']:.2f}")
    print(f"   New Devices: {stats['device_new_pct']:.0f}%")

    # Load edge cases
    edge = load_edge_cases()
    print(f"\n🔍 Edge Cases (edge_cases.json):")
    print(f"   Total: {len(edge)}")
    print(f"   Focus: Boundary conditions and corner cases")

    # Load historical cases
    historical = load_historical_cases()
    print(f"\n📜 Historical Cases (historical_cases.csv):")
    print(f"   Total: {len(historical)}")
    print(f"   Use: Grounding context for RAG")
    print(f"   Risk Scores: Manually calibrated")

    print("\n" + "="*60)


if __name__ == "__main__":
    # Example usage
    print_dataset_summary()

    # Load and explore data
    test_txns = load_transactions()
    print(f"\n✓ Loaded {len(test_txns)} test transactions")
    print("\nSample transactions:")
    print(test_txns[['transaction_id', 'amount', 'country', 'device_new', 'ground_truth']].head(10))

    # Export for evaluation
    export_for_evaluation()
