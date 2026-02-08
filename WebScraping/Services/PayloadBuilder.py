from typing import Any, Dict, List, Tuple


def parse_coauthors(bib: Dict[str, Any]) -> List[str]:
    coauthors = bib.get("author") or []
    if isinstance(coauthors, str):
        return [a.strip() for a in coauthors.split(" and ") if a.strip()]
    if isinstance(coauthors, list):
        return [str(a).strip() for a in coauthors if str(a).strip()]
    return []


def build_research_payload(
    *,
    title: str,
    pub_year: str,
    journal: str,
    publisher: str,
    no_of_citations: int,
    pages: str,
    volume: str,
    number: str,
    external_url: str,
    abstract: str,
    related_pub_url: str | None,
    contributions_payload: List[Dict[str, Any]],
    cites_payload: List[Dict[str, Any]],
    created_at: str | None,
) -> Dict[str, Any]:
    return {
        "DOI": "Not Avaliable",
        "Title": title,
        "Source": "Google Scholar",
        "PubYear": str(pub_year),
        "PubDate": None,
        "Journal": journal,
        "Publisher": publisher,
        "NoOfCititations": int(no_of_citations or 0),
        "IsConfirmed": "False",
        "created_at": created_at,
        "NoOfPages": pages,
        "Volume": volume,
        "Number": number,
        "ResearchLink": str(external_url),
        "Abstract": abstract,
        "RelatedResearchLink": str(related_pub_url) if related_pub_url else None,
        "Contributions": contributions_payload,
        "Cites": cites_payload,
    }
