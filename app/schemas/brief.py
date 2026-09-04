from app.schemas import CamelModel
from pydantic import Field

class CaseBrief(CamelModel):
    case_name: str
    holding: str
    reasoning: str
    citation: list[str] = Field(
        description="A list of full case names, docket numbers, or URLs referenced in the text for further reading."
    )