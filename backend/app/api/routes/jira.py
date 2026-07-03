from fastapi import APIRouter

from app.schemas.jira import JiraConnectionStatus

router = APIRouter(prefix="/jira", tags=["Jira"])


@router.get("/status", response_model=JiraConnectionStatus)
def jira_status():
    return JiraConnectionStatus(
        connected=False,
        message="Jira integration is not configured yet.",
    )
