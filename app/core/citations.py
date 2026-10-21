import re
import html
from urllib.parse import quote
from app.schemas.brief import CaseBrief, CitationItem

# Standard legal citation regex
CITATION_INDEX = re.compile(r'\b\d+\s+[A-Za-z\.\s]+\s+\d+\b')


def build_courtlistner_url(citation: str) -> str:
    """Build a direct CourtListner citation redirect url"""
    citation = citation.strip()
    if citation.startswith(('https', 'http')):
        return citation
    match = re.search(r'(\d+)\s+([A-Za-z0-9\.\s]+?)\s+(\d+)', citation)
    if match:
        return f"https://www.courtlistener.com/c/{quote(match.group(2).strip())}/{match.group(1)}/{match.group(3)}/"
    return f"https://www.courtlistener.com/?q={quote(citation)}&type=o"


def extract_citations(text: str) -> list[str]:
    """Extracts legal citations using eyecite if available, else falling back to regex"""
    try:
        from eyecite import get_citations

        citations = get_citations(text)
        return [c.matched_text() for c in citations]
    except ImportError:
        return re.findall(CITATION_INDEX, text)


def enrich_brief_citations(brief: CaseBrief) -> CaseBrief:
    """Enriches a CaseBrief by populating its citation_details with CourtListener URLs."""
    details = []
    for item in brief.citation:
        extracted = extract_citations(item)
        clean_ciation = extracted[0] if extracted else item
        url = build_courtlistner_url(clean_ciation)
        details.append(CitationItem(citation=clean_ciation, url=url))
    brief.citation_details = details
    return brief


def clean_opinion_text(raw_html: str, max_chars: int = 15000) -> str:
    """Strips HTML tags, finds the majority opinion starting point, and limits context length."""
    if not raw_html:
        return ""
    text = re.sub(r'<[^>]+>', ' ', raw_html)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Locate start of the substantive majority opinion if present to skip counsel lists
    markers = [
        'delivered the opinion of the Court',
        'Opinion of the court',
        'OPINION OF THE COURT',
        'delivered the opinion'
    ]
    for marker in markers:
        idx = text.find(marker)
        if idx != -1 and idx < len(text) - 1000:
            start_idx = max(0, idx - 100)
            text = text[start_idx:]
            break

    if len(text) > max_chars:
        last_period = text[:max_chars].rfind('.')
        if last_period > int(max_chars * 0.8):
            text = text[:last_period + 1]
        else:
            text = text[:max_chars]
    return text


def select_primary_opinion(search_results: list) -> tuple[dict, str | None]:
    """Identifies the primary landmark case from search results and extracts its lead opinion ID."""
    if not search_results:
        return {}, None

    # Top candidates sorted by citeCount to prioritize substantive merits decisions over cert denials
    candidates = search_results[:5]
    sorted_candidates = sorted(
        candidates,
        key=lambda c: (c.get('citeCount') or 0) if isinstance(c, dict) else 0,
        reverse=True
    )
    primary = sorted_candidates[0]
    if not isinstance(primary, dict):
        return {"snippet": str(primary), "caseName": str(primary)}, None

    # Find the lead or combined opinion ID
    opinions = primary.get('opinions', [])
    opinion_id = None
    if isinstance(opinions, list):
        for op in opinions:
            if isinstance(op, dict) and op.get('type') in ('lead-opinion', 'combined-opinion'):
                opinion_id = op.get('id')
                break
        if not opinion_id and opinions and isinstance(opinions[0], dict):
            opinion_id = opinions[0].get('id')
    if not opinion_id:
        opinion_id = primary.get('id') or primary.get('cluster_id')

    return primary, str(opinion_id) if opinion_id else None