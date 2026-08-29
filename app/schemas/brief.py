from pydantic import BaseModel

class CaseBrief(BaseModel):
    case_name: str
    holding: str
    reasoning: str