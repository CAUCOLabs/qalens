from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.auth.jira_oauth import build_authorization_url

router = APIRouter(prefix="/jira/oauth", tags=["OAuth"])


@router.get("/login")
def login():
    return RedirectResponse(build_authorization_url())