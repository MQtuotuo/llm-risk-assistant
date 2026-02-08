"""
Pydantic schemas for structured data validation.

This module defines the data structures used throughout the risk assessment
system, ensuring type safety and validation of API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class RiskAssessment(BaseModel):
    """
    Structured output schema for fraud risk assessment results.

    Attributes:
        risk_level (str): Overall risk classification of the transaction
                         (e.g., 'low', 'medium', 'high')
        key_risk_factors (List[str]): List of identified risk factors that
                                      influenced the assessment
        policy_references (List[str]): Relevant policy sections or rules that
                                       were applied to the assessment
        recommended_action (str): Recommended action for the transaction
                                 (e.g., 'approve', 'block', 'review')
        confidence (float): Confidence score of the assessment, ranging from
                           0.0 (low confidence) to 1.0 (high confidence)
    """

    risk_level: str = Field(..., description="Overall risk classification (low, medium, high)")
    key_risk_factors: List[str] = Field(..., description="Identified risk factors")
    policy_references: List[str] = Field(..., description="Relevant policy sections cited")
    recommended_action: str = Field(..., description="Recommended action (approve, block, review)")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    # Optional fields populated by local validation / post-processing
    validation_flag: Optional[bool] = Field(False, description="Whether the assessment was modified/flagged by post-response validation")
    validation_notes: Optional[str] = Field(None, description="Notes from post-response validation explaining any overrides or flags")
    raw_response: Optional[dict] = Field(None, description="Raw LLM response (or parsed representation) for offline inspection")
