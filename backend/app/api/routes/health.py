from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/")
def root():
    return {"status": "ok", "service": "QALens API"}

@router.get("/health")
def health():
    return {"status": "healthy"}
