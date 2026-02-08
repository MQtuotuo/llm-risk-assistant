"""
Deterministic decision logic for fraud risk assessment.

This module provides post-processing rules to ensure consistent, deterministic
mapping from risk level + confidence scores to recommended actions. This fixes
the 0% action consistency issue by eliminating non-deterministic LLM behavior.

The logic ensures that given the same risk_level and confidence, the same
action is ALWAYS recommended.
"""

from src.schemas import RiskAssessment
from typing import Tuple


def apply_decision_logic(assessment: RiskAssessment) -> RiskAssessment:
    """
    Apply deterministic decision rules to ensure consistent action mapping.

    This function overrides the LLM's recommended_action with a deterministic
    decision based on risk_level and confidence score. This ensures that:
    - Same inputs always produce same outputs
    - Business rules are consistently applied
    - No randomness from LLM affects the final decision

    Decision Rules:
    1. HIGH RISK + High Confidence (≥85%):   BLOCK
    2. HIGH RISK + Medium Confidence (≥70%): REVIEW
    3. HIGH RISK + Low Confidence (<70%):    REVIEW
    4. MEDIUM RISK + Any Confidence:         REVIEW
    5. LOW RISK + Any Confidence:            APPROVE

    Args:
        assessment (RiskAssessment): LLM-generated risk assessment

    Returns:
        RiskAssessment: Same assessment with deterministically mapped action
    """
    original_action = assessment.recommended_action
    risk_level = assessment.risk_level.lower()
    confidence = assessment.confidence

    # Apply deterministic decision rules
    if risk_level == "high":
        if confidence >= 0.85:
            new_action = "block"
        elif confidence >= 0.70:
            new_action = "review"
        else:
            new_action = "review"
    elif risk_level == "medium":
        new_action = "review"
    elif risk_level == "low":
        new_action = "approve"
    else:
        # Fallback for unexpected risk levels
        new_action = "review"

    # Create new assessment with deterministic action
    assessment.recommended_action = new_action

    return assessment


def get_decision_rationale(assessment: RiskAssessment) -> str:
    """
    Generate a human-readable explanation of the decision logic applied.

    Args:
        assessment (RiskAssessment): Risk assessment result

    Returns:
        str: Explanation of why this action was recommended
    """
    risk_level = assessment.risk_level.lower()
    confidence = assessment.confidence
    action = assessment.recommended_action

    rationale = f"Risk Level: {risk_level.upper()} | Confidence: {confidence:.1%} | Action: {action.upper()}\n"

    if risk_level == "high":
        if confidence >= 0.85:
            rationale += "Decision: HIGH confidence + HIGH risk → BLOCK transaction"
        elif confidence >= 0.70:
            rationale += "Decision: MEDIUM confidence + HIGH risk → REVIEW transaction (requires manual verification)"
        else:
            rationale += "Decision: LOW confidence + HIGH risk → REVIEW transaction (requires manual verification)"
    elif risk_level == "medium":
        rationale += "Decision: MEDIUM risk → REVIEW transaction (requires manual verification)"
    elif risk_level == "low":
        rationale += "Decision: LOW risk → APPROVE transaction"

    return rationale


def validate_decision_consistency(assessments: list) -> dict:
    """
    Validate that the same transaction always produces the same action.

    This is used for testing to ensure determinism works correctly.

    Args:
        assessments (list): Multiple RiskAssessment results for the same transaction

    Returns:
        dict: Consistency metrics
    """
    if not assessments:
        return {"consistency": 1.0, "all_actions_same": True, "actions": []}

    actions = [a.recommended_action for a in assessments]
    all_same = len(set(actions)) == 1
    consistency = sum(1 for a in actions if a == actions[0]) / len(actions)

    return {
        "consistency": consistency,
        "all_actions_same": all_same,
        "actions": actions,
        "action_distribution": {
            action: sum(1 for a in actions if a == action) for action in set(actions)
        }
    }
