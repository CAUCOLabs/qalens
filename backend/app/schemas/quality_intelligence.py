from typing import Any

from pydantic import BaseModel, Field

from app.schemas.change_intelligence import (
    ChangeAnalysisRequest,
    ChangeAnalysisResponse,
)
from app.schemas.traceability import TraceabilityReport


class QualityIntelligenceRequest(BaseModel):
    issue_key: str
    change: ChangeAnalysisRequest


class QualityIntelligenceResponse(BaseModel):
    issue_key: str

    issue_analysis: dict[str, Any]
    traceability: TraceabilityReport
    change_analysis: ChangeAnalysisResponse

    overall_risk_level: str
    release_readiness: str
    overall_quality_gate: str

    decision_reasons: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
