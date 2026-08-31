from app.schemas import CamelModel

class CaseBrief(CamelModel):
    case_name: str
    holding: str
    reasoning: str