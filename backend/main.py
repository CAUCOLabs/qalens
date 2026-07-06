from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.oauth import router as oauth_router
from app.api.routes.health import router as health_router
from app.api.routes.jira import router as jira_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="AI-powered QA intelligence platform for Jira.",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(jira_router)
app.include_router(oauth_router)