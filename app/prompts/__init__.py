import json
from importlib import resources
from typing import Type
from app.schemas import CamelModel


def get_prompt_template(template_name: str) -> str:
    """
    Reads a markdown file from the templates directory.
    Usage: get_prompt_template("briefing.md")
    """
    return resources.files("app.prompts.templates").joinpath(template_name).read_text(encoding="utf-8")

def get_global_rules() -> str:
    rules_dir = resources.files("app.prompts.rules")
    rules = ""
    for item in rules_dir.iterdir():
        if item.name.endswith(".md"):
            rules = rules + "\n" + item.read_text(encoding="utf-8")

    return rules

def build_schema_prompt(template_name: str, schema: Type[CamelModel], **kwargs) -> str:
    """
    Loads a template, converts a Pydantic schema to a JSON string, 
    and injects it along with any other variables.
    """
    formatted_schema = json.dumps(schema.model_json_schema(), indent=2)
    rules = get_global_rules()
    return get_prompt_template(template_name=template_name).format(schema=formatted_schema, **kwargs) + "\n\n" + rules

