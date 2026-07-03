from app.integrations.jira.client import JiraClient
from app.schemas.jira import JiraConnectionStatus


class JiraService:
    def __init__(self):
        self.client = JiraClient()

    def get_connection_status(self) -> JiraConnectionStatus:
        if self.client.is_configured():
            return JiraConnectionStatus(
                connected=True,
                message="Jira integration is configured.",
            )

        return JiraConnectionStatus(
            connected=False,
            message="Jira integration is not configured yet.",
        )
