from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers.test_heath import router as test_router
from app.api.routers.chat import router as chat_router
from app.core.logging import setup_logging
from app.core.middleware  import RequestContextMiddleware
from app.core.errors import AppError
from app.core.config import settings
from app.providers.fake_provider import FakeChatProvider
from app.providers.openai_provider import OpenAIChatProvider
from app.services.chat_services import ChatService

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="LLM Inference Gateway",
        version="1.0.0",
    )

    app.add_middleware(RequestContextMiddleware)

    if settings.openai_api_key:
        provider = OpenAIChatProvider()
    else:
        provider = FakeChatProvider()

    app.state.chat_service = ChatService(provider=provider)

    app.include_router(test_router, prefix="/v1")
    app.include_router(chat_router, prefix="/v1")

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "retryable": exc.retryable,
                    "details": exc.details,
                }
            },
        )
    
    return app

app = create_app