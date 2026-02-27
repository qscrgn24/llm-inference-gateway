from typing import cast

from fastapi import APIRouter, Request

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    """
    Thin route:
    - validates input via Pydantic
    - delegates business logic to ChatService
    - returns stable response schema

    ChatService is stored on app.state to keep wiring centralized in create_app().
    """
    chat_service = cast(ChatService, request.app.state.chat_service)
    return await chat_service.chat(req)