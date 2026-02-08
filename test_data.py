#!/usr/bin/env python3
"""
Quick test script to verify synthetic data and run sample evaluations.

Usage:
    python test_data.py

This will:
1. Load all synthetic datasets
2. Print statistics
3. Test the pipeline with sample transactions
4. Verify data quality
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import (
    load_transactions,
    load_historical_cases,
    load_edge_cases,
    get_statistics,
    print_dataset_summary
)


def test_data_loading():
    """Test that all data loads correctly."""
    print("\n" + "="*60)
    print("DATA LOADING TEST")
    print("="*60)

    try:
        test_txns = load_transactions()
        print(f"✓ Loaded test transactions: {len(test_txns)} records")
    except Exception as e:
        print(f"✗ Error loading test transactions: {e}")
        return False

    try:
        historical = load_historical_cases()
        print(f"✓ Loaded historical cases: {len(historical)} records")
    except Exception as e:
        print(f"✗ Error loading historical cases: {e}")
        return False

    try:
        edge_cases = load_edge_cases()
        print(f"✓ Loaded edge cases: {len(edge_cases)} records")
    except Exception as e:
        print(f"✗ Error loading edge cases: {e}")
        return False

    return True


def test_data_quality():
    """Verify data quality and schema."""
    print("\n" + "="*60)
    print("DATA QUALITY CHECK")
    print("="*60)

    test_txns = load_transactions()

    # Check required columns
    required_columns = [
        'transaction_id', 'amount', 'country', 'device_new',
        'velocity', 'merchant_category', 'account_age_days', 'ground_truth'
    ]

    missing_cols = [col for col in required_columns if col not in test_txns.columns]
    if missing_cols:
        print(f"✗ Missing columns: {missing_cols}")
        return False

    print(f"✓ All required columns present: {len(required_columns)}")

    # Check for missing values
    missing_values = test_txns.isnull().sum()
    if missing_values.any():
        print(f"✗ Found missing values:\n{missing_values[missing_values > 0]}")
        return False

    print(f"✓ No missing values in dataset")

    # Check ground truth values
    valid_labels = {'low', 'medium', 'high'}
    invalid_labels = set(test_txns['ground_truth'].unique()) - valid_labels
    if invalid_labels:
        print(f"✗ Invalid ground truth labels: {invalid_labels}")
        return False

    print(f"✓ Valid ground truth labels: {test_txns['ground_truth'].unique().tolist()}")

    # Check numeric ranges
    if (test_txns['amount'] < 0).any():
        print(f"✗ Found negative amounts")
        return False

    if (test_txns['velocity'] < 0).any():
        print(f"✗ Found negative velocity values")
        return False

    print(f"✓ Valid numeric ranges (amount, velocity)")

    # Check country codes
    if (test_txns['country'].str.len() != 2).any():
        print(f"✗ Invalid country codes (should be 2 letters)")
        return False

    print(f"✓ Valid country codes: {test_txns['country'].nunique()} unique")

    return True


def test_statistics():
    """Print and verify statistics."""
    print("\n" + "="*60)
    print("DATA STATISTICS")
    print("="*60)

    test_txns = load_transactions()
    stats = get_statistics(test_txns)

    print(f"\n📊 Overview:")
    print(f"  Total Records: {stats['count']}")
    print(f"  By Risk Level: {stats['by_label']}")
    print(f"  Countries: {stats['country_diversity']} unique")

    print(f"\n💰 Amount Statistics (€):")
    print(f"  Mean: €{stats['amount_stats']['mean']:,.2f}")
    print(f"  Median: €{stats['amount_stats']['median']:,.2f}")
    print(f"  Min: €{stats['amount_stats']['min']:,.2f}")
    print(f"  Max: €{stats['amount_stats']['max']:,.2f}")
    print(f"  StdDev: €{stats['amount_stats']['std']:,.2f}")

    print(f"\n📱 Device Profile:")
    print(f"  New Devices: {stats['device_new_pct']:.0f}%")
    print(f"  Average Velocity: {stats['avg_velocity']:.2f}")
    print(f"  Average Account Age: {stats['avg_account_age']:.0f} days")

    print(f"\n🌍 Geographic Distribution:")
    print(f"  Countries: {', '.join(stats['countries'])}")

    print(f"\n🏪 Merchant Categories:")
    print(f"  Categories: {stats['merchant_categories']} unique")

    return True


def test_edge_cases():
    """Verify edge cases dataset."""
    print("\n" + "="*60)
    print("EDGE CASES VALIDATION")
    print("="*60)

    edge_cases = load_edge_cases()
    print(f"✓ Loaded {len(edge_cases)} edge case scenarios")

    print(f"\nEdge Case Examples:")
    for idx, row in edge_cases.head(5).iterrows():
        print(f"  - {row['transaction_id']}: €{row['amount']} ({row['description']})")

    return True


def test_historical_cases():
    """Verify historical cases for RAG."""
    print("\n" + "="*60)
    print("HISTORICAL CASES FOR RAG")
    print("="*60)

    historical = load_historical_cases()
    print(f"✓ Loaded {len(historical)} historical cases")

    # Check risk score calibration
    print(f"\nRisk Score Distribution:")
    print(f"  Mean: {historical['risk_score'].mean():.2f}")
    print(f"  Median: {historical['risk_score'].median():.2f}")
    print(f"  Min: {historical['risk_score'].min():.2f}")
    print(f"  Max: {historical['risk_score'].max():.2f}")

    # Check label distribution
    print(f"\nLabel Distribution:")
    label_dist = historical['label'].value_counts()
    for label, count in label_dist.items():
        print(f"  {label}: {count} ({count/len(historical)*100:.0f}%)")

    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  SYNTHETIC DATA VALIDATION & TESTING")
    print("="*70)

    # Print dataset summary first
    print_dataset_summary()

    # Run tests
    all_passed = True

    tests = [
        ("Data Loading", test_data_loading),
        ("Data Quality", test_data_quality),
        ("Statistics", test_statistics),
        ("Edge Cases", test_edge_cases),
        ("Historical Cases", test_historical_cases),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
            all_passed = all_passed and passed
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
            all_passed = False

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} - {test_name}")

    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL TESTS PASSED - Data is ready for evaluation!")
        print("\nNext Steps:")
        print("  1. Run: jupyter notebook notebooks/evaluations.ipynb")
        print("  2. Set: export OPENAI_API_KEY=your-key")
        print("  3. Execute all cells to generate evaluation report")
    else:
        print("✗ SOME TESTS FAILED - Please check the data")
    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
