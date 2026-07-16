from fastapi import APIRouter, HTTPException

from app.schemas.quality_intelligence import (
    QualityIntelligenceRequest,
    QualityIntelligenceResponse,
)
from app.services.analysis_service import AnalysisService
from app.services.change_intelligence_service import ChangeIntelligenceService
from app.services.jira_service import JiraService
from app.services.quality_intelligence_service import QualityIntelligenceService
from app.services.traceability_service import TraceabilityService

router = APIRouter(
    prefix="/quality-intelligence",
    tags=["Quality Intelligence"],
)


@router.post(
    "/analyze",
    response_model=QualityIntelligenceResponse,
)
async def analyze_quality_intelligence(
    request: QualityIntelligenceRequest,
):
    jira_service = JiraService()

    issue = await jira_service.get_issue(
        issue_key=request.issue_key,
    )
    raw_issue = await jira_service.get_raw_issue(
        issue_key=request.issue_key,
    )

    if isinstance(issue, dict) and issue.get("error"):
        raise HTTPException(
            status_code=400,
            detail=issue["error"],
        )

    if isinstance(raw_issue, dict) and raw_issue.get("error"):
        raise HTTPException(
            status_code=400,
            detail=raw_issue["error"],
        )

    if (
        request.change.issue_key
        and request.change.issue_key != request.issue_key
    ):
        raise HTTPException(
            status_code=422,
            detail="The change issue_key must match the orchestrator issue_key.",
        )

    change_request = request.change.model_copy(
        update={"issue_key": request.issue_key}
    )

    issue_analysis = AnalysisService().analyze_issue(issue)

    traceability = TraceabilityService().analyze_issue_traceability(
        raw_issue
    )

    change_analysis = ChangeIntelligenceService().analyze_change(
        change_request
    )

    return QualityIntelligenceService().orchestrate(
        issue_key=request.issue_key,
        issue_analysis=issue_analysis,
        traceability=traceability,
        change_analysis=change_analysis,
    )
