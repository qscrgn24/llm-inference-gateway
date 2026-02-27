from fastapi import FastAPI

from app.api.routers.test_heath import router as test_router
from app.api.routers.chat import router as chat_router
from app.core.logging import setup_logging
from app.core.middleware  import RequestContextMiddleware
from app.providers.fake_provider import FakeChatProvider
from app.services.chat_services import ChatService

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="LLM Inference Gateway",
        version="1.0.0",
    )

    app.add_middleware(RequestContextMiddleware)

    app.state.chat_service = ChatService(provider=FakeChatProvider())

    app.include_router(test_router, prefix="/v1")
    app.include_router(chat_router, prefix="/v1")
    
    return app

app = create_app