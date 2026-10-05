from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CaseAnalyzeRequest(BaseModel):
    order_id: str = Field(..., min_length=3)
    customer_id: Optional[str] = None
    sku: Optional[str] = None
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    inventory_status: Optional[str] = None
    warehouse_status: Optional[str] = None
    carrier_status: Optional[str] = None
    shipping_address_status: Optional[str] = None
    expected_delivery_date: Optional[str] = None
    current_delivery_status: Optional[str] = None
    tracking_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    carrier_name: Optional[str] = None
    quantity: Optional[int] = None
    priority: Optional[str] = None
    order_value: Optional[float] = None
    customer_notes: Optional[str] = None
    operational_notes: Optional[str] = None
    failure_description: str = Field(..., min_length=10)


class ClassificationResult(BaseModel):
    failure_reason: str
    confidence_score: float
    severity: str
    evidence: List[str]
    missing_evidence: List[str]
    explanation: str
    recommended_action: str
    requires_human_review: bool
    final_decision: str


class CaseResponse(BaseModel):
    case_id: str
    order_id: str
    customer_id: Optional[str] = None
    sku: Optional[str] = None
    status: str
    classification: Optional[ClassificationResult] = None
    final_decision: Optional[str] = None
    workflow_id: Optional[str] = None


class DashboardStats(BaseModel):
    total_cases: int
    auto_classified: int
    human_review: int
    critical: int
    latest_case: str


class ReviewSubmission(BaseModel):
    reviewer: str = Field(..., min_length=2)
    final_classification: str
    decision: str
    notes: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    detail: str
