from typing import cast

from fastapi import APIRouter, Request

from app.schemas.embed import EmbeddingsRequest, EmbeddingsResponse
from app.services.embed_service import EmbeddingsService

router = APIRouter()


@router.post("/embeddings", response_model=EmbeddingsResponse)
async def embeddings(req: EmbeddingsRequest, request: Request) -> EmbeddingsResponse:
    embed_service = cast(EmbeddingsService, request.app.state.embeddings_service)
    return await embed_service.embed(req)