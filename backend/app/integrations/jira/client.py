from app.core.config import settings


class JiraClient:
    def __init__(self):
        self.base_url = settings.jira_base_url

    def is_configured(self) -> bool:
        return bool(self.base_url)
