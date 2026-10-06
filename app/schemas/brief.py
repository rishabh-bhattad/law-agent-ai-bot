from app.schemas import CamelModel
from pydantic import Field

class GenerateBriefRequest(CamelModel):
    """Request payload containing the legal research query."""
    query: str
    

class CaseBrief(CamelModel):
    """Structured case brief output."""
    case_name: str
    holding: str
    reasoning: str
    citation: list[str] = Field(
        description="A list of full case names, docket numbers, or URLs referenced in the text for further reading."
    )


class LegalAnalysis(CamelModel):
    """Intermediate extraction schema for legal issues and facts."""
    primary_issue: str
    material_facts: list[str]
    court_reasoning: str