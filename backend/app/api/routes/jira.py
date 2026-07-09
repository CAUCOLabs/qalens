from fastapi import APIRouter, HTTPException, Query

from app.schemas.analysis import IssueAnalysisResponse
from app.schemas.jira import JiraConnectionStatus, JiraIssue, JiraIssuesResponse
from app.services.analysis_service import AnalysisService
from app.services.jira_service import JiraService
from app.services.traceability_service import TraceabilityService

router = APIRouter(prefix="/jira", tags=["Jira"])


@router.get("/status", response_model=JiraConnectionStatus)
def jira_status():
    service = JiraService()
    return service.get_connection_status()


@router.get("/projects")
async def jira_projects():
    service = JiraService()
    return await service.get_projects()


@router.get("/issues", response_model=JiraIssuesResponse)
async def jira_issues(project_key: str = Query(...)):
    service = JiraService()
    return await service.get_issues(project_key=project_key)


@router.get("/issue/{issue_key}", response_model=JiraIssue)
async def jira_issue(issue_key: str):
    service = JiraService()
    return await service.get_issue(issue_key=issue_key)


@router.get("/issue/{issue_key}/analyze")
async def analyze_jira_issue(issue_key: str):
    jira_service = JiraService()
    analysis_service = AnalysisService()

    issue = await jira_service.get_issue(issue_key=issue_key)

    if isinstance(issue, dict) and issue.get("error"):
        raise HTTPException(status_code=400, detail=issue["error"])

    return analysis_service.analyze_issue(issue)


@router.get("/project/{project_key}/analyze")
async def analyze_jira_project(project_key: str):
    jira_service = JiraService()
    analysis_service = AnalysisService()

    issues_response = await jira_service.get_issues(project_key=project_key)

    if isinstance(issues_response, dict) and issues_response.get("error"):
        raise HTTPException(status_code=400, detail=issues_response["error"])

    return analysis_service.analyze_project(
        project_key=project_key,
        issues=issues_response.issues,
    )


@router.get("/issue/{issue_key}/traceability")
async def analyze_issue_traceability(issue_key: str):
    jira_service = JiraService()
    traceability_service = TraceabilityService()

    raw_issue = await jira_service.get_raw_issue(issue_key=issue_key)

    if isinstance(raw_issue, dict) and raw_issue.get("error"):
        raise HTTPException(status_code=400, detail=raw_issue["error"])

    return traceability_service.analyze_issue_traceability(raw_issue)

