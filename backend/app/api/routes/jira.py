from fastapi import APIRouter

from app.schemas.jira import JiraConnectionStatus
from app.services.jira_service import JiraService

router = APIRouter(prefix="/jira", tags=["Jira"])


@router.get("/status", response_model=JiraConnectionStatus)
def jira_status():
    service = JiraService()
    return service.get_connection_status()
