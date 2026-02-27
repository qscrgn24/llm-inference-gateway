from fastapi import FastAPI

from app.api.routers.test_heath import router as test_router
from app.core.logging import setup_logging
from app.core.middleware  import RequestContextMiddleware

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="LLM Inference Gateway",
        version="1.0.0",
    )

    app.add_middleware(RequestContextMiddleware)

    app.include_router(test_router, prefix="/v1")
    
    return app

app = create_app