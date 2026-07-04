from urllib.parse import urlencode

import httpx

from app.core.config import settings


AUTH_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"
ACCESSIBLE_RESOURCES_URL = "https://api.atlassian.com/oauth/token/accessible-resources"


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


async def exchange_code_for_token(code: str) -> dict:
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.jira_client_id,
        "client_secret": settings.jira_client_secret,
        "code": code,
        "redirect_uri": settings.jira_redirect_uri,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(TOKEN_URL, json=payload)
        response.raise_for_status()
        return response.json()


async def get_accessible_resources(access_token: str) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(ACCESSIBLE_RESOURCES_URL, headers=headers)
        response.raise_for_status()
        return response.json()
