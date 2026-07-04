from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from app.auth.jira_oauth import (
    build_authorization_url,
    exchange_code_for_token,
    get_accessible_resources,
)
from app.core.token_store import jira_resources, jira_token_data

router = APIRouter(prefix="/jira/oauth", tags=["OAuth"])


@router.get("/login")
def login():
    return RedirectResponse(build_authorization_url())


@router.get("/callback")
async def callback(code: str = Query(...)):
    token_data = await exchange_code_for_token(code)
    access_token = token_data["access_token"]

    resources = await get_accessible_resources(access_token)

    jira_token_data.clear()
    jira_token_data.update(token_data)

    jira_resources.clear()
    jira_resources.extend(resources)

    return {
        "message": "OAuth completed successfully",
        "site": resources[0]["url"] if resources else None,
        "cloud_id": resources[0]["id"] if resources else None,
        "has_access_token": bool(access_token),
        "has_refresh_token": bool(token_data.get("refresh_token")),
    }
