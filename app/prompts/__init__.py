import json
from pathlib import Path
from typing import Type
from app.schemas import CamelModel

TEMPLATES_DIR = Path(__file__).parent / "templates"

def get_prompt_template(template_name: str) -> str:
    """
    Reads a markdown file from the templates directory.
    Usage: get_prompt_template("briefing.md")
    """
    full_path = Path(TEMPLATES_DIR) / template_name
    return full_path.read_text(encoding="utf-8")


def build_schema_prompt(template_name: str, schema: Type[CamelModel], **kwargs) -> str:
    """
    Loads a template, converts a Pydantic schema to a JSON string, 
    and injects it along with any other variables.
    """
    formatted_schema = json.dumps(schema.model_json_schema(), indent=2)
    return get_prompt_template(template_name=template_name).format(schema=formatted_schema, **kwargs)

