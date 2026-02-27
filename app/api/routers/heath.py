from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/health")
def health(request: Request) -> dict:
    return {
        "status" : "ok",
        "version" : request.app.version,
    }