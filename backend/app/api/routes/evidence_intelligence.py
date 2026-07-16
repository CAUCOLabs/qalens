from fastapi import APIRouter

from app.schemas.evidence_intelligence import (
    EvidenceIntelligenceRequest,
    EvidenceIntelligenceResponse,
)
from app.services.evidence_intelligence_service import (
    EvidenceIntelligenceService,
)

router = APIRouter(
    prefix="/evidence-intelligence",
    tags=["Evidence Intelligence"],
)


@router.post(
    "/analyze",
    response_model=EvidenceIntelligenceResponse,
)
def analyze_evidence(request: EvidenceIntelligenceRequest):
    service = EvidenceIntelligenceService()
    return service.analyze(request)
