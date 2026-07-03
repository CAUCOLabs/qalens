from urllib.parse import urlencode

from app.core.config import settings


AUTH_URL = "https://auth.atlassian.com/authorize"


def build_authorization_url() -> str:
    params = {
        "audience": "api.atlassian.com",
        "client_id": settings.jira_client_id,
        "scope": (
            "read:jira-work "
            "read:jira-user "
            "write:jira-work "
            "offline_access"
        ),
        "redirect_uri": settings.jira_redirect_uri,
        "response_type": "code",
        "prompt": "consent",
    }

    return f"{AUTH_URL}?{urlencode(params)}"