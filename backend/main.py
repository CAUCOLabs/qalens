from fastapi import FastAPI

app = FastAPI(
    title="QALens API",
    description="AI-powered QA intelligence platform for Jira.",
    version="0.1.0",
)

@app.get("/")
def root():
    return {"status": "ok", "service": "QALens API"}

@app.get("/health")
def health():
    return {"status": "healthy"}
