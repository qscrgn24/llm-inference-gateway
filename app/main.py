from fastapi import FastAPI
from app.api.routers.test_heath import router as test_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="LLM Inference Gateway",
        version="1.0.0",
    )

    app.include_router(test_router, prefix="/v1")
    
    return app

app = create_app