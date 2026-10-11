from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_briefing_pipeline
from app.workflow.pipeline import BriefingPipeline
from app.schemas.brief import CaseBrief
from app.schemas.brief import GenerateBriefRequest

router = APIRouter()

@router.post("/generate", response_model=CaseBrief)
async def generate_brief_endpoint(
    request: GenerateBriefRequest,
    pipeline: BriefingPipeline = Depends(get_briefing_pipeline)
) -> CaseBrief:
    """Generates a structured legal case brief for the submitted query."""
    return await pipeline.execute(request.query)

@router.post("/generate/stream")
async def generate_brief_stream_endpoint(
    request: GenerateBriefRequest,
    pipeline: BriefingPipeline = Depends(get_briefing_pipeline)
) -> StreamingResponse:
    """Streams real-time SSE progress events and the final case Brief"""
    event_generator = pipeline.stream(request.query)
    return StreamingResponse(
        content=event_generator,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )