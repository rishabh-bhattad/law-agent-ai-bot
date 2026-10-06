from fastapi import APIRouter, Depends
from app.schemas import CamelModel

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