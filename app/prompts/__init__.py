from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

def get_prompt_template(template_name: str) -> str:
    """
    Reads a markdown file from the templates directory.
    Usage: get_prompt_template("briefing.md")
    """
    full_path = Path(TEMPLATES_DIR) / template_name
    return full_path.read_text(encoding="utf-8")

