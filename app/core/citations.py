import re
from urllib.parse import quote
from app.schemas.brief import CaseBrief, CitationItem

# Standard legal citation regex
CITATION_INDEX = re.compile(r'\b\d+\s+[A-Za-z\.\s]+\s+\d+\b')


def build_courtlistner_url(citation: str) -> str:
    """Build a direct CourtListner citation redirect url"""
    citation = citation.strip()
    if citation.startswith(('https', 'http')):
        return citation
    return f"https://www.courtlistener.com/c/{quote(citation)}/"


def extract_citations(text: str) -> list[str]:
    """Extracts legal citations using eyecite if available, else falling back to regex"""
    try:
        from eyecite import get_citations

        citations = get_citations(text)
        return [str(c) for c in citations]
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