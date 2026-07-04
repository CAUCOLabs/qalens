from fastapi import APIRouter, Query

from app.schemas.analysis import IssueAnalysisResponse
from app.schemas.jira import JiraConnectionStatus, JiraIssue, JiraIssuesResponse
from app.services.analysis_service import AnalysisService
from app.services.jira_service import JiraService

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


@router.get("/issue/{issue_key}/analyze", response_model=IssueAnalysisResponse)
async def analyze_jira_issue(issue_key: str):
    jira_service = JiraService()
    analysis_service = AnalysisService()

    issue = await jira_service.get_issue(issue_key=issue_key)

    return analysis_service.analyze_issue(issue)
