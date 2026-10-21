from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.deps import get_briefing_pipeline
from app.workflow.context import WorkflowBudgetExceededError
from app.workflow.pipeline import BriefingPipeline
from app.schemas.brief import CaseBrief, GenerateBriefRequest, RepairBriefRequest

router = APIRouter()

@router.post("/generate", response_model=CaseBrief)
async def generate_brief_endpoint(
    request: GenerateBriefRequest,
    pipeline: BriefingPipeline = Depends(get_briefing_pipeline)
) -> CaseBrief:
    """Generates a structured legal case brief for the submitted query."""
    try:
        return await pipeline.execute(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WorkflowBudgetExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Workflow execution timed out.") from exc

@router.post("/generate/stream")
async def generate_brief_stream_endpoint(
    request: GenerateBriefRequest,
    pipeline: BriefingPipeline = Depends(get_briefing_pipeline)
) -> StreamingResponse:
    """Streams real-time SSE progress events and the final case Brief"""
    try:
        event_generator = pipeline.stream(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WorkflowBudgetExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    return StreamingResponse(
        content=event_generator,
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.post("/brief/repair", response_model=CaseBrief)
async def repair_brief_endpoint(
    request: RepairBriefRequest,
    pipeline: BriefingPipeline = Depends(get_briefing_pipeline)
) -> CaseBrief:
    """Refines a specific section of an existing brief without full regeneration."""
    try:
        return await pipeline.repair(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WorkflowBudgetExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Workflow execution timed out.") from exc