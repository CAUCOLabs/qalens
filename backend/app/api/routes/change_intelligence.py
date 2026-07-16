from fastapi import APIRouter

from app.schemas.change_intelligence import (
    ChangeAnalysisRequest,
    ChangeAnalysisResponse,
)
from app.services.change_intelligence_service import ChangeIntelligenceService

router = APIRouter(
    prefix="/change-intelligence",
    tags=["Change Intelligence"],
)


@router.post("/analyze", response_model=ChangeAnalysisResponse)
def analyze_change(request: ChangeAnalysisRequest):
    service = ChangeIntelligenceService()
    return service.analyze_change(request)
