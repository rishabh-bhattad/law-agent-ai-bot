from app.schemas import CamelModel
from pydantic import Field


class TopicResearchRequest(CamelModel):
    """Request payload containing the legal topic or doctrine query."""
    topic: str


class PrecedentCase(CamelModel):
    """Structured representation of a landmark case establishing legal precedent."""
    case_name: str
    citation: str
    court: str = Field(description="Court name, e.g. 'Supreme Court of the United States'")
    year: str = Field(description="Decided year, e.g. '1966'")
    rule_or_precedent: str = Field(description="Core legal rule, test, or standard established by the decision.")
    courtroom_utility: str = Field(description="Practical litigation advice on when and how an attorney should cite this case.")
    key_holding: str = Field(description="Concise summary of the court's ultimate holding.")


class TopicPrecedentReport(CamelModel):
    """Synthesized research report on a legal topic or doctrine."""
    topic: str
    doctrine_overview: str = Field(description="Comprehensive explanation of the overarching legal doctrine and its modern test.")
    landmark_cases: list[PrecedentCase] = Field(description="Key foundational cases that define this legal doctrine.")
    practical_takeaway: str = Field(description="Strategic summary for attorneys litigating under this doctrine.")
