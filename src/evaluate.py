"""
Evaluation metrics for model performance.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd


def decision_accuracy(predictions: List[str], labels: List[str]) -> float:
    """Accuracy: proportion of correct predictions."""
    correct = sum(p == l for p, l in zip(predictions, labels))
    return correct / len(labels)


def calculate_precision_recall_f1(predictions: List[str], ground_truth: List[str]) -> Dict[str, Any]:
    """Calculate precision, recall, and F1 score (binary: 'high' vs rest)."""
    tp = sum(1 for p, g in zip(predictions, ground_truth) if p == 'high' and g == 'high')
    fp = sum(1 for p, g in zip(predictions, ground_truth) if p == 'high' and g != 'high')
    fn = sum(1 for p, g in zip(predictions, ground_truth) if p != 'high' and g == 'high')
    tn = sum(1 for p, g in zip(predictions, ground_truth) if p != 'high' and g != 'high')

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn
    }


def calculate_confusion_matrix(predictions: List[str], ground_truth: List[str], labels: List[str]) -> 'pd.DataFrame':
    """Calculate confusion matrix for multi-class classification."""
    label_to_idx = {label: i for i, label in enumerate(labels)}
    cm = np.zeros((len(labels), len(labels)), dtype=int)

    for pred, true in zip(predictions, ground_truth):
        if true in label_to_idx and pred in label_to_idx:
            true_idx = label_to_idx[true]
            pred_idx = label_to_idx[pred]
            cm[true_idx, pred_idx] += 1

    return pd.DataFrame(cm, index=labels, columns=labels)

