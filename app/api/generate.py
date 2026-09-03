from fastapi import APIRouter, Depends
from app.schemas import CamelModel

from app.api.deps import get_briefing_service
from app.services.briefing import BriefingService
from app.schemas.brief import CaseBrief

router = APIRouter()

class GenerateBriefRequest(CamelModel):
    query: str


@router.post("/generate", response_model=CaseBrief)
async def generate_brief_endpoint(
    request: GenerateBriefRequest,
    service: BriefingService = Depends(get_briefing_service)
) -> CaseBrief:
    return await service.generate_brief(request.query)